# Analiza modów

Model rozdziela **jakość obecnych rolli**, **potencjał dalszego rozwoju**, **dopasowanie do postaci** i **rodzaj następnej inwestycji**.

W raportach przeznaczonych do ręcznego wykonania mod identyfikowany jest wyłącznie przez slot, set, primary, secondary, gwiazdki, tier i poziom; wewnętrzne ID nie są pokazywane.

- Modów: **2192**
- UPGRADE: **28**
- SLICE: **1156**
- SLICE_6E: **240**
- CALIBRATE: **104**
- EQUIP: **0**
- REPLACE: **0**
- PATCH: **0**
- KEEP: **664**

## Profile SWGOH.GG — lokalna baza

Profile są przechowywane lokalnie i odświeżane tylko dla celu oraz dawców faktycznie wyznaczonego łańcucha transferów. Po pobraniu profili dawców łańcuch jest ponownie oceniany; jeśli zmieni się dawca, jego profil również zostanie sprawdzony. Cache ma ważność 5 dni. Nieudane lub niepełne pobranie nie nadpisuje poprzedniego poprawnego profilu.

| Postać (baseId) | Status |
|---|---|
| QUIGGOLD | cached |
| SANASTARROS | cached |
| SCORCH | cached |
| VEL | cached |

Dla dawców bez lokalnego profilu po próbie pobrania używany jest fallback modValue; nie jest to ocena dopasowania do indywidualnego profilu.

## Globalny optimizer 6-slotowy

Ocena kompletnego buildu: 40 pkt za statystyki główne, 60 pkt za maksymalnie 24 rolle secondary oraz bonusy setów ważone profilem postaci. Zgodność z profilem ma pierwszeństwo przed zachowaniem aktualnie założonych modów. Set nieobecny w profilu zachowuje 10% bazowej wagi bonusu; set z preferencją 100% otrzymuje pełną wagę. Zachowanie modów na celu jest dopiero końcowym tie-breakiem.

Ranking kandydujących buildów używa oddzielnej projekcji: brakujące rolle do limitu aktualnego tieru są optymistycznie przypisywane do najwyżej preferowanej statystyki profilu; mod 5A na poziomie 15 jest dodatkowo przeliczany do 6E. To górna granica potencjału, nie prognoza RNG ani rzeczywiste statystyki moda. Primary pozostaje na wartości z eksportu, ponieważ nie mamy w danych tabeli jego przyrostu dla każdego poziomu. Raport pokazuje osobno wynik aktualny i wynik po projekcji.

Bonus Speed Set używa bazowej szybkości 150, jeśli profil nie zawiera pola base_stats.Speed. Pozostałe bonusy procentowe są normalizowane względem maksymalnego rolla odpowiedniej statystyki.

## Najważniejsi kandydaci

| Akcja | Mod | Źródło | Set | Tier | Lvl | Quality | Value | Fit | 6E proj. | Speed | Potencjał | Inwestycja |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: SANASTARROS | Health | 6A | 15 | 100.0% | 71.3% | 42.5% | 0.0% | 76.7% | 71.3% | calibration |
| CALIBRATE | Cross Protection % 24% | POSTAĆ: SCORCH | Health | 6A | 15 | 100.0% | 69.5% | 42.3% | 0.0% | 73.3% | 69.5% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: JEDIKNIGHTREVAN | Health | 6A | 15 | 100.0% | 62.5% | 41.3% | 0.0% | 80.0% | 62.5% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: GLREY | Offense | 6A | 15 | 100.0% | 76.7% | 40.2% | 0.0% | 80.0% | 76.7% | calibration |
| CALIBRATE | Arrow Protection % 24% | POSTAĆ: JEDIKNIGHTREVAN | Speed | 6A | 15 | 100.0% | 68.2% | 40.2% | 0.0% | 80.0% | 68.2% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: MARAJADE | Potency | 6A | 15 | 100.0% | 78.3% | 40.1% | 0.0% | 70.0% | 78.3% | calibration |
| CALIBRATE | Triangle Health % 16% | POSTAĆ: NINTHSISTER | Tenacity | 6A | 15 | 100.0% | 79.7% | 37.9% | 0.0% | 83.3% | 79.7% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: COMMANDERLUKESKYWALKER | Offense | 6A | 15 | 100.0% | 76.0% | 37.9% | 0.0% | 80.0% | 76.0% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: SEVENTHSISTER | Speed | 6A | 15 | 100.0% | 63.8% | 37.7% | 0.0% | 76.7% | 63.8% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: JARJARBINKS | Speed | 6A | 15 | 100.0% | 63.5% | 37.7% | 0.0% | 86.7% | 63.5% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: SCORCH | Health | 6A | 15 | 100.0% | 65.5% | 36.8% | 0.0% | 91.7% | 65.5% | calibration |
| CALIBRATE | Arrow Protection % 24% | POSTAĆ: VANGUARDTEMPLEGUARD | Speed | 6A | 15 | 100.0% | 66.0% | 35.9% | 0.0% | 70.8% | 66.0% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: GLREY | Health | 6A | 15 | 100.0% | 65.3% | 35.6% | 0.0% | 73.3% | 65.3% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: VADER | Critical Damage | 6A | 15 | 100.0% | 82.0% | 35.5% | 0.0% | 76.7% | 82.0% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: VADER | Critical Damage | 6A | 15 | 100.0% | 61.3% | 34.5% | 0.0% | 83.3% | 61.3% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: FIFTHBROTHER | Speed | 6A | 15 | 100.0% | 66.7% | 33.6% | 0.0% | 70.8% | 66.7% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: GRANDMOFFTARKIN | Speed | 6A | 15 | 100.0% | 64.0% | 33.6% | 0.0% | 79.2% | 64.0% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: VANGUARDTEMPLEGUARD | Speed | 6A | 15 | 100.0% | 82.3% | 33.5% | 0.0% | 75.0% | 82.3% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: OPERATIVE | Speed | 6A | 15 | 100.0% | 78.5% | 33.5% | 0.0% | 79.2% | 78.5% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: EMPERORPALPATINE | Potency | 6A | 15 | 100.0% | 65.3% | 33.5% | 0.0% | 70.8% | 65.3% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: SEVENTHSISTER | Speed | 6A | 15 | 100.0% | 63.0% | 33.5% | 0.0% | 91.7% | 63.0% | calibration |
| CALIBRATE | Cross Health % 16% | POSTAĆ: JEDIKNIGHTREVAN | Health | 6A | 15 | 100.0% | 78.2% | 33.3% | 0.0% | 66.7% | 78.2% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: JARJARBINKS | Speed | 6A | 15 | 100.0% | 75.3% | 33.3% | 0.0% | 76.7% | 75.3% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: GLREY | Offense | 6A | 15 | 100.0% | 74.3% | 33.3% | 0.0% | 93.3% | 74.3% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: JARJARBINKS | Potency | 6A | 15 | 100.0% | 73.2% | 33.3% | 0.0% | 80.0% | 73.2% | calibration |
| CALIBRATE | Triangle Critical Chance % 20% | POSTAĆ: JARJARBINKS | Speed | 6A | 15 | 100.0% | 71.0% | 33.3% | 0.0% | 86.7% | 71.0% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: ENFYSNEST | Tenacity | 6A | 15 | 100.0% | 71.0% | 33.3% | 0.0% | 83.3% | 71.0% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: JARJARBINKS | Potency | 6A | 15 | 100.0% | 68.2% | 33.3% | 0.0% | 75.0% | 68.2% | calibration |
| CALIBRATE | Diamond Defense % 20% | MAGAZYN | Speed | 6A | 15 | 100.0% | 64.3% | 33.3% | 0.0% | 80.0% | 64.3% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: MARAJADE | Speed | 6A | 15 | 100.0% | 68.2% | 32.3% | 0.0% | 79.2% | 68.2% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: ENFYSNEST | Tenacity | 6A | 15 | 100.0% | 68.3% | 31.5% | 0.0% | 88.9% | 68.3% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: NINTHSISTER | Tenacity | 6A | 15 | 100.0% | 68.0% | 31.4% | 0.0% | 77.8% | 68.0% | calibration |
| CALIBRATE | Cross Offense % 8.5% | POSTAĆ: GLREY | Health | 6A | 15 | 100.0% | 69.3% | 31.3% | 0.0% | 79.2% | 69.3% | calibration |
| CALIBRATE | Cross Tenacity % 35% | POSTAĆ: NINTHSISTER | Tenacity | 6A | 15 | 100.0% | 62.0% | 31.3% | 0.0% | 83.3% | 62.0% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: HOTHLEIA | Critical Chance | 6A | 15 | 100.0% | 69.2% | 31.1% | 0.0% | 79.2% | 69.2% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: SCORCH | Defense | 6A | 15 | 100.0% | 51.8% | 30.3% | 0.0% | 88.9% | 51.8% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: VADER | Critical Damage | 6A | 15 | 100.0% | 67.3% | 30.0% | 0.0% | 75.0% | 67.3% | calibration |
| CALIBRATE | Triangle Health % 16% | POSTAĆ: JEDIKNIGHTREVAN | Speed | 6A | 15 | 100.0% | 58.0% | 30.0% | 0.0% | 79.2% | 58.0% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: BOOMADIER | Critical Chance | 6A | 15 | 100.0% | 55.3% | 30.0% | 0.0% | 87.5% | 55.3% | calibration |
| CALIBRATE | Triangle Protection % 24% | POSTAĆ: SCORCH | Health | 6A | 15 | 100.0% | 70.3% | 29.2% | 0.0% | 61.1% | 70.3% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: MARAJADE | Speed | 6A | 15 | 100.0% | 55.2% | 29.2% | 0.0% | 88.9% | 55.2% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: FIFTHBROTHER | Health | 6A | 15 | 100.0% | 54.5% | 29.2% | 0.0% | 83.3% | 54.5% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: VEL | Defense | 6A | 15 | 100.0% | 80.0% | 29.1% | 0.0% | 66.7% | 80.0% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: EPIXPOE | Offense | 6A | 15 | 100.0% | 64.8% | 29.1% | 0.0% | 100.0% | 64.8% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: HONDO | Speed | 6A | 15 | 100.0% | 55.3% | 29.0% | 0.0% | 83.3% | 55.3% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: COMMANDERLUKESKYWALKER | Offense | 6A | 15 | 100.0% | 79.4% | 28.9% | 0.0% | 87.5% | 79.4% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: VADER | Critical Chance | 6A | 15 | 100.0% | 74.3% | 28.9% | 0.0% | 70.8% | 74.3% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: REY | Critical Damage | 6A | 15 | 100.0% | 73.8% | 28.9% | 0.0% | 87.5% | 73.8% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: EPIXFINN | Speed | 6A | 15 | 100.0% | 68.8% | 28.9% | 0.0% | 77.8% | 68.8% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: BOSSNASS | Potency | 6A | 15 | 100.0% | 65.2% | 28.9% | 0.0% | 79.2% | 65.2% | calibration |
| CALIBRATE | Cross Potency % 30% | POSTAĆ: GRANDMOFFTARKIN | Speed | 6A | 15 | 100.0% | 73.3% | 27.1% | 0.0% | 100.0% | 73.3% | calibration |
| CALIBRATE | Triangle Critical Chance % 20% | POSTAĆ: COMMANDERLUKESKYWALKER | Tenacity | 6A | 15 | 100.0% | 63.2% | 26.9% | 0.0% | 94.4% | 63.2% | calibration |
| CALIBRATE | Cross Health % 16% | POSTAĆ: OPERATIVE | Health | 6A | 15 | 100.0% | 62.2% | 26.9% | 0.0% | 94.4% | 62.2% | calibration |
| CALIBRATE | Arrow Offense % 8.5% | POSTAĆ: GLREY | Offense | 6A | 15 | 100.0% | 59.5% | 26.9% | 0.0% | 77.8% | 59.5% | calibration |
| CALIBRATE | Cross Tenacity % 35% | POSTAĆ: ENFYSNEST | Tenacity | 6A | 15 | 100.0% | 56.0% | 26.9% | 0.0% | 77.8% | 56.0% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: MARAJADE | Speed | 6A | 15 | 100.0% | 81.0% | 26.8% | 0.0% | 88.9% | 81.0% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: GRANDMOFFTARKIN | Speed | 6A | 15 | 100.0% | 69.0% | 26.8% | 0.0% | 88.9% | 69.0% | calibration |
| CALIBRATE | Triangle Critical Chance % 20% | POSTAĆ: BB8 | Health | 6A | 15 | 100.0% | 67.0% | 26.8% | 0.0% | 83.3% | 67.0% | calibration |
| CALIBRATE | Cross Tenacity % 35% | POSTAĆ: SEVENTHSISTER | Speed | 6A | 15 | 100.0% | 74.0% | 26.7% | 0.0% | 83.3% | 74.0% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: HERMITYODA | Speed | 6A | 15 | 100.0% | 71.5% | 26.7% | 0.0% | 79.2% | 71.5% | calibration |
| CALIBRATE | Triangle Health % 16% | MAGAZYN | Potency | 6A | 15 | 100.0% | 65.1% | 26.7% | 0.0% | 83.3% | 65.1% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: VANGUARDTEMPLEGUARD | Speed | 6A | 15 | 100.0% | 65.1% | 26.7% | 0.0% | 75.0% | 65.1% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: FIFTHBROTHER | Health | 6A | 15 | 100.0% | 65.0% | 26.7% | 0.0% | 75.0% | 65.0% | calibration |
| CALIBRATE | Triangle Critical Damage % 42% | POSTAĆ: REY | Critical Chance | 6A | 15 | 100.0% | 64.5% | 26.7% | 0.0% | 79.2% | 64.5% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: EMPERORPALPATINE | Speed | 6A | 15 | 100.0% | 64.5% | 26.7% | 0.0% | 79.2% | 64.5% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: MARAJADE | Speed | 6A | 15 | 100.0% | 57.7% | 26.7% | 0.0% | 70.8% | 57.7% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: COMMANDERLUKESKYWALKER | Offense | 6A | 15 | 100.0% | 57.0% | 26.7% | 0.0% | 83.3% | 57.0% | calibration |
| CALIBRATE | Diamond Defense % 20% | POSTAĆ: REYJEDITRAINING | Health | 6A | 15 | 100.0% | 72.2% | 25.7% | 0.0% | 83.3% | 72.2% | calibration |
| CALIBRATE | Cross Defense % 20% | POSTAĆ: BB8 | Speed | 6A | 15 | 100.0% | 61.2% | 25.7% | 0.0% | 83.3% | 61.2% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: GRANDMOFFTARKIN | Potency | 6A | 15 | 100.0% | 64.3% | 24.7% | 0.0% | 75.0% | 64.3% | calibration |
| CALIBRATE | Cross Offense % 8.5% | POSTAĆ: BOOMADIER | Speed | 6A | 15 | 100.0% | 57.7% | 24.6% | 0.0% | 83.3% | 57.7% | calibration |
| CALIBRATE | Circle Protection % 24% | POSTAĆ: BB8 | Health | 6A | 15 | 100.0% | 66.5% | 24.5% | 0.0% | 91.7% | 66.5% | calibration |
| CALIBRATE | Square Offense % 8.5% | POSTAĆ: EMPERORPALPATINE | Potency | 6A | 15 | 100.0% | 60.3% | 24.5% | 0.0% | 88.9% | 60.3% | calibration |
| CALIBRATE | Circle Health % 16% | POSTAĆ: EPIXFINN | Speed | 6A | 15 | 100.0% | 65.8% | 24.4% | 0.0% | 88.9% | 65.8% | calibration |
| CALIBRATE | Triangle Offense % 8.5% | POSTAĆ: GLREY | Offense | 6A | 15 | 100.0% | 65.8% | 23.3% | 0.0% | 83.3% | 65.8% | calibration |

### VEL — najlepszy wirtualny build 6/6

- Wynik buildu po projekcji: **103.2** (lvl 15; 5A → 6E)
- Aktualny build bez projekcji: **67.5**
- Aktualny build po tej samej projekcji: **67.5**
- Zmiana potencjału względem projekcji obecnego buildu: **+35.7**
- Bonus setów w ocenie: **29.05**
| Slot | Mod — parametry wyszukiwalne | Źródło | Fit |
|---|---|---|---:|
| Square | Square / Defense / Offense % 5.88% / secondary: Protection % 3.36%, Speed 15, Defense % 2.69%, Health 326 / 5★ A lvl15 | POSTAĆ: QUIGGOLD | 36.9 |
| Diamond | Diamond / Defense / Defense % 20% / secondary: Offense % 3.81%, Speed 12, Protection 1558, Health % 6% / 6★ A lvl15 | POSTAĆ: VEL | 29.1 |
| Circle | Circle / Defense / Protection % 24% / secondary: Defense 13, Speed 16, Tenacity % 7.97%, Defense % 12.54% / 6★ A lvl15 | POSTAĆ: SCORCH | 30.3 |
| Arrow | Arrow / Defense / Offense % 5.88% / secondary: Defense % 1.37%, Speed 21, Protection 712, Tenacity % 2.79% / 5★ A lvl15 | MAGAZYN | 43.4 |
| Triangle | Triangle / Health / Critical Damage % 42% / secondary: Protection 764, Speed 23, Protection % 4.06%, Defense % 13.03% / 6★ A lvl15 | POSTAĆ: SANASTARROS | 42.5 |
| Cross | Cross / Health / Protection % 24% / secondary: Defense 24, Speed 22, Critical Chance % 3.97%, Health % 4.38% / 6★ A lvl15 | POSTAĆ: SCORCH | 42.3 |

## BEZPIECZNY ŁAŃCUCH — walidacja globalna

**STATUS: BLOKADA — nie wygenerowano bezpiecznej listy ruchów.**
- VEL: konflikt modów dla Circle / Defense — ponownie użyty mod ID: 
- VEL: konflikt modów dla Triangle / Health — ponownie użyty mod ID: 
- VEL: konflikt modów dla Cross / Health — ponownie użyty mod ID: 
- VEL: optimizer mod nie trafił na miejsce: Circle
- VEL: optimizer mod nie trafił na miejsce: Triangle
- VEL: optimizer mod nie trafił na miejsce: Cross

| Postać | Σ modValue przed | Σ modValue po | Δ modValue | Pełne sety przed | Pełne sety po |
|---|---:|---:|---:|---|---|
| QUIGGOLD | 361.3 | 389.8 | +28.5 | Defense=1, Health=2 | Health=2 |
| VEL | 402.2 | 415.9 | +13.7 | Defense=1, Health=2 | Defense=2, Health=1 |

### Zmiany setów — każda postać w łańcuchu

ROZBITO oznacza utratę co najmniej jednej pełnej grupy. BUDOWANY oznacza zwiększenie liczby modów danego setu bez ukończenia kolejnej grupy. UKOŃCZONO oznacza powstanie dodatkowej pełnej grupy. OSŁABIONY oznacza zmianę liczebności bez ukończenia lub rozbicia pełnej grupy.

| Postać | Set | Zmiana liczby modów | Pełne sety | Status |
|---|---|---:|---:|---|
| QUIGGOLD | Defense | 2/2 → 1/2 | 1 → 0 | ROZBITO |
| QUIGGOLD | Health | 4/2 → 5/2 | 2 → 2 | BUDOWANY |
| VEL | Defense | 2/2 → 4/2 | 1 → 2 | UKOŃCZONO |
| VEL | Health | 4/2 → 2/2 | 2 → 1 | ROZBITO |

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
