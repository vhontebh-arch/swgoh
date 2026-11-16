# SWGOH Character Importance Ranking

This experimental component imports the personalized **Stack Rank** export for
ally code `972-824-625`. Stack Rank is the only source used to assess character
importance in this branch. No SWGOH.GG relic counts, release-age cohorts,
HotUtils usage, GAC-only ranking, or popularity proxy is mixed into the result.

## Source snapshot

- Raw input: `data/stack_rank.tsv` (313 character rows; original columns retained).
- Generated output: `character_ranking.json`.
- Source page: [Stack Rank](https://swgoh.spineless.net/stackrank?omicronGac=true&omicronTw=true&omicronTb=true&omicronRaids=true&omicronConquest=true&allyCode=972824625&showFullDetails=true)
- Export settings: Omicron Boost enabled for GAC, Territory War, Territory Battle,
  Raids and Conquest; full details enabled.
- The snapshot in this repository was supplied on 2026-11-16.

Stack Rank is roster-personalized. Do not replace its `Final Tier` values with
base tiers from a public character list or another dataset.

## Interpretation

1. `Final Tier` is the primary importance measure. Lower tier means greater
   importance (tier 1 is highest; tier 19 is lowest).
2. `Rank` is the original overall position from the source and is retained as
   a secondary ordering value. It is not the same as `Final Tier`.
3. `importance_score = 20 - final_tier` is a simple inverse representation;
   it does not add another signal.
4. `Base Tier`, `Synergy Enhancement`, `Omicron Boost`,
   `Omicron Synergy Boost`, `Relic Gear Level` and `Ability Score` are
   retained for audit. They are not scored a second time because their effects
   are already represented in `Final Tier`.
5. `Sort Score` and `SubSort Score` are retained as source sort metadata,
   not independent importance signals.

The ranking module is standalone. It does not yet map every display name to a
game `baseId`, and it is not connected to `mod_analyzer.py` or
`protected_owners.json`. No mod protection behavior changes in this branch.

## Refreshing the snapshot

The Stack Rank page is dynamic and no supported public export endpoint has
been established. Therefore refresh is intentionally manual:

1. Open the source URL above with the same ally code and all five Omicron
   Boost options enabled.
2. Export/copy the complete table including all columns.
3. Replace `data/stack_rank.tsv` with the tab-delimited export.
4. Regenerate `character_ranking.json` and run the tests:

```bash
python character_ranking.py --input data/stack_rank.tsv --output character_ranking.json
python -m unittest discover -s tests -p "test_character_ranking.py" -v
```

5. Commit both the raw snapshot and generated JSON to
   `feature/character-importance-ranking`.

The workflow validates the committed snapshot and generated output; it does not
pretend to fetch fresh data from the website. No automated website scraping is
configured.

## Python interface

```python
from character_ranking import load_stack_rank, rank_characters, get_character_rank

rows = load_stack_rank("data/stack_rank.tsv")
importance_order = rank_characters(rows)
grogu = get_character_rank(rows, "Grogu & Anzellans")
```
