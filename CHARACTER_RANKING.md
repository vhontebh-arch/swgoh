# SWGOH Character Importance Ranking

Standalone character-ranking component. It does not import or depend on the mod
optimizer. Any script can import `rank_characters` / `get_character_rank`,
or consume the generated JSON file.

## Input

CSV required columns:

- `baseId`
- `name`
- `global_relic_r5_plus_players`

Optional count columns:

- `global_relic_r7_plus_players`
- `global_relic_r9_plus_players`

Optional `release_date` column (ISO `YYYY-MM-DD`). Alternatively provide
metadata JSON keyed by baseId:

```json
{
  "characters": {
    "50RT": {"release_date": "2024-01-01"}
  }
}
```

The input is deliberately a neutral contract: it can be exported by the
existing SWGOH data pipeline or assembled by a future collector. The ranking
module does not fetch data and does not modify source data.

## Scoring

1. Convert each available relic-tier count into a percentile across the
   supplied character population (ties receive a mid-rank).
2. Combine available tiers using weights R5+ 50%, R7+ 30%, R9+ 20%.
   Missing tiers are ignored and the remaining weights are renormalized.
3. Compare that combined score with characters released within +/- 365 days.
   The final score is 55% global standing + 45% age-cohort standing.
4. If fewer than five dated peers exist, age adjustment is omitted for that
   character; the output explicitly reports this.

This intentionally balances two signals: established broad usage remains
important, but a recent character can rank highly relative to its release
cohort instead of being automatically buried by older characters.

## Run

```bash
python character_ranking.py --input optimization_status.csv --metadata character_release_dates.json
```

Output: `character_ranking.json` (versioned schema).

## Import from another script

```python
from character_ranking import load_character_data, rank_characters, get_character_rank

rows = load_character_data("character_counts.csv", "character_release_dates.json")
ranking = rank_characters(rows)
fifty_rt = get_character_rank(ranking, "50RT")
```

## Important limitations of the first version

- The currently available dataset contains R5+ counts only. R7+/R9+ are
  supported but do not contribute until the upstream data supplies them.
- Release dates must be supplied as metadata. Unknown dates fall back to the
  global score and are marked as not age-adjusted.
- The weights and 365-day cohort window are explicit defaults, not claims of
  objective truth. They should be evaluated against a sample of old and new
  characters before the ranking is used to protect donors automatically.
