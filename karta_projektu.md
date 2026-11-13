**Grupa:** L3 (niestacjonarna) **Data zgłoszenia: 06.10.2026**

---

## 1. Skład zespołu

| Imię i nazwisko      | Nr albumu | Rola w zespole                         |
| -------------------- | --------- | -------------------------------------- |
| Cyprian Tomczak      | 31840     | implementacja, ewaluacja               |
| Piotr Bednarski      | 31071     | dokumentacja, implementacja, ewaluacja |
| Stanisław Kręgielski | 25772     | koordynacja, dane, implementacja       |

## 2. Tytuł projektu

**Po polsku: BobbyTables**

**Po angielsku: BobbyTables**

## 3. Problem

Aplikacja która otrzymuje od klienta żądanie HTTP z payloadem do weryfikacji. Wytrenowany model ma za zadanie zweryfikować czy otrzymany payload zawiera malicious code w postaci próby SQL injection lub XSS attack, czy jest jednak czysty. Przydatne dla usług, które korzystają z UGC i wymagają sanityzacji inputów, a chcą zezwolić na custom HTML lub inne powiązane funkcjonalności.

## 4. Dlaczego zwykły algorytm nie wystarczy

_Wskażcie jeden z trzech powodów omawianych na zajęciach i uzasadnijcie:_

- [x] reguł jest za dużo i zmieniają się w czasie

_Uzasadnienie, 2–3 zdania:_

Wariantów ataków XSS i SQL injection są setki tysięcy, a składnia, którą da się je wykonać, jest bardzo szeroka. Atrybuty typu `onmouseenter`, tagi `<video>` z autoplayem uruchamiającym złośliwy kod, kodowanie znaków i komentarze w zapytaniach SQL.
Lista regexów lub warunków if nigdy nie będzie kompletna i trzeba ją stale aktualizować.

Model SI natomiast uczy się wzorców z oznaczonych przykładów, więc nowe warianty będziemy musieli dodawać tylko jako dane treningowe, a nie pisać nowe reguły.

## 5. Technologia SI

- [ ] sieć neuronowa
- [ ] system ekspertowy / wnioskowanie regułowe
- [ ] algorytm genetyczny
- [x] klasyczne uczenie maszynowe
- [ ] inne:

_Dlaczego akurat ta technologia pasuje do tego problemu, 2–3 zdania:_

W zbiorach z Kaggle'a mamy tysiące oznaczonych przykładów na bazie atak/czysty, a payloady wysyłane przez userów również będą tekstem, więc nasz problem to klasyfikacja tekstu z nadzorem. Reguł w rozpoznawaniu ataków jest zbyt dużo, aby móc je zapisywać i rozszerzać ręcznie przez system ekspertowy. Algorytm genetyczny odpada całkowicie. Klasyczne ML dobrze wpasuje się tu również ze względu na n-gramy znaków i regresję logistyczną.
N-gramy pozwolą na wyłapywanie popularnych wektorów ataku takich jak `' or1=1`.

## 6. Dane

|                      |                         |
| -------------------- | ----------------------- |
| Źródło SQLi              | [dataset na kaggle ~31k wierszy](https://www.kaggle.com/datasets/sajid576/sql-injection-dataset)  |
| Źródło XSS              | [dataset na kaggle ~14k wierszy](https://www.kaggle.com/datasets/syedsaqlainhussain/cross-site-scripting-xss-dataset-for-deep-learning)  |
| Rozmiar i format     | .csv                    |
| Czy są już dostępne? | tak                     |

## 7. Stos technologiczny

- Python, Sci-Kit, Pandas, FastAPI
- .NET
- Docker

## 8. Kryterium sukcesu

Chcemy by na zbiorze testowym recall na atakach wynosił >= 95%, a odsetek false-positive'ów maksymalnie 1%.
Celujemy też, aby recall był co najmniej o 10 punktów procentowych wyższy niż baseline regex.
Punktem odniesienia będą typowe regexy na wzorce ataków pokroju `or1=1`, `<script on>` itd.

## 9. Zakres minimalny

API wołające wytrenowany model, próbujący wykrywać ataki XSS/SQL injection w otrzymanym payloadzie

## 10. Zakres opcjonalny

- Frontend aplikacji do zaprezentowania działania modelu poprzez prezentację na bazie fikcyjnego portalu aukcyjnego
- Klucze licencyjne i ich walidacja

## 11. Repozytorium

_Link:_ https://github.com/NullR3f0/BobbyTables

## 12. Główne ryzyko i plan awaryjny

Może się okazać, że model będzie wykrywał zbyt dużo false positive'ów, np. zobaczy tylko tagi HTML i od razu uzna je za malicious code.
Będziemy musieli go wtedy wytrenować na potencjalnie najczęściej używanych przy atakach XSS funkcjach.

## 13. Podział pracy w czasie

| Etap                     | Kto                       | Szacowany czas |
| ------------------------ | ------------------------- | -------------- |
| Dane i przygotowanie     | Stanisław                 | 3h             |
| Implementacja            | Stanisław, Cyprian, Piotr | 25h            |
| Eksperymenty i ewaluacja | Stanisław, Cyprian, Piotr | 5h             |
| Dokumentacja PL          | Stanisław, Cyprian, Piotr | 5h             |
| Dokumentacja EN          | Stanisław, Cyprian, Piotr | 5h             |
| Prezentacja              | Stanisław, Cyprian, Piotr | 1h             |
| **Razem na osobę**       |                           | **28–30 h**    |

---

## Decyzja prowadzącego

_Wypełnia prowadzący — nie edytujcie tej sekcji._

- [ ] zatwierdzony
- [ ] do poprawy

**Uwagi:**
