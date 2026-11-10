# Procedura pracy i kontroli zakresu — optymalizator modów

**Status:** obowiązkowa procedura operacyjna dla każdej pracy nad optymalizatorem SWGOH.  
**Branch roboczy:** `optimizer-v2`.  
**Cel:** zapobiegać samowolnemu rozszerzaniu zakresu, pomijaniu ustaleń i wykonywaniu niezamówionych zmian.

## 1. Kolejność dokumentacji przed rozpoczęciem pracy

Przed każdą analizą, raportem, zmianą kodu lub aktualizacją danych ChatGPT musi sprawdzić:

1. ten dokument — granice zlecenia i zasady zatwierdzania;
2. `MOD_OPTIMIZATION_RULES.md` — wymagania analizy i raportu;
3. `MOD_PROFILE_REFRESH.md` — pobieranie profili i ich świeżość;
4. `GRANDIVORY_METHOD_REVIEW.md` — aktualna architektura, algorytm i jawne ograniczenia, jeśli zadanie dotyczy implementacji lub interpretacji działania algorytmu.

Nie wolno polegać wyłącznie na streszczeniu rozmowy, pamięci ani wcześniejszym raporcie, jeżeli aktualny plik w repozytorium można odczytać.

## 2. Zamknięty zakres zlecenia

- Zakres pracy wyznacza ostatnia wyraźna prośba użytkownika wraz z nadal obowiązującymi ustaleniami.
- Wykonuj tylko czynności potrzebne do realizacji tego zakresu.
- Nie rozszerzaj zadania na inne postacie, profile, funkcje, pliki, workflow ani refaktoryzację tylko dlatego, że zauważono taką możliwość.
- W optymalizacji profili SWGOH.GG pobieraj dane wyłącznie dla postaci docelowej i dawców należących do aktualnego łańcucha. **Zakaz masowego profilowania rosteru lub wszystkich postaci w grze.**
- Nie zmieniaj istniejących statusów, rekordów ani danych, jeśli nie wpływają na wykonanie zleconego zadania lub użytkownik nie poprosił o ich korektę.
- Nie poprawiaj „przy okazji” niezwiązanych problemów. Zapisz obserwację i zapytaj o zgodę, zanim zaczniesz ją realizować.

## 3. Zasada zgody na zmianę zakresu

Jeżeli w trakcie pracy pojawi się działanie wykraczające poza zlecenie:

1. zatrzymaj się przed wykonaniem tej czynności;
2. krótko wyjaśnij, co zostało zauważone i dlaczego może mieć znaczenie;
3. wskaż proponowaną dodatkową zmianę oraz jej wpływ;
4. poczekaj na jednoznaczną zgodę użytkownika.

Brak sprzeciwu, wcześniejsza zgoda na inne zadanie ani techniczna możliwość wykonania zmiany nie oznaczają zgody. Nie wolno interpretować ogólnego „kontynuuj” jako akceptacji nowego, nieuzgodnionego zakresu, jeśli nie wynika on jasno z kontekstu.

## 4. Zasady profili — bez wyjątków ad hoc

- Obowiązuje TTL **5 dni** liczony od `fetched_at_utc` lub `refreshed_at_utc`; `checked_at_utc` nie odnawia TTL.
- Profil świeży i kompletny: użyj cache, bez ponownego pobierania stron.
- Profil nieobecny: pobierz oba wymagane źródła.
- Profil starszy niż 5 dni albo niekompletny: odśwież/uzupełnij oba źródła zgodnie z `MOD_PROFILE_REFRESH.md`.
- Sprawdzaj tylko uczestników aktualnego łańcucha: cel i rzeczywistych dawców.
- Zmiana łańcucha po ponownej optymalizacji oznacza kontrolę nowych uczestników, a nie rozszerzenie na cały roster.
- Nie zmieniaj progu świeżości ani źródeł bez zgody użytkownika.

## 5. Zasady zmian w repozytorium

- Pracuj na `optimizer-v2`, chyba że użytkownik wyraźnie wskaże inny branch.
- Nie zmieniaj `main` ani stabilnej wersji przez przypadek.
- Przed edycją odczytaj aktualną wersję pliku i sprawdź, czy zmiana jest zgodna z jego rzeczywistą zawartością.
- Ogranicz commit do plików koniecznych dla zlecenia.
- Nie nadpisuj danych ani nie usuwaj historii/profili, których zmiana nie jest wymagana.
- Po zapisie wykonaj read-back z GitHuba i sprawdź treść, branch oraz commit.
- Nie deklaruj wykonania zmiany przed potwierdzeniem zapisu.

## 6. Kontrola przed rozpoczęciem i przed zakończeniem

### Przed rozpoczęciem

- [ ] Odczytano obowiązujące dokumenty.
- [ ] Jednoznacznie określono cel i zakres bieżącego zlecenia.
- [ ] Wskazano, które dane/postacie/pliki są potrzebne.
- [ ] Sprawdzono, czy plan nie obejmuje niezamówionych działań.
- [ ] Potwierdzono właściwy branch.

### Przed zakończeniem

- [ ] Wykonano wyłącznie uzgodniony zakres.
- [ ] Nie dodano postaci ani profili spoza bieżącego łańcucha.
- [ ] Nie zmieniono niezwiązanych danych ani statusów.
- [ ] Wszystkie zmiany w repozytorium przeszły read-back.
- [ ] Niewykonane lub zablokowane punkty zostały jawnie wymienione.
- [ ] Każda dodatkowa sugestia została przedstawiona jako propozycja, a nie wykonana zmiana.

**Reguła blokująca:** jeśli nie wiadomo, czy czynność mieści się w uzgodnionym zakresie, nie wykonuj jej. Najpierw zapytaj użytkownika.

## 7. Krótka reguła operacyjna do stosowania w każdej rozmowie

**Najpierw sprawdź procedury. Następnie wykonaj wyłącznie zlecone zadanie. Profile pobieraj tylko dla celu i dawców aktualnego łańcucha, według TTL 5 dni. Każde rozszerzenie zakresu wymaga wcześniejszej zgody użytkownika.**
