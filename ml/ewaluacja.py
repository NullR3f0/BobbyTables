"""
Uruchomienie:
    python ewaluacja.py                # ocena na zbiorze testowym
    python ewaluacja.py --podzialy 5   # 5 różnych podziałów train/test
"""
import json
import sys

import joblib
import matplotlib

matplotlib.use("Agg")  # rysowanie do plików
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (ConfusionMatrixDisplay, confusion_matrix, f1_score,
                             precision_recall_curve, precision_score, recall_score, roc_curve)

import config
from baseline_regex import RegexBaseline
from przygotuj_dane import podziel


def metryki(y_true, y_pred):
    """Metryki z macierzy pomyłek"""
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),        # TP / (TP + FN)
        "fpr": round(float(fp / (fp + tn)) if (fp + tn) else 0.0, 4),                     # FP / (FP + TN)
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),  # TP / (TP + FP)
        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "macierz": {"TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp)},
    }


def recall_wg_typu(test, y_pred):
    """ Odsetek wykrytych ataków wg typu"""
    wynik = {}
    for typ in ["sqli", "xss"]:
        maska = (test["typ"] == typ).values
        if maska.any():
            wynik[typ] = round(float(y_pred[maska].mean()), 4)
    return wynik


def czy_sukces(m_model, m_baseline):
    return {
        f"recall >= {config.DOCELOWY_RECALL}": bool(m_model["recall"] >= config.DOCELOWY_RECALL),
        f"fpr <= {config.DOCELOWY_FPR}": bool(m_model["fpr"] <= config.DOCELOWY_FPR),
        f"recall - baseline >= {config.PRZEWAGA_NAD_BASELINE}":
            bool(m_model["recall"] - m_baseline["recall"] >= config.PRZEWAGA_NAD_BASELINE),
    }


def rysuj(y, wyniki, prog, y_pred, m_baseline):
    config.RESULTS.mkdir(parents=True, exist_ok=True)

    ConfusionMatrixDisplay.from_predictions(y, y_pred, display_labels=["czysty", "atak"], cmap="Blues")
    plt.title("Macierz pomyłek - model (zbiór testowy)")
    plt.savefig(config.RESULTS / "macierz_pomylek.png", dpi=150, bbox_inches="tight")
    plt.close()

    fpr, tpr, _ = roc_curve(y, wyniki)
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, label="model (TF-IDF + LogReg)")
    plt.plot(m_baseline["fpr"], m_baseline["recall"], "rs", label="baseline regex")
    plt.axvline(config.DOCELOWY_FPR, color="gray", ls="--", label=f"FPR = {config.DOCELOWY_FPR:.0%}")
    plt.xscale("log")
    plt.xlim(1e-4, 1)
    plt.xlabel("FPR (odsetek czystych oznaczonych jako atak), skala log")
    plt.ylabel("Recall (odsetek wykrytych ataków)")
    plt.title("Krzywa ROC")
    plt.legend(loc="lower right")
    plt.grid(alpha=0.3)
    plt.savefig(config.RESULTS / "krzywa_roc.png", dpi=150, bbox_inches="tight")
    plt.close()

    precyzja, czulosc, progi = precision_recall_curve(y, wyniki)
    plt.figure(figsize=(6, 5))
    plt.plot(progi, precyzja[:-1], label="precision")
    plt.plot(progi, czulosc[:-1], label="recall")
    plt.axvline(prog, color="gray", ls="--", label=f"wybrany próg = {prog:.2f}")
    plt.xlabel("próg decyzji (decision_function)")
    plt.title("Precision i recall w zależności od progu")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.savefig(config.RESULTS / "precision_recall_vs_prog.png", dpi=150, bbox_inches="tight")
    plt.close()


def zapisz_bledy(test, wyniki, y_pred, ile=30):
    """Najbardziej "pewne" pomyłki - materiał do sekcji Ograniczenia."""
    df = test.assign(score=wyniki, pred=y_pred)
    fp = df[(df["label"] == 0) & (df["pred"] == 1)].sort_values("score", ascending=False).head(ile)
    fn = df[(df["label"] == 1) & (df["pred"] == 0)].sort_values("score").head(ile)
    fp.to_csv(config.RESULTS / "bledy_fp.csv", index=False)
    fn.to_csv(config.RESULTS / "bledy_fn.csv", index=False)
    return len(fp), len(fn)


def tabela_markdown(df):
    """DataFrame -> tabela Markdown do wklejenia w dokumentację."""
    wiersze = ["| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
    wiersze += ["| " + " | ".join(str(v) for v in w) + " |" for w in df.itertuples(index=False)]
    return "\n".join(wiersze)


def eksperyment_podzialy(liczba):
    """Ten sam przepis treningu na kilku różnych podziałach train/test.

    Pokazuje, czy wynik nie jest "szczęśliwym trafem" jednego podziału.
    Dla każdego podziału próg jest dobierany od nowa, tylko na jego części treningowej
    """
    from trenuj_model import trenuj  # import tutaj, bo potrzebny tylko w tym trybie

    wszystko = pd.concat([pd.read_csv(config.TRAIN_CSV, keep_default_na=False),
                          pd.read_csv(config.TEST_CSV, keep_default_na=False)], ignore_index=True)
    with open(config.PROG_PATH, encoding="utf-8") as f:
        parametry = json.load(f)["najlepsze_parametry"]
    siatka = {k: [tuple(v) if isinstance(v, list) else v] for k, v in parametry.items()}  # bez szukania

    wiersze = []
    for seed in range(liczba):
        train, test = podziel(wszystko, seed=seed)
        model, info, _ = trenuj(train["payload"], train["label"].values, siatka, seed=seed, verbose=0)
        y_pred = (model.decision_function(test["payload"]) >= info["prog"]).astype(int)
        m = metryki(test["label"].values, y_pred)
        b = metryki(test["label"].values, RegexBaseline().predict(test["payload"]))
        wiersze.append({"podzial (seed)": seed,
                        "baseline recall": b["recall"], "baseline FPR": b["fpr"],
                        "model recall": m["recall"], "model FPR": m["fpr"]})
        print(wiersze[-1])

    tabela = pd.DataFrame(wiersze)
    srednia = tabela.drop(columns="podzial (seed)").agg(["mean", "std"]).round(4)
    srednia.insert(0, "podzial (seed)", ["średnia", "odch. std"])
    tekst = tabela_markdown(pd.concat([tabela, srednia], ignore_index=True))
    (config.RESULTS / "tabela_przypadki.md").write_text(tekst, encoding="utf-8")
    print("\n" + tekst)


def main():
    # sys.argv = lista słów wpisanych w terminalu, np. ["ewaluacja.py", "--podzialy", "5"]
    # Jeśli jest "--podzialy", liczba stoi zaraz za nim.
    liczba_podzialow = 0
    if "--podzialy" in sys.argv:
        liczba_podzialow = int(sys.argv[sys.argv.index("--podzialy") + 1])

    test = pd.read_csv(config.TEST_CSV, keep_default_na=False)
    model = joblib.load(config.MODEL_PATH)
    with open(config.PROG_PATH, encoding="utf-8") as f:
        prog = json.load(f)["prog"]

    X, y = test["payload"], test["label"].values
    wyniki = model.decision_function(X)
    y_model = (wyniki >= prog).astype(int)
    y_baseline = RegexBaseline().predict(X)

    m_model, m_baseline = metryki(y, y_model), metryki(y, y_baseline)
    raport = {
        "liczba_przykladow_testowych": len(test),
        "prog": prog,
        "model": {**m_model, "recall_wg_typu": recall_wg_typu(test, y_model)},
        "baseline_regex": {**m_baseline, "recall_wg_typu": recall_wg_typu(test, y_baseline)},
        "kryteria_sukcesu": czy_sukces(m_model, m_baseline),
    }

    rysuj(y, wyniki, prog, y_model, m_baseline)
    ile_fp, ile_fn = zapisz_bledy(test, wyniki, y_model)
    with open(config.RESULTS / "metryki.json", "w", encoding="utf-8") as f:
        json.dump(raport, f, indent=2, ensure_ascii=False)

    print(json.dumps(raport, indent=2, ensure_ascii=False))
    print(f"\nWykresy i błędy ({ile_fp} FP, {ile_fn} FN) zapisane w {config.RESULTS}")

    if liczba_podzialow > 0:
        eksperyment_podzialy(liczba_podzialow)


if __name__ == "__main__":
    main()
