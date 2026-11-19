import os
from pathlib import Path

SEED = 25772            # wspólny seed dla całego projektu
TEST_SIZE = 0.2      # 20% danych idzie do zbioru testowego

KATALOG_KODU = Path(__file__).resolve().parent
KATALOG_ROBOCZY = Path(os.environ.get("BOBBY_KATALOG_ROBOCZY", KATALOG_KODU))

DATA_RAW = KATALOG_ROBOCZY / "data" / "raw"
DATA_PROCESSED = KATALOG_ROBOCZY / "data" / "processed"
MODELS = KATALOG_ROBOCZY / "models"
RESULTS = KATALOG_ROBOCZY / "results"

TRAIN_CSV = DATA_PROCESSED / "train.csv"
TEST_CSV = DATA_PROCESSED / "test.csv"
MODEL_PATH = MODELS / "model.joblib"
PROG_PATH = MODELS / "prog.json"

PLIK_SQLI = DATA_RAW / "Modified_SQL_Dataset.csv"
KOLUMNA_SQLI_TEKST = "Query"
KOLUMNA_SQLI_ETYKIETA = "Label"      # 1 = atak, 0 = czysty

PLIK_XSS = DATA_RAW / "XSS_dataset.csv"
KOLUMNA_XSS_TEKST = "Sentence"
KOLUMNA_XSS_ETYKIETA = "Label"       # 1 = atak, 0 = czysty

KOLUMNY = ["payload", "label", "typ"]

DOCELOWY_FPR = 0.01          # maks. 1% false positive
DOCELOWY_RECALL = 0.95       # min. 95% wykrytych ataków
PRZEWAGA_NAD_BASELINE = 0.10  # recall min. o 10 pp. wyższy niż regex

DLUGOSC_PAYLOADU = 500 # Dłuższe payloady chunkujemy
DLUGOSC_OKNA = 500 # Dłuższe okna chunkujemy
