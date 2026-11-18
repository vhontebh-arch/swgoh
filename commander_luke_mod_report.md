# Raport modów — COMMANDERLUKESKYWALKER

**Raport użytkowy.** Pokazuje docelowe mody, kolejność przekładek i wpływ na dawców.

**Uruchomienie:** [GitHub Actions #44341960400](https://github.com/vhontebh-arch/swgoh/actions/runs/44341960400) — cap 1/2/3/5/8 zakończone powodzeniem; CSV i MD są identyczne we wszystkich pięciu przebiegach (SHA-256 MD: `5d4dd7056088e77fe3b8d1f71e4ee8bbb7d88991140873dbe137251ab5cb97c7`).
**Snapshot:** `optimizer-data` commit `cb7e5c084a11aa06fd7055831d64e8797e7d9193`, opublikowany 2026-11-18 16:00:16 UTC; 382 jednostki rosteru, 2196 modów.

## Status

- **Wykonalność fizyczna:** POTWIERDZONA
- **Walidacja fizyczna całego łańcucha:** POTWIERDZONA
- **Ocena:** KOMPROMIS — wynik modelu rośnie o 4.72 pkt, ale build traci 16 Speed z modów. Nie traktuj tego jako bezwarunkowej rekomendacji do wykonania.
- **Łączny bilans profilu rosteru:** +4.72 pkt
- **Liczba modów docelowych:** 6/6

## Bilans całej operacji — ta sama punktacja przed/po

| Postać | Rola w łańcuchu | Wynik przed | Wynik po | Zmiana |
|---|---|---:|---:|---:|
| COMMANDERLUKESKYWALKER | CEL | 154.51 | 159.24 | +4.72 |

**ŁĄCZNA ZMIANA: +4.72 pkt.**

### Kontrola rzeczywistej szybkości z modów

- **Przed:** 124 Speed z sześciu modów.
- **Po:** 108 Speed z sześciu modów.
- **Zmiana:** **−16 Speed**.
- Źródło różnicy: wymiana Arrow z primary Speed 32 na Arrow z primary Health 16% i secondary Speed 16. Pozostałe pięć slotów nie zmienia sumy Speed.
- Zysk punktowy wynika z lepszego dopasowania pozostałych secondary i zachowania kombinacji Offense + Tenacity; nie kompensuje automatycznie utraty 16 Speed w rzeczywistej statystyce postaci.

## Docelowy zestaw — COMMANDERLUKESKYWALKER

### Profil SWGOH.GG

- **Najczęstszy układ:** Offense + Tenacity
- **Układ po tej operacji:** Offense + Tenacity
- **Częstość układu po operacji:** 26.3%.
- Top 1000 Kyber GAC — 983 postaci z kompletnymi 6 modami.
- Top 100 Guilds — 4960 postaci z kompletnymi 6 modami.
- Kolejne kombinacje: Crit Damage + Potency (9.6%); Offense + Health (7.3%).
- **Priorytet secondary:** Speed, Tenacity, Offense, Offense %.

### Sześć modów docelowych

#### Arrow
- **Obecny mod:** Arrow / Tenacity / Speed 32 / secondary: Protection 482, Tenacity % 6.25%, Potency % 10.89%, Offense % 4.17% / 6★ A lvl15.
- **Proponowany mod:** Arrow / Offense / Health % 16% / secondary: Offense 117, Critical Chance % 5.16%, Offense % 1.4%, Speed 16 / 6★ C lvl15.
- **Źródło:** MAGAZYN.

#### Square
- **Obecny i końcowy mod:** Square / Offense / Offense % 8.5% / secondary: Tenacity % 7.59%, Speed 20, Protection 1881, Critical Chance % 3.53% / 6★ A lvl15.
- Bez zmiany.

#### Diamond
- **Obecny i końcowy mod:** Diamond / Offense / Defense % 20% / secondary: Speed 21, Offense % 5.76%, Defense 22, Critical Chance % 2.08% / 6★ A lvl15.
- Bez zmiany.

#### Triangle
- **Obecny i końcowy mod:** Triangle / Tenacity / Critical Chance % 20% / secondary: Health 1688, Protection % 3.69%, Speed 17, Defense % 8.3% / 6★ A lvl15.
- Bez zmiany.

#### Circle
- **Obecny i końcowy mod:** Circle / Offense / Protection % 24% / secondary: Health 1100, Offense % 2.65%, Defense % 6%, Speed 24 / 6★ A lvl15.
- Bez zmiany.

#### Cross
- **Obecny mod:** Cross / Offense / Offense % 8.5% / secondary: Speed 10, Health 845, Potency % 7.21%, Critical Chance % 10.17% / 6★ A lvl15.
- **Proponowany mod:** Cross / Tenacity / Offense % 5.88% / secondary: Speed 10, Potency % 1.43%, Protection 1422, Offense 80 / 5★ B lvl15.
- **Źródło:** MAGAZYN.

## MOD — mody przenoszone na cel

- **MAGAZYN → COMMANDERLUKESKYWALKER:** Arrow / Offense / Health % 16% / secondary: Offense 117, Critical Chance % 5.16%, Offense % 1.4%, Speed 16 / 6★ C lvl15.
- **MAGAZYN → COMMANDERLUKESKYWALKER:** Cross / Tenacity / Offense % 5.88% / secondary: Speed 10, Potency % 1.43%, Protection 1422, Offense 80 / 5★ B lvl15.

## PATCH — uzupełnienie dawców

Nie jest wymagany żaden PATCH. Oba proponowane mody pochodzą z magazynu; nie ma dawców ani kosztu u innych postaci.

## Kolejność przekładania

**Nie wykonuj przekładki automatycznie.** Najpierw zdecyduj, czy akceptujesz spadek o 16 Speed w zamian za wzrost punktacji profilu o 4.72 pkt.

1. Arrow — załóż na COMMANDERLUKESKYWALKER mod z MAGAZYN opisany powyżej.
2. Cross — załóż na COMMANDERLUKESKYWALKER mod z MAGAZYN opisany powyżej.

Zakładanie moda automatycznie przenosi poprzedni mod ze slotu do magazynu. Walidator potwierdził brak konfliktu i podwójnego użycia modów.

## Stan końcowy

- **Punktacja celu:** 154.51 → 159.24 (**+4.72**).
- **Szybkość z modów:** 124 → 108 (**−16**).
- **Sety:** przed i po 4× Offense + 2× Tenacity.
- **Dawcy/PATCH:** brak.
- **Profile:** Commander Luke Skywalker — dostępny i świeży; preflight przeszedł.
- **Pięć capów:** wszystkie zakończone powodzeniem, identyczne wyniki.

**Klasyfikacja: KOMPROMIS.** Przekładka jest fizycznie wykonalna i zwiększa punktację używanego modelu, ale obniża szybkość postaci o 16. To istotny koszt, którego sam dodatni bilans punktowy nie powinien ukrywać.

## Założenia i ograniczenia

- Punktacja porównuje pełny build przed/po bez projekcji przyszłych rolli i bez założeń o slice.
- Osobna projekcja potencjału nie jest traktowana jako aktualny wynik.
- Nie ma automatycznej ochrony dawcy; w tym wariancie nie ma jednak żadnego dawcy.
- Opisy modów zawierają slot, set, gwiazdki, tier, poziom, primary i wszystkie secondary; ID pozostają wyłącznie techniczne.
