# Every number in the running list's prose, checked against what ships (2026-11-12 00:29 -0800)

| where | the list says | what ships | source |
|---|---|---|---|
| Cracked Lands row | beauty 40 | `<Beauty>40</Beauty>` | RM_FossilCase.xml |
| Long Shade row | up to 16 cells | `MaxCastCells = 16f` | RM_MapComponent_ShadeGrid.cs |
| Rust Cathedral row | 120 HP a day | ticksPerHeal 500, tickerType Rare: 60000/500 = 120 HP per day | RM_PatternHull.xml; CompSelfhealHitpoints (1 HP per ticksPerHeal) |
| preamble | heat bank 10 heat/s | heatPerSecond 10 | RM_FurnaceHideBank.xml |
| preamble | hexplate Cleanliness 0.6 | 0.6 | RM_TelluroxHexplate.xml |
| preamble | fossil case Beauty 40 | as above | |

These are all the numbers in the gift and source columns and the judges' paragraph; the checker (ship_contributions.py)
verifies the named defs, not prose numbers, so this table is the check for them. A 'beauty 14' left over from before the
design judge's change was the one mismatch found (judge round 4) and is corrected above.
