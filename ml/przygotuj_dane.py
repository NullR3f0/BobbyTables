import sys
import json

import pandas as pd
from sklearn.model_selection import train_test_split

import config


def wczytaj_zbior(plik, kolumna_tekst, kolumna_etykieta, typ_ataku):
    if not plik.exists():
        raise FileNotFoundError(
            f"Brak pliku {plik}"
            f"wrzuć go do {config.DATA_RAW}."
        )
    df = pd.read_csv(plik, encoding="utf-8", encoding_errors="replace")
    brakujace = {kolumna_tekst, kolumna_etykieta} - set(df.columns)
    if brakujace:
        raise KeyError(
            f"W pliku {plik.name} nie ma kolumn {brakujace}. "
            f"Dostępne kolumny: {list(df.columns)}"
        )
    df = df[[kolumna_tekst, kolumna_etykieta]].rename(
        columns={kolumna_tekst: "payload", kolumna_etykieta: "label"}
    )
    df["label"] = pd.to_numeric(df["label"], errors="coerce")
    df["typ"] = df["label"].map({1: typ_ataku, 0: "czysty"})
    return df


# Czyścimy dataset - wyrzucamy puste wiersze, duplikaty, sprzeczności itd.
# Wyrzucamy również duplikaty przed podziałem, inaczej to samo trafiłoby do splitu train/test, zawyżając wynik
def wyczysc(df, deduplikuj=True):
    raport = {"na_wejsciu": len(df)}

    df = df.dropna(subset=["payload", "label"]).copy()
    df["payload"] = df["payload"].astype(str).str.strip()
    df = df[df["payload"] != ""]
    df = df[df["label"].isin([0, 1])]
    df["label"] = df["label"].astype(int)
    raport["po_usunieciu_brakow"] = len(df)

    if deduplikuj:
        liczba_etykiet = df.groupby("payload")["label"].nunique()
        sprzeczne = liczba_etykiet[liczba_etykiet > 1].index
        df = df[~df["payload"].isin(sprzeczne)]
        raport["usuniete_sprzeczne_payloady"] = int(len(sprzeczne))
        df = df.drop_duplicates(subset="payload")
        raport["po_deduplikacji"] = len(df)

    raport["na_wyjsciu"] = len(df)
    return df.reset_index(drop=True), raport


def podziel(df, seed=config.SEED, test_size=config.TEST_SIZE):
    return train_test_split(df, test_size=test_size, stratify=df["typ"], random_state=seed)


def statystyki(df):
    dlugosci = df["payload"].str.len()
    return {
        "liczba_wierszy": len(df),
        "liczba_wg_typu": df["typ"].value_counts().to_dict(),
        "odsetek_atakow": round(float(df["label"].mean()), 4),
        "dlugosc_payloadu": {
            "min": int(dlugosci.min()),
            "mediana": float(dlugosci.median()),
            "max": int(dlugosci.max()),
        },
    }


def main():
    bez_deduplikacji = "--bez-deduplikacji" in sys.argv

    sqli = wczytaj_zbior(config.PLIK_SQLI, config.KOLUMNA_SQLI_TEKST, config.KOLUMNA_SQLI_ETYKIETA, "sqli")
    xss = wczytaj_zbior(config.PLIK_XSS, config.KOLUMNA_XSS_TEKST, config.KOLUMNA_XSS_ETYKIETA, "xss")
    print(f"Wczytano: SQLi {len(sqli)} wierszy, XSS {len(xss)} wierszy")

    df, raport = wyczysc(pd.concat([sqli, xss], ignore_index=True), deduplikuj=not bez_deduplikacji)
    train, test = podziel(df)

    wyciek = set(train["payload"]) & set(test["payload"])
    if wyciek and not bez_deduplikacji:
        raise RuntimeError(f"{len(wyciek)} payloadów jest w train i test - to wyciek danych!")

    config.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    config.RESULTS.mkdir(parents=True, exist_ok=True)
    train[config.KOLUMNY].to_csv(config.TRAIN_CSV, index=False)
    test[config.KOLUMNY].to_csv(config.TEST_CSV, index=False)

    wynik = {
        "czyszczenie": raport,
        "wspolne_payloady_train_test": len(wyciek),
        "train": statystyki(train),
        "test": statystyki(test),
    }
    
    with open(config.RESULTS / "statystyki_danych.json", "w", encoding="utf-8") as f:
        json.dump(wynik, f, indent=2, ensure_ascii=False)

    print(json.dumps(wynik, indent=2, ensure_ascii=False))
    print(f"\nZapisano {config.TRAIN_CSV} i {config.TEST_CSV}")


if __name__ == "__main__":
    main()
