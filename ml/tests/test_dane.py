import numpy as np
import pandas as pd
import pytest

import config
from przygotuj_dane import podziel, wyczysc


def test_wyczysc_usuwa_braki_puste_i_zle_etykiety():
    df = pd.DataFrame({
        "payload": ["ok", None, "   ", "zła etykieta", "dobry atak"],
        "label": [0, 1, 0, 7, 1],
        "typ": ["czysty", "sqli", "czysty", None, "xss"],
    })
    wynik, raport = wyczysc(df)
    assert list(wynik["payload"]) == ["ok", "dobry atak"]
    assert raport["na_wejsciu"] == 5 and raport["na_wyjsciu"] == 2


def test_wyczysc_usuwa_duplikaty_i_sprzecznosci():
    df = pd.DataFrame({
        "payload": ["a", "a", "b", "b"],
        "label": [1, 1, 0, 1],         # "a" to duplikat, "b" ma sprzeczne etykiety
        "typ": ["sqli", "sqli", "czysty", "sqli"],
    })
    wynik, _ = wyczysc(df)
    assert list(wynik["payload"]) == ["a"]


def test_podzial_bez_wspolnych_payloadow(maly_zbior):
    df, _ = wyczysc(maly_zbior)
    train, test = podziel(df)
    assert not set(train["payload"]) & set(test["payload"])
    roznica = train["typ"].value_counts(normalize=True) - test["typ"].value_counts(normalize=True)
    assert np.abs(roznica).max() < 0.05


def test_podzial_jest_powtarzalny(maly_zbior):
    df, _ = wyczysc(maly_zbior)
    assert podziel(df)[1].index.equals(podziel(df)[1].index)


@pytest.mark.skipif(not config.TEST_CSV.exists(), reason="brak przygotowanych danych")
def test_prawdziwe_dane_bez_wycieku():
    train = pd.read_csv(config.TRAIN_CSV, keep_default_na=False)
    test = pd.read_csv(config.TEST_CSV, keep_default_na=False)
    assert list(train.columns) == config.KOLUMNY
    assert not set(train["payload"]) & set(test["payload"])
    assert (train["payload"] != "").all() and (test["payload"] != "").all()