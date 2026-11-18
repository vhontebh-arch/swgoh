# SWGOH Character Ranking and Transfer Gate

Stack Rank is the sole source of character importance. Lower Rank means greater importance; Rank 1 is highest. Final Tier and Sort Score are retained only for audit and do not affect eligibility or scoring.

## Hard transfer rule

An equipped mod may move only from a character with a numerically greater or equal Rank to a character with a numerically smaller or equal Rank. A more important character can never donate a mod to a less important character. This is a hard feasibility condition, not a multiplier or weighted objective.

- The rule applies to the initial MOD transfer and every subsequent PATCH in a recursive chain.
- Inventory mods have no character source and are exempt.
- Unknown Rank for either endpoint blocks an equipped-mod transfer (fail closed).
- Equal Rank is allowed; the current Stack Rank snapshot normally assigns unique ranks.
- Among chains that satisfy the rule, the optimizer retains its existing build-impact scoring and tie-breaks.

## Snapshot and mapping

- Input: data/stack_rank.tsv (315 character rows; original columns retained).
- Mapping: data/character_base_id_mapping.json.
- Generated output: character_ranking.json.
- Personalized export: https://swgoh.spineless.net/stackrank?omicronGac=true&omicronTw=true&omicronTb=true&omicronRaids=true&omicronConquest=true&allyCode=972824625&showFullDetails=true

All 315 names map to unique canonical baseIds. Stack Rank refresh remains manual because no supported public export endpoint has been established.

## Refresh

```bash
python character_ranking.py --input data/stack_rank.tsv --output character_ranking.json --expected-count 315
python -m unittest discover -s tests -p "test_character_ranking.py" -v
```
