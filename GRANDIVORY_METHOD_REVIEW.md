# Analiza metod Grandivory i adaptacja w optimizer-v2

**Repozytorium źródłowe:** https://github.com/grandivory/mods-optimizer  
**Przeanalizowany plik:** `public/workers/optimizer.js` (gałąź `develop`)  
**Licencja repozytorium:** MIT (potwierdzona w metadanych GitHub).  
**Status:** niezależna implementacja wybranych metod w `mod_analyzer.py`; bez kopiowania kodu źródłowego. Aktualny identyfikator analizatora w kodzie `optimizer-v2`: `2026-11-14-actual-donor-rebuild-score-experiment-v1`. Ten dokument rozdziela historyczne etapy rozwoju od zachowania aktualnego kodu; w razie rozbieżności rozstrzygający jest kod i testy na `optimizer-v2`.

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
- Wybór PATCH nie kończy się na pierwszym pasującym rekordzie. Dla bieżącej długości łańcucha algorytm ocenia wszystkie dostępne mody z magazynu i wszystkie możliwe przejścia przez dawców. Najpierw maksymalizuje zmianę liczby pełnych setów, następnie łączny zysk fit dawców i zmianę sumy `modValue`. Dzięki temu zachowuje ukończony set, jeśli istnieje wykonalny wariant, który go zachowuje; gdy wszystkie warianty go tracą, wybiera najlepszy pozostały bilans. Preferowana jest najkrótsza długość łańcucha, a dłuższe warianty są rozpatrywane tylko wtedy, gdy krótszy poziom nie ma wykonalnego zakończenia.
- Każdy plan jest odtwarzany niezależnie od stanu roboczego planera. Walidator sprawdza źródłowy slot, kolejność MOD/PATCH, zgodność slotu, brak duplikatów, końcowy układ slotów oraz zachowanie pełnego zbioru identyfikatorów modów (żaden mod nie może zniknąć ani zostać dodany).
- Pierwszy PATCH po zabraniu moda z dawcy uzupełnia fizycznie pusty slot. W bilansie logicznym porównuje się go z modem, który został zabrany w kroku MOD, ale w symulacji nie oczekuje się, że nadal będzie zajmował slot.
- Raport podaje dla każdej dotkniętej postaci sumę `modValue` założonych modów przed i po transferze oraz zmianę liczby pełnych setów. `modValue` jest ogólną miarą jakości samych modów, nie oceną całego buildu konkretnego dawcy.
- Nie ma automatycznej ochrony dawcy przed spadkiem jakości ani utratą setu. Użytkownik widzi bilans i podejmuje decyzję; algorytm nie ukrywa kosztu transferu.
- Testy regresyjne obejmują: equip z magazynu do pustego celu, zastąpienie moda w celu i jego zwrot do magazynu, naprawę pustego slotu dawcy, wykorzystanie moda wypieranego z celu jako PATCH, konflikt dwóch celów o ten sam mod oraz odrzucenie niewykonalnego transferu.
- **Ten opis jest historyczny i nie opisuje aktualnej wersji.** W aktualnym kodzie istnieje rekurencyjna przebudowa pełnego buildu profilowanego dawcy (z backtrackingiem), a dla pozostałych przypadków osobne wyszukiwanie fizycznego łańcucha MOD/PATCH. Aktualne zachowanie opisano w sekcji „Stan implementacji — 2026-11-14” poniżej.

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
- Globalnego optimum po wszystkich możliwych długościach łańcucha. Wersja v8 porównuje wszystkie wykonalne warianty na najkrótszym poziomie BFS; wybiera najpierw najlepszy łączny fit profilu dawców, następnie zmianę liczby pełnych setów i sumę `modValue`. Dłuższe łańcuchy są rozważane tylko wtedy, gdy na krótszym poziomie nie ma żadnego wykonalnego zakończenia. To świadomy priorytet prostoty transferu, a nie dowód globalnego optimum po wszystkich długościach.
- Automatycznego chronienia wszystkich dawców; bilans pozostaje jawny, a decyzja o akceptacji transferu należy do użytkownika.

Te ograniczenia są celowe i widoczne: nie udajemy, że samo przeniesienie metody doboru buildów rozwiązuje problemy łańcuchów i bilansu całego rosteru.

## Decyzje projektowe zachowane z ustaleń użytkownika

- Profile pozostają oparte na priorytetach statystyk i setów, bez obowiązkowych targetów wartości statystyk.
- Popularność konfiguracji jest wskazówką profilu, a nie automatycznym nakazem.
- Wybór sześciu modów jest oceniany jako komplet.
- Nowa implementacja znajduje się wyłącznie na `optimizer-v2`; gałęzie bazowej i `main` nie zmieniano.


## Historyczny etap: priorytet profilu i audyt przebudowy setów — v8 (zastąpiony)

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

## Dodatkowa kontrola łańcuchów dawców

Wersja integracyjna uwzględnia dokładną sześciomodową kombinację setów dawcy przy wyborze PATCH-a. Jest to kryterium porządkujące kandydatów o tej samej długości łańcucha, przed lokalnym fitem pojedynczego moda. Nie zmienia punktacji docelowego buildu. Jeżeli profil nie zawiera danej kombinacji, stosowany jest dotychczasowy fallback.


## Wspólna punktacja modów i pełnych buildów — 2026-11-12

- `profile_mod_score_components()` jest jedynym źródłem punktacji pojedynczego moda dla wyszukiwania buildów i oceny dopasowania do profilu.
- Model zachowuje proporcję 40 punktów dla primary i 60 punktów dla secondary, z tym samym limitem 24 rolli secondary oraz tymi samymi preferencjami profilu.
- Jakość primary jest mnożona przez preferencję primary i normalizowana do wspólnego maksimum 6-dot. Składowe są raportowane osobno jako `primaryPoints` i `secondaryPoints`.
- `score_profile()` nie dodaje preferencji setu do pojedynczego moda. Bonus setu pozostaje oceniany wyłącznie na poziomie kompletnego buildu.
- `profiled_build_score()` ocenia ustalony zestaw modów dawcy przed i po zmianie, z uwzględnieniem tych samych punktacji modów i bonusów setów co wyszukiwanie buildu. Jeśli profil dawcy jest dostępny, łańcuch transferów używa tej różnicy zamiast porównywania tylko pojedynczego moda. Bez profilu pozostaje jawny fallback `modValue`.
- Testy regresyjne sprawdzają zgodność punktacji pojedynczego moda z wynikiem optymalizatora, proporcję 40/60 i wpływ pełnego zestawu dawcy.



## Stan implementacji — 2026-11-14

Poniższy opis odpowiada kodowi `mod_analyzer.py` z identyfikatorem `2026-11-14-actual-donor-rebuild-score-experiment-v1`. Jest nadrzędny wobec starszych opisów etapów v3–v8 w tym dokumencie.

### Wspólna punktacja

- Pojedynczy mod jest oceniany wspólną funkcją `profile_mod_score_components()`.
- Skala wynosi 40 punktów za primary i 60 punktów za secondary; secondary są normalizowane względem maksymalnie 24 rolli.
- `profiled_build_score()` ocenia kompletny lub rzeczywiście dostępny build z uwzględnieniem preferencji profilu i bonusów setów. Nie dodaje preferencji setu do punktacji pojedynczego moda.
- Ocena dawców profilowanych porównuje wynik buildu przed i po transferze. Dla dawcy bez profilu pozostaje jawny fallback oparty na `modValue`/lokalnym dopasowaniu; raport nie może przedstawiać go jako pełnej oceny profilowej.

### Przebudowa profilowanego dawcy

- Jeżeli dawca ma profil, algorytm próbuje zbudować jego pełny sześciomodowy układ, zamiast oceniać wyłącznie pojedynczy zamiennik.
- Sloty nieobjęte transferem pozostają stałe, jeżeli istniejący układ nie pasuje do żadnej rozpoznanej kombinacji z profilu. W takim przypadku optymalizator nie naprawia samowolnie nietkniętych slotów.
- Uzupełniane są sloty opróżnione przez transfer oraz sloty, które były puste już wcześniej.
- Wybór zastępstw wykorzystuje optymalizator pełnego buildu z `projected=False`, rezerwację modów i rekurencyjne naprawianie kolejnych dawców.
- Backtracking wycofuje rezerwacje po nieudanej gałęzi i próbuje alternatywnego moda. Wykrywane są cykle i konflikty użycia tych samych modów.
- Profilowana przebudowa wymaga dostępnego profilu dawcy i sprawdza, czy można uzyskać kompletny build zgodny z rozpoznaną kombinacją setów, jeżeli bieżący build taką kombinację już realizował.

### Łańcuch fizycznych transferów MOD/PATCH

- Dla łańcuchów, które nie są obsłużone przez profilowaną przebudowę dawcy, kod wykonuje przeszukiwanie BFS według długości łańcucha.
- Na pierwszym poziomie z fizycznie wykonalnymi rozwiązaniami porównuje wszystkie znalezione zakończenia, a nie przyjmuje pierwszego napotkanego.
- Kryteria porównania w obrębie tej samej długości to kolejno: zmiana częstości dokładnej kombinacji setów dawcy, zysk dopasowania dawcy, zmiana liczby pełnych setów oraz zmiana `modValue`.
- Każdy właściciel może wystąpić w łańcuchu najwyżej raz; mod nie może być użyty ponownie. Mod wyparty z celu może zostać wykorzystany jako element uzupełniający.
- Preferowana jest najkrótsza wykonalna ścieżka. Nie jest to dowód globalnego optimum po wszystkich możliwych konfiguracjach i długościach łańcuchów.

### Ograniczenia wyszukiwania i interpretacji

- Nie należy opisywać aktualnego algorytmu jako nieograniczonego globalnego optymalizatora. W pomocniczym wyszukiwaniu naprawy obowiązują limity głębokości i liczby kandydatów; wyszukiwanie kandydatów jest celowo ograniczone dla czasu wykonania.
- Wynik zależy od dostępnych danych, profili, kandydatów i ograniczeń wyszukiwania. „Wykonalny” oznacza, że plan można odtworzyć bez konfliktu modów; nie oznacza matematycznego optimum całego rosteru.
- Nie ma automatycznej blokady strat dawcy. Bilans jest ujawniany w raporcie, a decyzja o zaakceptowaniu kompromisu należy do użytkownika.
- Profile SWGOH.GG są pobierane ręcznie na żądanie, dla celu i rzeczywistych uczestników łańcucha, zgodnie z TTL 5 dni opisanym w `MOD_PROFILE_REFRESH.md`.
