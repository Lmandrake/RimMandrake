# StructureInjections — validation walk
subject: src/RimMandrake/StructureInjections
deps: none (loadAfter Ludeon.RimWorld only; ships no content of its own)
list: minimal
status-hint: The engine half of the promise/whisper structure program — GenStep_RimplacePlan replays a compiled rimplace BuildPlan onto a map at generation time (foundation → terrain → things, transmitters before connectors → runs → roof → pawns last). Species/campaign-agnostic; content packs (RimStarWars, RimUtinni) supply the GenStepDef wiring and compiled plans, so this mod alone ships zero Defs.

## must be true
- `GenStep_RimplacePlan.ApplyPlan` replays a parsed plan in the fixed order the live bridge path already proved necessary: CLEAR → FOUNDATION → TERRAIN → THING (transmitters/`EverTransmitsPower` first) → RUN → ROOF → PAWN (absolute last).
- A missing `planFile`, an unresolvable `modContentPack`, or an unparsable plan file each `Log.Error`s once and returns cleanly — no exception escapes to abort the rest of mapgen.
- A single bad plan ITEM (one bad THING/TERRAIN/RUN/PAWN line) is caught per-item (`RunItem`'s try/catch) and only that item is skipped — the rest of the plan still applies, and the failure is a `Log.Error` naming the phase and label.
- An unknown directive verb in the plan text logs exactly one `Log.Warning` per distinct unknown verb (not one per line).
- `CLEAR` mode=`"all"` additionally destroys any mineable rock `Building` in the rect and replaces its terrain with that rock ThingDef's own `leaveTerrain`/`naturalTerrain` (read from the def, never a hardcoded table); a rock declaring neither logs a `Log.Warning` and leaves terrain as-is.
- `PAWN` refuses `faction="player"` unconditionally (`Log.Error`, no spawn) — a mapgen template must never spawn a colonist.
- The two shipped debug actions (`RMInject` category: "Run plan: dwelling_test.txt", "Run plan: moisture_farm_test.txt") replay a real template shipped in `Templates/` and log a one-line summary (`[RMInjectDebug] RAN <path> ... thingsSpawned=<n>`).

## the walk
1. [L] Player.log after load contains no `"Config error in mandrake.rm.injections"` (the mod ships no Defs, so no def-load errors are possible; this only proves the DLL itself loaded without a Harmony/assembly error)
2. [D] Templates on disk: `StructureInjections/Templates/dwelling_test.txt` exists and its header comment matches `RimplacePlan.Parse`'s expected format (`# rimplace flat plan v2`, a `FOOTPRINT` line, then `TERRAIN`/`CLEAR`/etc. directive lines) — confirms the fixture the debug actions read is present and well-formed before any live test depends on it
3. [B] `rimworld/search_debug_actions {"query": "Run plan: dwelling_test.txt"}` → returns exactly one match in category `RMInject`, giving its stable path for step 4
4. [B] `rimworld/execute_debug_action {"path": "<path from step 3>", "x": <cell>, "z": <cell>}` on a quicktest map → Player.log gets one `[RMInjectDebug] RAN .../dwelling_test.txt clicked=... offset=... foundationCells=0 terrainCells=<n> things=<n> roofCells=<n> thingsBefore=<n> thingsAfter=<n> thingsSpawned=<n>` line with `thingsSpawned` > 0 (dwelling_test.txt's own header proves it): `thingsBefore`/`thingsAfter` is a NET count, so cross-check against jawa/list_things in step 5 per the review-sheets caveat that a placement log's net count can go negative when a build clears plants — confirm the sign is right, not just that the line printed
5. [B] `jawa/list_things {"defName": "StrawMatting", "rect": "<footprint rect around the clicked cell>"}` → confirms the terrain cells the log claimed were actually set (terrain isn't a `Thing`, so read it via terrain-grid state, not `list_things`, for the STRAWMATTING count specifically — use `jawa/get_cell_info` per-cell or the terrain tool instead if `list_things` returns nothing for a TerrainDef, since terrain is not in the thing grid)
6. [D] repeat step 4 with a deliberately corrupted copy of the template (one line's ThingDef renamed to a defName that does not exist) placed at a scratch path, replayed via the same debug action → Player.log shows exactly one `Log.Error` naming the bad defName and phase, and every OTHER item in the plan still applied (proves the per-item catch in `RunItem`, not just that errors are logged)

[S] none — this is pure engine/ordering proof; the visual "does the resulting structure look right" pass belongs to whichever content pack's LandmarkDef/TileMutatorDef wiring actually ships a real plan (MOD_HUMAN_EXPLORATION_PASS_1, not here).
