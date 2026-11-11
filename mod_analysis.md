# Analiza modów

Model rozdziela **jakość obecnych rolli**, **potencjał dalszego rozwoju**, **dopasowanie do postaci** i **rodzaj następnej inwestycji**.

W raportach przeznaczonych do ręcznego wykonania mod identyfikowany jest wyłącznie przez slot, set, primary, secondary, gwiazdki, tier i poziom; wewnętrzne ID nie są pokazywane.

- Modów: **2194**
- Cel(e) optymalizacji: **50RT** (źródło: parametr --target)
- UPGRADE: **30**
- SLICE: **1156**
- SLICE_6E: **239**
- CALIBRATE: **104**
- EQUIP: **0**
- REPLACE: **0**
- PATCH: **0**
- KEEP: **665**

## Profile SWGOH.GG — lokalna baza

Profile są przechowywane lokalnie i odświeżane tylko dla celu oraz dawców faktycznie wyznaczonego łańcucha transferów. Po pobraniu profili dawców łańcuch jest ponownie oceniany; jeśli zmieni się dawca, jego profil również zostanie sprawdzony. Cache ma ważność 90 dni. Nieudane lub niepełne pobranie nie nadpisuje poprzedniego poprawnego profilu.

| Postać (baseId) | Status |
|---|---|
| 50RT | cached |
| AMILYNHOLDO | unavailable |
| BAZEMALBUS | unavailable |
| BT1 | unavailable |
| DARTHMALGUS | unavailable |
| EMPERORPALPATINE | unavailable |
| GLREY | unavailable |
| HERMITYODA | unavailable |
| JARJARBINKS | cached |
| JEDIKNIGHTREVAN | cached |
| MERRIN | cached |
| PADMEAMIDALA | unavailable |
| REYJEDITRAINING | unavailable |
| SECONDSISTER | unavailable |

Dla dawców bez lokalnego profilu po próbie pobrania używany jest fallback modValue; nie jest to ocena dopasowania do indywidualnego profilu.

## Globalny optimizer 6-slotowy

Ocena kompletnego buildu: 40 pkt za statystyki główne, 60 pkt za maksymalnie 24 rolle secondary oraz bonusy setów ważone profilem postaci. Zgodność z profilem ma pierwszeństwo przed zachowaniem aktualnie założonych modów. Set nieobecny w profilu zachowuje 10% bazowej wagi bonusu; set z preferencją 100% otrzymuje pełną wagę. Zachowanie modów na celu jest dopiero końcowym tie-breakiem.

Ranking kandydujących buildów używa oddzielnej projekcji: brakujące rolle do limitu aktualnego tieru są optymistycznie przypisywane do najwyżej preferowanej statystyki profilu; mod 5A na poziomie 15 jest dodatkowo przeliczany do 6E. To górna granica potencjału, nie prognoza RNG ani rzeczywiste statystyki moda. Primary pozostaje na wartości z eksportu, ponieważ nie mamy w danych tabeli jego przyrostu dla każdego poziomu. Raport pokazuje osobno wynik aktualny i wynik po projekcji.

Bonus Speed Set używa bazowej szybkości 150, jeśli profil nie zawiera pola base_stats.Speed. Pozostałe bonusy procentowe są normalizowane względem maksymalnego rolla odpowiedniej statystyki.

## Najważniejsi kandydaci

| Akcja | Mod | Źródło | Set | Tier | Lvl | Quality | Value | Fit | 6E proj. | Speed | Potencjał | Inwestycja |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| CALIBRATE | Circle Protection % 24% | POSTAĆ: JARJARBINKS | Speed | 6A | 15 | 100.0% | 75.3% | 49.5% | 0.0% | 76.7% | 75.3% | calibration |
| CALIBRATE | Cross Health % 16% | POSTAĆ: JEDIKNIGHTREVAN | Health | 6A | 15 | 100.0% | 78.2% | 47.3% | 0.0% | 66.7% | 78.2% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: JARJARBINKS | Speed | 6A | 15 | 100.0% | 63.5% | 46.8% | 0.0% | 86.7% | 63.5% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: GLREY | Offense | 6A | 15 | 100.0% | 74.3% | 46.1% | 0.0% | 93.3% | 74.3% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: JARJARBINKS | Potency | 6A | 15 | 100.0% | 73.2% | 44.9% | 0.0% | 80.0% | 73.2% | calibration |
| CALIBRATE | Arrow Speed 32 | POSTAĆ: JARJARBINKS | Speed | 6A | 15 | 100.0% | 58.2% | 44.7% | 0.0% | 0.0% | 58.2% | calibration |
| CALIBRATE | Triangle Critical Chance % 20% | POSTAĆ: JARJARBINKS | Speed | 6A | 15 | 100.0% | 71.0% | 44.6% | 0.0% | 86.7% | 71.0% | calibration |
| CALIBRATE | Arrow Protection % 24% | POSTAĆ: JEDIKNIGHTREVAN | Speed | 6A | 15 | 100.0% | 68.2% | 43.5% | 0.0% | 80.0% | 68.2% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: GLREY | Health | 6A | 15 | 100.0% | 65.3% | 43.2% | 0.0% | 73.3% | 65.3% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: JARJARBINKS | Potency | 6A | 15 | 100.0% | 68.2% | 42.2% | 0.0% | 75.0% | 68.2% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: HERMITYODA | Speed | 6A | 15 | 100.0% | 71.5% | 41.9% | 0.0% | 79.2% | 71.5% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: GLREY | Offense | 6A | 15 | 100.0% | 76.7% | 41.2% | 0.0% | 80.0% | 76.7% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: COMMANDERLUKESKYWALKER | Offense | 6A | 15 | 100.0% | 76.0% | 40.8% | 0.0% | 80.0% | 76.0% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: ENFYSNEST | Tenacity | 6A | 15 | 100.0% | 71.0% | 40.8% | 0.0% | 83.3% | 71.0% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: MARAJADE | Speed | 6A | 15 | 100.0% | 68.2% | 39.0% | 0.0% | 79.2% | 68.2% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: MARAJADE | Potency | 6A | 15 | 100.0% | 78.3% | 38.6% | 0.0% | 70.0% | 78.3% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: VADER | Critical Chance | 6A | 15 | 100.0% | 74.3% | 37.1% | 0.0% | 70.8% | 74.3% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: HOTHLEIA | Critical Chance | 6A | 15 | 100.0% | 69.2% | 37.0% | 0.0% | 79.2% | 69.2% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: REY | Critical Chance | 6A | 15 | 100.0% | 64.5% | 36.6% | 0.0% | 79.2% | 64.5% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: EMPERORPALPATINE | Speed | 6A | 15 | 100.0% | 64.5% | 36.6% | 0.0% | 79.2% | 64.5% | calibration |
| CALIBRATE | Cross Tenacity % 35% | POSTAĆ: NINTHSISTER | Tenacity | 6A | 15 | 100.0% | 62.0% | 36.6% | 0.0% | 83.3% | 62.0% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: HOTHLEIA | Critical Damage | 6A | 15 | 100.0% | 63.8% | 35.3% | 0.0% | 88.9% | 63.8% | calibration |
| CALIBRATE | Triangle Health % 16% | POSTAĆ: JEDIKNIGHTREVAN | Speed | 6A | 15 | 100.0% | 58.0% | 34.4% | 0.0% | 79.2% | 58.0% | calibration |
| CALIBRATE | Cross Tenacity % 35% | POSTAĆ: SEVENTHSISTER | Speed | 6A | 15 | 100.0% | 74.0% | 34.1% | 0.0% | 83.3% | 74.0% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: VADER | Critical Damage | 6A | 15 | 100.0% | 82.0% | 33.3% | 0.0% | 76.7% | 82.0% | calibration |
| CALIBRATE | Triangle Health % 16% | POSTAĆ: NINTHSISTER | Tenacity | 6A | 15 | 100.0% | 79.7% | 33.3% | 0.0% | 83.3% | 79.7% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: SANASTARROS | Health | 6A | 15 | 100.0% | 71.3% | 33.3% | 0.0% | 76.7% | 71.3% | calibration |
| CALIBRATE | Cross Protection % 24% | POSTAĆ: SCORCH | Health | 6A | 15 | 100.0% | 69.5% | 33.3% | 0.0% | 73.3% | 69.5% | calibration |
| CALIBRATE | Diamond Defense % 20% | MAGAZYN | Speed | 6A | 15 | 100.0% | 64.3% | 33.3% | 0.0% | 80.0% | 64.3% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: SEVENTHSISTER | Speed | 6A | 15 | 100.0% | 63.8% | 33.3% | 0.0% | 76.7% | 63.8% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: JEDIKNIGHTREVAN | Health | 6A | 15 | 100.0% | 62.5% | 33.3% | 0.0% | 80.0% | 62.5% | calibration |
| CALIBRATE | Triangle Protection % 24% | POSTAĆ: SCORCH | Health | 6A | 15 | 100.0% | 70.3% | 32.9% | 0.0% | 61.1% | 70.3% | calibration |
| CALIBRATE | Triangle Critical Chance % 20% | POSTAĆ: BB8 | Health | 6A | 15 | 100.0% | 67.0% | 32.4% | 0.0% | 83.3% | 67.0% | calibration |
| CALIBRATE | Arrow Protection % 24% | POSTAĆ: VANGUARDTEMPLEGUARD | Speed | 6A | 15 | 100.0% | 66.0% | 31.9% | 0.0% | 70.8% | 66.0% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: VANGUARDTEMPLEGUARD | Speed | 6A | 15 | 100.0% | 82.3% | 31.6% | 0.0% | 75.0% | 82.3% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: VADER | Critical Damage | 6A | 15 | 100.0% | 67.3% | 31.6% | 0.0% | 75.0% | 67.3% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: MARAJADE | Speed | 6A | 15 | 100.0% | 57.7% | 31.6% | 0.0% | 70.8% | 57.7% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: GRANDADMIRALTHRAWN | Speed | 6A | 15 | 100.0% | 70.0% | 30.5% | 0.0% | 83.3% | 70.0% | calibration |
| CALIBRATE | Triangle Offense % 8.5% | POSTAĆ: GLREY | Offense | 6A | 15 | 100.0% | 65.8% | 30.5% | 0.0% | 83.3% | 65.8% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: EPIXFINN | Speed | 6A | 15 | 100.0% | 65.8% | 30.5% | 0.0% | 88.9% | 65.8% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: BB8 | Speed | 6A | 15 | 100.0% | 63.7% | 30.3% | 0.0% | 77.8% | 63.7% | calibration |
| CALIBRATE | Triangle Critical Chance % 20% | POSTAĆ: COMMANDERLUKESKYWALKER | Tenacity | 6A | 15 | 100.0% | 63.2% | 29.9% | 0.0% | 94.4% | 63.2% | calibration |
| CALIBRATE | Arrow Offense % 8.5% | POSTAĆ: GLREY | Offense | 6A | 15 | 100.0% | 59.5% | 29.9% | 0.0% | 77.8% | 59.5% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: FIFTHBROTHER | Speed | 6A | 15 | 100.0% | 66.7% | 29.3% | 0.0% | 70.8% | 66.7% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: EMPERORPALPATINE | Potency | 6A | 15 | 100.0% | 65.3% | 29.1% | 0.0% | 70.8% | 65.3% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: VADER | Critical Damage | 6A | 15 | 100.0% | 62.0% | 28.8% | 0.0% | 75.0% | 62.0% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: BOOMADIER | Speed | 6A | 15 | 100.0% | 84.2% | 27.9% | 0.0% | 83.3% | 84.2% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: MARAJADE | Speed | 6A | 15 | 100.0% | 81.0% | 27.9% | 0.0% | 88.9% | 81.0% | calibration |
| CALIBRATE | Triangle Protection % 24% | POSTAĆ: FIFTHBROTHER | Speed | 6A | 15 | 100.0% | 76.0% | 27.9% | 0.0% | 94.4% | 76.0% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: EPIXFINN | Speed | 6A | 15 | 100.0% | 68.8% | 27.9% | 0.0% | 77.8% | 68.8% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: EMPERORPALPATINE | Potency | 6A | 15 | 100.0% | 60.3% | 27.4% | 0.0% | 88.9% | 60.3% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: HONDO | Speed | 6A | 15 | 100.0% | 55.3% | 27.4% | 0.0% | 83.3% | 55.3% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: MARAJADE | Speed | 6A | 15 | 100.0% | 55.2% | 27.4% | 0.0% | 88.9% | 55.2% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: REYJEDITRAINING | Health | 6A | 15 | 100.0% | 52.7% | 27.4% | 0.0% | 77.8% | 52.7% | calibration |
| CALIBRATE | Cross Protection % 24% | POSTAĆ: GRANDADMIRALTHRAWN | Speed | 6A | 15 | 100.0% | 51.8% | 27.4% | 0.0% | 83.3% | 51.7% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: GRANDMOFFTARKIN | Potency | 6A | 15 | 100.0% | 51.4% | 27.4% | 0.0% | 77.8% | 51.4% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: COMMANDERLUKESKYWALKER | Offense | 6A | 15 | 100.0% | 79.4% | 26.7% | 0.0% | 87.5% | 79.4% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: OPERATIVE | Speed | 6A | 15 | 100.0% | 78.5% | 26.7% | 0.0% | 79.2% | 78.5% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: REY | Critical Damage | 6A | 15 | 100.0% | 73.8% | 26.7% | 0.0% | 87.5% | 73.8% | calibration |
| CALIBRATE | Cross Offense % 8.5% | POSTAĆ: GLREY | Health | 6A | 15 | 100.0% | 69.3% | 26.7% | 0.0% | 79.2% | 69.3% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: SCORCH | Health | 6A | 15 | 100.0% | 65.5% | 26.7% | 0.0% | 91.7% | 65.5% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: BOSSNASS | Potency | 6A | 15 | 100.0% | 65.2% | 26.7% | 0.0% | 79.2% | 65.2% | calibration |
| CALIBRATE | Triangle Health % 16% | MAGAZYN | Potency | 6A | 15 | 100.0% | 65.1% | 26.7% | 0.0% | 83.3% | 65.1% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: VANGUARDTEMPLEGUARD | Speed | 6A | 15 | 100.0% | 65.1% | 26.7% | 0.0% | 75.0% | 65.1% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: FIFTHBROTHER | Health | 6A | 15 | 100.0% | 65.0% | 26.7% | 0.0% | 75.0% | 65.0% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: GRANDMOFFTARKIN | Speed | 6A | 15 | 100.0% | 64.0% | 26.7% | 0.0% | 79.2% | 64.0% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: SEVENTHSISTER | Speed | 6A | 15 | 100.0% | 63.0% | 26.7% | 0.0% | 91.7% | 63.0% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: VADER | Critical Damage | 6A | 15 | 100.0% | 61.3% | 26.7% | 0.0% | 83.3% | 61.3% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: COMMANDERLUKESKYWALKER | Offense | 6A | 15 | 100.0% | 57.0% | 26.7% | 0.0% | 83.3% | 57.0% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: BOOMADIER | Critical Chance | 6A | 15 | 100.0% | 55.3% | 26.7% | 0.0% | 87.5% | 55.3% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: EMPERORPALPATINE | Speed | 6A | 15 | 100.0% | 69.8% | 26.4% | 0.0% | 83.3% | 69.8% | calibration |
| CALIBRATE | Triangle Protection % 24% | POSTAĆ: GRANDADMIRALTHRAWN | Health | 6A | 15 | 100.0% | 77.0% | 24.9% | 0.0% | 72.2% | 77.0% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: NINTHSISTER | Tenacity | 6A | 15 | 100.0% | 68.0% | 24.9% | 0.0% | 77.8% | 68.0% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: FIFTHBROTHER | Health | 6A | 15 | 100.0% | 54.5% | 24.9% | 0.0% | 83.3% | 54.5% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: JEDIKNIGHTREVAN | Speed | 6A | 15 | 100.0% | 56.8% | 22.5% | 0.0% | 72.2% | 56.8% | calibration |

### 50RT — najlepszy wirtualny build 6/6

- Wynik buildu po projekcji: **99.8** (lvl 15; 5A → 6E)
- Aktualny build bez projekcji: **32.5**
- Aktualny build po tej samej projekcji: **32.5**
- Zmiana potencjału względem projekcji obecnego buildu: **+67.3**
- Bonus setów w ocenie: **13.14**
| Slot | Mod — parametry wyszukiwalne | Źródło | Fit |
|---|---|---|---:|
| Square | Square / Health / Offense % 5.88% / secondary: Critical Chance % 3.35%, Protection 459, Speed 20, Potency % 1.71% / 5★ A lvl15 | POSTAĆ: MERRIN | 40.0 |
| Diamond | Diamond / Speed / Defense % 20% / secondary: Tenacity % 5.13%, Potency % 3.46%, Speed 24, Protection 1994 / 6★ A lvl15 | MAGAZYN | 33.3 |
| Circle | Circle / Speed / Protection % 24% / secondary: Health 1116, Protection 1329, Speed 23, Offense 71 / 6★ A lvl15 | POSTAĆ: JARJARBINKS | 46.0 |
| Arrow | Arrow / Speed / Protection % 24% / secondary: Health 770, Defense % 9.48%, Protection 1035, Speed 24 / 6★ A lvl15 | POSTAĆ: JEDIKNIGHTREVAN | 38.3 |
| Triangle | Triangle / Speed / Critical Chance % 20% / secondary: Health 1349, Protection % 3.68%, Potency % 5.51%, Speed 26 / 6★ A lvl15 | POSTAĆ: JARJARBINKS | 40.8 |
| Cross | Cross / Health / Health % 16% / secondary: Health 694, Protection 1743, Speed 20, Offense 116 / 6★ A lvl15 | POSTAĆ: JEDIKNIGHTREVAN | 46.1 |

## BEZPIECZNY ŁAŃCUCH — walidacja globalna

**STATUS: BLOKADA — nie wygenerowano bezpiecznej listy ruchów.**
- 50RT: konflikt modów dla Circle / Speed
- 50RT: konflikt modów dla Arrow / Speed
- 50RT: konflikt modów dla Triangle / Speed
- 50RT: konflikt modów dla Cross / Health
- 50RT: optimizer mod nie trafił na miejsce: Circle
- 50RT: optimizer mod nie trafił na miejsce: Arrow
- 50RT: optimizer mod nie trafił na miejsce: Triangle
- 50RT: optimizer mod nie trafił na miejsce: Cross

| Postać | Σ modValue przed | Σ modValue po | Δ modValue | Pełne sety przed | Pełne sety po |
|---|---:|---:|---:|---|---|
| MERRIN | 369.9 | 403.4 | +33.5 | Health=1, Potency=1, Tenacity=1 | Health=1, Potency=1, Tenacity=1 |
| 50RT | 330.6 | 350.4 | +19.8 | Speed=1 | Health=1, Speed=1 |

### Dokładna kombinacja setów dawców

| Postać | Przed | Częstość | Po | Częstość |
|---|---|---:|---|---:|
| MERRIN | Health + Potency + Tenacity | 11.9% | Health + Potency + Tenacity | 11.9% |
| 50RT | brak w profilu | — | Speed + Health | 27.4% |

### Zmiany setów — każda postać w łańcuchu

ROZBITO oznacza utratę co najmniej jednej pełnej grupy. BUDOWANY oznacza zwiększenie liczby modów danego setu bez ukończenia kolejnej grupy. UKOŃCZONO oznacza powstanie dodatkowej pełnej grupy. OSŁABIONY oznacza zmianę liczebności bez ukończenia lub rozbicia pełnej grupy.

| Postać | Set | Zmiana liczby modów | Pełne sety | Status |
|---|---|---:|---:|---|
| 50RT | Health | 1/2 → 2/2 | 0 → 1 | UKOŃCZONO |
| 50RT | Speed | 5/4 → 4/4 | 1 → 1 | OSŁABIONY |

### Ruchy — kolejność fizyczna

**Ważne:** każdy mod jest przenoszony tylko raz. Najpierw właściwy mod z `Źródło` trafia **bezpośrednio** do celu. Dopiero potem wykonujemy PATCH-y. Ponieważ wyszukiwanie po postaci nie jest dostępne, każda operacja zawiera slot, set, primary, wszystkie dostępne secondary, liczbę gwiazdek, tier i poziom.

| Krok | Typ | Operacja | Mod — parametry wyszukiwalne | Status |
|---:|---|---|---|---|
| — | — | — | — | BLOCKED |

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
