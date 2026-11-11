# Analiza modów

Model rozdziela **jakość obecnych rolli**, **potencjał dalszego rozwoju**, **dopasowanie do postaci** i **rodzaj następnej inwestycji**.

W raportach przeznaczonych do ręcznego wykonania mod identyfikowany jest wyłącznie przez slot, set, primary, secondary, gwiazdki, tier i poziom; wewnętrzne ID nie są pokazywane.

- Modów: **2194**
- Cel(e) optymalizacji: **JARJARBINKS** (źródło: targets.json)
- UPGRADE: **30**
- SLICE: **1156**
- SLICE_6E: **238**
- CALIBRATE: **103**
- EQUIP: **0**
- REPLACE: **1**
- PATCH: **1**
- KEEP: **665**

## Profile SWGOH.GG — lokalna baza

Profile są przechowywane lokalnie i odświeżane tylko dla celu oraz dawców faktycznie wyznaczonego łańcucha transferów. Po pobraniu profili dawców łańcuch jest ponownie oceniany; jeśli zmieni się dawca, jego profil również zostanie sprawdzony. Cache ma ważność 90 dni. Nieudane lub niepełne pobranie nie nadpisuje poprzedniego poprawnego profilu.

| Postać (baseId) | Status |
|---|---|
| JARJARBINKS | cached |
| JEDIKNIGHTREVAN | cached |

Dla dawców bez lokalnego profilu po próbie pobrania używany jest fallback modValue; nie jest to ocena dopasowania do indywidualnego profilu.

## Globalny optimizer 6-slotowy

Ocena kompletnego buildu: 40 pkt za statystyki główne, 60 pkt za maksymalnie 24 rolle secondary oraz bonusy setów ważone profilem postaci. Zgodność z profilem ma pierwszeństwo przed zachowaniem aktualnie założonych modów. Set nieobecny w profilu zachowuje 10% bazowej wagi bonusu; set z preferencją 100% otrzymuje pełną wagę. Zachowanie modów na celu jest dopiero końcowym tie-breakiem.

Ranking kandydujących buildów używa oddzielnej projekcji: brakujące rolle do limitu aktualnego tieru są optymistycznie przypisywane do najwyżej preferowanej statystyki profilu; mod 5A na poziomie 15 jest dodatkowo przeliczany do 6E. To górna granica potencjału, nie prognoza RNG ani rzeczywiste statystyki moda. Primary pozostaje na wartości z eksportu, ponieważ nie mamy w danych tabeli jego przyrostu dla każdego poziomu. Raport pokazuje osobno wynik aktualny i wynik po projekcji.

Bonus Speed Set używa bazowej szybkości 150, jeśli profil nie zawiera pola base_stats.Speed. Pozostałe bonusy procentowe są normalizowane względem maksymalnego rolla odpowiedniej statystyki.

## Najważniejsi kandydaci

| Akcja | Mod | Źródło | Set | Tier | Lvl | Quality | Value | Fit | 6E proj. | Speed | Potencjał | Inwestycja |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| REPLACE | Arrow Protection % 24% | POSTAĆ: JEDIKNIGHTREVAN | Speed | 6A | 15 | 100.0% | 68.2% | 43.5% | 0.0% | 80.0% | 68.2% | calibration |
| PATCH | Arrow Health % 5.88% | MAGAZYN | Critical Chance | 5A | 15 | 100.0% | 87.2% | 0.0% | 51.2% | 83.3% | 87.2% | 6-dot |
| CALIBRATE | Cross Health % 16% | POSTAĆ: JEDIKNIGHTREVAN | Health | 6A | 15 | 100.0% | 78.2% | 47.3% | 0.0% | 66.7% | 78.2% | calibration |
| CALIBRATE | Triangle Health % 16% | POSTAĆ: JEDIKNIGHTREVAN | Speed | 6A | 15 | 100.0% | 58.0% | 34.4% | 0.0% | 79.2% | 58.0% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: JEDIKNIGHTREVAN | Health | 6A | 15 | 100.0% | 62.5% | 33.3% | 0.0% | 80.0% | 62.5% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: JEDIKNIGHTREVAN | Speed | 6A | 15 | 100.0% | 56.8% | 22.5% | 0.0% | 72.2% | 56.8% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: JEDIKNIGHTREVAN | Speed | 6A | 15 | 100.0% | 59.2% | 19.5% | 0.0% | 75.0% | 59.2% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: BOOMADIER | Speed | 6A | 15 | 100.0% | 84.2% | 0.0% | 0.0% | 83.3% | 84.2% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: GRANDADMIRALTHRAWN | Speed | 6A | 15 | 100.0% | 83.5% | 0.0% | 0.0% | 75.0% | 83.5% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: VANGUARDTEMPLEGUARD | Speed | 6A | 15 | 100.0% | 82.3% | 0.0% | 0.0% | 75.0% | 82.3% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: VADER | Critical Damage | 6A | 15 | 100.0% | 82.0% | 0.0% | 0.0% | 76.7% | 82.0% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: MARAJADE | Speed | 6A | 15 | 100.0% | 81.0% | 0.0% | 0.0% | 88.9% | 81.0% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: VEL | Defense | 6A | 15 | 100.0% | 80.0% | 0.0% | 0.0% | 66.7% | 80.0% | calibration |
| CALIBRATE | Triangle Health % 16% | POSTAĆ: NINTHSISTER | Tenacity | 6A | 15 | 100.0% | 79.7% | 0.0% | 0.0% | 83.3% | 79.7% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: COMMANDERLUKESKYWALKER | Offense | 6A | 15 | 100.0% | 79.4% | 0.0% | 0.0% | 87.5% | 79.4% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: OPERATIVE | Speed | 6A | 15 | 100.0% | 78.5% | 0.0% | 0.0% | 79.2% | 78.5% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: MARAJADE | Potency | 6A | 15 | 100.0% | 78.3% | 0.0% | 0.0% | 70.0% | 78.3% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: HERMITYODA | Speed | 6A | 15 | 100.0% | 78.3% | 0.0% | 0.0% | 91.7% | 78.3% | calibration |
| CALIBRATE | Triangle Protection % 24% | POSTAĆ: GRANDADMIRALTHRAWN | Health | 6A | 15 | 100.0% | 77.0% | 0.0% | 0.0% | 72.2% | 77.0% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: GLREY | Offense | 6A | 15 | 100.0% | 76.7% | 0.0% | 0.0% | 80.0% | 76.7% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: COMMANDERLUKESKYWALKER | Offense | 6A | 15 | 100.0% | 76.0% | 0.0% | 0.0% | 80.0% | 76.0% | calibration |
| CALIBRATE | Triangle Protection % 24% | POSTAĆ: FIFTHBROTHER | Speed | 6A | 15 | 100.0% | 76.0% | 0.0% | 0.0% | 94.4% | 76.0% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: JARJARBINKS | Speed | 6A | 15 | 100.0% | 75.3% | 0.0% | 0.0% | 76.7% | 75.3% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: VADER | Critical Chance | 6A | 15 | 100.0% | 74.3% | 0.0% | 0.0% | 70.8% | 74.3% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: GLREY | Offense | 6A | 15 | 100.0% | 74.3% | 0.0% | 0.0% | 93.3% | 74.3% | calibration |
| CALIBRATE | Cross Tenacity % 35% | POSTAĆ: SEVENTHSISTER | Speed | 6A | 15 | 100.0% | 74.0% | 0.0% | 0.0% | 83.3% | 74.0% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: REY | Critical Damage | 6A | 15 | 100.0% | 73.8% | 0.0% | 0.0% | 87.5% | 73.8% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: GRANDMOFFTARKIN | Speed | 6A | 15 | 100.0% | 73.3% | 0.0% | 0.0% | 100.0% | 73.3% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: JARJARBINKS | Potency | 6A | 15 | 100.0% | 73.2% | 0.0% | 0.0% | 80.0% | 73.2% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: REYJEDITRAINING | Health | 6A | 15 | 100.0% | 72.2% | 0.0% | 0.0% | 83.3% | 72.2% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: HERMITYODA | Speed | 6A | 15 | 100.0% | 71.5% | 0.0% | 0.0% | 79.2% | 71.5% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: SANASTARROS | Health | 6A | 15 | 100.0% | 71.3% | 0.0% | 0.0% | 76.7% | 71.3% | calibration |
| CALIBRATE | Triangle Critical Chance % 20% | POSTAĆ: JARJARBINKS | Speed | 6A | 15 | 100.0% | 71.0% | 0.0% | 0.0% | 86.7% | 71.0% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: ENFYSNEST | Tenacity | 6A | 15 | 100.0% | 71.0% | 0.0% | 0.0% | 83.3% | 71.0% | calibration |
| CALIBRATE | Triangle Protection % 24% | POSTAĆ: SCORCH | Health | 6A | 15 | 100.0% | 70.3% | 0.0% | 0.0% | 61.1% | 70.3% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: GRANDADMIRALTHRAWN | Speed | 6A | 15 | 100.0% | 70.0% | 0.0% | 0.0% | 83.3% | 70.0% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: EMPERORPALPATINE | Speed | 6A | 15 | 100.0% | 69.8% | 0.0% | 0.0% | 83.3% | 69.8% | calibration |
| CALIBRATE | Cross Protection % 24% | POSTAĆ: SCORCH | Health | 6A | 15 | 100.0% | 69.5% | 0.0% | 0.0% | 73.3% | 69.5% | calibration |
| CALIBRATE | Cross Offense % 8.5% | POSTAĆ: GLREY | Health | 6A | 15 | 100.0% | 69.3% | 0.0% | 0.0% | 79.2% | 69.3% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: HOTHLEIA | Critical Chance | 6A | 15 | 100.0% | 69.2% | 0.0% | 0.0% | 79.2% | 69.2% | calibration |
| CALIBRATE | Arrow Speed 32 | POSTAĆ: SEVENTHSISTER | Health | 6A | 15 | 100.0% | 69.0% | 0.0% | 0.0% | 0.0% | 69.0% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: GRANDMOFFTARKIN | Speed | 6A | 15 | 100.0% | 69.0% | 0.0% | 0.0% | 88.9% | 69.0% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: EPIXFINN | Speed | 6A | 15 | 100.0% | 68.8% | 0.0% | 0.0% | 77.8% | 68.8% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: REYJEDITRAINING | Health | 6A | 15 | 100.0% | 68.3% | 0.0% | 0.0% | 100.0% | 68.3% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: ENFYSNEST | Tenacity | 6A | 15 | 100.0% | 68.3% | 0.0% | 0.0% | 88.9% | 68.3% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: JARJARBINKS | Potency | 6A | 15 | 100.0% | 68.2% | 0.0% | 0.0% | 75.0% | 68.2% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: MARAJADE | Speed | 6A | 15 | 100.0% | 68.2% | 0.0% | 0.0% | 79.2% | 68.2% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: NINTHSISTER | Tenacity | 6A | 15 | 100.0% | 68.0% | 0.0% | 0.0% | 77.8% | 68.0% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: VADER | Critical Damage | 6A | 15 | 100.0% | 67.3% | 0.0% | 0.0% | 75.0% | 67.3% | calibration |
| CALIBRATE | Triangle Critical Chance % 20% | POSTAĆ: BB8 | Health | 6A | 15 | 100.0% | 67.0% | 0.0% | 0.0% | 83.3% | 67.0% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: FIFTHBROTHER | Speed | 6A | 15 | 100.0% | 66.7% | 0.0% | 0.0% | 70.8% | 66.7% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: BB8 | Health | 6A | 15 | 100.0% | 66.5% | 0.0% | 0.0% | 91.7% | 66.5% | calibration |
| CALIBRATE | Arrow Speed 32 | POSTAĆ: BENSOLO | Offense | 6A | 15 | 100.0% | 66.5% | 0.0% | 0.0% | 0.0% | 66.5% | calibration |
| CALIBRATE | Arrow Protection % 24% | POSTAĆ: VANGUARDTEMPLEGUARD | Speed | 6A | 15 | 100.0% | 66.0% | 0.0% | 0.0% | 70.8% | 66.0% | calibration |
| CALIBRATE | Triangle Offense % 8.5% | POSTAĆ: GLREY | Offense | 6A | 15 | 100.0% | 65.8% | 0.0% | 0.0% | 83.3% | 65.8% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: EPIXFINN | Speed | 6A | 15 | 100.0% | 65.8% | 0.0% | 0.0% | 88.9% | 65.8% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: SCORCH | Health | 6A | 15 | 100.0% | 65.5% | 0.0% | 0.0% | 91.7% | 65.5% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: GLREY | Health | 6A | 15 | 100.0% | 65.3% | 0.0% | 0.0% | 73.3% | 65.3% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: EMPERORPALPATINE | Potency | 6A | 15 | 100.0% | 65.3% | 0.0% | 0.0% | 70.8% | 65.3% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: BOSSNASS | Potency | 6A | 15 | 100.0% | 65.2% | 0.0% | 0.0% | 79.2% | 65.2% | calibration |
| CALIBRATE | Triangle Health % 16% | MAGAZYN | Potency | 6A | 15 | 100.0% | 65.1% | 0.0% | 0.0% | 83.3% | 65.1% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: VANGUARDTEMPLEGUARD | Speed | 6A | 15 | 100.0% | 65.1% | 0.0% | 0.0% | 75.0% | 65.1% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: FIFTHBROTHER | Health | 6A | 15 | 100.0% | 65.0% | 0.0% | 0.0% | 75.0% | 65.0% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: EPIXPOE | Offense | 6A | 15 | 100.0% | 64.8% | 0.0% | 0.0% | 100.0% | 64.8% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: REY | Critical Chance | 6A | 15 | 100.0% | 64.5% | 0.0% | 0.0% | 79.2% | 64.5% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: EMPERORPALPATINE | Speed | 6A | 15 | 100.0% | 64.5% | 0.0% | 0.0% | 79.2% | 64.5% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: REYJEDITRAINING | Health | 6A | 15 | 100.0% | 64.3% | 0.0% | 0.0% | 91.7% | 64.3% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: GRANDMOFFTARKIN | Potency | 6A | 15 | 100.0% | 64.3% | 0.0% | 0.0% | 75.0% | 64.3% | calibration |
| CALIBRATE | Diamond Defense % 20% | MAGAZYN | Speed | 6A | 15 | 100.0% | 64.3% | 0.0% | 0.0% | 80.0% | 64.3% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: GRANDMOFFTARKIN | Speed | 6A | 15 | 100.0% | 64.0% | 0.0% | 0.0% | 79.2% | 64.0% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: HOTHLEIA | Critical Damage | 6A | 15 | 100.0% | 63.8% | 0.0% | 0.0% | 88.9% | 63.8% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: SEVENTHSISTER | Speed | 6A | 15 | 100.0% | 63.8% | 0.0% | 0.0% | 76.7% | 63.8% | calibration |
| CALIBRATE | Cross Defense % 20% | POSTAĆ: HOTHLEIA | Critical Damage | 6A | 15 | 100.0% | 63.7% | 0.0% | 0.0% | 83.3% | 63.7% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: BB8 | Speed | 6A | 15 | 100.0% | 63.7% | 0.0% | 0.0% | 77.8% | 63.7% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: JARJARBINKS | Speed | 6A | 15 | 100.0% | 63.5% | 0.0% | 0.0% | 86.7% | 63.5% | calibration |

## BEZPIECZNY ŁAŃCUCH — walidacja globalna

**STATUS: OK — transfery są fizycznie wykonalne i nie dublują modów.**
Bilans pokazuje sumę modValue wyposażonych modów oraz pełne sety przed i po transferze. modValue jest wskaźnikiem jakości samych modów, a nie indywidualnym wynikiem buildu dawcy. Utrata wartości lub setu u dawcy nie blokuje ruchu; to jawna informacja do ręcznej decyzji.
Wariant łańcucha wybierany jest na najkrótszym wykonalnym poziomie według fit profilu dawcy, następnie zmiany pełnych setów i sumy modValue. Istniejące sety nie są twardą ochroną. Każda zmiana liczby modów w secie i liczby pełnych grup jest wyszczególniona niżej dla każdej postaci w łańcuchu. Dla dawców bez własnego profilu fit korzysta z ogólnego modValue.

| Postać | Σ modValue przed | Σ modValue po | Δ modValue | Pełne sety przed | Pełne sety po |
|---|---:|---:|---:|---|---|

### Dokładna kombinacja setów dawców

| Postać | Przed | Częstość | Po | Częstość |
|---|---|---:|---|---:|
| — | — | — | — | — |

### Zmiany setów — każda postać w łańcuchu

ROZBITO oznacza utratę co najmniej jednej pełnej grupy. BUDOWANY oznacza zwiększenie liczby modów danego setu bez ukończenia kolejnej grupy. UKOŃCZONO oznacza powstanie dodatkowej pełnej grupy. OSŁABIONY oznacza zmianę liczebności bez ukończenia lub rozbicia pełnej grupy.

| Postać | Set | Zmiana liczby modów | Pełne sety | Status |
|---|---|---:|---:|---|
| — | — | — | — | Bez zmian |

### Ruchy — kolejność fizyczna

**Ważne:** każdy mod jest przenoszony tylko raz. Najpierw właściwy mod z `Źródło` trafia **bezpośrednio** do celu. Dopiero potem wykonujemy PATCH-y. Ponieważ wyszukiwanie po postaci nie jest dostępne, każda operacja zawiera slot, set, primary, wszystkie dostępne secondary, liczbę gwiazdek, tier i poziom.

| Krok | Typ | Operacja | Mod — parametry wyszukiwalne | Status |
|---:|---|---|---|---|

## Definicje

- **Quality** — jakość wykonanych rolli względem zakresu dla 5-dot/6-dot.
- **Value** — jakość rolla pomnożona przez ogólną, niezależną od postaci użyteczność statystyki.
- **Fit** — dopasowanie pojedynczego moda do aktywnego profilu celu; nie zawiera bonusu całego kompletu.
- **SetBonusDelta** — zmiana rzeczywistego bonusu zestawów 6 modów celu po założeniu proponowanego moda.
- **FitAfterSet** — Fit moda powiększony o SetBonusDelta; pokazuje wpływ kompletu bez mieszania go z jakością secondary.
- **AccountGain** — bilans całej operacji przeniesienia i PATCH-a dla źródła; dla źródeł bez profilu używany jest globalny ModValue.
- **Potential** — sufit wartości przy idealnych przyszłych rollach; nie jest prognozą RNG.
- **Źródło MAGAZYN** — mod nie jest obecnie założony na żadnej postaci.
- **Źródło POSTAĆ: [nazwa]** — mod jest obecnie założony na wskazanej postaci.
- **EQUIP** — pusty slot celu; mod jest przydzielany tylko wtedy, gdy bilans całej operacji dla konta jest dodatni.
- **PATCH** — mod z magazynu, który bezpośrednio zastępuje mod zabrany z innej postaci.
- **REPLACE** — mod jest przenoszony do celu tylko wtedy, gdy poprawa celu i uwzględniona strata źródłowej postaci dają dodatni bilans dla konta.
- **AccountGain** — zysk celu minus strata wartości źródłowej postaci; dzięki temu mod nie jest zabierany, jeśli operacja pogarsza cały roster. Dla postaci bez profilu strata jest liczona przez globalny ModValue.
- **UPGRADE** — mod nie jest jeszcze na 15.
- **SLICE** — kolejny tier ma uzasadnienie jakościowe lub profilowe.
- **SLICE_6E** — 5A jest oceniane również przez projekcję jakości po wzroście statystyk do 6E.
- **CALIBRATE** — 6A jest na końcu slicing i może korzystać z calibration.

Calibration pozostaje losowe: wybrany roll jest usuwany z wybranego secondary, a nowy roll trafia losowo do dostępnych secondary. Analyzer wskazuje kandydatów, ale nie udaje, że zna wynik konkretnej próby.
