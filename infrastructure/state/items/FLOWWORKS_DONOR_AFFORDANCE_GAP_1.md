# FLOWWORKS_DONOR_AFFORDANCE_GAP_1

## Thin item — no spec existed

Queue title was the entire brief. No `## spec`/`## verify` section, no prose
file, before this one. Picked up per FOUNDRY doctrine for thin items: decided
the approach myself, recorded the reasoning below rather than blocking.

## What was measured (re-measured, not trusted from the title)

`mandrake.rm.flowworks` (`src/RimMandrake/FlowWorks/`) generates its liquid
TerrainDefs from a table in `Tools/generate_liquid_suite.py`, which unions
`<affordances>` straight off the FROZEN dump's post-patch `WaterShallow`/
`WaterDeep` leaves (dump `OFFICIAL-2026-08-29`, captured with donor mods
active). That union pulled in two donor-owned `TerrainAffordanceDef`s:

- `BMT_DeepWaterBridgeable` — **38** occurrences (real count; title said
  "x38", confirmed exact), 2 per file × 19 generated `Defs/LiquidTypes/
  TerrainDefs/RM_*.xml` files (one on the Shallow variant, one on the Deep
  variant). Donor: **`biomesteam.biomescore`** ("Biomes! Core"), label
  "Water of any depth" — read straight from the live `TerrainAffordanceDef`
  dump entry, not guessed.
- `TST_TerrainForMeditationStone` — **19** occurrences (title said "x19",
  confirmed exact), 1 per file (Shallow variant only). Donor:
  **`toastyman.moreritualseats`** ("More Ritual Seats"), label "natural
  terrain or shallow water".
- Both names also appear once each in the generator script's own docstring/
  comment prose (`generate_liquid_suite.py`) — not a live reference, not
  touched beyond updating that comment to describe the fix.
- `RM_Churnmud.xml` (hand-authored, not table-generated) carries neither
  string — confirmed by diffing the regen output against it (script leaves
  it untouched, as documented in its own header).

## Fix chosen: MayRequire on both, not an owned affordance

Both affordances are read from `TerrainAffordanceDef` dumps as things a
**donor mod's own building/recipe** checks for on terrain it might place
something on (a bridge buildable on any water depth; a meditation stone
placeable on shallow/natural terrain) — nothing FlowWorks ships checks for
either affordance itself. That rules out "own affordance": defining
`RM_DeepWaterBridgeable`/`RM_TerrainForMeditationStone` and repointing our
terrain at those would do *nothing* — the donor's own thing still checks for
its own affordance name specifically, so an RM_ substitute would neither
preserve the donor's placement behavior when it IS loaded, nor mean anything
to any of our own content. So: keep the exact donor defName (so Biomes! Core/
More Ritual Seats content still places correctly on our liquids when that
mod is present) and gate the `<li>` with `MayRequire="<donor packageId>"` so
it silently drops (no cross-reference resolution error, no missing-affordance
log spam) when the donor is absent — this is the established repo pattern
for a plain string `<li>` (confirmed prior art: `RM_OrganicScaldNative.xml`,
`RUT_RareTwilightCatches.xml`, `RM_FeverWood.xml`, etc., all gate individual
list `<li>` entries with `MayRequire` outside of a `<Patch>` file).

The `dbh_water` tag also union-carried from the same leaf (see the
generator's own comment) is untouched: `<tags>` is a plain string list with
no cross-reference resolution, so an absent donor never breaks load from a
tag — only `<affordances>` (a `List<TerrainAffordanceDef>`) can fail to
resolve. Out of scope for this item on that basis.

## What changed

- `src/RimMandrake/FlowWorks/Tools/generate_liquid_suite.py`: added a
  `DONOR_AFFORDANCE_MAYREQUIRE` map and wired `build_terrain_xml`'s
  `<affordances>` emission to wrap only those two known donor affordances in
  `MayRequire="<packageId>"`; updated the generated-file header comment to
  describe the gating. **Fixed at the generator, not by hand-editing the 19
  output files** — they carry "GENERATED … edit the table, never this file"
  and would silently regress to the bare donor reference on the next
  regeneration otherwise.
- Regenerated all 19 `Defs/LiquidTypes/TerrainDefs/RM_*.xml` files from the
  same frozen dump (`OFFICIAL-2026-08-29`) that originally produced them —
  diffed the regen output against the committed files first and confirmed
  the ONLY deltas were the header comment and the two affordance `<li>`
  lines gaining `MayRequire`; nothing else (tags, native overrides,
  modExtensions, render precedence) moved.

## Validation

`skills/rimworld-modding/scripts/validate_patch.py` against
`Defs/LiquidTypes/TerrainDefs/` (20 files, includes hand-authored
`RM_Churnmud.xml`):
- `--live` against the freshest capture (`2026-09-26T01-08-12Z`): **0
  errors, 0 warnings**.
- `--defs` against RimWorld's `Data`, Workshop content and local `Mods`
  folders (628 active mods, matched on disk): **0 errors, 0 warnings**.

## Not done / not in scope

No other donor-affordance leaks were found in FlowWorks beyond these two —
this item's grep was scoped to the two named strings per the brief, not a
sweep of every FlowWorks def for every possible donor cross-reference.
