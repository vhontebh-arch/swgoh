# Kanoniczny snapshot danych optymalizatora

## Zasada nadrzędna

Eksport C-3PO jest jednym z wejściowych plików wspólnego snapshotu danych konta. Należy rozróżniać źródło eksportu od gałęzi, z której optymalizator pobiera gotowy, zweryfikowany snapshot:

- **miejsce aktualizacji surowych danych konta:** `main` w repozytorium `vhontebh-arch/swgoh`;
- **kanoniczna gałąź danych dla uruchomień optymalizatora:** `optimizer-data`;
- **manifest snapshotu:** `data_manifest.json` na `optimizer-data`;
- **plik eksportu C-3PO:** `c3po.json`.

Nowy eksport C-3PO należy aktualizować w źródłowym repozytorium zgodnie z dotychczasowym sposobem pracy. Następnie publikowany jest wspólny snapshot na `optimizer-data`. Optymalizator nie traktuje lokalnej kopii pliku na `optimizer-v2` jako samodzielnego źródła prawdy.

## Synchronizacja przed analizą

Workflow `.github/workflows/update-swgoh.yml` uruchamia `sync_optimizer_data.py` przed analizą. Synchronizator:

1. Odczytuje aktualny commit gałęzi `optimizer-data`.
2. Pobiera `data_manifest.json` z tego konkretnego, niezmiennego commita.
3. Weryfikuje obecność wszystkich wymaganych wpisów manifestu.
4. Pobiera wymagane pliki z tego samego commita.
5. Oblicza Git blob SHA każdego pobranego pliku i porównuje go z wartością zapisaną w manifeście.
6. Zapisuje pliki lokalnie dopiero po poprawnym pobraniu i weryfikacji.

Wymagany zestaw obejmuje: `swgoh_972824625.json`, `c3po.json`, `data.json`, `localization.json`, `roster.csv`, `ships.csv`, `mods.csv` i `mod_profiles.json`.

Domyślnym repozytorium i branchem synchronizatora są `vhontebh-arch/swgoh` oraz `optimizer-data`. Można je jawnie nadpisać parametrami `--repository` i `--branch`. Nie istnieje obecnie parametr `C3PO_SOURCE_COMMIT` ani pole `c3po_source_commit` w `workflow_dispatch`; identyfikatorem snapshotu jest commit gałęzi danych odczytany na początku uruchomienia.

## Porównywanie uruchomień

Wszystkie pliki wejściowe jednego uruchomienia pochodzą z jednego commita `optimizer-data`. Dzięki temu nie mieszamy eksportów pobranych w różnych chwilach.

Aby porównać dwa uruchomienia, należy porównać wartość `Snapshot commit` z logu synchronizatora lub podsumowania Actions. Równość tego commita oznacza, że oba uruchomienia pobrały ten sam zestaw plików manifestu. Manifest zawiera również Git blob SHA poszczególnych plików.

## Awaria i niekompletny snapshot

Jeżeli gałąź, manifest, wymagany plik albo hash nie są dostępne lub zgodne, synchronizacja kończy się błędem. Analiza nie powinna być kontynuowana na częściowo pobranym lub niespójnym zestawie danych.

## Odpowiedzialność gałęzi

- `main`: miejsce aktualizacji źródłowych eksportów i pozostałych danych zgodnie z istniejącym procesem repozytorium.
- `optimizer-data`: opublikowany, kanoniczny snapshot wejściowy, konsumowany przez wersje optymalizatora.
- `optimizer-v2`: kod aktywnego optymalizatora, testy, dokumentacja i generowane raporty.

Workflow optymalizatora nie publikuje pobranych plików wejściowych z powrotem na `optimizer-v2`; zapisuje wyłącznie wygenerowane raporty.
