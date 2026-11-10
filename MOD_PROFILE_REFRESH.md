# Odświeżanie profili modów SWGOH.GG

**Obowiązujący sposób:** ręczny odczyt źródła przez ChatGPT na żądanie użytkownika. GitHub Actions i skrypty repozytorium nie pobierają profili ze SWGOH.GG.

## Świeżość danych i kontrola przy łańcuchach optymalizatora

- **Okres ważności profilu: 5 dni** od `fetched_at_utc` (lub równoważnego `refreshed_at_utc`, jeśli brak osobnego pola pobrania).
- Przy każdym uruchomieniu optymalizacji sprawdź wszystkie postacie występujące w pełnym łańcuchu: cel oraz wszystkich dawców.
- Jeśli postać nie istnieje w `mod_profiles.json`, pobierz i zweryfikuj jej profil z obu źródeł.
- Jeśli profil istnieje i jego dane źródłowe mają najwyżej 5 dni, wystarczy odnotować kontrolę (`checked_at_utc`); nie pobieraj ponownie stron.
- Jeśli profil jest starszy niż 5 dni, odśwież go z obu źródeł. Profil niekompletny wymaga uzupełnienia niezależnie od wieku.
- `checked_at_utc` oznacza ostatnią kontrolę, a nie datę pobrania — samo sprawdzenie nie przedłuża ważności danych. Ważność liczymy od `fetched_at_utc` / `refreshed_at_utc`.
- Nie zmieniaj danych profilu ani nie oznaczaj go jako świeżego wyłącznie na podstawie kontroli jego obecności.

## Przebieg

1. Użytkownik wskazuje postać (BASE_ID) lub prosi o odświeżenie konkretnego profilu.
2. ChatGPT otwiera stronę SWGOH.GG Best Mods dla tej postaci i odczytuje dostępne dane źródłowe.
3. Należy rozdzielić co najmniej dwa źródła/slice, jeżeli profil ma być zbudowany z Kyber GAC i Top 100 Guilds. Nie wolno zastępować brakującego slice domysłem ani powielać danych z pierwszej strony.
4. Każdy odczyt zapisuje się osobno w `source_model.sources[]`, wraz z dokładnym URL, nazwą slice, liczbą analizowanych jednostek (jeśli jest podana) oraz wartościami faktycznie widocznymi na stronie.
5. **Secondary Stat Focus: wymagane są wyłącznie cztery najwyżej sklasyfikowane statystyki (TOP 4) z każdego źródła.** Dla każdej z nich zapisujemy nazwę, `focus_pct` i `average`, zachowując dokładną kolejność podaną przez SWGOH.GG. Nie kopiujemy ani nie wymagamy pozycji 5–12. TOP 4 odczytujemy niezależnie dla każdego slice — listy mogą zawierać inne statystyki lub inną kolejność.
6. Pozostałe wymagane sekcje (kombinacje setów i primary stats) odczytuje się normalnie dla każdego źródła.
7. Profil pochodny (set_combinations, set_preferences, primary_preferences, secondary_preferences) można wyliczyć dopiero po odczytaniu i walidacji wymaganych sekcji. Przy wyliczaniu preferencji drugorzędnych należy korzystać z dostępnych TOP 4 obu źródeł; brakujące pozycje poza TOP 4 nie mogą być uzupełniane domysłem.
8. ChatGPT aktualizuje `mod_profiles.json` bezpośrednio na branchu `optimizer-v2`, zachowując pozostałe profile bez zmian.
9. Po zapisie ponownie odczytuje plik z GitHuba i sprawdza JSON, BASE_ID, źródła, timestamp oraz niezmienność pozostałych profili.

## Dokładny algorytm profilu pochodnego

Obowiązuje algorytm odtworzony z wcześniejszej implementacji `build_profile()` i zweryfikowany na istniejącym profilu `JARJARBINKS`. Nie należy zastępować go nową heurystyką.

1. **Agregacja źródeł:** dla każdej wartości liczbowej w kombinacjach setów, primary stats i Secondary Stat Focus liczymy średnią równoważoną 50/50: `(Kyber + Top 100 Guilds) / 2`. Jeśli klucz nie występuje w jednym ze źródeł, jego wkład w tym źródle wynosi 0. Dla Secondary Stat Focus osobno uśredniamy `average` i `focus_pct`. Nie dopisujemy brakujących danych do surowych źródeł.
2. **`set_combinations`:** mapa średnich częstości kombinacji z obu źródeł.
3. **`set_preferences`:** sumujemy częstości wszystkich kombinacji zawierających dany set (np. Speed + Potency zwiększa wynik obu setów); następnie dzielimy każdy wynik przez najwyższy wynik pojedynczego setu. Maksimum = 1.
4. **`primary_preferences`:** w obrębie każdego slotu (Arrow, Triangle, Circle, Cross) dzielimy średnią wartość każdego primary przez sumę średnich wartości wszystkich primary tego slotu. Suma preferencji slotu = 1.
5. **`secondary_preferences`:** bierzemy uśrednione `focus_pct` z TOP 4 każdego źródła, dzielimy je przez najwyższe uśrednione `focus_pct`. Maksimum = 1. Pozostałe statystyki z ustalonego słownika statystyk otrzymują 0; nie oznacza to odczytanego zera na stronie, tylko brak wartości w wymaganym zakresie TOP 4.
6. **Precyzja:** wartości pochodne zaokrąglamy do 4 miejsc po przecinku. Kolejność surowych pozycji TOP 4 pozostaje bez zmian; sortowanie map pochodnych nie jest kryterium preferencji.

Weryfikacja algorytmu na `JARJARBINKS` odtworzyła wszystkie zapisane wartości pochodne (różnice dotyczyły wyłącznie kolejności kluczy JSON). Wagi scoringowe analizatora (obecnie 20% primary / 80% secondary) są osobną warstwą i nie zmieniają powyższego algorytmu agregacji źródeł.

## Statusy

- `refreshed`: wymagane dane źródłowe odczytane, sparsowane, zweryfikowane i zapisane; commit potwierdzony odczytem zwrotnym.
- `partial`: strona dostępna, ale co najmniej jedna wymagana sekcja lub slice jest niepełna. W przypadku Secondary Stat Focus wystarczy poprawne TOP 4; brak pozycji 5–12 nie oznacza niekompletności.
- `unavailable`: nie udało się wiarygodnie odczytać wymaganych danych.
- `cached`: używany jest wcześniejszy profil; nie oznacza świeżego odczytu.

Sama widoczność strony w wynikach wyszukiwania nie wystarcza do ustawienia `refreshed`. Nie wpisywać statystyk, których nie da się wskazać w odczytanym źródle. Jeżeli narzędzie udostępnia jedynie tekstowy wyciąg strony, odnotować ograniczenie; nie przedstawiać go jako surowego, kompletnego eksportu.

## Ograniczenie operacyjne

Odczyt przez ChatGPT jest wykonywany na żądanie w aktywnej rozmowie. Nie działa w tle i nie odświeża profili samoczynnie. Do automatycznego, cyklicznego odświeżania potrzebne byłoby osobne, stabilne źródło danych lub usługa, która ma niezawodny dostęp do SWGOH.GG.
