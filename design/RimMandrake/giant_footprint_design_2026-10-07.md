# Huge Things — solid trunks for huge plants, hitboxes for huge pawns (2026-10-07)

Item: `HUGE_THINGS_FOOTPRINT_1`. Mod: `src/RimMandrake/HugeThings` (`mandrake.rm.hugethings`, namespace
`RimMandrake.HugeThings`, free `RM_` tier, Harmony id `mandrake.rm.hugethings`).

## The rulings this builds

- **Option 1, picked by the owner 2026-10-07 07:17**: *"Solid trunk, open canopy — the stem blocks a small patch
  (~2×2 to 4×4 by species) so pawns path around it; clicking anywhere on the trunk selects it; you walk under the
  cap like a tree canopy."* His typed note: *"(1) and this may be related to another mod we have for enormous
  animals needing similar treatment"*.
- Then, typed: *"This might be an extractable mod to handle "huge plants" and "huge animals" together?"* So this
  is its own standalone free mod, not a biome kit: The Rot and TitanicCreatures opt in.

## The problem

`TheRot/Patches/RotSpecies_NamesAndSizes.xml` (ruling `ROT_FLORA_FAUNA_VERDICTS_1`) draws several fungi up to 20
cells wide, but each is still a one-cell plant: it can only be clicked on its base cell, pawns walk through the
stem, and things can be built inside it.

## Mechanism

**Trunk = invisible blocker Buildings.** `RM_HugeTrunkBlocker` is an impassable edifice with no graphic, no hit
points, no flammability, not selectable, not deconstructible or claimable (`Building_TrunkBlocker`). Because it
is an ordinary impassable edifice, vanilla's own systems do the rest with no patches: the path grid and regions
route pawns around it, `GenConstruct.CanPlaceBlueprintAt` refuses building in it (`canBuildNonEdificesUnder`
false refuses conduits too), and plants can't grow in it.

**Shape.** `Plant.Print` lifts a single-mesh plant so its sprite's base sits on the bottom edge of the plant's
own cell, so the stem stands *north* of that cell. The trunk rect is `trunkWidth × trunkDepth` with its south
edge on the plant's row, centred on its column (even widths lean east, as `GenAdj.OccupiedRect` does). The
plant's own cell is never blocked: it stays reachable from the south, so cutting, harvesting and fire work on it
exactly as vanilla (`Touch` reaches it from the open row below).

**Growth.** Scale = drawn size now ÷ drawn size at full growth (`visualSizeRange`). Each dimension is
`max(1, round_half_up(full × scale × settings scale))`. Below `minGrowthToBlock` (default 0.25) the plant blocks
nothing; a rect of one cell blocks nothing. The grath elder is drawn ~full size from birth (19.88~20), so once
past 0.25 growth it has its full trunk.

**Cells it will not take.** A trunk never grows over a building (of any kind, including another trunk), a
blueprint or frame, a pawn, a tree, another huge plant, an undestroyable thing, or unwalkable ground. Those cells
just stay open and are retried on the next refresh. Small plants and filth under it are wiped; items are moved
aside (`WipeMode.VanishOrMoveAside`).

**Lifecycle.** `CompHugeFootprint` is attached at startup to every plant def carrying `RM_HugePlantExtension`.
It registers with `MapComponent_HugeFootprints`, which refreshes a newly registered plant on the next tick (after
map generation finishes, via `FinalizeInit`) and every plant every 2000 ticks for growth. Despawning the plant
(cut, killed, burned, eaten) removes its blockers at once (`PostDeSpawn`). Blockers are saved Things that
remember their owner; the comp saves nothing and re-links them after load by scanning the largest possible
trunk rect. A blocker whose owner is gone (mod removed from the def, a hand-edited save) destroys itself on its
rare tick. Changing Mod Settings re-shapes every trunk at once.

**Selection.** Vanilla already selects any Thing whose `CustomRectForSelector` contains the clicked cell
(`GenUI.ThingsUnderMouse`, listing the `WithCustomRectForSelector` group) and draws the selection brackets
around that rect. Plant and Pawn never supply one. A Harmony postfix on `Thing.CustomRectForSelector`'s getter
supplies it for opted-in defs only, and opting in sets `ThingDef.hasCustomRectForSelector` at startup, before
any Thing registers. For a plant the click area is the trunk width running north for `stemHeight` (the drawn
stem), so it covers the stem, not the whole cap: clicks on the cap still reach what is under it.

**Pawns.** A race carrying `RM_HugePawnExtension` is clicked by a rect of (its current life stage's drawSize ×
`hitboxFraction` (0.6) × settings scale), centred on the pawn, never smaller than its footprint. When Large Pawns
is loaded its `OccupiedRect` square is the footprint; our postfix runs at `Priority.Last` and only widens it.

**Why not the alternatives.** A plant def with `size > 1`: plants are registered, printed, sown and spread as
one cell; vanilla has no multi-cell plant. Patching `GenAdj.OccupiedRect` for the plant: region listers register
a thing over its OccupiedRect, so a rect that grows between register and deregister strands entries. A path-cost
patch: it would not refuse buildings or stop plants, and the 1.6 path grid is rebuilt from things anyway.

## Per-species trunks (The Rot)

Every Rot plant drawn 6+ cells wide. Applied by `TheRot/Patches/RotGiants_HugeFootprint.xml` (per-def
`PatchOperationConditional`, extension `<li MayRequire="mandrake.rm.hugethings">` so the Rot loads without the
mod). Pinned by `HugeThings/selftest_hugethings_footprint.py`, which also fails if a new 6+ giant appears without
a row.

| def | name | drawn | trunk (w×d) | stem (click height) | blocked cells |
|---|---|---|---|---|---|
| AB_AgariluxPrime | grath elder | 20 | 4×4 | 8 | 15 |
| AB_DribblingCap | ruvvak weeper | 12 | 3×3 | 5 | 8 |
| RM_Nogtyl | brommok timber | 12 | 3×3 | 5 | 8 |
| RM_Arpeau | churrun mast | 10 | 2×2 | 5 | 3 |
| AB_ArbuscularMycorrhiza | bollusk trunk | 9 | 3×3 | 4 | 8 |
| AB_AgaricusDomeCap | skarrow dome | 7 | 3×2 | 3 | 5 |
| AB_GiantAgarilux | vokkun pillar | 6 | 2×2 | 3 | 3 |
| RM_PaleTree | quellan tree | 6 | 2×2 | 3 | 3 |
| AB_WitchesOyster | turrok shelf | 6 | 2×1 | 2 | 1 |

These are first guesses from the drawn widths and the descriptions (a "mast" and a "pillar" are thin, a "dome"
is low and wide, a "shelf" grows from a single foot), not from looking at the art. **They need a live look.**

## TitanicCreatures

TitanicCreatures now depends on Huge Things and opts every tiered race in (`HugeThingsApi.OptInPawn`, called from
its existing startup pass), so a titan can be clicked anywhere on its drawn body. Nothing moved out of it: its
footprint is Large Pawns' (via `LargePawnsBridge`, which is driven by Titanic's own tier ladder), and its wake,
roof avoidance, yield curve and corpse site are titan behaviour, not "huge" machinery. TitanicCreatures is not in
`ModsConfig.FULL.LATEST.xml` and no creature is wired to it, so the pawn hitbox has no live subject yet.

## Settings

`plantTrunkEnabled`, `plantSelectionEnabled`, `plantTrunkScale` (0.5–1.5×), `pawnHitboxEnabled`,
`pawnHitboxScale` (0.5–1.5×). All off is vanilla.

## Load order

After Harmony and Large Pawns, before `mandrake.rm.titaniccreatures` and `mandrake.rm.biomes`. Added to
`infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` directly before `mandrake.rm.biomes`.

## Open

- A live look at a Rot map: trunk sizes against the art, the click area, pawns walking under the caps.
- Removing Huge Things from a running save leaves `RM_HugeTrunkBlocker` Things the loader cannot resolve; it
  drops them with a load error. Turn `plantTrunkEnabled` off and save once before removing the mod.
