[Si karta tematu szablon.md](https://github.com/user-attachments/files/33116963/Si.karta.tematu.szablon.md)
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

_Co system ma robić i dla kogo. Opis sytuacji, nie nazwy technologii. 3–5 zdań._

## 4. Dlaczego zwykły algorytm nie wystarczy

_Wskażcie jeden z trzech powodów omawianych na zajęciach i uzasadnijcie:_

- [ X ] reguł jest za dużo i zmieniają się w czasie

_Uzasadnienie, 2–3 zdania:_

Sposobów wykonywania ataków XSS i SQL Injection są setki tysięcy. Syntax za pomocą którego można wykonać atak XSS jest zbyt szeroki - mogą to być eventy onmouseenter, mountujące się na starcie tagi video z autoplayem, który wywołuje malicious code itd.

Zakres jest zbyt duży by móc to zweryfikować zwykłym regexem lub ifami/strategiami.

## 5. Technologia SI

- [ ] sieć neuronowa
- [ X ] system ekspertowy / wnioskowanie regułowe
- [ ] algorytm genetyczny
- [ ] klasyczne uczenie maszynowe
- [ ] inne:

_Dlaczego akurat ta technologia pasuje do tego problemu, 2–3 zdania:_
Do rozpoznawania ataków SQL i XSS jest potrzebna ekspercka znajomość tematu oraz wnioskowania regułowego.
Reguł w rozpoznawaniu ataków jest zbyt dużo, aby móc to zapisać w inny sposób. Algorytm genetyczny odpada całkowicie, a klasyczne uczenie może patrzeć zbyt płytko.

## 6. Dane

|                      |                         |
| -------------------- | ----------------------- |
| Źródło               | https://www.kaggle.com/ |
| Rozmiar i format     | .csv                    |
| Czy są już dostępne? | tak                     |

## 7. Stos technologiczny

- Python, Sci-Kit, Pandas
- .NET, Tensorflow .NET
- Docker

## 8. Kryterium sukcesu

Lepsza detekcja niż baseline Regex

## 9. Zakres minimalny

API wołające wytrenowany model, próbujący wykrywać ataki XSS/SQL injection w otrzymanym payloadzie

## 10. Zakres opcjonalny

- Frontend aplikacji do zaprezentowania działania modelu poprzez prezentację na bazie fikcyjnego portalu aukcyjnego
- Klucze licencyjne i ich walidacja

## 11. Repozytorium

_Link:_

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
