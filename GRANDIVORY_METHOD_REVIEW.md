# Analiza metod Grandivory i adaptacja w optimizer-v2

**Repozytorium źródłowe:** https://github.com/grandivory/mods-optimizer  
**Przeanalizowany plik:** `public/workers/optimizer.js` (gałąź `develop`)  
**Licencja repozytorium:** MIT (potwierdzona w metadanych GitHub).  
**Status:** niezależna implementacja wybranych metod w `mod_analyzer.py`; bez kopiowania kodu źródłowego. Aktualny analizator: `2026-11-10-profile-first-set-audit-v8`.

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


## Projekcja rozwoju modów — v4 (oczekiwana)

- Projekcja rankingu zakłada, że mod może zostać podniesiony do poziomu 15.
- Brakujące rolle do limitu aktualnego tieru otrzymują wartość średnią z zakresu danego secondary (środek przedziału), a nie wartość maksymalną.
- Nieznany przyszły przydział rolli nie jest przypisywany do jednej, najwyżej preferowanej statystyki. Jego oczekiwany wkład jest liczony jako średnia preferencji profilu po możliwych secondary, pomnożona przez średnią jakość rolla (50% zakresu).
- Istniejące wartości secondary, liczba gwiazdek i tier pozostają bez zmian. Mod 5A nie jest automatycznie przeliczany na 6E.
- Slice i calibration nie wchodzą do punktacji ani rankingu buildu. Mogą być pokazane osobno jako sugestie inwestycyjne, które użytkownik może pominąć.
- Bonus setu jest liczony jak dla poziomu 15, ale bez zakładania ulepszenia 5★ → 6★.
- Wartość primary pozostaje taka jak w eksporcie. Nie mamy jeszcze zweryfikowanej tabeli przyrostów primary dla każdego poziomu, więc nie wolno udawać, że ta część projekcji jest dokładna.
- Wynik i różnica gain oznaczają oczekiwaną ocenę buildu po samym podniesieniu do poziomu 15; nie są gwarantowanym wynikiem RNG ani wynikiem po slice/calibration.
## Łańcuchy transferów i bilans dawców — v4

- Cel jest rozpoznawany również wtedy, gdy nie ma obecnie żadnego założonego moda: identyfikator instancji postaci jest odtwarzany z mapowania rosteru.
- Pula naprawcza obejmuje wszystkie mody z magazynu, również poniżej poziomu 15. Koszt ich ulepszenia jest osobną decyzją inwestycyjną, a nie powodem do ukrycia ich z wyszukiwania.
- Wyszukiwanie łańcucha nie ucina kandydatów do top 50 i nie ma arbitralnego limitu długości 10. Przeszukuje poziomami najkrótsze ścieżki, odwiedzając właściciela najwyżej raz.
- Ukończone sety nie są już twardym warunkiem blokującym ruch. Są kryterium preferencji przy wyborze zastępstwa; rzeczywista zmiana liczby pełnych setów jest raportowana przed/po.
- Mod wyparty z docelowego slotu jest dostępny jako mod z magazynu dla naprawy źródłowego slotu. Jeśli nie zostanie użyty w łańcuchu, raport pokazuje jego zwrot do magazynu.
- Wybór PATCH nie kończy się na pierwszym pasującym rekordzie. Dla bieżącej długości łańcucha algorytm ocenia wszystkie dostępne mody z magazynu i wszystkie możliwe przejścia przez dawców. Najpierw maksymalizuje zmianę liczby pełnych setów, następnie łączny zysk fit dawców i zmianę sumy `modValue`. Dzięki temu zachowuje ukończony set, jeśli istnieje wykonalny wariant, który go zachowuje; gdy wszystkie warianty go tracą, wybiera najlepszy pozostały bilans. Preferowana jest najkrótsza długość łańcucha, a dłuższe warianty są rozpatrywane tylko wtedy, gdy krótszy poziom nie ma wykonalnego zakończenia.
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

- Dokładnego przewidywania rzeczywistego przydziału przyszłych rolli; bieżący model liczy ich wartość oczekiwaną przez średnią wartość rolla i średnie dopasowanie profilu, a nie konkretny losowy wynik.
- Dokładnego przeliczenia primary dla poziomów poniżej 15. Primary pozostaje na wartości z eksportu, ponieważ wejściowe dane nie zawierają tabeli przyrostu primary na każdym poziomie.
- Dokładnej projekcji primary do poziomu 15; pozostaje ono na wartości eksportowej do czasu potwierdzenia tabeli przyrostów.
- Pełnej globalnej optymalizacji wielu celów jednocześnie.
- Globalnego optimum po wszystkich możliwych długościach łańcucha. Wersja v8 porównuje wszystkie wykonalne warianty na najkrótszym poziomie BFS; wybiera najpierw najlepszy łączny fit profilu dawców, następnie zmianę liczby pełnych setów i sumę `modValue`. Dłuższe łańcuchy są rozważane tylko wtedy, gdy na krótszym poziomie nie ma żadnego wykonalnego zakończenia. To świadomy priorytet prostoty transferu, a nie dowód globalnego optimum po wszystkich długościach.
- Automatycznego chronienia wszystkich dawców; bilans pozostaje jawny, a decyzja o akceptacji transferu należy do użytkownika.

Te ograniczenia są celowe i widoczne: nie udajemy, że samo przeniesienie metody doboru buildów rozwiązuje problemy łańcuchów i bilansu całego rosteru.

## Decyzje projektowe zachowane z ustaleń użytkownika

- Profile pozostają oparte na priorytetach statystyk i setów, bez obowiązkowych targetów wartości statystyk.
- Popularność konfiguracji jest wskazówką profilu, a nie automatycznym nakazem.
- Wybór sześciu modów jest oceniany jako komplet.
- Stabilna gałąź `optimizer-v2` i `main` pozostają nietknięte. Eksperymentalna implementacja i testy są prowadzone na gałęzi `vel-sartha-analysis-20261110`.


## Priorytet profilu i audyt przebudowy setów — v8

- Kompletny build celu jest oceniany przede wszystkim według profilu postaci: primary, secondary oraz bonusów setów ważonych preferencjami setów z profilu SWGOH.GG.
- Waga bonusu setu wynosi od 10% do 100% jego wartości statystycznej: set nieobecny w profilu nie jest zakazany, ale set z preferencją 100% ma pełną wagę. Zachowanie aktualnie założonych modów jest dopiero tie-breakiem po wyniku buildu i preferencji setów.
- W łańcuchu transferów fit dawcy ma pierwszeństwo przed zachowaniem jego dotychczasowych pełnych setów. Sety nie są twardą blokadą; ich zmiana musi być jednak jawna.
- Walidacja zapisuje dla każdej dotkniętej postaci liczbę modów każdego setu oraz liczbę pełnych grup przed i po operacji. Raport wyświetla każdą zmianę jako: `ROZBITO` (ubyła pełna grupa), `BUDOWANY` (przybył mod do niepełnego setu), `UKOŃCZONO` (powstała pełna grupa) lub `OSŁABIONY` (zmiana liczebności bez tych dwóch zdarzeń).
- Raport obejmuje cel, źródło moda i każdego dawcę PATCH w łańcuchu. Nie ogranicza się do postaci docelowej.
- Profil SWGOH.GG opisuje popularność/priorytety buildów w wybranej populacji, a nie bezwzględny wymóg. Nadal jest to miękki model preferencji, nie nakaz kopiowania jednego szablonu.
- Ograniczenie danych pozostaje istotne: w aktualnym pliku `mod_profiles.json` może brakować profili wielu postaci. Dla dawcy bez profilu algorytm nie potrafi ocenić jego rzeczywistego dopasowania; stosuje jawny fallback `modValue`. Raport musi ten brak ujawniać, a nie sugerować, że fit dawcy został oceniony profilowo.


## Lokalna baza profili SWGOH.GG — obowiązująca procedura

- `mod_profiles.json` jest trwałym cache profili. Zawiera profile, datę ostatniego poprawnego pobrania, źródła oraz osobny status ostatniej próby odświeżenia.
- **TTL profilu wynosi 5 dni** od `fetched_at_utc` (lub `refreshed_at_utc`, jeśli brak osobnego pola pobrania). `checked_at_utc` nie przedłuża ważności.
- Profile pobiera się **wyłącznie na potrzeby konkretnej analizy**: dla wskazanej postaci docelowej oraz dawców występujących w aktualnie wyznaczonym łańcuchu. Nie wolno profilować całego rosteru, wszystkich postaci w grze ani budować bazy na zapas.
- Dla każdej postaci w łańcuchu: brak profilu oznacza pobranie obu źródeł; profil starszy niż 5 dni — odświeżenie obu źródeł; profil niekompletny — uzupełnienie niezależnie od wieku; profil kompletny i nie starszy niż 5 dni — użycie cache bez ponownego pobierania stron.
- Po wstępnym wyznaczeniu łańcucha sprawdza się profile wszystkich jego uczestników. Jeżeli ponowna optymalizacja zmieni łańcuch, kontrolę profili i ocenę powtarza się dla nowego łańcucha aż do ustabilizowania wyniku.
- Każdy poprawnie pobrany profil jest zapisywany atomowo po walidacji. Niepełna odpowiedź, błąd odczytu lub brak danych nie może zastąpić poprzedniego poprawnego profilu.
- Jeżeli odświeżenie starego profilu się nie powiedzie, można użyć ostatniej poprawnej kopii wyłącznie z jawnym oznaczeniem jej jako nieaktualnej; raport nie może przedstawiać jej jako świeżego profilu. Jeżeli profilu nigdy nie było, stosuje się jawny fallback `modValue` i ujawnia brak oceny profilowej.
- Odczyt profili wykonuje ChatGPT bezpośrednio ze stron SWGOH.GG na żądanie użytkownika. GitHub Actions i skrypty repozytorium nie są używane do pobierania profili SWGOH.GG.
- Szczegółowy przebieg odczytu, walidacji dwóch źródeł, zapisu i read-back opisuje `MOD_PROFILE_REFRESH.md`.
## Audyt kolejności wykonania — v16

- Niezależny symulator odtwarza teraz dokładnie kolejność pokazywaną w raporcie: w obrębie celu najpierw wszystkie operacje MOD w kolejności slotów, a następnie wszystkie PATCH-e według głębokości łańcucha.
- Symulacja kontroluje rzeczywiste położenie każdego moda w chwili wykonania, zawartość slotu docelowego, brak duplikatów oraz zachowanie pełnego zbioru modów.
- Raport pokazuje faktyczne źródło moda w chwili danego kroku; jeśli wcześniejszy krok przeniósł go do magazynu, źródłem jest magazyn, a nie pierwotny właściciel.
- Nieudana symulacja dokładnej kolejności blokuje status bezpiecznego łańcucha.