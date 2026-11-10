# Analiza metod Grandivory i adaptacja w optimizer-v2

**Repozytorium źródłowe:** https://github.com/grandivory/mods-optimizer  
**Przeanalizowany plik:** `public/workers/optimizer.js` (gałąź `develop`)  
**Licencja repozytorium:** MIT (potwierdzona w metadanych GitHub).  
**Status:** niezależna implementacja wybranych metod w `mod_analyzer.py`; bez kopiowania kodu źródłowego. Aktualny analizator: `2026-11-10-global-chain-balance-v4`.

## Co robi Grandivory

1. **Ocenia cały zestaw sześciu modów.** `scoreModSet()` najpierw sumuje statystyki z modów i bonusów setów, a następnie ocenia wynik według wag statystyk celu. Nie traktuje sześciu modów wyłącznie jako sześciu niezależnych rankingów.
2. **Przelicza bonusy setów na statystyki postaci.** `getSetBonusStatsFromModSet()` rozróżnia pełny bonus od połowy bonusu zależnej od poziomu modów. `flattenStatValues()` zamienia bonus procentowy na wartość bezwzględną z użyciem bazowych statystyk postaci.
3. **Buduje kompletne kombinacje setów.** Generator łączy warianty 4+2 oraz 2+2+2, sprawdza możliwe przypisania setów do slotów i dopuszcza rozluźnienie ograniczeń, gdy nie ma wykonalnego zestawu.
4. **Uwzględnia modyfikacje prognozowane.** `getUpgradedMod()` może symulować podniesienie moda do poziomu 15 oraz slice 5A→6E, w tym zmianę primary i secondary.
5. **Rozstrzyga remisy na korzyść mniejszej liczby zmian.** Przy takim samym wyniku preferowany jest build, który zachowuje więcej modów już przypisanych do optymalizowanej postaci.
6. **Optymalizuje postacie sekwencyjnie.** Po przydzieleniu modów jednej postaci usuwa je z puli dostępnej dla kolejnych postaci. To podejście jest proste, ale wynik zależy od kolejności optymalizacji i samo w sobie nie rozwiązuje globalnego problemu dawców.

## Co zostało zaimplementowane w optimizer-v2

Nowa funkcja `optimize_target_build()` (wersja `2026-11-10-grandivory-projected-build-scoring-v3`):

- ocenia sześć slotów jako jeden build;
- oddziela punktację primary i secondary od preferencji setów;
- uwzględnia wszystkie dostępne statystyki secondary i liczbę ich rolli;
- dolicza bonusy ukończonych setów, także wielokrotne sety 2-elementowe;
- rozróżnia pełny i połowiczny bonus w zależności od poziomu modów;
- porównuje kompletne kombinacje setów przez DP po licznikach setów;
- nie stosuje wcześniejszych arbitralnych limitów 12 modów na set i 48 modów na slot;
- przy równym wyniku preferuje build zachowujący więcej modów na postaci docelowej;
- używa preferencji setów jako kryterium rozstrzygającego remis, a nie jako sztucznej premii dodawanej do każdego moda.

### Redukcja kandydatów bez arbitralnego top-K

Dla danego slotu i danego setu zachowujemy najlepszego kandydata. Przy obecnym modelu punktacji każdy mod z tej samej pary slot+set daje identyczny bonus setu, a jego własny wynik nie zależy od pozostałych modów. Słabszy mod z tej samej pary nie może więc poprawić wyniku żadnej kombinacji. To dokładna redukcja przestrzeni wyszukiwania, a nie przycięcie do arbitralnej liczby kandydatów.

DP przechowuje liczbę elementów każdego setu aż do maksymalnej liczby pełnych grup możliwych na sześciu slotach: trzy grupy dla setu 2-elementowego lub jedną dla setu 4-elementowego. Nie stosuje wcześniejszego limitu beam 2000 stanów.

### Skala punktacji

- 40 punktów: statystyki główne, równomiernie rozłożone na sześć slotów;
- 60 punktów: secondary, znormalizowane względem maksymalnie 24 rolli;
- bonus setu: równoważnik maksymalnych rolli odpowiedniej statystyki, pomnożony przez jej preferencję w profilu.

To zachowuje prosty model profili oparty na preferencjach statystyk i setów. Nie wprowadzono targetów wartości statystyk z Grandivory.


## Projekcja rozwoju modów — v3

- `project_mod_for_build()` tworzy kopię moda do oceny; nie zmienia danych źródłowych ani bieżących statystyk w rosterze.
- Dla moda poniżej 15 poziomu dopisuje brakujące rolle do limitu wynikającego z aktualnego tieru. Wartość założonego rolla to środek zakresu dla danej statystyki; jego przypisanie do najlepiej ocenianej statystyki profilu jest optymistycznym założeniem.
- Dla moda 5★ na poziomie 15 i tierze A przelicza każdy secondary do odpowiedniego zakresu 6-dot, tworząc wariant 6E. Roll count pozostaje bez zmian.
- Ranking pełnych buildów i bonusy setów są liczone na kopiach po projekcji. Wynik aktualny i wynik po projekcji są raportowane oddzielnie. `gain` oznacza różnicę między najlepszym buildem po projekcji a obecnym buildem po tej samej projekcji — nie jest to zysk już osiągnięty ani zatwierdzony transfer.
- Wartość primary pozostaje taka jak w eksporcie; nie jest sztucznie podbijana w projekcji poziomu.


## Łańcuchy transferów i bilans dawców — v4

- Cel jest rozpoznawany również wtedy, gdy nie ma obecnie żadnego założonego moda: identyfikator instancji postaci jest odtwarzany z mapowania rosteru.
- Pula naprawcza obejmuje wszystkie mody z magazynu, również poniżej poziomu 15. Koszt ich ulepszenia jest osobną decyzją inwestycyjną, a nie powodem do ukrycia ich z wyszukiwania.
- Wyszukiwanie łańcucha nie ucina kandydatów do top 50 i nie ma arbitralnego limitu długości 10. Przeszukuje poziomami najkrótsze ścieżki, odwiedzając właściciela najwyżej raz.
- Ukończone sety nie są już twardym warunkiem blokującym ruch. Są kryterium preferencji przy wyborze zastępstwa; rzeczywista zmiana liczby pełnych setów jest raportowana przed/po.
- Mod wyparty z docelowego slotu jest dostępny jako mod z magazynu dla naprawy źródłowego slotu. Jeśli nie zostanie użyty w łańcuchu, raport pokazuje jego zwrot do magazynu.
- Każdy plan jest odtwarzany niezależnie od stanu roboczego planera. Walidator sprawdza źródłowy slot, kolejność MOD/PATCH, zgodność slotu, brak duplikatów, końcowy układ slotów oraz zachowanie pełnego zbioru identyfikatorów modów (żaden mod nie może zniknąć ani zostać dodany).
- Pierwszy PATCH po zabraniu moda z dawcy uzupełnia fizycznie pusty slot. W bilansie logicznym porównuje się go z modem, który został zabrany w kroku MOD, ale w symulacji nie oczekuje się, że nadal będzie zajmował slot.
- Raport podaje dla każdej dotkniętej postaci sumę `modValue` założonych modów przed i po transferze oraz zmianę liczby pełnych setów. `modValue` jest ogólną miarą jakości samych modów, nie oceną całego buildu konkretnego dawcy.
- Nie ma automatycznej ochrony dawcy przed spadkiem jakości ani utratą setu. Użytkownik widzi bilans i podejmuje decyzję; algorytm nie ukrywa kosztu transferu.
- Testy regresyjne obejmują: equip z magazynu do pustego celu, zastąpienie moda w celu i jego zwrot do magazynu, naprawę pustego slotu dawcy, wykorzystanie moda wypieranego z celu jako PATCH, konflikt dwóch celów o ten sam mod oraz odrzucenie niewykonalnego transferu.
- Ograniczenie bieżącej wersji: wyszukiwanie wybiera bezpośredni PATCH z dostępnej puli magazynowej przed rozważaniem kolejnych dawców. Nie jest to jeszcze optymalizacja alternatywnych łańcuchów wielodawcowych; ten etap pozostaje otwarty i nie należy zakładać, że raport znajduje globalnie najlepszy łańcuch.

### Ograniczenie interpretacji bilansu

Obecny zestaw profili zawiera profile celów optymalizacji, a nie indywidualny profil każdej postaci w rosterze. Dlatego nie wolno nazywać sumy `modValue` pełnym wynikiem buildu dawcy. Jest to jawny, porównywalny wskaźnik jakości wyposażonych modów; do dokładnego bilansu statystyk postaci potrzebne byłyby profile statystyk wszystkich dawców lub pełne bazowe statystyki postaci.

## Ograniczenie danych — ważne

Grandivory może przeliczać procentowe bonusy setów na dokładne wartości bezwzględne, ponieważ jego model postaci zawiera `baseStats`. Obecne pliki wejściowe naszego projektu (`mods.csv`, `roster.csv` i eksport C-3PO) nie dostarczają wprost kompletnego zestawu bazowych statystyk postaci w formacie wymaganym do takiego przeliczenia.

Dlatego obecna implementacja używa równoważników maksymalnych rolli secondary:
- dla bonusów procentowych, które mają odpowiednik procentowej statystyki secondary, stosunek bonusu setu do maksymalnego rolla jest niezależny od bazowej wartości statystyki;
- Speed Set przelicza procent bazowej szybkości na punkty Speed, używając `profile.base_stats.Speed`, jeśli pole istnieje, a w przeciwnym razie jawnej wartości referencyjnej 150.

To jest jawne przybliżenie, a nie pełna reprodukcja dokładnego przeliczenia statystyk Grandivory. Nie należy przedstawiać wyniku bonusu Speed jako dokładnego dla każdej postaci, dopóki nie dostarczymy jej bazowej szybkości.

## Czego ta zmiana jeszcze nie obejmuje

- Dokładnego przewidywania wyniku levelowania, ponieważ nie znamy przyszłych losowych rolli. Projekcja w `project_mod_for_build()` jest jawnie optymistycznym wariantem: brakujące rolle do limitu aktualnego tieru przypisuje do najwyżej preferowanej statystyki profilu. Nie jest to średnia statystyczna ani gwarantowany wynik.
- Dokładnego przeliczenia primary dla poziomów poniżej 15. Primary pozostaje na wartości z eksportu, ponieważ wejściowe dane nie zawierają tabeli przyrostu primary na każdym poziomie.
- Projekcji 5A→6E dla modów innych niż 5A na poziomie 15; nie zakładamy, że można pominąć wcześniejsze etapy slice.
- Pełnej globalnej optymalizacji wielu celów jednocześnie.
- Globalnego wyszukiwania i optymalizacji alternatywnych łańcuchów wielodawcowych. Obecna wersja ma fizyczną walidację i bilans końcowy, ale nie gwarantuje najlepszego łańcucha ani nie eksploruje wszystkich alternatyw.
- Automatycznego chronienia wszystkich dawców; bilans pozostaje jawny, a decyzja o akceptacji transferu należy do użytkownika.

Te ograniczenia są celowe i widoczne: nie udajemy, że samo przeniesienie metody doboru buildów rozwiązuje problemy łańcuchów i bilansu całego rosteru.

## Decyzje projektowe zachowane z ustaleń użytkownika

- Profile pozostają oparte na priorytetach statystyk i setów, bez obowiązkowych targetów wartości statystyk.
- Popularność konfiguracji jest wskazówką profilu, a nie automatycznym nakazem.
- Wybór sześciu modów jest oceniany jako komplet.
- Nowa implementacja znajduje się wyłącznie na `optimizer-v2`; gałęzie bazowej i `main` nie zmieniano.
