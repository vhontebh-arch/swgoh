# Analiza modów

Model rozdziela **jakość obecnych rolli**, **potencjał dalszego rozwoju**, **dopasowanie do postaci** i **rodzaj następnej inwestycji**.

W raportach przeznaczonych do ręcznego wykonania mod identyfikowany jest wyłącznie przez slot, set, primary, secondary, gwiazdki, tier i poziom; wewnętrzne ID nie są pokazywane.

- Modów: **2192**
- UPGRADE: **26**
- SLICE: **349**
- SLICE_6E: **193**
- CALIBRATE: **84**
- EQUIP: **0**
- REPLACE: **4**
- PATCH: **3**
- KEEP: **1533**

## Profile SWGOH.GG — lokalna baza

Profile są przechowywane lokalnie i odświeżane tylko dla celu oraz dawców faktycznie wyznaczonego łańcucha transferów. Po pobraniu profili dawców łańcuch jest ponownie oceniany; jeśli zmieni się dawca, jego profil również zostanie sprawdzony. Cache ma ważność 5 dni. Nieudane lub niepełne pobranie nie nadpisuje poprzedniego poprawnego profilu.

| Postać (baseId) | Status |
|---|---|
| KUIIL | unavailable |
| MASTERQUIGON | unavailable |
| STORMTROOPER | unavailable |
| VEL | cached |

Dla dawców bez lokalnego profilu po próbie pobrania używany jest fallback modValue; nie jest to ocena dopasowania do indywidualnego profilu.

## Globalny optimizer 6-slotowy

Ocena kompletnego buildu: 40 pkt za statystyki główne, 60 pkt za maksymalnie 24 rolle secondary oraz bonusy setów ważone profilem postaci. Zgodność z profilem ma pierwszeństwo przed zachowaniem aktualnie założonych modów. Set nieobecny w profilu zachowuje 10% bazowej wagi bonusu; set z preferencją 100% otrzymuje pełną wagę. Zachowanie modów na celu jest dopiero końcowym tie-breakiem.

Ranking kandydujących buildów używa oddzielnej projekcji: brakujące rolle do limitu aktualnego tieru są optymistycznie przypisywane do najwyżej preferowanej statystyki profilu; mod 5A na poziomie 15 jest dodatkowo przeliczany do 6E. To górna granica potencjału, nie prognoza RNG ani rzeczywiste statystyki moda. Primary pozostaje na wartości z eksportu, ponieważ nie mamy w danych tabeli jego przyrostu dla każdego poziomu. Raport pokazuje osobno wynik aktualny i wynik po projekcji.

Bonus Speed Set używa bazowej szybkości 150, jeśli profil nie zawiera pola base_stats.Speed. Pozostałe bonusy procentowe są normalizowane względem maksymalnego rolla odpowiedniej statystyki.

## Najważniejsi kandydaci

| Akcja | Mod | Źródło | Set | Tier | Lvl | Quality | Value | Fit | 6E proj. | Speed | Potencjał | Inwestycja |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| REPLACE | Triangle Critical Damage % 36% | POSTAĆ: KUIIL | Defense | 5E | 15 | 71.6% | 56.1% | 21.4% | 0.0% | 83.3% | 56.1% | slice |
| REPLACE | Circle Health % 5.88% | MAGAZYN | Defense | 5E | 15 | 67.6% | 51.1% | 19.0% | 0.0% | 83.3% | 51.1% | slice |
| REPLACE | Arrow Speed 30 | POSTAĆ: STORMTROOPER | Defense | 5E | 15 | 79.4% | 35.5% | 17.1% | 0.0% | 0.0% | 35.5% | slice |
| REPLACE | Square Offense % 5.88% | POSTAĆ: MASTERQUIGON | Defense | 5A | 15 | 72.9% | 47.7% | 16.7% | 69.9% | 83.3% | 47.7% | 6-dot |
| PATCH | Square Offense % 0.63% | MAGAZYN | Health | 5B | 1 | 74.3% | 55.6% | 33.5% | 0.0% | 83.3% | 81.0% | upgrade |
| PATCH | Triangle Critical Chance % 1.5% | MAGAZYN | Health | 5B | 1 | 78.8% | 60.8% | 25.0% | 0.0% | 83.3% | 83.2% | upgrade |
| PATCH | Arrow Health % 5.88% | MAGAZYN | Potency | 5D | 15 | 71.5% | 62.8% | 12.4% | 0.0% | 83.3% | 62.8% | slice |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: GLREY | Offense | 6A | 15 | 47.6% | 42.6% | 27.8% | 0.0% | 93.3% | 42.6% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: SCORCH | Health | 6A | 15 | 56.9% | 40.9% | 26.1% | 0.0% | 91.7% | 40.9% | calibration |
| CALIBRATE | Triangle Health % 16% | POSTAĆ: NINTHSISTER | Tenacity | 6A | 15 | 60.3% | 47.4% | 25.5% | 0.0% | 83.3% | 47.4% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: SEVENTHSISTER | Speed | 6A | 15 | 58.8% | 41.6% | 25.2% | 0.0% | 91.7% | 41.6% | calibration |
| CALIBRATE | Triangle Critical Chance % 20% | POSTAĆ: JARJARBINKS | Speed | 6A | 15 | 64.8% | 45.8% | 24.3% | 0.0% | 86.7% | 45.8% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: JEDIKNIGHTREVAN | Health | 6A | 15 | 57.7% | 36.1% | 23.9% | 0.0% | 80.0% | 36.1% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: MARAJADE | Speed | 6A | 15 | 65.2% | 38.6% | 23.8% | 0.0% | 88.9% | 38.6% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: JARJARBINKS | Speed | 6A | 15 | 56.0% | 39.7% | 23.5% | 0.0% | 86.7% | 39.7% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: SANASTARROS | Health | 6A | 15 | 54.2% | 37.4% | 23.3% | 0.0% | 76.7% | 37.4% | calibration |
| CALIBRATE | Arrow Protection % 24% | POSTAĆ: JEDIKNIGHTREVAN | Speed | 6A | 15 | 46.5% | 33.3% | 22.2% | 0.0% | 80.0% | 33.3% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: VADER | Critical Damage | 6A | 15 | 61.8% | 38.4% | 22.0% | 0.0% | 83.3% | 38.4% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: ENFYSNEST | Tenacity | 6A | 15 | 61.0% | 42.4% | 21.9% | 0.0% | 88.9% | 42.4% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: GLREY | Offense | 6A | 15 | 40.5% | 33.8% | 21.7% | 0.0% | 80.0% | 33.8% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: COMMANDERLUKESKYWALKER | Offense | 6A | 15 | 49.8% | 39.5% | 20.8% | 0.0% | 80.0% | 39.5% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: BOOMADIER | Critical Chance | 6A | 15 | 58.1% | 35.8% | 20.6% | 0.0% | 87.5% | 35.8% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: ENFYSNEST | Tenacity | 6A | 15 | 52.0% | 38.9% | 20.5% | 0.0% | 83.3% | 38.9% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: MARAJADE | Speed | 6A | 15 | 60.5% | 49.9% | 20.3% | 0.0% | 88.9% | 49.9% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: SCORCH | Defense | 6A | 15 | 53.5% | 31.1% | 20.3% | 0.0% | 88.9% | 31.1% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: GRANDMOFFTARKIN | Speed | 6A | 15 | 60.9% | 46.4% | 20.2% | 0.0% | 88.9% | 46.4% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: GRANDMOFFTARKIN | Speed | 6A | 15 | 45.2% | 30.0% | 19.7% | 0.0% | 79.2% | 30.0% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: JARJARBINKS | Potency | 6A | 15 | 40.2% | 34.1% | 19.4% | 0.0% | 80.0% | 34.1% | calibration |
| CALIBRATE | Cross Protection % 24% | POSTAĆ: SCORCH | Health | 6A | 15 | 50.8% | 33.1% | 19.4% | 0.0% | 73.3% | 33.1% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: REY | Critical Damage | 6A | 15 | 48.9% | 38.8% | 19.3% | 0.0% | 87.5% | 38.8% | calibration |
| CALIBRATE | Triangle Critical Chance % 20% | POSTAĆ: COMMANDERLUKESKYWALKER | Tenacity | 6A | 15 | 53.1% | 36.6% | 19.3% | 0.0% | 94.4% | 36.6% | calibration |
| CALIBRATE | Cross Tenacity % 35% | POSTAĆ: NINTHSISTER | Tenacity | 6A | 15 | 65.3% | 40.7% | 19.1% | 0.0% | 83.3% | 40.7% | calibration |
| CALIBRATE | Cross Health % 16% | POSTAĆ: OPERATIVE | Health | 6A | 15 | 49.6% | 35.3% | 19.1% | 0.0% | 94.4% | 35.3% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: COMMANDERLUKESKYWALKER | Offense | 6A | 15 | 50.8% | 40.3% | 19.0% | 0.0% | 87.5% | 40.3% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: MARAJADE | Speed | 6A | 15 | 61.0% | 40.6% | 18.7% | 0.0% | 79.2% | 40.6% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: VADER | Critical Damage | 6A | 15 | 46.7% | 36.5% | 18.6% | 0.0% | 76.7% | 36.5% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: MARAJADE | Potency | 6A | 15 | 47.4% | 36.2% | 18.2% | 0.0% | 70.0% | 36.2% | calibration |
| CALIBRATE | Diamond Defense % 20% | MAGAZYN | Speed | 6A | 15 | 48.2% | 32.4% | 18.1% | 0.0% | 80.0% | 32.4% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: EPIXFINN | Speed | 6A | 15 | 56.1% | 39.9% | 17.8% | 0.0% | 88.9% | 39.9% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: SEVENTHSISTER | Speed | 6A | 15 | 46.8% | 29.7% | 17.8% | 0.0% | 76.7% | 29.7% | calibration |
| CALIBRATE | Triangle Protection % 24% | POSTAĆ: FIFTHBROTHER | Speed | 6A | 15 | 59.1% | 50.4% | 17.7% | 0.0% | 94.4% | 50.4% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: OPERATIVE | Speed | 6A | 15 | 56.2% | 41.7% | 17.7% | 0.0% | 79.2% | 41.7% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: HOTHLEIA | Critical Chance | 6A | 15 | 61.1% | 40.2% | 17.7% | 0.0% | 79.2% | 40.2% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: COMMANDERLUKESKYWALKER | Offense | 6A | 15 | 56.6% | 33.6% | 17.6% | 0.0% | 83.3% | 33.6% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: VANGUARDTEMPLEGUARD | Speed | 6A | 15 | 56.1% | 45.9% | 17.4% | 0.0% | 75.0% | 45.9% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: JARJARBINKS | Speed | 6A | 15 | 45.1% | 35.1% | 17.0% | 0.0% | 76.7% | 35.1% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: HONDO | Speed | 6A | 15 | 45.7% | 27.0% | 17.0% | 0.0% | 83.3% | 27.0% | calibration |
| CALIBRATE | Cross Offense % 8.5% | POSTAĆ: KYLEKATARN | Health | 6A | 15 | 60.2% | 32.0% | 16.9% | 0.0% | 94.4% | 32.0% | calibration |
| CALIBRATE | Cross Tenacity % 35% | POSTAĆ: SEVENTHSISTER | Speed | 6A | 15 | 62.0% | 46.6% | 16.7% | 0.0% | 83.3% | 46.6% | calibration |
| CALIBRATE | Triangle Health % 16% | MAGAZYN | Potency | 6A | 15 | 56.2% | 37.2% | 16.7% | 0.0% | 83.3% | 37.2% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: EMPERORPALPATINE | Potency | 6A | 15 | 62.8% | 38.5% | 16.4% | 0.0% | 88.9% | 38.5% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: JARJARBINKS | Potency | 6A | 15 | 44.7% | 31.2% | 16.3% | 0.0% | 75.0% | 31.2% | calibration |
| CALIBRATE | Cross Offense % 8.5% | POSTAĆ: GLREY | Health | 6A | 15 | 63.5% | 43.1% | 15.9% | 0.0% | 79.2% | 43.1% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: BOSSNASS | Potency | 6A | 15 | 63.5% | 42.8% | 15.9% | 0.0% | 79.2% | 42.8% | calibration |
| CALIBRATE | Triangle Health % 16% | POSTAĆ: JEDIKNIGHTREVAN | Speed | 6A | 15 | 44.8% | 27.0% | 15.7% | 0.0% | 79.2% | 27.0% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: EMPERORPALPATINE | Potency | 6A | 15 | 46.6% | 31.0% | 15.6% | 0.0% | 70.8% | 31.0% | calibration |
| CALIBRATE | Triangle Critical Chance % 20% | POSTAĆ: BB8 | Health | 6A | 15 | 51.5% | 35.4% | 15.5% | 0.0% | 83.3% | 35.4% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: FIFTHBROTHER | Speed | 6A | 15 | 55.7% | 33.3% | 15.5% | 0.0% | 70.8% | 33.3% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: FIFTHBROTHER | Health | 6A | 15 | 47.9% | 27.8% | 15.5% | 0.0% | 83.3% | 27.8% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: NINTHSISTER | Tenacity | 6A | 15 | 35.7% | 27.7% | 15.2% | 0.0% | 77.8% | 27.7% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: EMPERORPALPATINE | Speed | 6A | 15 | 59.5% | 36.6% | 15.0% | 0.0% | 79.2% | 36.6% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: EPIXFINN | Speed | 6A | 15 | 44.5% | 33.3% | 14.9% | 0.0% | 77.8% | 33.3% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: GLREY | Health | 6A | 15 | 55.8% | 32.9% | 14.9% | 0.0% | 73.3% | 32.9% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: HOTHLEIA | Critical Damage | 6A | 15 | 61.7% | 39.5% | 14.6% | 0.0% | 88.9% | 39.5% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: HERMITYODA | Speed | 6A | 15 | 52.9% | 37.7% | 14.6% | 0.0% | 79.2% | 37.7% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: REY | Critical Chance | 6A | 15 | 51.8% | 29.9% | 14.6% | 0.0% | 88.9% | 29.9% | calibration |
| CALIBRATE | Cross Offense % 8.5% | POSTAĆ: BOOMADIER | Speed | 6A | 15 | 65.1% | 37.1% | 13.8% | 0.0% | 83.3% | 37.1% | calibration |
| CALIBRATE | Cross Tenacity % 35% | POSTAĆ: REY | Critical Damage | 6A | 15 | 55.4% | 35.1% | 13.8% | 0.0% | 83.3% | 35.1% | calibration |
| CALIBRATE | Triangle Offense % 8.5% | POSTAĆ: GLREY | Offense | 6A | 15 | 43.3% | 30.9% | 13.8% | 0.0% | 83.3% | 30.9% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: REY | Critical Chance | 6A | 15 | 47.2% | 32.1% | 13.4% | 0.0% | 79.2% | 32.1% | calibration |
| CALIBRATE | Arrow Offense % 8.5% | POSTAĆ: GLREY | Offense | 6A | 15 | 50.0% | 29.8% | 13.4% | 0.0% | 77.8% | 29.8% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: VADER | Critical Damage | 6A | 15 | 54.4% | 37.1% | 13.3% | 0.0% | 75.0% | 37.1% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: VANGUARDTEMPLEGUARD | Speed | 6A | 15 | 31.2% | 24.9% | 13.2% | 0.0% | 75.0% | 24.9% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: FIFTHBROTHER | Health | 6A | 15 | 68.8% | 40.9% | 13.1% | 0.0% | 75.0% | 40.9% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: ENFYSNEST | Tenacity | 6A | 15 | 54.9% | 31.7% | 13.1% | 0.0% | 83.3% | 31.7% | calibration |

### VEL — najlepszy wirtualny build 6/6

- Wynik buildu po projekcji: **40.7** (lvl 15; 5A → 6E)
- Aktualny build bez projekcji: **48.5**
- Aktualny build po tej samej projekcji: **22.9**
- Zmiana potencjału względem projekcji obecnego buildu: **+17.8**
- Bonus setów w ocenie: **38.03**
| Slot | Mod — parametry wyszukiwalne | Źródło | Fit |
|---|---|---|---:|
| Square | Square / Defense / Offense % 5.88% / secondary: Speed 5, Health % 2.97%, Protection 1303, Health 752 / 5★ A lvl15 | POSTAĆ: MASTERQUIGON | 16.7 |
| Diamond | Diamond / Defense / Defense % 20% / secondary: Offense % 3.81%, Speed 12, Protection 1558, Health % 6% / 6★ A lvl15 | POSTAĆ: VEL | 10.7 |
| Circle | Circle / Defense / Health % 5.88% / secondary: Potency % 1.22%, Offense % 0.55%, Critical Chance % 1.91%, Speed 5 / 5★ E lvl15 | MAGAZYN | 19.0 |
| Arrow | Arrow / Defense / Speed 30 / secondary: Health % 1.02%, Critical Chance % 1.98%, Defense 9, Health 357 / 5★ E lvl15 | POSTAĆ: STORMTROOPER | 17.1 |
| Triangle | Triangle / Defense / Critical Damage % 36% / secondary: Defense % 1.49%, Speed 5, Offense % 0.55%, Protection % 1.49% / 5★ E lvl15 | POSTAĆ: KUIIL | 21.4 |
| Cross | Cross / Defense / Protection % 23.5% / secondary: Health % 2.48%, Critical Chance % 1.73%, Speed 11, Health 648 / 5★ A lvl15 | POSTAĆ: VEL | 21.8 |

## BEZPIECZNY ŁAŃCUCH — walidacja globalna

**STATUS: BLOKADA — nie wygenerowano bezpiecznej listy ruchów.**
- profil dawcy: KUIIL — brak zweryfikowanego profilu; łańcuch nie może być zatwierdzony
- profil dawcy: MASTERQUIGON — brak zweryfikowanego profilu; łańcuch nie może być zatwierdzony
- profil dawcy: STORMTROOPER — brak zweryfikowanego profilu; łańcuch nie może być zatwierdzony

| Postać | Σ modValue przed | Σ modValue po | Δ modValue | Pełne sety przed | Pełne sety po |
|---|---:|---:|---:|---|---|
| VEL | 220.7 | 268.8 | +48.1 | Defense=1, Health=2 | Defense=3 |
| STORMTROOPER | 224.1 | 251.4 | +27.3 | Defense=3 | Defense=2 |
| MASTERQUIGON | 210.9 | 218.8 | +7.9 | Defense=1, Speed=1 | Speed=1 |
| KUIIL | 242.4 | 247.1 | +4.7 | Health=1 | Health=2 |

### Zmiany setów — każda postać w łańcuchu

ROZBITO oznacza utratę co najmniej jednej pełnej grupy. BUDOWANY oznacza zwiększenie liczby modów danego setu bez ukończenia kolejnej grupy. UKOŃCZONO oznacza powstanie dodatkowej pełnej grupy. OSŁABIONY oznacza zmianę liczebności bez ukończenia lub rozbicia pełnej grupy.

| Postać | Set | Zmiana liczby modów | Pełne sety | Status |
|---|---|---:|---:|---|
| VEL | Defense | 2/2 → 6/2 | 1 → 3 | UKOŃCZONO |
| VEL | Health | 4/2 → 0/2 | 2 → 0 | ROZBITO |
| STORMTROOPER | Defense | 6/2 → 5/2 | 3 → 2 | ROZBITO |
| STORMTROOPER | Potency | 0/2 → 1/2 | 0 → 0 | BUDOWANY |
| MASTERQUIGON | Defense | 2/2 → 1/2 | 1 → 0 | ROZBITO |
| MASTERQUIGON | Health | 0/2 → 1/2 | 0 → 0 | BUDOWANY |
| KUIIL | Defense | 1/2 → 0/2 | 0 → 0 | OSŁABIONY |
| KUIIL | Health | 3/2 → 4/2 | 1 → 2 | UKOŃCZONO |

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
