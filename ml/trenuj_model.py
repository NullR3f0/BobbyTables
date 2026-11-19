"""Trening modelu - TF-IDF na n-gramach znaków, a potem robiona jest regresja logistyczna.
    python trenuj_model.py - szybkie trenowanie na małej ilości parametrów
    python trenuj_model.py --pelna-siatka - pełny zakres/dłużej
"""
import json
import sys
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline

import config
from normalizacja import normalizuj

MALA_SIATKA = {
    "tfidf__ngram_range": [(1, 3), (1, 5)],
    "clf__C": [1.0, 10.0],
}
PELNA_SIATKA = {
    "tfidf__analyzer": ["char", "char_wb"],
    "tfidf__ngram_range": [(1, 3), (1, 4), (1, 5)],
    "clf__C": [0.1, 1.0, 10.0],
}


def zbuduj_pipeline():
    """TF-IDF na n-gramach znaków + regresja logistyczna."""
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            preprocessor=normalizuj,   # dekodowanie URL/HTML + małe litery
            analyzer="char_wb",        # n-gramy znaków w obrębie słów
            ngram_range=(1, 5),
            min_df=2,                  # n-gram musi wystąpić min. w 2 dokumentach
            max_features=200_000,      # ograniczenie pamięci
            sublinear_tf=True,         # log zamiast surowej liczby wystąpień
        )),
        ("clf", LogisticRegression(
            C=10.0,                    # odwrotność siły regularyzacji
            class_weight="balanced",   # wyrównuje wagę klas
            solver="liblinear",
            max_iter=1000,
            random_state=config.SEED,
        )),
    ])


def walidacja_krzyzowa(n_splits=3, seed=config.SEED):
    # stały seed, żeby foldy były za każdym razem takie same
    return StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)


def wybierz_prog(y_true, wyniki, docelowy_fpr=config.DOCELOWY_FPR):
    """Najniższy próg, przy którym FPR <= docelowy_fpr, czyli największy możliwy recall."""
    fpr, tpr, progi = roc_curve(y_true, wyniki)
    dozwolone = np.where(fpr <= docelowy_fpr)[0]
    i = dozwolone[np.argmax(tpr[dozwolone])]
    return float(progi[i]), float(tpr[i]), float(fpr[i])


def trenuj(X, y, siatka=MALA_SIATKA, n_splits=3, seed=config.SEED, verbose=1):
    """GridSearch, próg z CV i model na całym train. Zwraca model, info i wyniki_grid_search."""
    cv = walidacja_krzyzowa(n_splits, seed)

    # roc_auc, czyli jak dobrze model szereguje ataki nad czystymi wpisami, niezależnie od progu.
    szukacz = GridSearchCV(zbuduj_pipeline(), siatka, cv=cv, scoring="roc_auc",
                           n_jobs=-1, verbose=verbose)
    szukacz.fit(X, y)

    # Wyniki dla każdego przykładu z train, liczone modelem, który go nie widział.
    wyniki_cv = cross_val_predict(szukacz.best_estimator_, X, y, cv=cv,
                                  method="decision_function", n_jobs=-1)
    prog, recall_cv, fpr_cv = wybierz_prog(y, wyniki_cv)

    info = {
        "najlepsze_parametry": {k: list(v) if isinstance(v, tuple) else v
                                for k, v in szukacz.best_params_.items()},
        "roc_auc_cv": round(float(szukacz.best_score_), 5),
        "prog": prog,
        "recall_cv_przy_progu": round(recall_cv, 5),
        "fpr_cv_przy_progu": round(fpr_cv, 5),
        "docelowy_fpr": config.DOCELOWY_FPR,
        # Okno do oceny długich payloadów, czyli dłuższe niż 95% w train
        "dlugosc_okna": int(max(50, np.percentile(pd.Series(X).str.len(), 95))),
    }
    # GridSearch po wyborze parametrów sam trenuje najlepszy model na całym X
    return szukacz.best_estimator_, info, pd.DataFrame(szukacz.cv_results_)


def main():
    pelna_siatka = "--pelna-siatka" in sys.argv

    train = pd.read_csv(config.TRAIN_CSV, keep_default_na=False)
    X, y = train["payload"], train["label"].values
    print(f"Train: {len(train)} przykładów, ataki: {y.mean():.1%}")

    start = time.time()
    model, info, cv_results = trenuj(X, y, PELNA_SIATKA if pelna_siatka else MALA_SIATKA)
    info["czas_treningu_s"] = round(time.time() - start, 1)

    config.MODELS.mkdir(parents=True, exist_ok=True)
    config.RESULTS.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, config.MODEL_PATH)
    with open(config.PROG_PATH, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)

    kolumny = [c for c in cv_results.columns if c.startswith("param_")] + ["mean_test_score", "std_test_score", "mean_fit_time"]
    cv_results[kolumny].sort_values("mean_test_score", ascending=False).to_csv(
        config.RESULTS / "grid_search.csv", index=False)

    print(json.dumps(info, indent=2, ensure_ascii=False))
    print(f"\nZapisano {config.MODEL_PATH} i {config.PROG_PATH}")


if __name__ == "__main__":
    main()
