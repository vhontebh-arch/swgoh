# Raport modów — GLREY

**Raport użytkowy.** Pokazuje wyłącznie docelowe mody, kolejność przekładek i wpływ na dawców.

## Status

- **Wykonalność fizyczna:** ZABLOKOWANA
- **Walidacja fizyczna całego łańcucha:** ZABLOKOWANA
- **Ocena:** BLOKADA — nie wykonuj przekładek
- **Interpretacja:** bilans obejmuje cel i wszystkich dotkniętych dawców, liczony tą samą nieprojekcyjną punktacją pełnego buildu.
- **Łączny bilans profilu rosteru:** NIEZATWIERDZONY — łańcuch przekładek jest zablokowany
- **Liczba modów docelowych:** 6/6

## Docelowy zestaw — GLREY

### Profil SWGOH.GG

**Najczęstszy układ w profilu:** Offense + Health
**Układ po tej operacji:** Offense + Health
**Zgodność z głównym układem profilu:** TAK.
**Częstość układu po operacji w profilu:** 80.5%.

- Top 1000 Kyber GAC — 947 postaci z kompletnymi 6 modami
- Top 100 Guilds — 4871 postaci z kompletnymi 6 modami
- Najczęstsze kombinacje: Offense + Health (80.5%); Speed + Health (7.1%); Offense + Crit Chance (0.2%)
- Priorytet secondary: Speed, Offense %, Offense, Health %

### Sześć modów docelowych

#### Arrow
- **Obecny mod:** Arrow / Offense / Offense % 8.5% / secondary: Speed 14, Defense % 8.89%, Health 1516, Protection 1576 / 6★ A lvl15
- **Proponowany mod:** Arrow / Offense / Health % 16% / secondary: Offense 117, Critical Chance % 5.16%, Offense % 1.4%, Speed 16 / 6★ C lvl15
- **Źródło:** MAGAZYN
  - Zmiana dopasowania do profilu: +4.5 pkt (7.5 → 12.0).
#### Square
- **Obecny mod:** Square / Offense / Offense % 8.5% / secondary: Protection 488, Speed 24, Offense 96, Defense % 8.17% / 6★ A lvl15
- **Proponowany mod:** pozostaje bez zmian — Square / Offense / Offense % 8.5% / secondary: Protection 488, Speed 24, Offense 96, Defense % 8.17% / 6★ A lvl15
- **Korzyść:** zachowanie obecnej konfiguracji slotu.
#### Diamond
- **Obecny mod:** Diamond / Offense / Defense % 20% / secondary: Offense 98, Health 591, Speed 28, Critical Chance % 2.87% / 6★ A lvl15
- **Proponowany mod:** pozostaje bez zmian — Diamond / Offense / Defense % 20% / secondary: Offense 98, Health 591, Speed 28, Critical Chance % 2.87% / 6★ A lvl15
- **Korzyść:** zachowanie obecnej konfiguracji slotu.
#### Triangle
- **Obecny mod:** Triangle / Offense / Offense % 8.5% / secondary: Offense 139, Speed 15, Tenacity % 3.65%, Defense 34 / 6★ A lvl15
- **Proponowany mod:** pozostaje bez zmian — Triangle / Offense / Offense % 8.5% / secondary: Offense 139, Speed 15, Tenacity % 3.65%, Defense 34 / 6★ A lvl15
- **Korzyść:** zachowanie obecnej konfiguracji slotu.
#### Circle
- **Obecny mod:** Circle / Health / Health % 16% / secondary: Defense % 2.81%, Critical Chance % 4.06%, Health 1818, Speed 22 / 6★ A lvl15
- **Proponowany mod:** pozostaje bez zmian — Circle / Health / Health % 16% / secondary: Defense % 2.81%, Critical Chance % 4.06%, Health 1818, Speed 22 / 6★ A lvl15
- **Korzyść:** zachowanie obecnej konfiguracji slotu.
#### Cross
- **Obecny mod:** Cross / Health / Offense % 8.5% / secondary: Potency % 5.12%, Defense % 5.92%, Speed 19, Protection % 10.77% / 6★ A lvl15
- **Proponowany mod:** Cross / Health / Health % 16% / secondary: Health 694, Protection 1743, Speed 20, Offense 116 / 6★ A lvl15
- **Źródło:** STORMTROOPERLUKE
  - Zmiana dopasowania do profilu: +5.7 pkt (10.0 → 15.7).

- **Zmiana potencjału buildu:** +10.2 pkt (optymistyczna projekcja do 15; brakujące rolle przypisane do najwyżej preferowanej secondary; dla 5A projekcja secondary do 6E; primary pozostaje bez zmian; bez slice i calibration).

## MOD — mody przenoszone na cel

Brak zatwierdzonych transferów MOD.

## PATCH — uzupełnienie dawców

Nie jest wymagany żaden PATCH.

## Kolejność przekładania

**Nie wykonuj jeszcze żadnej przekładki.** Poniższy build jest wariantem roboczym; walidacja nie zatwierdziła pełnego łańcucha.

### Co blokuje zatwierdzenie

- **walidacja fizyczna:** transfer PATCH narusza Stack Rank: GLREY -> STORMTROOPERLUKE
- **walidacja fizyczna:** końcowy stan slotów po symulacji różni się od stanu zaplanowanego
## Diagnostyka przeszukiwania wariantów łańcucha

Limit kompletnych wariantów na głównego dawcę: **5**.
Wyniki poniżej to ważony Rank bilans zmian danego dawcy i jego rekurencyjnych pod-dawców; wyższy wynik jest lepszy.

- **STORMTROOPERLUKE:** sprawdzono 5 kompletnych wariantów; wyniki: -9.2097, -9.8922, -11.1122, -11.2360, -11.3320; najlepszy: -9.2097.

## Kontrola profili użytych w łańcuchu

- GLREY: profil dostępny, 2 źródła.
- STORMTROOPERLUKE: profil dostępny, 2 źródła.

## Założenia projekcji

- Poziom 15 jest traktowany jako osiągalny bez ograniczenia materiałami.
- Brakujące secondary są liczone jako wartość średnia rolla, a nie maksymalna; ich przyszły przydział do statystyk jest uśredniony według profilu zamiast przypisywany do najlepszego secondary.
- Slice i calibration nie wpływają na ranking ani wynik buildu. Mogą pojawić się wyłącznie jako osobne sugestie inwestycyjne i można je pominąć.
- Primary pozostaje dokładnie na wartości z eksportu; zależy od obecnej liczby gwiazdek, a podniesienie moda do poziomu 15 go nie zmienia. Nie zakładamy slice 5★ → 6★.

## Jak czytać opisy modów

Każdy opis zawiera slot, set, primary, wszystkie dostępne secondary oraz gwiazdki, tier i poziom. Dzięki temu mod można znaleźć w grze bez korzystania z wewnętrznego ID.

Plik CSV pozostaje technicznym zapleczem optymalizatora; nie jest instrukcją ręcznego przekładania.
