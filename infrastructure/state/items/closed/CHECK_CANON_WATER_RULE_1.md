# CHECK_CANON_WATER_RULE_1

## Bug

`check_canon.py`'s `[water]` rule matched any bare `25%` / `22–28%` / `6.9%` /
`8.6%` in a cell whose `context` regex was `water|ocean|sea\b|tiles`. `tiles`
is not water-specific vocabulary — it's the generic word for the planet's grid
cells, desert terrain, and even table row-pools — so its bare presence
anywhere in the cell was enough to validate an unrelated percentage as a
"water contradiction". Two real hits on 2026-09-12:

- `design/Jawa/worldbuilding/biomes/the_slime_gene_lists.md:45` — the
  Amphibious-lungs gene's cost cell, `"skin must stay moist: on desert tiles
  thirst +25%, −3 mood in dry air…"`. A thirst-rate stat, not water fraction.
  Contains `tiles`; contains no `water`/`ocean`/`sea`.
- `design/Jawa/worldbuilding/enrichment/REVIEW.md:26` — `"tiles. No def
  exceeds 25% of a plan's row count."` A row-count cap on a mutator/landmark
  placement plan. Same shape: `tiles` present, no water vocabulary present.

## Fix

Dropped `tiles` from the water rule's `context` regex and added `\b` word
boundaries so `underwater` etc. can't satisfy it either:

```
context=r"\bwater\b|\bocean\b|\bsea\b|\baquifer\b|\bhydration\b|\bmoisture\b"
```

No change to `bad` (the value-matching regex) — every genuine water-fraction
statement in this corpus already pairs its percentage with the word `water`
itself (confirmed via `selftest_check_canon.py`'s existing "water 25%" and
"water 6.9%" cases, which still fire). This follows the file's own documented
convention (`Rule.__init__` docstring): the counted noun/vocabulary is what
disambiguates a coincidental number from a real claim, and the vocabulary
must actually be specific to the fact, not a generic word that happens to
co-occur.

Added two regression cases to `selftest_check_canon.py` reproducing the exact
2026-09-12 false positives (gene thirst stat, row-count cap) so they cannot
silently return.

## Verification

Before (`python3 src/RimMandrake/Utils/check_canon.py`):
```
CONTRADICTS CANON — 2
  design/Jawa/worldbuilding/biomes/the_slime_gene_lists.md:45  [water] found '25%', canon says 6.62%
  design/Jawa/worldbuilding/enrichment/REVIEW.md:26  [water] found '25%', canon says 6.62%
470 file(s) checked. 2 contradiction(s), 17 advisory.
```

After:
```
470 file(s) checked. 0 contradiction(s), 17 advisory.
✅ no design doc contradicts canon.
```

Both false positives gone; the 17 pre-existing advisory hits (unrelated
`modlist_undated`/`terminator` rules) are unchanged, confirming no collateral
change to other rules.

`python3 src/RimMandrake/Utils/selftest_check_canon.py`: **39/39 passed**
(37 pre-existing cases, still all green — including the two genuine
true-positive water cases "water 25%" and "water 6.9%" — plus the 2 new
regression cases added for this fix). No false negative introduced.

## Files touched

- `src/RimMandrake/Utils/check_canon.py` — the `[water]` Rule's `context` regex.
- `src/RimMandrake/Utils/selftest_check_canon.py` — two new regression cases.
