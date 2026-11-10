# Odświeżanie profili modów SWGOH.GG

**Obowiązujący sposób:** ręczny odczyt źródła przez ChatGPT na żądanie użytkownika. GitHub Actions i skrypty repozytorium nie pobierają profili ze SWGOH.GG.

## Przebieg

1. Użytkownik wskazuje postać (BASE_ID) lub prosi o odświeżenie konkretnego profilu.
2. ChatGPT otwiera stronę SWGOH.GG Best Mods dla tej postaci i odczytuje dostępne dane źródłowe.
3. Należy rozdzielić co najmniej dwa źródła/slice, jeżeli profil ma być zbudowany z Kyber GAC i Top 100 Guilds. Nie wolno zastępować brakującego slice domysłem ani powielać danych z pierwszej strony.
4. Każdy odczyt zapisuje się osobno w `source_model.sources[]`, wraz z dokładnym URL, nazwą slice, liczbą analizowanych jednostek (jeśli jest podana) oraz wartościami faktycznie widocznymi na stronie.
5. Profil pochodny (set_combinations, set_preferences, primary_preferences, secondary_preferences) można wyliczyć dopiero po odczytaniu i walidacji wymaganych sekcji.
6. ChatGPT aktualizuje `mod_profiles.json` bezpośrednio na branchu `optimizer-v2`, zachowując pozostałe profile bez zmian.
7. Po zapisie ponownie odczytuje plik z GitHuba i sprawdza JSON, BASE_ID, źródła, timestamp oraz niezmienność pozostałych profili.

## Statusy

- `refreshed`: wymagane dane źródłowe odczytane, sparsowane, zweryfikowane i zapisane; commit potwierdzony odczytem zwrotnym.
- `partial`: strona dostępna, ale co najmniej jedna wymagana sekcja lub slice jest niepełna. Nie używać takiego profilu jako kompletnego celu optymalizacji.
- `unavailable`: nie udało się wiarygodnie odczytać wymaganych danych.
- `cached`: używany jest wcześniejszy profil; nie oznacza świeżego odczytu.

Sama widoczność strony w wynikach wyszukiwania nie wystarcza do ustawienia `refreshed`. Nie wpisywać statystyk, których nie da się wskazać w odczytanym źródle. Jeżeli narzędzie udostępnia jedynie tekstowy wyciąg strony, odnotować ograniczenie; nie przedstawiać go jako surowego, kompletnego eksportu.

## Ograniczenie operacyjne

Odczyt przez ChatGPT jest wykonywany na żądanie w aktywnej rozmowie. Nie działa w tle i nie odświeża profili samoczynnie. Do automatycznego, cyklicznego odświeżania potrzebne byłoby osobne, stabilne źródło danych lub usługa, która ma niezawodny dostęp do SWGOH.GG.
