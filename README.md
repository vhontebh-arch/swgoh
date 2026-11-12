# Canonical SWGOH optimizer data

This branch is the single source of truth for every active optimizer version.

## Producers and consumers

- `main` / `.github/workflows/update-swgoh.yml` is the only account-data producer. It acquires the Comlink player export and C3PO inventory, downloads current game data and localization, derives the account CSV files, validates them, and publishes one atomic snapshot here.
- `optimizer-v2` is a consumer. Its analysis workflow downloads all inputs from one immutable commit on this branch and verifies every Git blob SHA before running.
- Mod profiles are maintained centrally using the agreed direct SWGOH.GG page-reading process (Top 1000 Kyber GAC and Top 100 Guilds). Updated profiles are published here and shared by every optimizer version; GitHub Actions does not scrape profile pages.
- Local copies on optimizer branches are temporary runtime files. Optimizer workflows do not publish independent copies of source data.

## Snapshot files

- `swgoh_972824625.json` — raw Comlink player export
- `c3po.json` — C3PO inventory export
- `data.json` — normalized game units, equipment and recipes
- `localization.json` — ENG_US localization
- `roster.csv` — derived character roster
- `ships.csv` — derived ship roster
- `mods.csv` — complete derived mod inventory
- `mod_profiles.json` — shared SWGOH.GG mod profiles
- `data_manifest.json` — source commit, acquisition/publication timestamps, record counts, SHA-256 and Git blob SHA for every file

## Consistency rules

1. A consumer resolves the branch head once, then downloads the manifest and all requested files from that exact commit SHA. It never mixes files from different branch heads.
2. Each file is checked against its Git blob SHA before it is written to the working directory. A missing file or hash mismatch stops the analysis.
3. The account export and all derived account files are published together from one producer run.
4. A recent in-game change can legitimately differ between exports taken minutes apart. The manifest records the player-export acquisition time; consumers use one published snapshot rather than comparing it with an older branch copy.
5. Mod profiles follow the agreed five-day freshness policy and are shared across optimizer versions.
6. Only active versions `main` and `optimizer-v2` are maintained as producer/consumer workflows. Historical experiment branches are not independent data sources.

The initial live snapshot is documented in `data_manifest.json`.
