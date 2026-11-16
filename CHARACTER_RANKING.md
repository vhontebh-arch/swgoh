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

The mapping uses the player's roster export for 308 characters.
The remaining 5 names, absent from that export, were resolved
against the pinned full unit catalog: The Ronin (`THERONIN`), Third Sister (`THIRDSISTER`), Taron Malicos
(`TARONMALICOS`), Dark Trooper Moff Gideon (`MOFFGIDEONS3`) and Jaxxon
(`JAXXON`). This is a catalog mapping, not a claim that those five are owned.

## Importance model

1. **Rank is the sole primary importance signal.** Lower Rank means greater importance; Rank 1 is highest.
2. `importance_score` is a bounded, monotonic transformation of Rank:
   `1 + 2 * (1 - (rank - 1) / (record_count - 1))^2`.
   It ranges from 3.0 for Rank 1 to 1.0 for the last-ranked character. The nonlinear curve gives more separation to the highest-ranked characters without creating an extreme multiplier.
3. **Final Tier is audit metadata only.** It is not used to reorder characters or added again to the importance score.
4. **Sort Score is audit metadata for now.** It is not combined with Rank as a second importance signal. It may later be used only as a small, separate donor-protection adjustment after testing on complete transfer chains.
5. Base Tier, synergy/Omicron fields, Relic Gear Level and Ability Score remain available for auditing the source export; their effects are not scored again.

The score is a relative weighting input for chain evaluation, not a claim that a character is exactly two or three times as useful in gameplay.

## Rank-weighted transfer-chain objective

- Every affected character's complete-build before/after delta, including the target, is multiplied by that character's Rank-derived `importance_score`.
- Positive and negative deltas use exactly the same rule. There is no special multiplier exemption for the target.
- Deltas are grouped by character before weighting, so multiple PATCH operations for one character do not multiply its importance repeatedly.
- The recursive donor-rebuild search compares up to five complete alternatives at each root donor (default cap: 5). Child donor rebuilds use their best feasible result; the resulting whole recursive chain is ranked by the sum of Rank-weighted donor deltas.
- The simpler breadth-first chain fallback also ranks same-depth terminal alternatives by Rank-weighted donor deltas. Exact set-combination preservation is a secondary tie-break.
- If an affected character is missing from Stack Rank, its neutral weight is 1.0.
- The recursive donor-branch search compares alternatives by weighted donor impact. For a fixed target mod, the target contribution is constant across those donor alternatives, so weighting it symmetrically does not change their relative order. The account-level result and comparisons between target improvements do include the target's Rank weight.
- The final user report displays both the ordinary unweighted roster balance and the fully Rank-weighted balance, including a separate weighted target contribution. The recommendation status uses the fully Rank-weighted balance.

A sensitivity run for GOPHERANTS compared caps 1, 2, 3, 5 and 8 on the same checked-in account snapshot. Caps 1–3 selected the same chain and produced a Rank-weighted account balance of +97.26. Cap 5 found a fourth complete Emperor Palpatine donor alternative, changing the recursive PATCH chain and improving the balance to +116.01. Cap 8 produced the same chain and score as cap 5; only four complete alternatives were found for that donor. Thus cap 3 demonstrably stopped too early in this case, while cap 5 reached the observed plateau.

This is a bounded search, not an exhaustive search of every physically possible mod permutation. It deliberately limits recursive alternative exploration to keep runtime manageable; the sensitivity test does not prove that no fifth or later alternative could exist in other cases.

## Refreshing

Stack Rank refresh remains manual because no supported public export endpoint has been established. Replace the TSV snapshot and, if new characters appear, refresh the pinned baseId map from a canonical game-unit catalog. Then run:

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
