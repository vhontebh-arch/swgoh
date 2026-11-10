# Analiza modów

Model rozdziela **jakość obecnych rolli**, **potencjał dalszego rozwoju**, **dopasowanie do postaci** i **rodzaj następnej inwestycji**.

W raportach przeznaczonych do ręcznego wykonania mod identyfikowany jest wyłącznie przez slot, set, primary, secondary, gwiazdki, tier i poziom; wewnętrzne ID nie są pokazywane.

- Modów: **2192**
- UPGRADE: **26**
- SLICE: **349**
- SLICE_6E: **193**
- CALIBRATE: **83**
- EQUIP: **0**
- REPLACE: **4**
- PATCH: **3**
- KEEP: **1534**

## Profile SWGOH.GG — lokalna baza

Profile są przechowywane lokalnie i odświeżane tylko dla celu oraz dawców faktycznie wyznaczonego łańcucha transferów. Po pobraniu profili dawców łańcuch jest ponownie oceniany; jeśli zmieni się dawca, jego profil również zostanie sprawdzony. Cache ma ważność 5 dni. Nieudane lub niepełne pobranie nie nadpisuje poprzedniego poprawnego profilu.

| Postać (baseId) | Status |
|---|---|
| MASTERQUIGON | cached |
| SCORCH | cached |
| VEL | cached |
| ZAALBAR | unavailable |

Dla dawców bez lokalnego profilu po próbie pobrania używany jest fallback modValue; nie jest to ocena dopasowania do indywidualnego profilu.

## Globalny optimizer 6-slotowy

Ocena kompletnego buildu: 40 pkt za statystyki główne, 60 pkt za maksymalnie 24 rolle secondary oraz bonusy setów ważone profilem postaci. Zgodność z profilem ma pierwszeństwo przed zachowaniem aktualnie założonych modów. Set nieobecny w profilu zachowuje 10% bazowej wagi bonusu; set z preferencją 100% otrzymuje pełną wagę. Zachowanie modów na celu jest dopiero końcowym tie-breakiem.

Ranking kandydujących buildów używa oddzielnej projekcji: brakujące rolle do limitu aktualnego tieru są optymistycznie przypisywane do najwyżej preferowanej statystyki profilu; mod 5A na poziomie 15 jest dodatkowo przeliczany do 6E. To górna granica potencjału, nie prognoza RNG ani rzeczywiste statystyki moda. Primary pozostaje na wartości z eksportu, ponieważ nie mamy w danych tabeli jego przyrostu dla każdego poziomu. Raport pokazuje osobno wynik aktualny i wynik po projekcji.

Bonus Speed Set używa bazowej szybkości 150, jeśli profil nie zawiera pola base_stats.Speed. Pozostałe bonusy procentowe są normalizowane względem maksymalnego rolla odpowiedniej statystyki.

## Najważniejsi kandydaci

| Akcja | Mod | Źródło | Set | Tier | Lvl | Quality | Value | Fit | 6E proj. | Speed | Potencjał | Inwestycja |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| REPLACE | Circle Protection % 24% | POSTAĆ: SCORCH | Defense | 6A | 15 | 53.5% | 31.1% | 37.5% | 0.0% | 88.9% | 31.1% | calibration |
| REPLACE | Triangle Protection % 24% | POSTAĆ: ZAALBAR | Health | 6E | 15 | 72.4% | 50.3% | 34.3% | 0.0% | 100.0% | 50.3% | slice |
| REPLACE | Arrow Protection % 24% | MAGAZYN | Health | 6E | 15 | 58.0% | 29.6% | 16.9% | 0.0% | 100.0% | 29.6% | slice |
| REPLACE | Square Offense % 5.88% | POSTAĆ: MASTERQUIGON | Defense | 5A | 15 | 72.9% | 47.7% | 16.7% | 69.9% | 83.3% | 47.7% | 6-dot |
| PATCH | Square Offense % 0.63% | MAGAZYN | Health | 5D | 1 | 54.8% | 54.8% | 43.9% | 0.0% | 66.7% | 91.0% | upgrade |
| PATCH | Circle Protection % 23.5% | MAGAZYN | Health | 5C | 15 | 48.3% | 35.6% | 39.2% | 0.0% | 83.3% | 35.6% | slice |
| PATCH | Triangle Critical Chance % 1.5% | MAGAZYN | Health | 5B | 1 | 78.8% | 60.8% | 27.6% | 0.0% | 83.3% | 83.2% | upgrade |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: MARAJADE | Speed | 6A | 15 | 65.2% | 38.6% | 39.6% | 0.0% | 88.9% | 38.6% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: BOOMADIER | Critical Chance | 6A | 15 | 58.1% | 35.8% | 37.9% | 0.0% | 87.5% | 35.8% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: COMMANDERLUKESKYWALKER | Offense | 6A | 15 | 49.8% | 39.5% | 36.5% | 0.0% | 80.0% | 39.5% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: REY | Critical Damage | 6A | 15 | 48.9% | 38.8% | 35.1% | 0.0% | 87.5% | 38.8% | calibration |
| CALIBRATE | Cross Protection % 24% | POSTAĆ: SCORCH | Health | 6A | 15 | 50.8% | 33.1% | 34.6% | 0.0% | 73.3% | 33.1% | calibration |
| CALIBRATE | Triangle Protection % 24% | POSTAĆ: FIFTHBROTHER | Speed | 6A | 15 | 59.1% | 50.4% | 33.6% | 0.0% | 94.4% | 50.4% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: HOTHLEIA | Critical Chance | 6A | 15 | 61.1% | 40.2% | 33.4% | 0.0% | 79.2% | 40.2% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: EMPERORPALPATINE | Potency | 6A | 15 | 46.6% | 31.0% | 33.4% | 0.0% | 70.8% | 31.0% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: VANGUARDTEMPLEGUARD | Speed | 6A | 15 | 56.1% | 45.9% | 33.1% | 0.0% | 75.0% | 45.9% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: JARJARBINKS | Speed | 6A | 15 | 45.1% | 35.1% | 32.8% | 0.0% | 76.7% | 35.1% | calibration |
| CALIBRATE | Arrow Protection % 24% | POSTAĆ: JEDIKNIGHTREVAN | Speed | 6A | 15 | 46.5% | 33.3% | 31.8% | 0.0% | 80.0% | 33.3% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: FIFTHBROTHER | Speed | 6A | 15 | 55.7% | 33.3% | 31.3% | 0.0% | 70.8% | 33.3% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: JEDIKNIGHTREVAN | Health | 6A | 15 | 57.7% | 36.1% | 30.1% | 0.0% | 80.0% | 36.1% | calibration |
| CALIBRATE | Triangle Health % 16% | POSTAĆ: NINTHSISTER | Tenacity | 6A | 15 | 60.3% | 47.4% | 28.4% | 0.0% | 83.3% | 47.4% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: VADER | Critical Chance | 6A | 15 | 44.5% | 29.9% | 28.1% | 0.0% | 70.8% | 29.9% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: GLREY | Offense | 6A | 15 | 47.6% | 42.6% | 27.8% | 0.0% | 93.3% | 42.6% | calibration |
| CALIBRATE | Cross Protection % 24% | POSTAĆ: GRANDADMIRALTHRAWN | Speed | 6A | 15 | 44.5% | 25.2% | 27.7% | 0.0% | 83.3% | 25.2% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: SEVENTHSISTER | Speed | 6A | 15 | 58.8% | 41.6% | 26.4% | 0.0% | 91.7% | 41.6% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: SCORCH | Health | 6A | 15 | 56.9% | 40.9% | 26.1% | 0.0% | 91.7% | 40.9% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: ENFYSNEST | Tenacity | 6A | 15 | 52.0% | 38.9% | 24.7% | 0.0% | 83.3% | 38.9% | calibration |
| CALIBRATE | Triangle Protection % 24% | POSTAĆ: SCORCH | Health | 6A | 15 | 58.2% | 36.9% | 24.7% | 0.0% | 61.1% | 36.9% | calibration |
| CALIBRATE | Triangle Protection % 24% | POSTAĆ: GRANDADMIRALTHRAWN | Health | 6A | 15 | 49.2% | 35.2% | 24.6% | 0.0% | 72.2% | 35.2% | calibration |
| CALIBRATE | Triangle Critical Chance % 20% | POSTAĆ: JARJARBINKS | Speed | 6A | 15 | 64.8% | 45.8% | 24.5% | 0.0% | 86.7% | 45.8% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: JARJARBINKS | Speed | 6A | 15 | 56.0% | 39.7% | 24.3% | 0.0% | 86.7% | 39.7% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: VADER | Critical Damage | 6A | 15 | 61.8% | 38.4% | 23.9% | 0.0% | 83.3% | 38.4% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: SANASTARROS | Health | 6A | 15 | 54.2% | 37.4% | 23.3% | 0.0% | 76.7% | 37.4% | calibration |
| CALIBRATE | Arrow Protection % 24% | POSTAĆ: VANGUARDTEMPLEGUARD | Speed | 6A | 15 | 39.0% | 24.9% | 22.7% | 0.0% | 70.8% | 24.9% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: EPIXFINN | Speed | 6A | 15 | 56.1% | 39.9% | 22.1% | 0.0% | 88.9% | 39.9% | calibration |
| CALIBRATE | Cross Health % 16% | POSTAĆ: OPERATIVE | Health | 6A | 15 | 49.6% | 35.3% | 22.0% | 0.0% | 94.4% | 35.3% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: ENFYSNEST | Tenacity | 6A | 15 | 61.0% | 42.4% | 21.9% | 0.0% | 88.9% | 42.4% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: GLREY | Offense | 6A | 15 | 40.5% | 33.8% | 21.7% | 0.0% | 80.0% | 33.8% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: HONDO | Speed | 6A | 15 | 45.7% | 27.0% | 21.3% | 0.0% | 83.3% | 27.0% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: MARAJADE | Speed | 6A | 15 | 60.5% | 49.9% | 20.3% | 0.0% | 88.9% | 49.9% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: GRANDMOFFTARKIN | Speed | 6A | 15 | 60.9% | 46.4% | 20.2% | 0.0% | 88.9% | 46.4% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: COMMANDERLUKESKYWALKER | Offense | 6A | 15 | 56.6% | 33.6% | 19.9% | 0.0% | 83.3% | 33.6% | calibration |
| CALIBRATE | Triangle Health % 16% | MAGAZYN | Potency | 6A | 15 | 56.2% | 37.2% | 19.7% | 0.0% | 83.3% | 37.2% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: JARJARBINKS | Potency | 6A | 15 | 40.2% | 34.1% | 19.7% | 0.0% | 80.0% | 34.1% | calibration |
| CALIBRATE | Diamond Defense % 20% | MAGAZYN | Speed | 6A | 15 | 48.2% | 32.4% | 19.7% | 0.0% | 80.0% | 32.4% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: GRANDMOFFTARKIN | Speed | 6A | 15 | 45.2% | 30.0% | 19.7% | 0.0% | 79.2% | 30.0% | calibration |
| CALIBRATE | Triangle Critical Chance % 20% | POSTAĆ: COMMANDERLUKESKYWALKER | Tenacity | 6A | 15 | 53.1% | 36.6% | 19.5% | 0.0% | 94.4% | 36.6% | calibration |
| CALIBRATE | Cross Tenacity % 35% | POSTAĆ: NINTHSISTER | Tenacity | 6A | 15 | 65.3% | 40.7% | 19.3% | 0.0% | 83.3% | 40.7% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: MARAJADE | Potency | 6A | 15 | 47.4% | 36.2% | 19.2% | 0.0% | 70.0% | 36.2% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: GLREY | Health | 6A | 15 | 55.8% | 32.9% | 19.2% | 0.0% | 73.3% | 32.9% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: MARAJADE | Speed | 6A | 15 | 61.0% | 40.6% | 19.0% | 0.0% | 79.2% | 40.6% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: COMMANDERLUKESKYWALKER | Offense | 6A | 15 | 50.8% | 40.3% | 19.0% | 0.0% | 87.5% | 40.3% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: VADER | Critical Damage | 6A | 15 | 46.7% | 36.5% | 18.6% | 0.0% | 76.7% | 36.5% | calibration |
| CALIBRATE | Triangle Health % 16% | POSTAĆ: JEDIKNIGHTREVAN | Speed | 6A | 15 | 44.8% | 27.0% | 18.6% | 0.0% | 79.2% | 27.0% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: EMPERORPALPATINE | Speed | 6A | 15 | 59.5% | 36.6% | 17.8% | 0.0% | 79.2% | 36.6% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: SEVENTHSISTER | Speed | 6A | 15 | 46.8% | 29.7% | 17.8% | 0.0% | 76.7% | 29.7% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: OPERATIVE | Speed | 6A | 15 | 56.2% | 41.7% | 17.7% | 0.0% | 79.2% | 41.7% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: FIFTHBROTHER | Health | 6A | 15 | 47.9% | 27.8% | 17.3% | 0.0% | 83.3% | 27.8% | calibration |
| CALIBRATE | Cross Tenacity % 35% | POSTAĆ: SEVENTHSISTER | Speed | 6A | 15 | 62.0% | 46.6% | 16.9% | 0.0% | 83.3% | 46.6% | calibration |
| CALIBRATE | Cross Offense % 8.5% | POSTAĆ: KYLEKATARN | Health | 6A | 15 | 60.2% | 32.0% | 16.9% | 0.0% | 94.4% | 32.0% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: REY | Critical Chance | 6A | 15 | 51.8% | 29.9% | 16.8% | 0.0% | 88.9% | 29.9% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: EMPERORPALPATINE | Potency | 6A | 15 | 62.8% | 38.5% | 16.4% | 0.0% | 88.9% | 38.5% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: JARJARBINKS | Potency | 6A | 15 | 44.7% | 31.2% | 16.3% | 0.0% | 75.0% | 31.2% | calibration |
| CALIBRATE | Cross Offense % 8.5% | POSTAĆ: GLREY | Health | 6A | 15 | 63.5% | 43.1% | 15.9% | 0.0% | 79.2% | 43.1% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: BOSSNASS | Potency | 6A | 15 | 63.5% | 42.8% | 15.9% | 0.0% | 79.2% | 42.8% | calibration |
| CALIBRATE | Triangle Critical Chance % 20% | POSTAĆ: BB8 | Health | 6A | 15 | 51.5% | 35.4% | 15.7% | 0.0% | 83.3% | 35.4% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: REY | Critical Chance | 6A | 15 | 47.2% | 32.1% | 15.5% | 0.0% | 79.2% | 32.1% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: NINTHSISTER | Tenacity | 6A | 15 | 35.7% | 27.7% | 15.5% | 0.0% | 77.8% | 27.7% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: EPIXFINN | Speed | 6A | 15 | 44.5% | 33.3% | 14.9% | 0.0% | 77.8% | 33.3% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: HOTHLEIA | Critical Damage | 6A | 15 | 61.7% | 39.5% | 14.6% | 0.0% | 88.9% | 39.5% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: HERMITYODA | Speed | 6A | 15 | 52.9% | 37.7% | 14.6% | 0.0% | 79.2% | 37.7% | calibration |
| CALIBRATE | Triangle Offense % 8.5% | POSTAĆ: GLREY | Offense | 6A | 15 | 43.3% | 30.9% | 14.5% | 0.0% | 83.3% | 30.9% | calibration |
| CALIBRATE | Cross Tenacity % 35% | POSTAĆ: REY | Critical Damage | 6A | 15 | 55.4% | 35.1% | 14.1% | 0.0% | 83.3% | 35.1% | calibration |
| CALIBRATE | Cross Health % 16% | POSTAĆ: JEDIKNIGHTREVAN | Health | 6A | 15 | 46.9% | 34.2% | 13.9% | 0.0% | 66.7% | 34.2% | calibration |
| CALIBRATE | Cross Offense % 8.5% | POSTAĆ: BOOMADIER | Speed | 6A | 15 | 65.1% | 37.1% | 13.8% | 0.0% | 83.3% | 37.1% | calibration |

### VEL — najlepszy wirtualny build 6/6

- Wynik buildu po projekcji: **50.0** (lvl 15; 5A → 6E)
- Aktualny build bez projekcji: **70.9**
- Aktualny build po tej samej projekcji: **44.9**
- Zmiana potencjału względem projekcji obecnego buildu: **+5.1**
- Bonus setów w ocenie: **31.65**
| Slot | Mod — parametry wyszukiwalne | Źródło | Fit |
|---|---|---|---:|
| Square | Square / Defense / Offense % 5.88% / secondary: Speed 5, Health % 2.97%, Protection 1303, Health 752 / 5★ A lvl15 | POSTAĆ: MASTERQUIGON | 16.7 |
| Diamond | Diamond / Defense / Defense % 20% / secondary: Offense % 3.81%, Speed 12, Protection 1558, Health % 6% / 6★ A lvl15 | POSTAĆ: VEL | 10.7 |
| Circle | Circle / Defense / Protection % 24% / secondary: Defense 13, Speed 16, Tenacity % 7.97%, Defense % 12.54% / 6★ A lvl15 | POSTAĆ: SCORCH | 37.5 |
| Arrow | Arrow / Health / Protection % 24% / secondary: Speed 6, Potency % 3.5%, Offense % 2.5%, Critical Chance % 6.61% / 6★ E lvl15 | MAGAZYN | 16.9 |
| Triangle | Triangle / Health / Protection % 24% / secondary: Tenacity % 6.59%, Offense % 3.14%, Potency % 2.98%, Speed 12 / 6★ E lvl15 | POSTAĆ: ZAALBAR | 34.3 |
| Cross | Cross / Defense / Protection % 23.5% / secondary: Health % 2.48%, Critical Chance % 1.73%, Speed 11, Health 648 / 5★ A lvl15 | POSTAĆ: VEL | 36.9 |

## BEZPIECZNY ŁAŃCUCH — walidacja globalna

**STATUS: BLOKADA — nie wygenerowano bezpiecznej listy ruchów.**
- profil dawcy: ZAALBAR — brak zweryfikowanego profilu; łańcuch nie może być zatwierdzony

| Postać | Σ modValue przed | Σ modValue po | Δ modValue | Pełne sety przed | Pełne sety po |
|---|---:|---:|---:|---|---|
| VEL | 220.7 | 237.1 | +16.4 | Defense=1, Health=2 | Defense=2, Health=1 |
| MASTERQUIGON | 210.9 | 218.0 | +7.1 | Defense=1, Speed=1 | Speed=1 |
| SCORCH | 201.9 | 206.4 | +4.5 | Defense=1, Health=2 | Health=2 |
| ZAALBAR | 231.5 | 242.0 | +10.5 | Health=3 | Health=3 |

### Zmiany setów — każda postać w łańcuchu

ROZBITO oznacza utratę co najmniej jednej pełnej grupy. BUDOWANY oznacza zwiększenie liczby modów danego setu bez ukończenia kolejnej grupy. UKOŃCZONO oznacza powstanie dodatkowej pełnej grupy. OSŁABIONY oznacza zmianę liczebności bez ukończenia lub rozbicia pełnej grupy.

| Postać | Set | Zmiana liczby modów | Pełne sety | Status |
|---|---|---:|---:|---|
| VEL | Defense | 2/2 → 4/2 | 1 → 2 | UKOŃCZONO |
| VEL | Health | 4/2 → 2/2 | 2 → 1 | ROZBITO |
| MASTERQUIGON | Defense | 2/2 → 1/2 | 1 → 0 | ROZBITO |
| MASTERQUIGON | Health | 0/2 → 1/2 | 0 → 0 | BUDOWANY |
| SCORCH | Defense | 2/2 → 1/2 | 1 → 0 | ROZBITO |
| SCORCH | Health | 4/2 → 5/2 | 2 → 2 | BUDOWANY |

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
