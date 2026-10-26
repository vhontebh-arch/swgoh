# ROTE reference data

To avoid invented requirements, reference data must be imported from versioned, inspectable sources and validated before optimization.

## Candidate sources to evaluate

- SWGoH Wiki: Rise of the Empire, Zone Information, Operations. Useful for human-readable cross-checking.
- `swgoh-utils/gamedata`: investigate versioned game data such as territory battle definitions and ROTE operation definitions.
- SWGOH.GG territory battle pages: useful as a secondary cross-check for platoon coverage and counts.

## Required normalized entities

- `phase`: phase number/order and start/end rules if relevant.
- `planet`: stable ID, display name, alignment, phase, route/chain relationships.
- `zone`: stable ID, planet, territory type and lock/preload dependencies.
- `platoon`: stable ID, zone, operation/ability, slot list.
- `platoon_slot`: stable slot ID and required unit base ID.
- `mission`: stable ID, zone, type (combat/special/fleet), requirements, waves and point values.
- `star_threshold`: zone/phase, star count, required territory points.
- `source_metadata`: source URL, source version/commit, retrieval time and validation status.

## Validation rules

- Every referenced unit ID must resolve to a known game unit.
- Each platoon must have the expected number of slots according to the source version; do not silently pad or truncate.
- Duplicate requirements are separate slots and must remain separate.
- Changes in upstream source version must trigger re-import and a diff report.
- Human-readable wiki tables are cross-checks, not permission to infer missing IDs or requirements.
- Unknown values remain null and block a claim of a complete plan.