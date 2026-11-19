import re
import sys

import numpy as np

from normalizacja import normalizuj

# Każdy wzorzec = jedna "reguła" z list WAF / cheat-sheetów OWASP.
WZORCE = {
    # --- SQL injection ---
    "sqli_tautologia": r"['\"]\s*(or|and)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+",  # ' or 'a'='a
    "sqli_or_1_1": r"\bor\s+1\s*=\s*1\b",
    "sqli_union": r"\bunion\s+(all\s+)?select\b",
    "sqli_stacked": r";\s*(drop|delete|insert|update|shutdown|exec)\b",
    "sqli_komentarz": r"['\"]\s*(--|#|/\*)",                                  # ' --
    "sqli_czasowe": r"\b(sleep|benchmark)\s*\(|\bwaitfor\s+delay\b",
    # --- XSS ---
    "xss_script": r"<\s*script\b",
    "xss_handler": r"\bon[a-z]+\s*=",                                        # onerror=, onload=
    "xss_js_uri": r"javascript\s*:",
    "xss_tagi": r"<\s*(iframe|object|embed|svg|img)\b[^>]*(src|on|data)",
    "xss_funkcje": r"\b(alert|prompt|confirm|eval)\s*\(|document\.cookie",
}


class RegexBaseline:
    def __init__(self, wzorce=None):
        self.wzorce = {n: re.compile(w, re.IGNORECASE) for n, w in (wzorce or WZORCE).items()}

    def fit(self, X, y=None):       
        return self

    def dopasowane_reguly(self, tekst):
        tekst = normalizuj(tekst)
        return [nazwa for nazwa, wzorzec in self.wzorce.items() if wzorzec.search(tekst)]

    def predict(self, X):
        return np.array([1 if self.dopasowane_reguly(t) else 0 for t in X], dtype=int)


if __name__ == "__main__":
    tekst = sys.argv[1] if len(sys.argv) > 1 else "' or 1=1 --"
    reguly = RegexBaseline().dopasowane_reguly(tekst)
    print(f"{tekst!r} -> {'ATAK' if reguly else 'czysty'} {reguly}")
