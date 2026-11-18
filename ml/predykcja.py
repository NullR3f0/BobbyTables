"""Użycie wytrenowanego modelu na pojedynczym payloadzie"""

import json
import sys

import joblib
import numpy as np

import config


def podziel_na_okna(tekst, dlugosc):
    """Tnie długi tekst na okna z zakładką (1/4 okna), żeby nie przeciąć krótkich ataków."""
    if len(tekst) <= dlugosc:
        return [tekst]
    zakladka = dlugosc // 4
    krok = dlugosc - zakladka
    return [tekst[i:i + dlugosc] for i in range(0, len(tekst) - zakladka, krok)]


class Detektor:
    def __init__(self, model=None, prog=None, dlugosc_okna=None):
        """inicjalizuje długość okna, model, i próg z dysku jeśli są puste."""
        if model is None:
            if not config.MODEL_PATH.exists():
                raise FileNotFoundError(f"Brak {config.MODEL_PATH} - najpierw uruchom trenuj_model.py")
            model = joblib.load(config.MODEL_PATH)
        if prog is None:
            with open(config.PROG_PATH, encoding="utf-8") as f:
                info = json.load(f)
            prog = info["prog"]
            dlugosc_okna = dlugosc_okna or info.get("dlugosc_okna")
        self.model = model
        self.prog = float(prog)
        self.dlugosc_okna = int(dlugosc_okna or config.DLUGOSC_OKNA)

    def ocen(self, payload):
        """Zwraca wynik jako słownik. Nie wywala się, tylko zwraca uwage."""
        if payload is None:
            return self._wynik(False, None, uwaga="brak payloadu")
        if not isinstance(payload, str):
            payload = str(payload)  # np. liczba z JSON-a
        if payload.strip() == "":
            return self._wynik(False, None, uwaga="pusty payload")

        # Dzielimy payload na okna i bierzemy najgorszy, czyli najwyzszy wynik.
        okna = podziel_na_okna(payload, self.dlugosc_okna)
        wynik = float(np.max(self.model.decision_function(okna)))
        uwaga = f"oceniono w {len(okna)} oknach" if len(okna) > 1 else None
        return self._wynik(wynik >= self.prog, wynik, uwaga=uwaga)

    def _wynik(self, atak, wynik, uwaga=None):
        return {
            "malicious": bool(atak),
            "score": None if wynik is None else round(wynik, 4),
            # pewność w skali 0-1 (0.5 = dokładnie na progu)
            "confidence": None if wynik is None else round(float(1 / (1 + np.exp(-(wynik - self.prog)))), 4),
            "threshold": round(self.prog, 4),
            "note": uwaga,
        }


if __name__ == "__main__":
    tekst = sys.argv[1] if len(sys.argv) > 1 else "<img src=x onerror=alert(1)>"
    print(json.dumps(Detektor().ocen(tekst), indent=2, ensure_ascii=False))
