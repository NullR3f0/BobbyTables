import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # import modułów z katalogu nadrzędnego

ATAKI_SQLI = [
    "' or 1=1 --", "admin' --", "1' union select username, password from users --",
    "1; drop table users", "' or 'a'='a", "1' and sleep(5) --", "\" or \"\"=\"",
    "1' order by 3 --", "' union all select null, null --", "x' or 1=1#",
]
ATAKI_XSS = [
    "<script>alert(1)</script>", "<img src=x onerror=alert(1)>", "<svg onload=alert(document.cookie)>",
    "<a href=\"javascript:alert(1)\">klik</a>", "<body onload=prompt(1)>", "%3Cscript%3Ealert(1)%3C/script%3E",
    "<iframe src=javascript:alert(1)>", "<div onmouseover=\"alert(1)\">x</div>",
    "<video><source onerror=alert(1)></video>", "&lt;script&gt;alert(1)&lt;/script&gt;",
]
CZYSTE = [
    "Sprzedam rower w dobrym stanie", "Jan Kowalski", "select the best option", "Ile kosztuje wysyłka?",
    "<b>Nowy</b> telefon, gwarancja", "<p>Opis aukcji</p>", "Zamówienie nr 12345", "tak, oczywiście",
    "Union Square apartment", "Kontakt: jan@example.com", "Cena do negocjacji", "<i>Okazja</i>",
    "Wymiary 20x30 cm", "Pozdrawiam serdecznie", "Działa bez zarzutu", "Odbiór osobisty w Poznaniu",
    "<ul><li>Pamięć 128GB</li></ul>", "Bardzo polecam sprzedawcę", "Kolor: czarny", "Rok produkcji 2020",
]

# Fixture dla wszystkich testów, tak abyśmy nie mielili niepotrzebnie całego kaggle'a, a także mieli jeden wspólny zbiór dla nich
@pytest.fixture
def maly_zbior():
    wiersze = []
    for i in range(6):
        wiersze += [(f"{t} {i}", 1, "sqli") for t in ATAKI_SQLI]
        wiersze += [(f"{t} {i}", 1, "xss") for t in ATAKI_XSS]
        wiersze += [(f"{t} {i}", 0, "czysty") for t in CZYSTE]
    return pd.DataFrame(wiersze, columns=["payload", "label", "typ"])
