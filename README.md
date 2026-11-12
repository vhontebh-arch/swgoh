# Canonical SWGOH optimizer data

This branch is the single source of truth for data consumed by every optimizer version.

## Files
- `mods.csv` — derived mod inventory
- `roster.csv` — derived player roster
- `c3po.json` — C3PO inventory export
- `mod_profiles.json` — shared SWGOH.GG mod profiles
- `data_manifest.json` — provenance and data contract

## Rules
1. Every optimizer version must fetch these files from `optimizer-data`; local branch copies are runtime caches only.
2. Account data publication must be atomic: acquire player export and C3PO inventory in one run, generate both CSV files from that same acquisition, validate, then publish all files and the manifest together.
3. Record acquisition timestamps, source metadata, and SHA-256 for each published file in the manifest.
4. A recent in-game change can cause legitimate differences between exports taken minutes apart. Compare timestamps and publish one internally consistent snapshot.
5. Shared mod profiles follow the agreed 5-day refresh rule.

The bootstrap manifest records the exact origins of the initial shared dataset. Workflow integration is the next step.
