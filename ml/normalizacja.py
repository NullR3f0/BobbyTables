"""Normalizacja tekstu przed wektoryzacją"""
import html
from urllib.parse import unquote_plus


def normalizuj(tekst: str) -> str:
    """Sprowadza różne zapisy tego samego ataku do jednej postaci."""
    tekst = str(tekst)
    for _ in range(2):
        zdekodowany = html.unescape(unquote_plus(tekst))
        if zdekodowany == tekst:
            break
        tekst = zdekodowany
    return tekst.lower()
