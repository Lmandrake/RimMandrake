# THE_SCALD_LOST_ITS_WATER_1 — run 1, live, full-583

## RESULT: the choice was already MADE, in the artifact, before this item was worked.
## Option 2 is in force and is now measured live. One half of the criteria needs the owner.

The item offers three ways out "for DECIDE or the owner" and warns ⚠️ *DO NOT "fix" this by
dropping the elevation until the cost below is weighed.* **It had already been dropped.**
`world/ASHKARR_WORLDMAP_tiles.csv` commit **`bd5dad0` (08:34)**, *"The Scald was a lake
perched 1,300 m above its own shoreline"*, sets those 312 tiles to elevation **−30**. The
CSV is the frozen authority, so **option 2 is the standing decision** and this item was
deliberating a question the artifact had already answered.

The live world had not caught up — see WORLD_PAINT_IS_PRESENT_1, it predated that commit
by 9 minutes. Importing the frozen CSV made it current, and the verify section's numbers
came out exactly as the item predicted for option 2:

| | before import | after import | item predicted |
|---|---|---|---|
| `world_stats` water | 6.71%, 2 bodies | **8.14%, 3 bodies** | 8.14% |
| `world_lint.lakesAboveSeaLevel` | 312 | **0** | 0 |

## ⚠️ But the finding did not go away — it MOVED, and the new home is a lint bug

    landBiomeSubmerged: 312     "Land biome with elevation <= 0."
    examples: tile 86 Lake -30.0 · 146 Lake -30.0 · 202 Lake -30.0 · 204 · 205 · 382 …

All 312 are the Scald. The check calls a **`Lake` at elevation −30 a submerged LAND
biome** — but a lake below its own shoreline is the definition of a lake, not a defect.
The sibling check already knows this: `waterBiomeOnRaisedLand` says *"Lake is EXCLUDED - a
lake at altitude is ordinary"*. `landBiomeSubmerged` never got the same exclusion, so
sinking the Scald swapped 312 informational findings (that check *"scores ZERO"*) for 312
that count toward the lint's total. The planet got better and the score got worse.

Filed as LINT_COUNTS_LAKE_AS_LAND_1 for BUILD. Until it is fixed, `landBiomeSubmerged:
312` on this planet is EXPECTED and is not a fault — which is precisely the annotation
this item's third criterion asks for, arriving on the other option's row.

## What is NOT done, and cannot be done by this seat
🔴 The item's second criterion: *"the owner looks at the relief around the Scald afterwards
and does not name it as a defect."* Option 2 moves relief, the rain shadow, the Spine and
the drainage story — that is a LOOK, and the owner's. `needs` set to `owner`.

## Also settled, and worth keeping
`SurfaceTile.WaterCovered => elevation <= 0f` is the whole mechanism, and it is why the
statistic is an ELEVATION reading and not a biome reading. ⚠️ Twice now the 6.71/8.14 gap
has been rationalised as *"world_stats counts Ocean only"* — the item's own notes record
that guess, and CHECK made it again independently at 10:30 today before measuring. It is
wrong both times. The `Lake` biome was present on all 312 tiles the entire time; only the
elevation was wrong. **The biome was never the thing being counted.**
