# ROTE Guild Planner

Projekt narzędzia do planowania Territory Battle **Rise of the Empire (ROTE)** dla całej gildii SWGOH.

## Cel

Wyznaczać plan, który maksymalizuje łączną liczbę gwiazdek przy uwzględnieniu:
- rosterów wszystkich członków gildii (posiadanie postaci, gwiazdki, gear/relic),
- Operations / Platoons: przypisania konkretnych jednostek do konkretnych slotów i członków,
- limitów przekazywania jednostek na planetę i fazę,
- planet, faz, wymagań misji i punktów rozmieszczenia (deployments),
- pre-loadów i kolejności blokowania / otwierania stref,
- punktów z misji bojowych i specjalnych oraz celu gwiazdek,
- ręcznych blokad, wyjątków i zmian zatwierdzonych przez oficerów.

## Zasady wiarygodności

1. Nie wolno uznawać jednostki za dostępną, jeśli roster członka nie potwierdza jej posiadania i wymaganej rangi.
2. Nie wolno przydzielić tej samej jednostki temu samemu członkowi ponad limit gry dla tej planety/fazy.
3. Każde przypisanie musi wskazywać członka, jednostkę, fazę, planetę/strefę i slot Operations.
4. Brak danych o rosterze, wymaganiu lub punktacji oznaczamy jako **nieznane** — nie zgadujemy.
5. Dane referencyjne ROTE muszą być wersjonowane i mieć wskazane źródło; nie należy mieszać wymagań z różnych wersji gry.
6. Wynik optymalizatora jest propozycją; oficer może zablokować lub ręcznie zmienić przydziały.

## Plan etapów

### Etap 1 — źródła i model danych
- [ ] Zidentyfikować wiarygodne źródło danych referencyjnych ROTE (strefy, sloty, jednostki, progi relic/gwiazdek, punkty).
- [ ] Ustalić import pełnej gildii i rosterów członków; osobny status świeżości dla każdego członka.
- [ ] Normalizować identyfikatory postaci i jednostek, bez zależności od lokalizowanych nazw.

### Etap 2 — pokrycie Operations
- [ ] Obliczać dostępność każdego wymaganego egzemplarza jednostki na podstawie rosterów.
- [ ] Wykrywać braki i rzadkie jednostki, ograniczenia oraz konflikty między slotami.
- [ ] Przydzielać jednostki algorytmem rzadkości (najpierw sloty z najmniejszą liczbą kandydatów), z preferencją dla oddania niższego relic/GP, jeśli nie pogarsza to rozwiązania.

### Etap 3 — harmonogram i optymalizacja gwiazdek
- [ ] Modelować fazy, łańcuchy planet/stref, pre-loady, progi gwiazdek i punkty.
- [ ] Porównywać scenariusze: aktualny roster, ręczne ograniczenia, alternatywne rozmieszczenie.
- [ ] Pokazywać wynik bazowy, przewidywany wynik, założenia i przyczyny ograniczeń.

### Etap 4 — raporty i interfejs
- [ ] Raport dzienny dla oficerów: przydziały Operations, członkowie, braki i ostrzeżenia.
- [ ] Widok planet/faz i celów gwiazdek.
- [ ] Import/eksport planu (JSON/CSV); później interfejs webowy i eksport kompatybilny z innymi narzędziami, jeśli format zostanie potwierdzony.

## Architektura wstępna

- `reference/`: wersjonowane dane misji i Operations.
- `imports/`: dane gildii i rosterów (generowane; nie commitować prywatnych danych bez potrzeby).
- `src/`: normalizacja danych, pokrycie platoonów, optymalizator.
- `reports/`: generowane raporty.
- GitHub Actions może uruchamiać import/analizę w chmurze, zgodnie z istniejącym sposobem pracy repozytorium.

## Ważne ograniczenie początkowe

Obecny pipeline repozytorium pobiera roster jednego konta. To nie wystarcza do wiarygodnego planowania gildii. Zanim pokażemy realne przydziały lub prognozę gwiazdek, należy wdrożyć import rosterów wszystkich członków i zweryfikować sposób uzyskania danych gildii.

## Import całej gildii

Workflow `.github/workflows/import-rote-guild.yml` uruchamia Comlink w GitHub Actions i pobiera:
1. profil konta wskazanego jako Ally Code,
2. identyfikator gildii z profilu,
3. listę członków gildii,
4. profile i roster każdego członka.

Uruchomienie: GitHub → Actions → **Import ROTE guild rosters** → Run workflow. Domyślnie używa Ally Code już skonfigurowanego w repozytorium; można go zmienić w polu wejściowym. Nie trzeba mieć kodów pozostałych członków.

Dane rosterów są tworzone wyłącznie w katalogu tymczasowym runnera i nie są commitowane ani publikowane jako artefakt. Workflow na tym etapie wypisuje w logu tylko nazwę gildii, liczbę członków i łączną liczbę jednostek. To celowe zabezpieczenie przed przypadkowym ujawnieniem rosterów całej gildii w publicznym repozytorium.

Importer odrzuca niekompletny wynik zamiast generować plan na podstawie części rosterów. Zapisuje surowe pola źródłowe jednostek, ponieważ mapowanie gwiazdek, gearu i reliktów do wspólnego modelu musi być osobno zweryfikowane na rzeczywistej odpowiedzi Comlink.
