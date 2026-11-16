"""Normalizacja tekstu przed wektoryzacją (odpowiada: Cyprian).

Dlaczego osobny plik? Funkcja trafia do Pipeline'u jako `preprocessor`
TfidfVectorizera, a joblib zapisuje ją jako referencję "moduł.funkcja".
Gdyby była zdefiniowana w trenuj_model.py uruchamianym jako skrypt,
zapisałaby się jako "__main__.normalizuj" i serwer nie umiałby wczytać modelu.
"""
import html
from urllib.parse import unquote_plus


def normalizuj(tekst: str) -> str:
    """Sprowadza różne zapisy tego samego ataku do jednej postaci.

    Przykład: "%3Cscript%3E", "&lt;script&gt;" i "<SCRIPT>" -> "<script>".
    """
    tekst = str(tekst)
    # Atakujący często kodują payload kilka razy, dlatego dekodujemy do 2 razy.
    for _ in range(2):
        zdekodowany = html.unescape(unquote_plus(tekst))
        if zdekodowany == tekst:
            break
        tekst = zdekodowany
    return tekst.lower()
