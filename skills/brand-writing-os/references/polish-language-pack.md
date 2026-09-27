# Pakiet języka polskiego

Stosuj ten pakiet przy redagowaniu tekstu po polsku. Najpierw ustal, co tekst ma powiedzieć i jakie fakty potwierdzają źródła. Potem usuń pusty język, sprawdź kompozycję i dopracuj rytm. Reguły poniżej są wskazówkami redakcyjnymi, a nie zakazem każdego wystąpienia danego słowa.

## Sygnały do sprawdzenia

- Otwieracze bez treści: „W dzisiejszych czasach”, „W dobie”, „Warto zauważyć, że”, „Należy podkreślić, że”, „Nie jest tajemnicą, że”, „Co ciekawe”. Zacznij od rzeczy, którą czytelnik powinien wiedzieć.
- Wzmacniacze bez dowodu: „To kluczowe”, „I to zmienia wszystko”, „Nie sposób przecenić”. Pokaż skutek, jeśli źródła go potwierdzają.
- Mgliste oferty: „kompleksowe rozwiązania”, „holistyczne podejście”, „szeroki wachlarz usług”, „wartość dodana”, „dedykowane rozwiązanie”, „optymalizacja procesów”. Nazwij usługę, działanie lub korzyść.
- Metakomentarz: „Przyjrzyjmy się temu bliżej”, „W dalszej części omówimy”. Przejdź do sedna.
- Puste zakończenia: „Potencjał jest ogromny”, „To dopiero początek”, „Przyszłość należy do...”. Zakończ na ostatnim konkretnym ustaleniu.
- Nadużywane przysłówki i łączniki: „niezwykle”, „zdecydowanie”, „absolutnie”, „naprawdę”, „po prostu”, „tak naprawdę”, „de facto”, „innymi słowy”. Usuń je, gdy nie zmieniają znaczenia.
- Bierna i pozorna sprawczość: „zostało wdrożone”, „dane pokazują”, „technologia umożliwia”. Gdy źródło na to pozwala, nazwij osobę lub zespół i opisz czynność.
- Deklaracje udające doświadczenie: „Wierzcie mi”, „Będę z Wami szczery”, „Jako ktoś, kto...”. Jeśli autor ma własne doświadczenie, opisz je na podstawie materiału źródłowego.

Nie zamieniaj każdego trafienia na jeden stały synonim. Sprawdź zdanie w kontekście. Cytat źródłowy i świadomy wybór głosu mogą zostać.

## Tempo i kompozycja

- Otwieraj tekst od ustalenia, problemu albo pytania, które naprawdę wynika z materiału. Unikaj symetrycznych przeciwstawień, takich jak „To nie X, lecz Y”, używanych tylko dla efektu.
- Nie układaj wszystkich akapitów w podobnej długości. Krótki akapit ma mieć powód, podobnie jak dłuższe wyjaśnienie.
- Lista ma pomagać czytelnikowi. Nie dodawaj trzech punktów tylko po to, by tekst wyglądał na uporządkowany.
- Nie dopisuj podsumowania, które powtarza początek. Zatrzymaj się po ostatniej informacji, która coś wnosi.
- Przy serii tekstów zestaw obok siebie pierwsze zdania i zakończenia. Jeśli mają ten sam wzór, zmień budowę jednego z tekstów.
- Mieszaj budowę zdań, nie tylko ich długość. Po krótkim stwierdzeniu może przyjść wyjaśnienie, warunek albo przykład, jeśli są potrzebne.

Szczegół, liczba, cytat i opis doświadczenia muszą pochodzić z zatwierdzonego materiału. Nie dodawaj ich dla naturalnego brzmienia.

## Przykłady ilustracyjne

Poniższe sytuacje i firmy są wymyślone. Pokazują redakcję zdań, nie stanowią twierdzeń do publikacji.

**Przed:** „W dzisiejszych czasach nasze kompleksowe rozwiązanie zapewnia wartość dodaną małym piekarniom.”

**Po:** „Przykładowa piekarnia wpisuje zamówienia do jednego kalendarza. Pracownicy widzą w nim, co trzeba upiec następnego dnia.”

**Przed:** „Warto zauważyć, że nowy terminarz to dopiero początek. To kluczowe dla rozwoju salonu.”

**Po:** „W przykładowym salonie recepcja zapisuje wizyty w terminarzu. Na koniec dnia sprawdza w nim jutrzejszy grafik.”

## Kontrola skanerem

Uruchom `audit_copy.py tekst.md --language pl`. Skaner zgłasza wybrane frazy jako ostrzeżenia `polish-tell`; opcja `--strict` nadaje ostrzeżeniom kod wyjścia 1. To sygnał do oceny zdania, nie automatyczna decyzja o jego usunięciu. Własne zakazane frazy i wzorce marki nadal należą do profilu.
