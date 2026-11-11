# Standard optymalizacji modów SWGOH

**Status:** obowiązujący standard pracy analitycznej  
**Zakres:** dobór modów dla postaci, przenoszenie modów, zamienniki, łańcuchy zmian i raport końcowy.  
**Zasada nadrzędna:** optymalizujemy roster jako całość, a nie tylko sześć slotów jednej postaci.

Ten dokument jest obowiązkową specyfikacją dla każdej ręcznej lub automatycznej optymalizacji modów. Jeżeli propozycja nie przechodzi kontroli opisanych niżej, nie wolno przedstawiać jej jako gotowej rekomendacji.

**Procedura nadrzędna:** przed rozpoczęciem pracy stosuj `OPTIMIZER_WORK_PROTOCOL.md`. Określa ona granice zlecenia, kolejność sprawdzania dokumentacji i zasadę uzyskania zgody przed rozszerzeniem zakresu. W przypadku rozbieżności dotyczących pobierania profili obowiązuje `MOD_PROFILE_REFRESH.md` (TTL 5 dni).

## 1. Źródła danych i kontrola wejścia

Przed każdą analizą należy pobrać najnowsze dostępne eksporty:
- `mods.csv` — wszystkie mody wyposażone i niewyposażone;
- `roster.csv` — roster, identyfikatory jednostek i ich aktualny rozwój.

Wymagania:
1. Używać danych z jednego, spójnego przebiegu eksportu. Jeżeli pliki mają różne czasy aktualizacji lub pochodzą z różnych przebiegów, zgłosić to i nie zakładać, że stan jest aktualny.
2. Wczytywać CSV parserem respektującym cudzysłowy i przecinki wewnątrz pól. Nie dzielić wierszy przez `split(",")`.
3. Zweryfikować nagłówki, liczbę rekordów, unikalność identyfikatorów modów oraz poprawność przypisań `assignedTo` do jednostek z rosteru.
4. Rozróżniać mody wyposażone od magazynu. Mod wyposażony musi mieć poprawnego właściciela; mod magazynowy nie może być jednocześnie traktowany jako wyposażony.
5. Nie utożsamiać braku rekordu z brakiem moda, jeśli eksport jest niekompletny.
6. Nie opierać decyzji na nieaktualnym raporcie lub poprzednim zrzucie, jeżeli dostępny jest nowszy eksport.
7. Jeżeli brakuje danych, pola są nieczytelne albo występują sprzeczności, zatrzymać analizę w miejscu, którego dotyczą. Nie uzupełniać braków domysłem.

Dane o postaciach należy łączyć z modami po identyfikatorze jednostki, a nie po nazwie wyświetlanej.

## 2. Profil docelowej postaci

Profil postaci ustala się **przed** wyszukiwaniem modów i dawców.

Profil musi określać:
- rolę i sposób działania postaci;
- preferowane zestawy oraz liczbę elementów każdego zestawu;
- wymagane lub preferowane sloty i statystyki główne;
- priorytety statystyk drugorzędnych;
- istotne progi, szybkość względną lub wymagania drużyny, jeśli mają zastosowanie;
- ograniczenia wynikające z trybu gry i aktualnego celu użytkownika.

Hierarchia źródeł profilu:
1. aktualne, wiarygodne dane użytkownika i ustalenia dla jego konta;
2. aktualne statystyki użycia i rekomendacje dla tej postaci z uznanych źródeł;
3. mechanika postaci i uzasadniona analiza jej zestawu umiejętności.

Jeżeli źródła są rozbieżne, należy to zaznaczyć. Popularność zestawu nie jest automatycznie dowodem, że jest on najlepszy dla konkretnego konta.

Nie wolno zmieniać profilu docelowego tylko dlatego, że łatwiej zbudować inny zestaw z aktualnie dostępnych modów. Odstępstwo musi być przedstawione jako osobny kompromis i uzasadnione.

## 3. Ocena pojedynczego moda

Każdy kandydat musi być oceniany na podstawie kompletu dostępnych danych:
- slot;
- zestaw;
- liczba gwiazdek;
- poziom i tier;
- statystyka główna;
- wszystkie dostępne statystyki drugorzędne;
- wartość i rodzaj przyrostów/rolli, jeśli eksport je udostępnia;
- aktualny właściciel albo informacja, że mod jest w magazynie.

Nie wolno:
- oceniać moda wyłącznie po sumie Speed;
- pomijać statystyk innych niż Speed;
- używać samej liczby ID moda jako opisu dla użytkownika;
- zakładać, że mod z wyższym Speed jest zawsze lepszy;
- porównywać modów o różnych slotach bez uwzględnienia statystyki głównej i funkcji slotu.

W raporcie użytkowym mod identyfikujemy opisowo: **slot + zestaw + gwiazdki + poziom/tier + statystyka główna + wszystkie drugorzędne**. ID może być używane wewnętrznie do śledzenia rekordu, ale nie zastępuje opisu.

## 3A. Projekcja rozwoju moda w rankingu buildu

Wirtualny build jest oceniany przy założeniu, że użytkownik może podnieść wybrane mody do poziomu 15. Projekcja ma być oczekiwana, a nie maksymalna:

1. Brakujące rolle do limitu aktualnego tieru wyceniaj wartością średnią z zakresu danego secondary (środek przedziału), nie maksymalnym rollem.
2. Nie przypisuj wszystkich przyszłych rolli do najwyżej preferowanej statystyki profilu. Ponieważ nie znamy przyszłego rozkładu rolli, używaj oczekiwanej wartości dopasowania: najpierw modeluj dodawanie brakujących typów secondary aż do czterech, a pozostałe rolle jako ulepszenia jednego z tych czterech. W obu etapach stosuj równe wagi możliwych wyników, ponieważ nie mamy zweryfikowanych prawdopodobieństw losowania poszczególnych statystyk.
3. W rankingu nie zakładaj slice 5★ → 6★ ani calibration. Nie zmieniaj liczby gwiazdek, wartości istniejących secondary ani tieru w projekcji buildu.
4. Slice i calibration mogą występować w raporcie jako osobne sugestie inwestycyjne. Nie są warunkiem wykonalności moda ani warunkiem jego uwzględnienia w analizie; użytkownik może je pominąć.
5. Bonus setu licz dla poziomu 15, ale nie zakładaj bonusu 6-dot dla moda 5★.
6. Primary pozostaw dokładnie na wartości z eksportu: zależy od obecnej liczby gwiazdek moda, a podniesienie poziomu do 15 jej nie zmienia. Nie przeliczaj primary na inną wartość ani nie przeliczaj moda 5★ na 6★ — slice pozostaje opcjonalny. Przy ocenie jakości primary normalizuj wartość względem maksimum dla tej samej liczby gwiazdek (5★ lub 6★), nigdy względem uniwersalnego maksimum 6★.

Raport musi nazywać ten wynik oczekiwaną oceną po poziomie 15, a nie maksymalnym potencjałem ani gwarantowaną wartością w grze.

## 4. Wyszukiwanie zestawu docelowego

1. Rozważyć wszystkie prawidłowe kombinacje sześciu slotów z magazynu i od potencjalnych dawców.
2. Sprawdzić zgodność liczby elementów zestawów z bonusem zestawu. Nie zakładać, że sześć modów o dobrych statystykach tworzy dobry zestaw.
3. Najpierw szukać zestawu realizującego profil docelowy bez przenoszenia modów. Następnie rozważyć przeniesienia.
4. Porównywać kompletne zestawy, a nie wybierać sześciu niezależnych zwycięzców bez sprawdzenia ich wspólnego efektu.
5. Uwzględniać łączny efekt statystyk głównych, drugorzędnych i bonusów zestawów.
6. Nie wymuszać jednego sztywnego układu, jeżeli dane i profil uzasadniają kilka wariantów. W takim przypadku przedstawić najlepszy wariant oraz istotną alternatywę.
7. Jeżeli nie da się osiągnąć profilu docelowego, pokazać najbliższy wykonalny wariant jako kompromis albo zgłosić brak uzasadnionego rozwiązania.

## 5. Ochrona dawców i koszt przeniesienia

Każdy mod zdjęty z postaci oznacza zmianę konfiguracji dawcy. Nie wolno oceniać przeniesienia wyłącznie przez pryzmat korzyści postaci docelowej.

Dla każdego dawcy należy ustalić:
- jego rolę i znaczenie na koncie;
- aktualny komplet modów i aktywne bonusy zestawów;
- dokładnie, które statystyki i bonusy traci;
- czy po zabraniu moda nadal ma prawidłowy i sensowny zestaw;
- czy zamiennik jest dostępny i czy jego jakość jest akceptowalna;
- końcowy stan dawcy po wszystkich zmianach w łańcuchu.

Priorytet ochrony:
- nie naruszać jednostek wyraźnie wyłączonych przez użytkownika;
- nie zabierać modów z postaci, których zestawy lub rozwój są aktualnie chronione, bez wyraźnej potrzeby i jawnego uzasadnienia;
- nie rozbijać kompletnego zestawu tylko po to, by uzyskać marginalną poprawę;
- nie traktować każdego kompletnego zestawu jako nietykalnego. Można go naruszyć, jeżeli bilans całej operacji jest rzeczywiście korzystny i koszt jest jawnie przedstawiony.

Lista wyłączeń i ochrony może być aktualizowana przez użytkownika. Obowiązujące, znane ograniczenia konta należy respektować, w szczególności:
- nie pobierać modów Jar Jara Binksa;
- nie pobierać modów z Inkwizytorów, Tarkina, Hondo ani Eighth Brother;
- nie traktować Pietta jako aktualnego celu progresji tylko dlatego, że był wcześniejszym etapem Executor. Ewentualne użycie jego modów nadal wymaga oceny obecnej konfiguracji.

## 6. Łańcuch przeniesień i zamienniki

Każda propozycja musi być rozpisana do końca.

Dla każdego moda:
1. wskazać jego aktualne miejsce: magazyn albo konkretny dawca;
2. wskazać slot docelowy;
3. jeżeli mod jest zabrany dawcy, wskazać konkretny zamiennik dla tego samego slotu;
4. jeśli zamiennik pochodzi od kolejnego dawcy, powtórzyć ocenę i wskazać jego zamiennik;
5. zakończyć łańcuch dopiero wtedy, gdy wszystkie zmiany są pokryte modami z magazynu lub kompletnym, sprawdzonym łańcuchem;
6. sprawdzić, czy żaden mod nie został użyty dwa razy.

Zamiennik ocenia się względem moda zabranego **w kontekście całej konfiguracji dawcy**. Należy sprawdzić:
- zgodność slotu;
- wpływ na bonusy zestawów;
- zmianę statystyki głównej;
- zmianę wszystkich istotnych statystyk drugorzędnych;
- gwiazdki, poziom i tier;
- wpływ na rolę i użyteczność dawcy.

Nie wolno przedstawiać zamiennika jako równoważnego, jeśli jest wyraźnie słabszy. Jeżeli donor po zamianie traci bonus zestawu lub istotne statystyki, musi to być pokazane w bilansie. Sam fakt, że mod zastępczy pochodzi z magazynu, nie oznacza, że operacja jest bezkosztowa.

## 7. Ocena bilansu całej operacji

Porównać stan **przed** i **po** dla:
- postaci docelowej;
- każdego dawcy bezpośredniego i pośredniego;
- aktywnych bonusów zestawów;
- kluczowych statystyk i ich sum;
- jakości modów pozostających u dawców;
- liczby modów w magazynie i wykorzystania każdego rekordu.

Nie stosować arbitralnego, nieuzgodnionego współczynnika, który pozwala ukryć dużą stratę dawcy za małą korzyścią postaci docelowej. Jeżeli algorytm używa punktacji, jej składniki, wagi i ograniczenia muszą być jawne i możliwe do sprawdzenia.

Wyniki należy klasyfikować:
- **REKOMENDACJA** — wykonalna operacja, która spełnia profil docelowy i ma uzasadniony dodatni bilans całego rosteru;
- **KOMPROMIS** — wykonalna operacja z konkretną, opisaną stratą lub odstępstwem; wymaga pokazania kosztu i korzyści;
- **BRAK ROZWIĄZANIA** — brak wykonalnego wariantu, którego bilans można uczciwie uzasadnić.

Nie wolno nazywać kompromisu rekomendacją ani przedstawiać braku rozwiązania jako powodu do obniżenia wymagań bez zgody użytkownika.

## 8. Obowiązkowa walidacja przed raportem

Raport nie może zostać wygenerowany jako gotowa rekomendacja, dopóki wszystkie poniższe kontrole nie zostaną zaliczone:

- [ ] Dane wejściowe są aktualne, kompletne i spójne.
- [ ] Wszystkie sześć slotów postaci docelowej jest obsadzonych dokładnie jednym modem.
- [ ] Każdy mod spełnia wymagania slotu i profilu albo odstępstwo jest jawnie oznaczone.
- [ ] Bonusy zestawów postaci docelowej zostały policzone.
- [ ] Wszystkie statystyki główne i drugorzędne zostały uwzględnione.
- [ ] Każdy zabrany mod ma wskazanego dawcę.
- [ ] Każdy dawca ma sprawdzony stan końcowy.
- [ ] Każdy potrzebny zamiennik jest konkretnym, dostępnym modem o zgodnym slocie.
- [ ] Każdy łańcuch zamian kończy się w magazynie lub jest kompletny.
- [ ] Żaden mod nie jest użyty więcej niż raz.
- [ ] Nie naruszono jednostek i ograniczeń chronionych przez użytkownika.
- [ ] Zmiany bonusów zestawów i downgrade'y są ujawnione.
- [ ] Bilans obejmuje wszystkie dotknięte postacie, nie tylko cel.
- [ ] Niezależna symulacja odtwarza dokładnie kolejność MOD/PATCH pokazaną użytkownikowi: wszystkie mody celu, następnie PATCH-y warstwami.
- [ ] Klasyfikacja REKOMENDACJA/KOMPROMIS/BRAK ROZWIĄZANIA odpowiada wynikom kontroli.

**Zasada blokująca:** niezaliczona kontrola oznacza brak gotowej rekomendacji. Można pokazać robocze warianty, ale trzeba je wyraźnie oznaczyć jako niezweryfikowane.

## 9. Format raportu dla użytkownika

Raport ma być konkretny i operacyjny, zgodny z zaakceptowanym stylem raportów modów (np. Vel Sarthy i Cinta Kaz).

Wymagane sekcje:
1. **Cel i profil docelowy** — zestawy, główne statystyki i priorytety.
2. **MOD** — sześć modów docelowych, każdy opisany pełnym zestawem cech.
3. **PATCH** — wszystkie zamienniki dla dawców, z pełnymi opisami.
4. **Koszt u dawców** — co każdy dawca zyskuje/traci, w tym bonusy zestawów i istotne statystyki.
5. **Bilans końcowy** — stan przed/po i suma kluczowych statystyk.
6. **Status walidacji** — zaliczone kontrole, odstępstwa i klasyfikacja wyniku.

Nie używać samych ID modów. Nie pomijać drugorzędnych statystyk. Nie opisywać moda skrótowo, jeśli użytkownik wymaga pełnej identyfikacji. Nie ukrywać braków danych.

### Kolejność raportowania transferów

- Raport nie wypisuje osobnych czynności „zdejmij mod”. Założenie nowego moda automatycznie przenosi poprzedni mod z tego slotu do magazynu.
- Kolejność wykonania jest warstwowa: najpierw wszystkie mody docelowe na główną postać; następnie uzupełnianie dawców poziomu 1 (bezpośrednich źródeł modów celu); potem poziomu 2 (dawców, od których pochodzą zamienniki dla poziomu 1); dalej analogicznie aż do końca łańcucha.
- Wszystkie operacje PATCH na danym poziomie należy pokazać razem, zanim raport przejdzie do kolejnego poziomu.
- Nie pomijać żadnego PATCH potrzebnego do fizycznego zamknięcia łańcucha. Poziom oznacza odległość dawcy od głównej postaci, a nie kolejność slotów ani kolejność znalezienia moda.
- Jeśli kilka niezależnych łańcuchów ma ten sam poziom, można zachować kolejność slotów głównej postaci, aby raport był łatwy do wykonania.

### Obowiązkowa procedura w odpowiedzi dla użytkownika

Po każdej zakończonej analizie pełna sekcja **„Kolejność przekładania”** musi być podana bezpośrednio w odpowiedzi ChatGPT. Nie wystarczy umieścić jej wyłącznie w pliku `mod_analysis.md`, podać linku ani opisać samego wyniku.

Sekcja w odpowiedzi musi być wiernym, kompletnym odwzorowaniem końcowego planu:
1. wszystkie mody dla głównej postaci, w kolejności slotów: Arrow, Square, Diamond, Triangle, Circle, Cross;
2. wszystkie operacje PATCH dla dawców poziomu 1;
3. wszystkie operacje PATCH dla dawców poziomu 2;
4. kolejne poziomy aż do pełnego zamknięcia łańcucha.

Każdy krok ma podawać postać, slot i pełną identyfikację moda (zestaw, gwiazdki, poziom/tier, statystyka główna i wszystkie drugorzędne). Wszystkie kroki danego poziomu należy zgrupować razem. Nie wolno pomijać żadnego zamiennika ani naprawy dawcy pośredniego. Nie wypisuje się osobnych czynności zdejmowania moda — założenie nowego moda automatycznie przenosi poprzedni do magazynu.

Jeżeli plan nie przeszedł walidacji albo łańcuch jest niekompletny, nie przedstawiaj go jako wykonalnej procedury. Wskaż wyraźnie, które kroki są zablokowane lub czego brakuje.

## 10. Zmiany po stronie użytkownika i zatwierdzanie

- Analiza jest propozycją, a nie zgodą na automatyczne przeniesienie modów.
- Nie wykonywać zmian w grze ani nie zakładać, że użytkownik zaakceptował wariant.
- Po zmianach wykonanych przez użytkownika należy pobrać nowy eksport przed następną optymalizacją.
- Jeżeli użytkownik poprawi dane lub zgłosi błąd, ponownie przeliczyć wszystkie zależne elementy, a nie tylko poprawić opis w raporcie.

## 11. Odpowiedzialność implementacyjna

Ten standard opisuje wymagany wynik analizy. Samo dodanie dokumentu nie oznacza, że istniejący skrypt już realizuje wszystkie reguły.

- `generate_mods.py` odpowiada za ekstrakcję i normalizację danych modów do CSV; nie należy umieszczać w nim reguł wyboru dawców ani oceny bilansu, jeśli nie jest modułem optymalizatora.
- Logika optymalizacji powinna oddzielać: profil celu, ocenę kandydatów, symulację zmian, ocenę dawców i walidację.
- Walidator powinien działać na końcowym planie zmian i blokować status REKOMENDACJA, jeżeli którykolwiek wymagany warunek nie został spełniony.
- Testy powinny obejmować co najmniej: komplet bez przeniesień, przeniesienie z magazynu, przeniesienie od dawcy z zachowaniem zestawu, utratę bonusu zestawu, łańcuch wielopoziomowy, brak zamiennika, podwójne użycie moda, chronionego dawcę i niekompletne dane.
- Przed modyfikacją istniejącego algorytmu należy ustalić jego rzeczywisty plik wejściowy i aktualną architekturę. Nie wolno zgadywać nazw plików ani wprowadzać zmian do generatora eksportu jako pozornej naprawy optymalizatora.

## 12. Krótka lista kontrolna do każdej nowej analizy

Przed rozpoczęciem:
- [ ] Pobrałem świeże i spójne pliki.
- [ ] Znam aktualny profil celu i ograniczenia użytkownika.
- [ ] Wyszukuję kandydatów w całym rosterze i magazynie.

Przed przedstawieniem:
- [ ] Mam sześć modów docelowych.
- [ ] Mam pełne łańcuchy MOD/PATCH.
- [ ] Znam końcowy stan każdego dawcy.
- [ ] Policzyłem bonusy zestawów i statystyki przed/po.
- [ ] Przeszedłem walidację.
- [ ] Uczciwie sklasyfikowałem wynik.

Jeśli nie można zaznaczyć wszystkich wymaganych pól, wynik pozostaje roboczy — nie jest rekomendacją.

## Eksperymentalne punktowanie dokładnej kombinacji setów — v19

Na gałęzi `vel-sartha-analysis-20261110` dostępny jest wariant porównawczy `set_combo_mode="exact"`. Domyślny tryb `base` pozostaje bez zmian i stanowi punkt odniesienia.

- Wariant exact zachowuje liczebność setów: rozróżnia np. `Double Health + Defense` od `Double Defense + Health`, a także poprawnie uwzględnia sety 4-elementowe, takie jak Speed i Offense.
- Pełny build sześciu modów jest dopasowywany do dokładnej kombinacji zapisanej w profilu. Częstość kombinacji jest normalizowana względem najczęstszej kombinacji tego profilu.
- Dla rozpoznanej kombinacji waga bonusów setów wynosi `0.10 + 0.90 × znormalizowana częstość`; ta sama preferencja jest używana jako tie-break.
- Jeżeli kombinacji nie ma w profilu albo build nie zawiera kompletu sześciu modów, wariant exact wraca do dotychczasowych preferencji pojedynczych setów.
- Jest to eksperyment porównawczy, a nie zmiana zatwierdzonego algorytmu. Nie przenosić go do stabilnej gałęzi bez osobnej oceny wyników na identycznym snapshotcie C-3PO.
