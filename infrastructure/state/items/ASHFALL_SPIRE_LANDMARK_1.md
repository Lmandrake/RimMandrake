# ASHFALL_SPIRE_LANDMARK_1 — The Spire landmark, Ashfall Research Base site

## 2026-09-12 (FOUNDRY) — mechanism-checked live; blocked, needs real content authoring, not a bare bridge placement

Read `design/Jawa/worldbuilding/ashfall_research_base.md` first (no item file
existed before this note). Candidate site: the 3 donor tiles the doc itself
cites (lat -2.0/-0.7/-1.4, lon 63.1/63.2/64.3 -> world tiles **4299, 9158,
9159**, all `AB_OcularForest`/Contagion per `CONTAGION_BIOME_PLACEMENT_1`'s
already-painted 24-tile Ashfall Range set). Picked **tile 4299** (highest,
2190m) as the peak site.

**Live-checked, not guessed** (`jawa/world_tile_get` on the loaded
`CANONICAL_ASHKARR_2026-09-09` save, 592 mods, no crash — see
`BUILDING_THEFT_HAULER_1`'s sibling note tonight for the thingClass fix that
made this load possible at all): all three candidate tiles are
**`hilliness: Impassable`** (confirmed against the engine's own enum via the
bridge, not the CSV's ambiguous encoding), unlike every existing NPC
settlement in this save (`Mountainous`, checked against 3 Empire settlements
as a control). `jawa/tile_settleable` independently refuses tile 4299 with
"You cannot land on impassable mountains."

**Tried, then rolled back**: `jawa/world_objects_add {def:Settlement,
tile:4299, faction:RUT_Jawa_AscendantHelix, name:"The Spire"}` succeeds
(the tool does not enforce `tile_settleable`) — but this is the ONLY
settlement in the whole save that would sit on Impassable terrain, and
nothing here proves a caravan or quest could actually generate a map on it.
Removed again via `jawa/world_objects_remove` + `world_commit` before this
session's own save-write (tile 4299 confirmed clean afterward, 0 residual
settlements at 4299/9158/9159) — this was a probe, not a shipped state.

**Read `RimWorld/LandmarkDef.cs` via RimSage before trying the LandmarkDef
route instead** (the doc's own vocabulary: "the world-map landmark write"):
two hard blockers, not a styling choice —
1. `LandmarkDef.IsValidTile` returns **false unconditionally** when
   `tile.hilliness == Hilliness.Impassable` — the exact engine method that
   decides whether a landmark may exist there. `world_landmarks_set`'s own
   `isValidTile` is evaluated after the write and never blocks it (known
   trap, `mutators-and-objects.md`), so I could still force a landmark onto
   4299, but the game's own rule for whether one BELONGS there says no.
2. `LandmarkDef.ConfigErrors()` requires **at least one `mutatorChances`
   entry with `chance >= 1`** — a bare/empty marker LandmarkDef is not a
   legal def; it would log a config error on every future load, forever.
   A real LandmarkDef here means committing to at least one guaranteed
   mutator roll on the tile (with the AddLandmark-displaces-existing-
   mutators trap this file already knows about for `sw_Sarlacc`), which is
   a real content decision (what mutator represents "a fixed research
   installation," on an ALREADY-painted Contagion tile), not a placement
   detail.
3. Landmark display names come from `nameMaker` (a `RulePackDef`), not from
   any bridge-settable field — getting the owner's exact fixed name **"The
   Spire"** (not a randomized one like the `sw_Sarlacc` placements got:
   "Hehieran Sarlacc", "Sarlacc Pit", "The Sarlacc") needs a purpose-built
   one-rule RulePackDef, again real authoring, not a bridge call.

**Verdict**: "place The Spire landmark" is not a bare world-edit — it needs a
new `RUT_`-tier LandmarkDef (icon texture, one mutator, a fixed-output
nameMaker) authored and validated like any other def, same shape as
`dungeons_arc_spec.md`'s precedent (`RUT_Slough_GelatinousBreach` for V5) —
and per the design doc's own "no defNames are minted in this doc," that
authoring pass was never done. Doing it live under tonight's time budget
risked either a permanent ConfigError (empty mutatorChances) or an
unreviewed mutator/biome change on an already-ruled Contagion tile. Setting
`needs=offline` rather than closing: whoever authors the LandmarkDef (icon +
nameMaker + one deliberate mutator) can place and read it back in minutes
once it exists; nothing here blocks the DUNGEON shell itself, which the
design doc already defers ("its campaign function may not proceed" — that
was never in this item's scope).

**World state**: unchanged from before this pass — tile 4299/9158/9159
carry no settlement, no landmark, no mutator changes. Nothing here needs
undoing before the next save.

## spec (inherited from the design doc, no formal item file existed before tonight)
Place a landmark named "The Spire" at the Ashfall Research Base site (one of
CONTAGION_BIOME_PLACEMENT_1's Ashfall Range tiles, `design/Jawa/worldbuilding/ashfall_research_base.md`
§3/§6). Display register: "a mysterious thin black needle of a building with
a disc landing near the top, visible only occasionally due to the
atmospheric turbulence over the Scald's mountains" (owner, verbatim). Dungeon
shell/KCSG content and campaign function are explicitly NOT this item's
scope (owner: "Not ready to resolve this yet").

## verify
The landmark reads back from the live world at the chosen tile via
`jawa/world_landmarks_get`, carrying the fixed name "The Spire" (not a
randomized nameMaker output), with `world_tile_get` before/after confirming
no mutator or biome change beyond what the new LandmarkDef's own mutator
deliberately adds.

## criteria
A real, config-error-free `RUT_`-tier LandmarkDef exists (icon, one
guaranteed mutator, one-rule nameMaker), is placed once on a live-checked
Ashfall Range Contagion tile, and reads back with the exact name "The
Spire". No dungeon content, no campaign-function wiring.
