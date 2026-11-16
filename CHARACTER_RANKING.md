# SWGOH Character Importance Ranking

This experimental component imports the personalized **Stack Rank** export for
ally code `972-824-625`. Stack Rank is the only source used to assess character
importance in this branch. No SWGOH.GG relic counts, release-age cohorts,
HotUtils usage, GAC-only ranking, or popularity proxy is mixed into the result.

## Source snapshot

- Raw input: `data/stack_rank.tsv` (313 character rows; original columns retained).
- baseId map: `data/character_base_id_mapping.json` (313 unique mappings).
- Generated output: `character_ranking.json`.
- Stack Rank page: [personalized export](https://swgoh.spineless.net/stackrank?omicronGac=true&omicronTw=true&omicronTb=true&omicronRaids=true&omicronConquest=true&allyCode=972824625&showFullDetails=true)
- Mapping catalog: [DrPivot/SWGOH-Guild-Progress unit_list.csv](https://github.com/DrPivot/SWGOH-Guild-Progress/blob/f6f2e182cab19602a9d45399235eb26caf0f0cce/data/unit_list.csv), pinned to commit `f6f2e182cab19602a9d45399235eb26caf0f0cce`.
- Matching: normalized display-name match (case, diacritics and punctuation normalized). All 313 names matched exactly one catalog entry and all 313 baseIds are unique.

The player roster CSV contained 308 of the 313 Stack Rank characters. The five
not present in that roster export were resolved against the pinned full unit
catalog: The Ronin (`THERONIN`), Third Sister (`THIRDSISTER`), Taron Malicos
(`TARONMALICOS`), Dark Trooper Moff Gideon (`MOFFGIDEONS3`) and Jaxxon
(`JAXXON`). This is a catalog mapping, not a claim that those five are owned.

## Interpretation

1. `Final Tier` is the primary importance measure. Lower tier means greater
   importance (tier 1 is highest; tier 19 is lowest).
2. `Rank` is the original overall position from the source and is retained as
   a secondary ordering value. It is not the same as `Final Tier`.
3. `importance_score = 20 - final_tier` is a simple inverse representation;
   it does not add another signal.
4. Base Tier, synergy/Omicron fields, Relic Gear Level and Ability Score remain
   audit fields; their effects are not scored a second time.
5. Sort Score and SubSort Score remain source sort metadata.

The ranking is standalone and is not connected to `mod_analyzer.py` or
`protected_owners.json`; no mod protection behavior changes in this branch.

## Refreshing

Stack Rank refresh remains manual because no supported public export endpoint
has been established. Replace the TSV snapshot and, if new characters appear,
refresh the pinned baseId map from a canonical game-unit catalog. Then run:

```bash
python character_ranking.py --input data/stack_rank.tsv --output character_ranking.json --expected-count 313
python -m unittest discover -s tests -p "test_character_ranking.py" -v
```

The workflow validates the snapshot and generated JSON; it does not scrape the
Stack Rank website.

## Python interface

```python
from character_ranking import load_stack_rank, rank_characters, get_character_rank

rows = load_stack_rank("data/stack_rank.tsv", "data/character_base_id_mapping.json")
importance_order = rank_characters(rows)
grogu = get_character_rank(rows, "GROGUANZELLANS")
```
