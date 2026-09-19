# TILE_STRUCTURE_REVIEW_SAVE_1 — 21 structure templates, one map, load and judge

Built live 2026-09-02 (BENCH) on the owner's instruction *"Save user review
options as save games"*, granularity settled by card: **one map, all options.**

## how to look at it

Load **`REVIEW_tile_structures_21`** (86 MB, Ash'karr, desert, 250×250, paused,
full mod list). Every one of the 21 authored rimplace templates is standing on
it, on a 48-cell grid. Pan; nothing is hidden and nothing is fogged.

| | x=6 | x=54 | x=102 | x=150 | x=198 |
|---|---|---|---|---|---|
| **z=6** | bantha_graveyard | broken_ring | cistern | dead_beacon | dwelling |
| **z=54** | glass_sea | hunting_lodge | imperial_waystation | junkers_cantina_block | junkers_depot |
| **z=102** | junkers_dwelling_cluster | junkers_scrapyard | krayt_graveyard | moisture_farm | monument |
| **z=150** | mynock_roost | nursery | oasis_shrine | podracer_wreck | rakatan_trace |
| **z=198** | toll_gap | | | | |

Each cell above is the plan's **origin corner**, not its centre: the structure
extends up and right from it.

## what is being asked

Keep / cut / rework, per structure. These are the content half of
`TILE_STRUCTURE_DESIGNS_1` — the engine that places them is proven
(`RIMPLACE_GENSTEP_LIVE_PROOF_1`), and none of them is wired to an Ash'karr tile
yet, so nothing here is live in the campaign.

## how they were built, and the two things worth knowing

Exported with `rimplace export <template> --out <path>` and replayed through
`GenStep_RimplacePlan`'s debug action. Sources: `design/Jawa/templates/*.lua`.

🔴 **Four templates render NOTHING at the default 16×12 canvas** —
`hunting_lodge`, `junkers_cantina_block`, `junkers_depot`, `junkers_scrapyard`
each refuse with a named reason (*"16x12 too small for a depot floor (>=10 wide)
plus a 6-row office"*) and emit a 2-line empty plan. They are on the map at
`--rect 0,0,40,40`. ⇒ **A template's canvas is part of its design and is not
recorded anywhere in the template.** Whatever wires these to a TileMutatorDef
must carry the rect, or four of the roster's best rooms silently generate as
bare ground. The refusal is good behaviour — `lint` names it — but the caller
has to be listening.

⚠️ **The debug action's `thingsSpawned` is a NET count and lies about emptiness.**
`moisture_farm` logged `thingsSpawned=3` and has **77 buildings** standing;
`monument` logged **-10**. Spawning into a cell destroys the plant under it, so
the delta says nothing about what landed. Verified all 21 by counting buildings
in each slot with `jawa/list_things` instead — every one is non-empty. (Counts
cap at 200 per call, so the larger ones are floors, not totals.)

## retention

Owner's ruling by card, 2026-09-02: **review saves stay until he says delete.**
Not auto-purged, not replaced by the next review. `SAVEGAME_PURGE_KEEP_B_1`'s
two keepers (`WORLDMAP_V1_original_b`, `gravship_scratch_b`) were backed up
before this save was written and verified untouched afterwards — `save_game`
has silently overwritten the current slot before (2026-08-24), and it did not
this time.
