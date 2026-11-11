# Wspólne źródło danych C-3PO

## Zasada nadrzędna

Jedynym kanonicznym źródłem eksportu C-3PO dla wszystkich wersji optymalizatora jest:

- repozytorium: `vhontebh-arch/swgoh`
- gałąź: `main`
- plik: `c3po.json`

Nowy eksport C-3PO należy wgrywać wyłącznie na `main`. Kopie `c3po.json` znajdujące się na pozostałych gałęziach są tylko historycznymi lustrami i nie mogą być traktowane jako niezależne źródło danych.

## Każde uruchomienie

Przed generowaniem `mods.csv` każda wersja workflow musi:

1. Ustalić commit `main` albo użyć jawnie wskazanego `C3PO_SOURCE_COMMIT`.
2. Pobrać `c3po.json` bezpośrednio z tego konkretnego commita, a nie z ruchomego URL gałęzi.
3. Zweryfikować JSON, ally code oraz obecność listy `inventory.unequippedMod`.
4. Zapisać w logu i podsumowaniu Actions: commit źródłowy, Git blob SHA, SHA-256 oraz liczbę modów magazynowych.
5. Wygenerować wszystkie pliki pochodne w tym samym przebiegu, z tego samego snapshotu.

Nie wolno generować `mods.csv` na podstawie lokalnej kopii gałęzi, która nie przeszła synchronizacji.

## Porównywanie wersji

Wszystkie wersje uruchomione automatycznie pobierają najnowszy commit `main` na początku przebiegu. Aby zagwarantować identyczny snapshot podczas porównywania wersji, w `workflow_dispatch` można podać ten sam commit w polu `c3po_source_commit`.

Wyniki wolno porównywać jako test algorytmów tylko wtedy, gdy ich podsumowania pokazują ten sam:

- `C3PO_SOURCE_COMMIT`
- `C3PO_BLOB_SHA`
- `C3PO_SHA256`

## Zapis danych

Workflow na gałęziach roboczych nie powinien commitować pobranego `c3po.json` z powrotem na swoją gałąź. Jedynym miejscem ręcznej aktualizacji kanonicznego eksportu jest `main`. Pliki pochodne (`mods.csv`, raporty i inne dane) mogą być zapisywane zgodnie z procedurą danej wersji.
