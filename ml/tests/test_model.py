"""Testy modelu i predykcji"""
import numpy as np
import pytest

from predykcja import Detektor, podziel_na_okna
from trenuj_model import trenuj, wybierz_prog

SIATKA_TESTOWA = {"tfidf__ngram_range": [(1, 3)], "clf__C": [10.0]}


@pytest.fixture
def wytrenowany(maly_zbior):
    model, info, _ = trenuj(maly_zbior["payload"], maly_zbior["label"].values, SIATKA_TESTOWA, verbose=0)
    return model, info


def test_powtarzalnosc_dwa_treningi_daja_to_samo(maly_zbior):
    X, y = maly_zbior["payload"], maly_zbior["label"].values
    m1, info1, _ = trenuj(X, y, SIATKA_TESTOWA, verbose=0)
    m2, info2, _ = trenuj(X, y, SIATKA_TESTOWA, verbose=0)
    assert info1["prog"] == info2["prog"]
    assert np.allclose(m1.decision_function(X), m2.decision_function(X))


def test_wybierz_prog_spelnia_fpr():
    y = np.array([0] * 100 + [1] * 100)
    wyniki = np.concatenate([np.linspace(-3, 1, 100), np.linspace(0, 4, 100)])
    prog, recall, fpr = wybierz_prog(y, wyniki, docelowy_fpr=0.01)
    assert fpr <= 0.01
    assert ((wyniki[y == 0] >= prog).mean()) <= 0.01


def test_model_rozpoznaje_oczywiste_przypadki(wytrenowany):
    detektor = Detektor(wytrenowany[0], wytrenowany[1]["prog"])
    assert detektor.ocen("<script>alert('x')</script>")["malicious"]
    assert not detektor.ocen("Sprzedam rower")["malicious"]


@pytest.mark.parametrize("wejscie", [None, "", "   ", 12345, "ą" * 20])
def test_dziwne_wejscie_nie_wywraca_detektora(wytrenowany, wejscie):
    wynik = Detektor(wytrenowany[0], wytrenowany[1]["prog"]).ocen(wejscie)
    assert set(wynik) == {"malicious", "score", "confidence", "threshold", "note"}


class AtrapaModelu:
    """Udaje model do testu okien."""
    def decision_function(self, okna):
        return np.array([10.0 if "<script" in o else -10.0 for o in okna])


def test_atak_na_koncu_dlugiego_payloadu_jest_wykryty():
    detektor = Detektor(AtrapaModelu(), prog=0.0, dlugosc_okna=100)
    dlugi = "Opis aukcji. " * 2000 + "<script>alert(document.cookie)</script>"
    wynik = detektor.ocen(dlugi)
    assert wynik["malicious"] and "okn" in wynik["note"]


def test_okna_pokrywaja_caly_tekst_z_zakladka():
    tekst = "".join(chr(65 + i % 26) for i in range(1000))
    okna = podziel_na_okna(tekst, 100)
    assert all(len(o) <= 100 for o in okna)
    assert okna[0] == tekst[:100] and tekst.endswith(okna[-1])
    # każdy fragment długości <= 25 mieści się w całości w oknie
    assert all(any(tekst[i:i + 25] in o for o in okna) for i in range(len(tekst) - 25))
