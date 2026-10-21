# World parity: root causes and fix plans for U1, U2, U4 (2026-10-20)

Follows `Transient/world_parity_2026-10-20.md` (old = `CANONICAL_ASHKARR_START_2026-09-12.rws`,
new = `ASHKARR_DEV_START_2026-10-20_RECORDLINKS.rws`, read-only copies in
`D:\ClaudeWork\rimmandrake\scratch\parity\`). Offline only: no bridge, no game, no save written.
Probe scripts: `D:\ClaudeWork\rimmandrake\scratch\paritycause\`.

Plans (built by `src/RimMandrake/Utils/parity_fix_plans.py`, selftest
`src/RimMandrake/Utils/selftest_parity_fix_plans.py`), applied live by
`world/_parity_apply_2026-10-20.py <u1|u2|u4> <outdir> [--apply]` (dry run by default; checks
every `before` value against the live world first, refuses on any mismatch):

| fix | plan | live writes |
|---|---|---|
| U1 labels | `world/ASHKARR_PARITY_U1_labels_2026-10-20_plan.json` | 71 `world_features_set` |
| U2 mutators | `world/ASHKARR_PARITY_U2_mutators_2026-10-20_plan.json` | 28,280 removals, 123 re-adds |
| U4 river flow | `world/ASHKARR_PARITY_U4_riverdist_2026-10-20_plan.json` + `world/ASHKARR_PARITY_U4_links_mouthfirst_2026-10-20.csv` | one `world_links_import clearFirst` |

## U1. Region labels: the new world is right; the audit used a mirrored frame

**The parity table's 52 of 63 "wrong" labels was an instrument error.** `feature_drawcenter_audit.py`
turned a raw engine `drawCenter` into a worldgeom vector as `(x, y, -z)`: a reflection, fitted on
2026-10-09 so that two hand-picked labels (Fall Line, The Breaks) lined up. The engine's own
inverse is `PlanetLayer.LongLatOf` (1.6 source, read through RimSage): `lon = atan2(x, -z)`,
`lat = asin(y / r)`. worldgeom's lat/lon came from that same function, so the right mapping is
`vec = (-z, y, x) / r`: a 90-degree rotation, not a reflection.

The evidence, three independent ways:
1. **Engine source:** the `LongLatOf` formula above.
2. **Engine-written data:** `world_features_import` puts every label on `GetTileCenter(<the middle
   CSV row of the region>)`. A rotation fit of all 71 dev drawCenters against those middle tiles gives
   exactly `(x, y, z) -> (z, y, -x)`, determinant +1, median error 0.004 degrees, worst 0.14.
3. **Counts** (single-piece labels more than 5 degrees from their own tiles):

| save | old mirrored frame | engine frame |
|---|---|---|
| canonical before 2026-10-09 (backup `...bak-pre-biomescore-retire-20260927T055758Z`) | 52 wrong | **0** (all within 0.14 degrees) |
| canonical now | 2 wrong | **51 wrong** |
| dev 2026-10-20 | 52 wrong | **0** (all within 0.14 degrees) |

So **on 2026-10-09 the audit "fix" moved 60 canonical labels (52 single-piece plus 8 multi-piece)
off their regions.** That is the frame that called the dev world wrong. Fall Line and The Breaks
passed in both frames, so the self-check could not tell the two apart. Fixed:
`feature_drawcenter_audit.py` now uses the engine frame and self-checks the LongLatOf identity on
real tiles. The selftest pins four engine-placed labels and fails under the old frame. If the old
canonical save is ever used again, put its drawCenters back from
`CANONICAL_ASHKARR_START_2026-09-12.rws.bak-pre-labelcurve-drawcenter-20261009`. Sizes are a
separate change and stay. ⛔ Do not run the old `--out` fix on the dev world: it would move 52
correct labels onto the wrong ground.

**Sizes were a real regression.** `world_features_import` (JawaBench) sizes every label as
`max(6, sqrt(tiles) * 1.35)` and has no way to receive the canonical sizes. The canonical sizes are the
`world_label_curve.py` curve the owner approved by card on 2026-10-09
(`WORLD_LABEL_SIZE_HIERARCHY_1`). 68 of 71 differ, 5 of them by more than 1: Fall Line 16.81 to
26, Salt Gate 6 to 10, The Abandoned Mines 7.87 to 10, Hollow Verge 8.54 to 10, and Quiet Ground
8.85 to 10. The rest are within 0.5. `WORLD_FEATURE_LABELS_OVERSIZED_1` is closed (fixed by looking,
2026-09-10), so no size complaint is open and every canonical size is restored. K is unchanged.

**Plan U1:** for each of the 71 labels (matched by name), set the size to the canonical size, and
`centerOnTile` to the member tile nearest the centroid of the region's biggest piece. That is the
2026-10-09 rule, now applied in the right frame. Before the change every label already sits on its
own tile. The import's middle-row tile is a median of 8.1 degrees from the region's middle. Salt (4
pieces) is the one label that is not on its biggest piece. The plan stores each label's position
and size before the change, and the tile under it.

**Stamp side (done 2026-10-20, source + staging build; live deploy owed):** `world_features_import`
takes `featuresPath`, a features CSV keyed by name whose optional `size` and `centerTile` columns
override the computed label (its `drawCenter` column is never read: it holds the mirrored-frame
positions). The bundle's features CSV carries both (`paint_inputs_build.add_label_centres`, from the
U1 plan) and `w9_run.py` stage 6 passes it. With no features file the import computes
`max(6, sqrt(tiles) * 1.35)` as before. Selftest: `src/RimMandrake/Utils/selftest_w9_stamp_parity.py`.

## U2. Mutators: 28,616 entries the stamp never wrote

**The cause is confirmed by subtraction.** The stamp's input is
`world/paint_inputs_2026-10-20/ASHKARR_WORLDMAP_mutators.csv`, which `w9_run.py` used instead of
the record. It holds 27,645 entries. On the dev save:

- The 56,070 dev entries all resolve (0 unresolved hashes).
- **28,616 dev entries are not in the stamp.** They span 150 defs, and 66 of those defs (15,423
  entries) the canonical world never held. Examples: `VEE_LargerRegion` 1,154, `VEE_SmallerRegion`
  1,061, and a dozen `VEE_*` wildlife and vent defs at 380 to 480 each. `Mountain` 2,064 sits on 1,124
  Flat tiles, so it does not follow the new hilliness. `Caves` 1,093.
- 191 stamp entries did not land (Coast 104, River 37, RiverIsland 12, Oasis 10, Headwater 9, ...).
- As a sanity check, the canonical save against the record is identical apart from the 2,142 retired-donor
  entries, which were renamed one for one.

These are mutators the engine rolled at world generation for seed `safety`, before the stamp ran.
Stage 3 of the stamp clears only stale Coast and marine entries, so nothing removed the rest. That
breaks the frozen-world rule. Stage 4b adds; it never subtracts.

**One kept:** `RM_SeaCoast`, 336 entries. It is our drop-in twin of vanilla Coast beside the modded
seas (`src/RimMandrake/SeaShores/Defs/TileMutatorDefs/RM_SeaCoast.xml`). All 336 placements border
stamped water and none is on water, so it is derived from geography, not rolled content. It takes
the shared Coast slot on 68 tiles where the stamp wrote Coast. Those 68 stamp entries are listed
as `superseded` and are not re-added.

**Ours, but still rolled (13 defs, 4,703 entries):** for example `RM_EdibleAirborneMicrofungi` 889,
`RM_MoldyEnvironment` 878, `RM_OllathrixNest` 546 and `RM_AmbientRadiation` 519. These are the
remake's own defs, but these placements came from their world-generation chances, not from the
authored world. They are in the removal list by the frozen-world rule. The plan's
`counts.removeOurPrefix` lists them in case the owner wants to keep them.

**Plan U2:** remove 28,280 (tile, def) entries across 149 defs, then re-add the 123 stamp entries
that never landed (River 37, Coast 36, RiverIsland 12, Oasis 10, Headwater 9, ...). Most were
pushed out of a shared slot by a rolled entry. Anything that still fails to land shows up in the
read-back as a conflict inside the record itself. This also clears the icon clutter from Mutator
World Icons. **Stamp side (done 2026-10-20):** `w9_run.py` stage 4a strips every live (tile, mutator) its
input does not hold, keeping only `KEEP_DERIVED` (`RM_SeaCoast`). It runs after stage 4, so it
also takes the mutators `AddLandmark` rolls, and before 4b, so the input's entries find their
shared slots free. A truncated live read stops the run rather than strip from a partial view.

## U4. River flow: the importer laid rivers in export order, not mouth-first

**The cause is proven by simulation.** `WorldGrid.OverlayRiver(from, to)` sets
`to.riverDist = max(to.riverDist, from.riverDist + 1)`, and only when the link is new: a repeat
link returns early (1.6 source). Running `world_links_import` over the input links CSV in file
order gives the dev world's `riverDist` on **335 of 335** river tiles, maximum 5. The CSV was
exported from the save, and its a/b columns and row order are whatever the save had: 93 of 326
rows do not name the downstream end first, and the rows are not in mouth-first order.

The walk from mouth to head shows the canonical meaning:
- 11 river systems and 335 river tiles, with exactly one `riverDist` 0 per system.
- 322 of 326 links step by exactly 1.
- Heads at 50, 37, 37, 13, 9, 9, 7, 5, 5, 4 and 4.

On the dev world the same systems have 58 zero tiles, 100 tiles with no downstream neighbour, 82
level links, and every head at 5 or below. Direction and flow semantics are lost; geometry is intact.

Two side notes:
- The canonical maximum of 95 was a stale value on a tile with no river. 803 canonical tiles off
  the rivers carry old nonzero values with no links. Dev keeps 0 there, which is correct, and the
  plan does not touch them.
- 7 of the 11 canonical mouths do not border one of the 4 sea biomes. They may be inland sinks.
  This is reported only, not changed.

**Plan U4:** a lay order of all 326 links, each laid once, rivers first and then the 1,242 roads
unchanged. Fed through the OverlayRiver rule it reproduces the canonical `riverDist` on all 335
river tiles; 314 tiles change. It handles the two canonical level links at tiles 14323, 6225 and
14322 by laying 14323's outflow while 14323 is still at 18. `world_links_import clearFirst` re-lays
them live. The edges and defs are the same, which the plan builder checks before it writes. The
same order now replaces the river rows of `world/paint_inputs_2026-10-20/ASHKARR_WORLDMAP_links.csv`
(same edge set; the builder asserted that), so a re-stamp lays them right.
`world/ASHKARR_WORLDMAP_links.csv` is the record and is left as it is.

**Stamp side (done 2026-10-20):** the row order no longer has to be right. `w9_run.py` stage 2
reads `DIR/ASHKARR_WORLDMAP_riverdist.csv` (tile, river_dist: the canonical values, written by
`paint_inputs_build.write_river_dist` from the U4 plan) and lays the river rows in the order
`river_lay.order_links_mouth_first` finds, refusing if that order misses any tile. The mouth
cannot be inferred from geometry instead: 3 of the 11 canonical mouths are neither the lowest
tile nor the largest-river leaf of their system. With no riverdist file, stage 2 lays the file
order as before and warns.
