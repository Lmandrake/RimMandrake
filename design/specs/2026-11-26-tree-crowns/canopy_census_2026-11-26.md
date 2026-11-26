# Canopy census, 2026-11-26 (TREE_SHADE_SELFTEST_PROVE_FOREST_IS_SHADE spec 1, design §6 T2 live half)

MEASURED on ArchSmall (tier `explosivegrowth_solo`, Baroque Biomes of commit 3819a1186915), a quicktest game on the flat
tile 30979, each biome set on that tile and the map regenerated, by
`python.exe src/RimMandrake/CreatureBehaviors/live_canopy_census.py RM_Greentide RM_Miasma RM_Webwork`. Log:
`design/specs/2026-11-26-tree-crowns/canopy_census_ArchSmall_2026-11-26.log`. Two runs gave the same numbers.

Open ground = cells not under a roof and not indoors, terrain not water by name (none on these maps). Covered = a crown's
shade of at least 0.99 there. The quicktest world has a day/night cycle, so the grid casts each disc under its crown
(the same area as down-sun, less the map-edge loss).

| Biome | open cells | crown-covered | design §2.2 estimate | T2 bar |
|---|---|---|---|---|
| `RM_Greentide` | 60717 | 0.974 | 0.99 | at least 0.60: holds; within 10 points: holds |
| `RM_Miasma` | 60825 | 0.274 | 0.97 | at least 0.60: FAILS; within 10 points: FAILS |
| `RM_Webwork` | 60830 | 0.694 | 0.97 | (no 0.60 bar); within 10 points: FAILS |

Why the Miasma differs from the estimate: most of its open ground is `Mud` (34289 cells) and `RM_MiasmaSaltCrust`
(6414), where its trees do not grow; the estimate placed plants on every cell at plantDensity with no fertility, rock or
water (its own docstring). The crown model itself shades the ground under its trees (the live scene
`live_tree_crowns.py`: 69 of 69 cells under a veluthar). The 0.60 Miasma clause of T2 rests on that estimate.

A mountainous tile (67905) gave far less open ground (13524 cells) and Greentide 0.53, Miasma 0.08, Webwork 0.23 of it:
the regenerate keeps the tile's mountain, and its trees stand in the valleys.

Not measured: the caster-plant cell count of spec 1 (the bar reads the covered share, measured here directly); the
Fever Wood and the Contagion (both held by the owner, `src/RimMandrake/rimflow/mod_owner_hold.json`); the `RUT_` twins
of the spec (deleted 2026-11-06, BIOME_TWINS_RETIRE_TWENTY_FIVE_FROZEN).
