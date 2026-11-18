# ADMIRAL PIETT — RAPORT MODÓW

**Snapshot danych:** eksport gracza 2026-11-18 15:05:47 UTC; publikacja snapshotu 15:06:09 UTC; 2196 modów.  
**Analiza:** [GitHub Actions #44331550349](https://github.com/vhontebh-arch/swgoh/actions/runs/44331550349) — wszystkie warianty cap 1/2/3/5/8 zakończone powodzeniem i dały ten sam wynik.

## 1. MOD

### Cel i profil docelowy

- **Cel:** ADMIRALPIETT — Stack Rank 2, Sort Score 5; G13 R8.
- **Profil:** Speed + Health; najczęstsza kombinacja w profilu: 54,2%.
- **Priorytety secondary:** Speed, Potency %, Offense, Health.
- **Układ setów przed:** 4× Speed + 2× Health.
- **Układ setów po:** 4× Speed + 2× Health.
- **Wynik pełnego buildu przed:** 87,37 pkt.

### Sześć slotów Pietta

#### Arrow — bez zmiany
- **Obecny i końcowy mod:** Speed, 6★ A, lvl 15.
- **Primary:** Speed 32.
- **Secondary:** Critical Chance 9,28%; Potency 1,53%; Health 1122; Defense 8,45%.

#### Square — MAGAZYN → ADMIRALPIETT
- **Proponowany mod:** Health, 5★ B, lvl 15.
- **Primary:** Offense 5,88%.
- **Secondary:** Protection 1985; Speed 9; Protection 1,29%; Defense 9.
- **Obecny mod Pietta:** Speed, 6★ C, lvl 15; Offense 8,5%; Protection 6,91%; Health 2,44%; Tenacity 7,46%; Speed 9.

#### Diamond — MAGAZYN → ADMIRALPIETT
- **Proponowany mod:** Speed, 5★ C, lvl 15.
- **Primary:** Defense 11,75%.
- **Secondary:** Speed 5; Health 1,53%; Potency 4,01%; Protection 757.
- **Obecny mod Pietta:** Health, 6★ D, lvl 15; Defense 20%; Health 1,1%; Speed 15; Critical Chance 4,59%; Defense 25.

#### Triangle — bez zmiany
- **Obecny i końcowy mod:** Speed, 6★ A, lvl 15.
- **Primary:** Health 16%.
- **Secondary:** Speed 19; Defense 33; Critical Chance 3,91%; Health 1007.

#### Circle — MAGAZYN → ADMIRALPIETT
- **Proponowany mod:** Health, 5★ A, lvl 11.
- **Primary:** Protection 17,5%.
- **Secondary:** Speed 14; Critical Chance 2,23%; Potency 3,78%; Tenacity 1,66%.
- **Obecny mod Pietta:** Health, 5★ A, lvl 15; Protection 23,5%; Offense 0,29%; Speed 5; Defense 12; Health 1343.

#### Cross — bez zmiany
- **Obecny i końcowy mod:** Speed, 6★ D, lvl 15.
- **Primary:** Offense 8,5%.
- **Secondary:** Protection 1310; Speed 13; Potency 2,16%; Tenacity 7,1%.

### Kontrola błędnego przypisania Square do Mara Jade

Poprzedni raport przypisał Mara Jade mod Square Speed 6★ A z Offense 8,5%, Potency 8,71%, Health 698, Tenacity 4,38% i Speed 17. To przypisanie było błędne.

- **Square faktycznie założony na MARAJADE:** Potency, 6★ A, lvl 15; Offense 8,5%; Health 1376; Health 2,89%; Speed 16; Potency 9,57%.
- **Mod Speed Square o statystykach podanych w poprzednim raporcie:** w świeżym eksporcie jest założony na STORMTROOPERLUKE, nie na MARAJADE.
- Żaden mod z MARAJADE nie został użyty w aktualnym wariancie.

## 2. PATCH

**Nie ma PATCH — łańcuch nie pobiera modów od żadnego dawcy.** Trzy proponowane mody pochodzą bezpośrednio z magazynu. Nie zmienia się wyposażenie Mara Jade, Stormtrooper Luke'a ani innych postaci.

## 3. Kolejność wykonania

**Nie wykonuj tej przekładki.** Jest fizycznie wykonalna, ale obniża aktualny wynik pełnego buildu Pietta.

Robocza kolejność, którą walidator sprawdził:

1. Square — MAGAZYN → ADMIRALPIETT.
2. Diamond — MAGAZYN → ADMIRALPIETT.
3. Circle — MAGAZYN → ADMIRALPIETT.

Po założeniu moda poprzedni mod z danego slotu Pietta wraca do magazynu. Każdy z trzech wskazanych modów jest odrębnym rekordem magazynowym; nie ma konfliktu ani podwójnego użycia.

## 4. Stan końcowy

### Bilans punktacji pełnego buildu

| Postać | Rola | Przed | Po | Zmiana |
|---|---|---:|---:|---:|
| ADMIRALPIETT | Cel | 87,37 | 85,86 | **−1,51** |
| **ŁĄCZNIE** | | **87,37** | **85,86** | **−1,51** |

- **Speed z modów przed:** 93.
- **Speed z modów po:** 92.
- **Sety przed i po:** 4× Speed + 2× Health.
- **Zmiana potencjału po projekcji do lvl 15:** +4,0 pkt. To wynik hipotetyczny, nie aktualny wynik buildu; nie zmienia ujemnego bilansu bieżących modów.

### Walidacja

- [x] Świeży, spójny snapshot; pliki pobrane i zweryfikowane przez manifest.
- [x] Sześć slotów Pietta zweryfikowanych na podstawie jednego eksportu.
- [x] Twarde ograniczenie Stack Rank stosowane już podczas selekcji kandydatów, a następnie ponownie podczas walidacji transferów.
- [x] Mody z magazynu nie wymagają sprawdzania Rank poprzedniego właściciela.
- [x] Brak donorów i PATCH; nie ma kosztu u innych postaci.
- [x] Cap 1, 2, 3, 5 i 8 dały identyczny wynik.
- [x] Testy regresyjne optymalizatora zakończone powodzeniem: [run #44331237335](https://github.com/vhontebh-arch/swgoh/actions/runs/44331237335).
- [ ] Dodatni bilans bieżącego buildu — **niezaliczony**.

**Klasyfikacja: BRAK ROZWIĄZANIA.** Znaleziony wariant jest fizycznie wykonalny, ale obniża bieżący wynik Pietta o 1,51 pkt. Nie jest rekomendacją do wykonania. Poprzedni raport z transferem Square z Mara Jade i bilansem +48,15 pkt zostaje zastąpiony tym wynikiem.
