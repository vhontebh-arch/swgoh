# Stormtrooper Luke — proponowana optymalizacja modów

**Zakres:** Stormtrooper Luke i wyłącznie dawcy z zatwierdzonego łańcucha.  
**Stan celu w eksporcie:** 4★, G12, 0/6 modów.  
**Podstawa:** udany przebieg walidacji GitHub Actions nr 43735251561; snapshot z commita 20a3215b917c0f2cc15b7866528794b2b9b3a410.  
**Wynik:** łańcuch 25 fizycznie wykonalnych przekładek; kompromis dla rosteru, nie automatyczna zgoda na wykonanie.

## Status

- **Wykonalność fizyczna:** POTWIERDZONA
- **Walidacja fizyczna całego łańcucha:** POTWIERDZONA
- **Ocena:** KOMPROMIS — bilans całego rosteru dodatni, ale kilku dawców traci punkty pełnego buildu.
- **Łączny bilans profilu rosteru:** +107,97 pkt.
- **Liczba modów docelowych:** 6/6.
- **Warunek Pietta:** jego Triangle nie jest zabierany; Piett oddaje wyłącznie Arrow i otrzymuje Arrow od JKR.

## 1. Cel i profil docelowy

Najczęstsza kombinacja profilu SWGOH.GG dla Stormtrooper Luke'a to **Speed + Health** — 60,1% kompletnych buildów.

- Priorytety secondary: Speed, Health, Protection, Offense.
- Najczęstsze primary: Arrow — Speed (94,67%); Triangle — Protection (55,96%); Circle — Protection (69,54%); Cross — Protection (56,14%).
- Źródła profilu: Top 1000 Kyber GAC (945 kompletnych buildów) oraz Top 100 Guilds (4858 kompletnych buildów).

Proponowany build zachowuje kombinację setów Speed + Health, ale nie wszystkie primary odpowiadają najczęstszym wyborom profilu. Odstępstwa są wskazane przy konkretnych slotach.

### Sześć modów docelowych

Wszystkie sloty Stormtrooper Luke'a są obecnie puste. Każdy proponowany mod ma pełny opis i wskazane aktualne miejsce.

#### Arrow

- **Obecny mod:** brak — pusty slot.
- **Proponowany mod:** Speed, 6★ A, lvl 15; primary Protection 24%; secondary: Health 770, Defense 9,48%, Protection 1035, Speed 24.
- **Źródło:** Luke Starkiller.
- **Uzasadnienie:** set Speed i bardzo dobre secondary pod przeżywalność oraz szybkość, w tym Speed +24. **Odstępstwo od profilu:** primary Protection zamiast najczęstszego Speed na strzałce.

#### Square

- **Obecny mod:** brak — pusty slot.
- **Proponowany mod:** Speed, 6★ A, lvl 15; primary Offense 8,5%; secondary: Potency 8,71%, Health 698, Tenacity 4,38%, Speed 17.
- **Źródło:** Luke Starkiller.
- **Uzasadnienie:** set Speed, Speed +17 i Health 698; dodatkowo wysoka Potency. Primary Offense jest naturalnym primary dla kwadratu.

#### Diamond

- **Obecny mod:** brak — pusty slot.
- **Proponowany mod:** Speed, 6★ A, lvl 15; primary Defense 20%; secondary: Tenacity 5,13%, Potency 3,46%, Speed 24, Protection 1994.
- **Źródło:** Luke Starkiller.
- **Uzasadnienie:** set Speed, Speed +24 oraz Protection 1994; primary Defense jest stałym primary diamentu.

#### Triangle

- **Obecny mod:** brak — pusty slot.
- **Proponowany mod:** Health, 6★ A, lvl 15; primary Critical Damage 42%; secondary: Protection 764, Speed 23, Protection 4,06%, Defense 13,03%.
- **Źródło:** 50RT.
- **Uzasadnienie:** bardzo dobre secondary defensywne i Speed +23, a mod domyka zestaw Health. **Odstępstwo od profilu:** najczęstszy primary trójkąta to Protection, a proponowany ma Critical Damage.

#### Circle

- **Obecny mod:** brak — pusty slot.
- **Proponowany mod:** Speed, 6★ A, lvl 15; primary Protection 24%; secondary: Defense 15,26%, Speed 16, Health 1181, Critical Chance 2,93%.
- **Źródło:** Mara Jade.
- **Uzasadnienie:** primary Protection zgodny z najczęstszym wyborem profilu; bardzo wysoka Defense, Speed +16 i Health 1181.

#### Cross

- **Obecny mod:** brak — pusty slot.
- **Proponowany mod:** Health, 6★ A, lvl 15; primary Health 16%; secondary: Health 694, Protection 1743, Speed 20, Offense 116.
- **Źródło:** magazyn.
- **Uzasadnienie:** bardzo dobre statystyki przeżywalności i Speed +20; razem z trójkątem tworzy drugi set Health. **Odstępstwo od profilu:** primary Health zamiast najczęstszego Protection.

**Zestaw końcowy Luke'a:** 4× Speed + 2× Health. Zgodność kombinacji setów z najczęstszym profilem: TAK (60,1%). Odstępstwa primary dotyczą Arrow, Triangle i Cross.

## MOD — mody przenoszone na cel

1. **LUKESTARKILLER → STORMTROOPERLUKE, Arrow:** Speed, 6★ A lvl15; Protection 24%; Health 770, Defense 9,48%, Protection 1035, Speed 24.
2. **LUKESTARKILLER → STORMTROOPERLUKE, Square:** Speed, 6★ A lvl15; Offense 8,5%; Potency 8,71%, Health 698, Tenacity 4,38%, Speed 17.
3. **LUKESTARKILLER → STORMTROOPERLUKE, Diamond:** Speed, 6★ A lvl15; Defense 20%; Tenacity 5,13%, Potency 3,46%, Speed 24, Protection 1994.
4. **50RT → STORMTROOPERLUKE, Triangle:** Health, 6★ A lvl15; Critical Damage 42%; Protection 764, Speed 23, Protection 4,06%, Defense 13,03%.
5. **MARAJADE → STORMTROOPERLUKE, Circle:** Speed, 6★ A lvl15; Protection 24%; Defense 15,26%, Speed 16, Health 1181, Critical Chance 2,93%.
6. **MAGAZYN → STORMTROOPERLUKE, Cross:** Health, 6★ A lvl15; Health 16%; Health 694, Protection 1743, Speed 20, Offense 116.

## PATCH — uzupełnienie dawców

Każdy PATCH jest konkretnym modem dla konkretnego slotu. Przekładki z magazynu są jawnie oznaczone.

1. **ADMIRALPIETT → LUKESTARKILLER, Arrow:** Speed, 5★ A lvl15; Speed 30; Offense 1,02%, Tenacity 1,66%, Offense 107, Critical Chance 3,6%.
2. **LUKESTARKILLER → 50RT, Triangle:** Potency, 6★ A lvl15; Critical Damage 42%; Health 5,16%, Tenacity 4,33%, Offense 67, Speed 21.
3. **SANASTARROS → MARAJADE, Circle:** Speed, 5★ A lvl15; Health 5,88%; Potency 1,38%, Speed 5, Defense 4,06%, Health 1024.
4. **JEDIKNIGHTREVAN → LUKESTARKILLER, Diamond:** Speed, 6★ A lvl15; Defense 20%; Defense 21, Speed 13, Tenacity 13,01%, Offense 71.
5. **MAGAZYN → LUKESTARKILLER, Triangle:** Potency, 6★ A lvl15; Health 16%; Protection 6,75%, Protection 1368, Speed 20, Critical Chance 5,58%.
6. **KUIIL → SANASTARROS, Circle:** Speed, 5★ D lvl15; Health 5,88%; Health 819, Critical Chance 1,81%, Defense 8, Speed 5.
7. **EMPERORPALPATINE → LUKESTARKILLER, Square:** Speed, 6★ A lvl15; Offense 8,5%; Protection 6,07%, Speed 18, Critical Chance 3,86%, Protection 1109.
8. **JEDIKNIGHTREVAN → KUIIL, Circle:** Health, 6★ A lvl15; Health 16%; Tenacity 7,16%, Defense 11, Speed 24, Defense 9,53%.
9. **JEDIKNIGHTREVAN → ADMIRALPIETT, Arrow:** Speed, 6★ A lvl15; Speed 32; Critical Chance 9,28%, Potency 1,53%, Health 1122, Defense 8,45%.
10. **ZAALBAR → JEDIKNIGHTREVAN, Circle:** Health, 6★ E lvl15; Protection 24%; Speed 15, Protection 1730, Offense 2,8%, Defense 14.
11. **MAGAZYN → JEDIKNIGHTREVAN, Arrow:** Speed, 5★ B lvl15; Health 5,88%; Speed 16, Protection 1247, Critical Chance 1,25%, Defense 6.
12. **VEL → ZAALBAR, Circle:** Health, 5★ A lvl15; Protection 23,5%; Offense 0,35%, Health 636, Speed 11, Health 2,58%.
13. **MAGAZYN → EMPERORPALPATINE, Square:** Speed, 6★ A lvl15; Offense 8,5%; Speed 9, Critical Chance 8,02%, Protection 4,67%, Offense 129.
14. **FINN → VEL, Circle:** Health, 5★ B lvl15; Protection 23,5%; Potency 2,24%, Speed 13, Protection 614, Defense 15.
15. **EMPERORPALPATINE → JEDIKNIGHTREVAN, Diamond:** Speed, 6★ A lvl15; Defense 20%; Tenacity 8,31%, Offense 1,33%, Speed 19, Health 1560.
16. **MAGAZYN → FINN, Circle:** Health, 5★ C lvl15; Health 5,88%; Speed 15, Defense 8, Offense 0,45%, Protection 2,16%.
17. **MARAJADE → EMPERORPALPATINE, Diamond:** Speed, 6★ A lvl15; Defense 20%; Offense 116, Protection 5,98%, Health 5,46%, Speed 16.
18. **50RT → MARAJADE, Diamond:** Speed, 5★ D lvl15; Defense 11,75%; Critical Chance 1,49%, Potency 2,11%, Offense 70, Speed 5.
19. **MAGAZYN → 50RT, Diamond:** Health, 5★ C lvl15; Defense 11,75%; Health 277, Speed 9, Offense 70, Protection 493.

## Kolejność przekładania

Wykonuj dokładnie w tej kolejności. Założenie moda na zajęty slot automatycznie przenosi poprzedni mod do magazynu. Żaden mod nie jest użyty dwukrotnie.

1. **MOD:** LUKESTARKILLER → STORMTROOPERLUKE, Arrow — MOD 1.
2. **MOD:** LUKESTARKILLER → STORMTROOPERLUKE, Square — MOD 2.
3. **MOD:** LUKESTARKILLER → STORMTROOPERLUKE, Diamond — MOD 3.
4. **MOD:** 50RT → STORMTROOPERLUKE, Triangle — MOD 4.
5. **MOD:** MARAJADE → STORMTROOPERLUKE, Circle — MOD 5.
6. **MOD:** MAGAZYN → STORMTROOPERLUKE, Cross — MOD 6.
7. **PATCH:** ADMIRALPIETT → LUKESTARKILLER, Arrow — PATCH 1.
8. **PATCH:** LUKESTARKILLER → 50RT, Triangle — PATCH 2.
9. **PATCH:** SANASTARROS → MARAJADE, Circle — PATCH 3.
10. **PATCH:** JEDIKNIGHTREVAN → LUKESTARKILLER, Diamond — PATCH 4.
11. **PATCH:** MAGAZYN → LUKESTARKILLER, Triangle — PATCH 5.
12. **PATCH:** KUIIL → SANASTARROS, Circle — PATCH 6.
13. **PATCH:** EMPERORPALPATINE → LUKESTARKILLER, Square — PATCH 7.
14. **PATCH:** JEDIKNIGHTREVAN → KUIIL, Circle — PATCH 8.
15. **PATCH:** JEDIKNIGHTREVAN → ADMIRALPIETT, Arrow — PATCH 9.
16. **PATCH:** ZAALBAR → JEDIKNIGHTREVAN, Circle — PATCH 10.
17. **PATCH:** MAGAZYN → JEDIKNIGHTREVAN, Arrow — PATCH 11.
18. **PATCH:** VEL → ZAALBAR, Circle — PATCH 12.
19. **PATCH:** MAGAZYN → EMPERORPALPATINE, Square — PATCH 13.
20. **PATCH:** FINN → VEL, Circle — PATCH 14.
21. **PATCH:** EMPERORPALPATINE → JEDIKNIGHTREVAN, Diamond — PATCH 15.
22. **PATCH:** MAGAZYN → FINN, Circle — PATCH 16.
23. **PATCH:** MARAJADE → EMPERORPALPATINE, Diamond — PATCH 17.
24. **PATCH:** 50RT → MARAJADE, Diamond — PATCH 18.
25. **PATCH:** MAGAZYN → 50RT, Diamond — PATCH 19.

## Bilans całej operacji — ta sama punktacja przed/po

Wynik pełnego buildu celu i każdego dawcy, liczony tym samym modelem:

| Postać | Rola w łańcuchu | Wynik przed | Wynik po | Zmiana |
|---|---|---:|---:|---:|
| STORMTROOPERLUKE | CEL | 0,00 | 121,96 | +121,96 |
| 50RT | DAWCA | 64,42 | 69,81 | +5,39 |
| SANASTARROS | DAWCA | 65,24 | 66,62 | +1,38 |
| VEL | DAWCA | 108,04 | 108,82 | +0,77 |
| ADMIRALPIETT | DAWCA | 85,68 | 87,03 | +1,34 |
| FINN | DAWCA | 115,95 | 115,00 | -0,95 |
| KUIIL | DAWCA | 44,84 | 56,32 | +11,48 |
| LUKESTARKILLER | DAWCA | 129,88 | 109,49 | -20,39 |
| ZAALBAR | DAWCA | 139,95 | 139,78 | -0,18 |
| MARAJADE | DAWCA | 109,80 | 97,00 | -12,80 |
| EMPERORPALPATINE | DAWCA | 98,73 | 96,39 | -2,33 |
| JEDIKNIGHTREVAN | DAWCA | 94,41 | 96,72 | +2,30 |

**ŁĄCZNA ZMIANA: +107,97 pkt.**

## Wpływ na postacie-dawców

Poniżej zmiana wyniku pełnego buildu oraz pomocnicza suma modValue. ModValue nie zastępuje wyniku profilu — pokazuje jedynie surową zmianę wartości modów.

- **50RT:** wynik 64,42 → 69,81 (+5,39); Σ modValue 359,4 → 378,5 (+19,1). Sety: przed 3× Health + 3× Speed, po 3× Health + 2× Speed + 1× Potency. Dokładna kombinacja nie występuje w zebranym profilu.
- **SANASTARROS:** wynik 65,24 → 66,62 (+1,38); Σ modValue 355,6 → 356,1 (+0,5). Speed + Health zachowane (30,7% profilu).
- **VEL:** wynik 108,04 → 108,82 (+0,77); Σ modValue 410,1 → 398,9 (-11,2). Double Health + Defense zachowane (29,2% profilu).
- **ADMIRALPIETT:** wynik 85,68 → 87,03 (+1,34); Σ modValue 363,5 → 335,6 (-27,9). Speed + Health zachowane (54,2% profilu). Piett traci Arrow, ale otrzymuje Arrow JKR; Triangle nie jest ruszany.
- **FINN:** wynik 115,95 → 115,00 (-0,95); Σ modValue 364,4 → 382,8 (+18,4). Triple Health zachowane (20,1% profilu). Spadek wyniku pełnego buildu mimo wzrostu surowej sumy modValue.
- **KUIIL:** wynik 44,84 → 56,32 (+11,48); Σ modValue 395,5 → 407,0 (+11,5). Sety: przed 2× Defense + 2× Health + 2× Speed, po 2× Defense + 3× Health + 1× Speed. Dokładna kombinacja nie występuje w zebranym profilu.
- **LUKESTARKILLER:** wynik 129,88 → 109,49 (-20,39); Σ modValue 402,0 → 384,2 (-17,8). Speed + Potency zachowane (60,5% profilu), ale jest to największa strata punktowa.
- **ZAALBAR:** wynik 139,95 → 139,78 (-0,18); Σ modValue 381,6 → 380,3 (-1,3). Triple Health zachowane (32,7% profilu).
- **MARAJADE:** wynik 109,80 → 97,00 (-12,80); Σ modValue 372,5 → 351,4 (-21,1). Speed + Potency zachowane (60,3% profilu); druga największa strata punktowa.
- **EMPERORPALPATINE:** wynik 98,73 → 96,39 (-2,33); Σ modValue 436,9 → 447,5 (+10,6). Speed + Potency zachowane (47,0% profilu).
- **JEDIKNIGHTREVAN:** wynik 94,41 → 96,72 (+2,30); Σ modValue 333,3 → 384,5 (+51,2). Speed + Health zachowane (69,2% profilu).

Największy koszt ponoszą Luke Starkiller i Mara Jade. Ich kombinacje setów zostają zachowane, ale jakość pełnego buildu spada. To główny powód klasyfikacji całej operacji jako kompromisu.

## Stan końcowy wszystkich dawców

Poniżej komplet sześciu slotów każdego dawcy po wykonaniu całego łańcucha. Wszystkie mody są na poziomie 15; tier i liczba gwiazdek podane przy każdym.

### Luke Starkiller

- **Arrow:** Speed, 5★ A; Speed 30; Offense 1,02%, Tenacity 1,66%, Offense 107, Critical Chance 3,6%.
- **Square:** Speed, 6★ A; Offense 8,5%; Protection 6,07%, Speed 18, Critical Chance 3,86%, Protection 1109.
- **Diamond:** Speed, 6★ A; Defense 20%; Defense 21, Speed 13, Tenacity 13,01%, Offense 71.
- **Triangle:** Potency, 6★ A; Health 16%; Protection 6,75%, Protection 1368, Speed 20, Critical Chance 5,58%.
- **Circle:** Potency, 6★ A; Protection 24%; Health 298, Speed 17, Tenacity 8,64%, Health 5,09%.
- **Cross:** Speed, 6★ A; Potency 30%; Defense 15, Health 2082, Health 3,6%, Speed 19.

### Admiral Piett

- **Arrow:** Speed, 6★ A; Speed 32; Critical Chance 9,28%, Potency 1,53%, Health 1122, Defense 8,45%.
- **Square:** Speed, 5★ A; Offense 5,88%; Protection 3,95%, Health 0,57%, Tenacity 5,59%, Speed 8.
- **Diamond:** Health, 5★ A; Defense 11,75%; Health 0,62%, Speed 14, Critical Chance 2,63%, Defense 15.
- **Triangle:** Speed, 6★ A; Health 16%; Speed 19, Defense 33, Critical Chance 3,91%, Health 1007.
- **Circle:** Health, 5★ A; Protection 23,5%; Offense 0,29%, Speed 5, Defense 12, Health 1343.
- **Cross:** Speed, 5★ A; Offense 5,88%; Protection 1183, Speed 12, Potency 1,62%, Tenacity 3,33%.

### Jedi Knight Revan

- **Arrow:** Speed, 5★ B; Health 5,88%; Speed 16, Protection 1247, Critical Chance 1,25%, Defense 6.
- **Square:** Speed, 5★ B; Offense 5,88%; Health 613, Speed 8, Potency 1,73%, Defense 12.
- **Diamond:** Speed, 6★ A; Defense 20%; Tenacity 8,31%, Offense 1,33%, Speed 19, Health 1560.
- **Triangle:** Speed, 6★ A; Protection 24%; Protection 2497, Defense 15,19%, Defense 20, Speed 10.
- **Circle:** Health, 6★ E; Protection 24%; Speed 15, Protection 1730, Offense 2,8%, Defense 14.
- **Cross:** Health, 6★ A; Protection 24%; Defense 24, Speed 22, Critical Chance 3,97%, Health 4,38%.

### Emperor Palpatine

- **Arrow:** Speed, 5★ B; Health 5,88%; Speed 9, Protection 1,65%, Protection 1028, Offense 61.
- **Square:** Speed, 6★ A; Offense 8,5%; Speed 9, Critical Chance 8,02%, Protection 4,67%, Offense 129.
- **Diamond:** Speed, 6★ A; Defense 20%; Offense 116, Protection 5,98%, Health 5,46%, Speed 16.
- **Triangle:** Speed, 5★ B; Offense 5,88%; Protection 1973, Tenacity 2,02%, Speed 5, Offense 72.
- **Circle:** Potency, 5★ A; Health 5,88%; Offense 0,83%, Speed 18, Protection 2,05%, Defense 1,19%.
- **Cross:** Potency, 5★ A; Potency 24%; Protection 622, Offense 0,42%, Health 2,53%, Speed 15.

### 50RT

- **Arrow:** Health, 5★ C; Speed 30; Health 742, Tenacity 1,64%, Critical Chance 2,15%, Defense 2,53%.
- **Square:** Health, 5★ A; Offense 5,88%; Critical Chance 3,35%, Protection 459, Speed 20, Potency 1,71%.
- **Diamond:** Health, 5★ C; Defense 11,75%; Defense 14, Speed 9, Protection 685, Health 0,61%.
- **Triangle:** Potency, 6★ A; Critical Damage 42%; Health 5,16%, Tenacity 4,33%, Offense 67, Speed 21.
- **Circle:** Speed, 5★ D; Health 5,88%; Speed 5, Critical Chance 1,51%, Health 682, Protection 823.
- **Cross:** Speed, 5★ D; Health 5,88%; Offense 42, Protection 1099, Speed 4, Defense 0,95%.

### Mara Jade

- **Arrow:** Potency, 6★ A; Speed 32; Protection 4,2%, Defense 11,27%, Health 3,18%, Potency 8,61%.
- **Square:** Potency, 6★ A; Offense 8,5%; Health 1376, Health 2,89%, Speed 16, Potency 9,57%.
- **Diamond:** Speed, 5★ D; Defense 11,75%; Critical Chance 1,49%, Potency 2,11%, Offense 70, Speed 5.
- **Triangle:** Speed, 6★ A; Critical Damage 42%; Offense 4,09%, Potency 9,67%, Critical Chance 5,83%, Speed 12.
- **Circle:** Speed, 5★ A; Health 5,88%; Potency 1,38%, Speed 5, Defense 4,06%, Health 1024.
- **Cross:** Speed, 6★ A; Potency 30%; Offense 199, Protection 1913, Speed 10, Defense 5,94%.

### Sana Starros

- **Arrow:** Speed, 5★ B; Health 5,88%; Speed 11, Defense 2,2%, Protection 417, Offense 0,94%.
- **Square:** Speed, 5★ D; Offense 5,88%; Critical Chance 3,21%, Health 364, Potency 1,55%, Speed 5.
- **Diamond:** Speed, 5★ C; Defense 11,75%; Potency 1,54%, Speed 5, Health 1,53%, Defense 14.
- **Triangle:** Health, 6★ A; Protection 24%; Defense 13,63%, Offense 172, Health 481, Speed 11.
- **Circle:** Speed, 5★ D; Health 5,88%; Health 819, Critical Chance 1,81%, Defense 8, Speed 5.
- **Cross:** Health, 6★ A; Offense 8,5%; Protection 9,75%, Potency 4,82%, Speed 10, Defense 41.

### Kuiil

- **Arrow:** Speed, 5★ E; Speed 30; Health 0,69%, Offense 0,43%, Defense 5, Protection 605.
- **Square:** Defense, 5★ A; Offense 5,88%; Protection 3,36%, Speed 15, Defense 2,69%, Health 326.
- **Diamond:** Health, 5★ E; Defense 11,75%; Potency 1,18%, Offense 0,31%, Speed 5, Protection 1,68%.
- **Triangle:** Defense, 5★ E; Critical Damage 36%; Defense 1,49%, Speed 5, Offense 0,55%, Protection 1,49%.
- **Circle:** Health, 6★ A; Health 16%; Tenacity 7,16%, Defense 11, Speed 24, Defense 9,53%.
- **Cross:** Health, 5★ E; Potency 24%; Protection 2,15%, Defense 1,61%, Defense 5, Speed 5.

### Zaalbar

- **Arrow:** Health, 6★ A; Critical Avoidance 35%; Protection 4054, Critical Chance 5,79%, Defense 39, Speed 6.
- **Square:** Health, 6★ E; Offense 8,5%; Potency 1,65%, Offense 68, Speed 14, Tenacity 4,68%.
- **Diamond:** Health, 5★ A; Defense 11,75%; Protection 3,81%, Health 2,39%, Speed 9, Health 425.
- **Triangle:** Health, 6★ E; Protection 24%; Tenacity 6,59%, Offense 3,14%, Potency 2,98%, Speed 12.
- **Circle:** Health, 5★ A; Protection 23,5%; Offense 0,35%, Health 636, Speed 11, Health 2,58%.
- **Cross:** Health, 6★ E; Protection 24%; Speed 9, Defense 39, Protection 1077, Critical Chance 1,58%.

### Vel

- **Arrow:** Health, 6★ C; Speed 32; Offense 79, Protection 6,18%, Offense 4,08%, Defense 7,05%.
- **Square:** Health, 5★ B; Offense 5,88%; Defense 8, Speed 15, Tenacity 3,23%, Potency 1,89%.
- **Diamond:** Defense, 6★ A; Defense 20%; Offense 3,81%, Speed 12, Protection 1558, Health 6%.
- **Triangle:** Health, 5★ A; Protection 23,5%; Defense 3,92%, Tenacity 2,07%, Speed 8, Defense 14.
- **Circle:** Health, 5★ B; Protection 23,5%; Potency 2,24%, Speed 13, Protection 614, Defense 15.
- **Cross:** Defense, 5★ A; Protection 23,5%; Health 2,48%, Critical Chance 1,73%, Speed 11, Health 648.

### Finn

- **Arrow:** Health, 5★ B; Speed 30; Defense 1,27%, Tenacity 1,3%, Protection 3,72%, Potency 4,66%.
- **Square:** Health, 5★ B; Offense 5,88%; Protection 3,72%, Protection 1496, Speed 9, Potency 1,98%.
- **Diamond:** Health, 5★ B; Defense 11,75%; Protection 1088, Defense 12, Health 0,72%, Speed 9.
- **Triangle:** Health, 5★ C; Protection 23,5%; Tenacity 1,85%, Speed 11, Critical Chance 1,15%, Defense 2,47%.
- **Circle:** Health, 5★ C; Health 5,88%; Speed 15, Defense 8, Offense 0,45%, Protection 2,16%.
- **Cross:** Health, 5★ C; Protection 23,5%; Critical Chance 3,99%, Offense 0,67%, Offense 39, Speed 5.

## Kontrola profili użytych w łańcuchu

Każdy uczestnik łańcucha ma profil z obu wymaganych źródeł:

- 50RT — 2 źródła.
- ADMIRALPIETT — 2 źródła.
- EMPERORPALPATINE — 2 źródła.
- FINN — 2 źródła.
- JEDIKNIGHTREVAN — 2 źródła.
- KUIIL — 2 źródła.
- LUKESTARKILLER — 2 źródła.
- MARAJADE — 2 źródła.
- SANASTARROS — 2 źródła.
- STORMTROOPERLUKE — 2 źródła.
- VEL — 2 źródła.
- ZAALBAR — 2 źródła.

## Magazyn i nierozwiązane kwestie

- W łańcuchu wykorzystano **6 modów z magazynu**: Cross dla Luke'a, Triangle dla Luke'a Starkillera, Arrow dla JKR, Square dla Emperor Palpatine, Circle dla Finna i Diamond dla 50RT.
- Po przekładkach pozostaje **490 modów w magazynie**; żaden mod nie został użyty dwukrotnie.
- Piett oddaje wyłącznie Arrow i otrzymuje Arrow JKR. Jego Triangle pozostaje na miejscu.
- 50RT i Kuiil mają po zmianach kombinacje setów nieobecne w zebranych profilach SWGOH.GG. Ich wyniki profilowe rosną, ale są to odstępstwa wymagające świadomej akceptacji.
- Luke Starkiller i Mara Jade zachowują kombinacje setów, ale tracą odpowiednio 20,39 i 12,80 pkt pełnego buildu.
- Build Luke'a ma zgodną kombinację Speed + Health, ale odstępstwa primary na Arrow, Triangle i Cross.

## Założenia projekcji

- Poziom 15 traktowany jest jako osiągalny bez ograniczenia materiałami.
- Brakujące secondary liczone są według średniej wartości rolla, nie maksymalnej; ich przyszły przydział jest uśredniany według profilu.
- Slice i calibration nie wpływają na ranking ani wynik buildu i nie są wymagane do wykonania tej propozycji.
- Primary pozostaje na wartości z eksportu; nie zakładamy przyszłego slice 5★ → 6★.
- Raport opisuje stan po symulacji łańcucha, a nie zmianę wykonaną w grze.

## Status końcowy

**KOMPROMIS — nie wykonuj automatycznie.** Łańcuch jest fizycznie wykonalny i daje dodatni bilans całego rosteru, ale koszt u Luke'a Starkillera i Mary Jade oraz odstępstwa primary wymagają świadomej decyzji. Stormtrooper Luke nie jest oznaczony jako zoptymalizowany.
