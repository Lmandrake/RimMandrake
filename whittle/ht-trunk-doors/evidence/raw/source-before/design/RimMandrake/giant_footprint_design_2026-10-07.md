# Huge Things — ground footprints for huge plants, hitboxes for huge pawns (2026-10-07)

Item: `HUGE_THINGS_FOOTPRINT_1`. Mod: `src/RimMandrake/HugeThings` (`mandrake.rm.hugethings`, namespace
`RimMandrake.HugeThings`, free `RM_` tier, Harmony id `mandrake.rm.hugethings`).

## The rulings this builds

- **Option 1, picked by the owner 2026-10-07 07:17**: *"Solid trunk, open canopy — the stem blocks a small patch
  (~2×2 to 4×4 by species) so pawns path around it; clicking anywhere on the trunk selects it; you walk under the
  cap like a tree canopy."* His typed note: *"(1) and this may be related to another mod we have for enormous
  animals needing similar treatment"*.
- **Rework, decision taken by question card 2026-10-07 20:05 PDT:** the selection rect wraps the WHOLE drawn picture
  (cap, roots, stem) at its current growth, where the engine draws it; pawns are blocked wherever the art touches the
  ground (stem, roots, body base), measured from the art, never under an overhanging cap. This replaces the
  hand-sized trunk rect of the first build.
- **Cover, decision taken by question card 2026-10-07 20:38 PDT:** trunk cells give partial cover, and shots that hit
  them damage the giant itself, once per projectile / blast.
- Then, typed: *"This might be an extractable mod to handle "huge plants" and "huge animals" together?"* So this
  is its own standalone free mod, not a biome kit: The Rot opts in, and its titan half (Titanic Creatures, merged in 2026-10-07) opts every tiered race in.

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

**Draw transform (decompiled 1.6, RimSage).** `Plant.Print` draws a single-mesh plant as a SQUARE quad of side
`drawSize.x × visualSizeRange.LerpThroughRange(growth)`, centred on the cell plus a ±0.05 random x/z jitter, then
lifted so its bottom sits on the root cell's south edge (the lift compares with the visual size, not the side). It
mirrors the picture with a random `flipUv` and picks a `Graphic_Random` variant at random, all seeded by the cell.
`Source/Kernel/RM_HugeFootprintKernel.cs` holds the exact transform (with the methods cited); `CompHugeFootprint`
replays the seeded draws, so the footprint follows the very picture on screen.

**Footprint.** `HugeThings/measure_huge_plant_masks.py` measures every Rot plant drawn 6+ cells wide from its own
texture(s): the visible-pixel box, and the ground-contact cells (the base band of the silhouette, between the base's
own edges, so a cap wider than its base never counts). It writes `TheRot/Patches/RotGiants_HugeFootprint.xml`; a new
giant is one tool run. At runtime the contact cells are mirrored with `flipUv` and scaled with growth and the
settings multiplier, and a cell blocks only if its centre is inside the drawn picture. The root cell is never
blocked: an impassable edifice there would wipe the plant (`GenSpawn.SpawningWipes`, `BlocksPlanting`).

**Making it safe (GPT review 2026-10-07, `Transient/huge_things_bounds_2026-10-07/GPT_REVIEW.md`).**
`MapComponent_HugeFootprints` keeps a map-wide claim ledger (overlapping giants share cells; one blocker per cell;
order-independent) and closes a claimed cell only when it holds no pawn and no item (nothing is ever moved aside or
destroyed), is not protected (buildings, blueprints, frames, their interaction cells, door approaches, trees, other
giants), and closing it neither cuts a cell off from open ground nor cuts a giant's root off from every open
neighbour. A refused cell stays claimed and is retried. After load every blocker on the map is indexed and anything
unclaimed or duplicated is removed. Blockers do not carve zones (patched); stockpiles and sowing already refuse the
cell. Refreshes happen only when a plant's footprint signature changes (growth, harvest, graphic, settings), a few
per tick. A gravship landing that clears a giant's blocker or root removes that giant.

**Cover and damage.** Trunk cells are `fillPercent` 0.4 (reasoning in the def): partial cover, never full (rooms,
sight and roofs are unchanged). A shot that hits one is forwarded to the plant; an explosion reroutes through the
blast's own damaged-things list, so it hits the giant once however many cells it covers.

**Selection.** Vanilla already selects any Thing whose `CustomRectForSelector` contains the clicked cell
(`GenUI.ThingsUnderMouse`, listing the `WithCustomRectForSelector` group) and draws the selection brackets
around that rect. A Harmony postfix supplies it for opted-in defs (widening any rect another mod supplies): for a
plant, every cell the visible picture overlaps plus every blocked cell. Duplicate mouse candidates are removed, so
click cycling still reaches what lies under the canopy.

**Pawns.** A race carrying `RM_HugePawnExtension` is clicked by a rect of (its current life stage's drawSize ×
`hitboxFraction` (0.6) × settings scale), centred on the pawn, never smaller than its footprint. When Large Pawns
is loaded its `OccupiedRect` square is the footprint; our postfix runs at `Priority.Last` and only widens it.

**Why not the alternatives.** A plant def with `size > 1`: plants are registered, printed, sown and spread as
one cell; vanilla has no multi-cell plant. Patching `GenAdj.OccupiedRect` for the plant: region listers register
a thing over its OccupiedRect, so a rect that grows between register and deregister strands entries. A path-cost
patch: it would not refuse buildings or stop plants, and the 1.6 path grid is rebuilt from things anyway.

## Per-species footprints (The Rot)

Generated, not hand-tuned: see the header of `TheRot/Patches/RotGiants_HugeFootprint.xml` and
`Transient/huge_things_bounds_2026-10-07/REWORK.md` for the measured cell counts per variant. Pinned by
`HugeThings/selftest_hugethings_footprint.py` (which also re-runs the tool in `--check` mode), the kernel fuzz
`Utils/selftest_hugethings_fuzz.py` with its mutation set, and `Utils/selftest_hugethings_lint.py`.

## TitanicCreatures

Titanic Creatures merged into Huge Things on 2026-10-07 (owner: "Merge into one mod called Huge Things"); its code is
the titan half under `src/RimMandrake/HugeThings/Source/Titanic/`, and it opts every tiered race in (`HugeThingsApi.OptInPawn`, called from
its existing startup pass), so a titan can be clicked anywhere on its drawn body. Nothing moved out of it: its
footprint is Large Pawns' (via `LargePawnsBridge`, which is driven by Titanic's own tier ladder), and its wake,
roof avoidance, yield curve and corpse site are titan behaviour, not "huge" machinery. TitanicCreatures is not in
`ModsConfig.FULL.LATEST.xml` and no creature is wired to it, so the pawn hitbox has no live subject yet.

## Settings

`plantTrunkEnabled`, `plantSelectionEnabled`, `plantTrunkScale` (0.5–1.5×), `pawnHitboxEnabled`,
`pawnHitboxScale` (0.5–1.5×). All off is vanilla.

## Load order

After Harmony and Large Pawns, before `mandrake.rm.biomes` (Titanic Creatures has since merged into this mod). Added to
`infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` directly before `mandrake.rm.biomes`.

## Open

- A live look at a Rot map: footprints against the art, the click area, pawns walking under the caps, a shot into a
  trunk.
- Removing Huge Things from a running save leaves `RM_HugeTrunkBlocker` Things the loader cannot resolve; it
  drops them with a load error. Turn `plantTrunkEnabled` off and save once before removing the mod.
