# RimBridge traps

📁 **Which file am I in?** This catalogue holds **BRIDGE, CLIENT, BUILD and WORKFLOW** mistakes. If a RimWorld ENGINE method
reported success and changed nothing, you want `silent-failures.md` instead.

**First law — most entries are a special case of it: `success: true` means the tool RAN, not that the game CHANGED.**

**The entries marked 🔴 have each destroyed something real.** Read those before your first mutation, whatever else you skip.

The traps live in seven topic files under [traps/](traps/); every entry's title is listed below with its file, so a citation of
"traps.md" by title is one search away. Grep `references/traps/` for your verb. Symptom, cause, fix, **recurs when**; add a new trap
to its topic file. Promote into `SKILL.md` anything that should change default behaviour, and delete it here when you do.
Admission test and entry format: `skills/rimworld-modding/references/traps.md`.

## [Calling the bridge: parameter names, return shapes, the client, python.exe from WSL](traps/calling.md)

- 🔴 `python.exe` vs `python3` is a PER-SCRIPT choice, and the rule you carry points the wrong way half the time
- Client-call gotchas that cost real minutes — the exact spellings
- ⚠️ `jawa/inspect_string` takes `thingIds`, and a JSON LIST throws
- 🔑 Two things that worked first time, worth reaching for
- ⚠️ From WSL, `python.exe` dies on non-ASCII output
- `.get("children") or []` turns a FAILED call into "zero results"
- Three parameter names that produced fake catastrophes in one session — 2026-08-21, CHECK
- 🔴 The bridge SILENTLY DROPS any parameter a tool's schema does not declare
- An UNKNOWN call blocks the bridge client until reconciled

## [Loading, readiness, saves, maps and bridge time (ticks, pause)](traps/lifecycle.md)

- `token=NO` during a load is the game still loading, not the WSL bug
- 🔴 `Player.log` PERSISTS between runs — the readiness grep matches the LAST session
- ⚠️ An "ended" GameCondition still lists while the game is PAUSED
- 🔴 Bridge time is TICKS, and a step is not the step you asked for
- `rimworld/load_game_ready` is NOT a readiness poll
- A game can wedge on "Loading world." forever, and nothing on the bridge recovers it
- `rimworld/save_game` DOES honour a filename — under `saveName`
- `[JawaBench] ready` is LAZY — a missing line is not a failed deploy
- `rimworld/start_debug_game_ready` returns before the map is DRIVABLE
- 🔴 `rimworld/start_debug_game_ready` called with a `forcePause` modal on the stack killed the process
- 🔴 Closing the ESCAPE MENU resumes the game at its previous speed
- 🔴 `jawa/world_tile_map_generate`'s SECOND call at a DIFFERENT tile, same session, silently reuses the FIRST map
- `jawa/world_tile_map_generate` on an unfamiliar tile spawns that tile's own faction
- Standing up a bridge test site that survives save and a long chain
- GameComponentTick-driven async delivery never drains while PAUSED
- A swapped Greater Landforms recipe needs a full process restart
- A failed `jawa/set_current_map` does not stop later calls
- A "Playing" wait does not prove a map was regenerated or reloaded
- `status: game_loaded` is not proof the game loaded (zombie session)
- 0b. 🔴 Claim the bridge before you drive it — `rimflow bridge take`/`release`
- 1. Connect

## [Camera, rendering and screenshots](traps/camera.md)

- A screenshot taken while paused can be the previous frame
- You cannot photograph a stale mesh — moving the camera repaints it
- 🔴 Zooming below the engine's floor renders the whole map FLAT RED — and it looks exactly like catastrophic texture corruption
- `take_screenshot` names files by the SECOND, so a burst silently collapses to one file
- 🔴 `set_camera_zoom` takes `rootSize` (a NUMBER), not `zoom` (a string)
- 🔴 A modal dialog FREEZES the rendered frame and corrupts its colours
- `rimworld/screenshot_cell_rect` captures the SCREEN, top window and all
- `rimworld/jump_camera_to_pawn` — `pawnId` needs a `Thing_` prefix, and it is NOT animals
- 🔴 Whole-map Set-terrain-(rect) cascaded into a per-frame NRE storm and render corruption (2026-08-29)
- CORRECTION on the 2026-08-29 render-death: it is the WALL-MOUNT/shielded turret spawns, and it happened twice identically
- 🔴 A `world_tile_map_generate`'d map can render as a blank void — correct data, dead mesh
- `rimworld/screenshot_cell_rect` cannot frame a whole 250x250+ map, even with zoom extension on

## [Debug actions, designators, dialogs and clicks](traps/debug-actions-ui.md)

- An armed architect designator swallows every later click, and nothing on the bridge disarms it
- A jammed UI does NOT block the companion route
- 🔴 `search_debug_actions` walks the whole tree and FROZE the game — twice
- ⚠️ `rimworld/search_debug_actions` timed out at 30 s even on a 13-mod list
- `Actions\Spawn Pawn...` reports success and places nobody on a blocked cell
- `jawa/clear_ui` defaults do NOT close an open info card
- `rimworld/search_debug_actions` times out; the walk it exists to replace does not
- `visible: false` on a debug node is not "absent" — and `category` is not a tree level
- 🔴 `rimworld/search_debug_actions` WEDGES the bridge on a full mod list
- 🔑 A Dialog_NodeTree can absorb ALL input while ignoring its OWN buttons
- `select_pawn` and every `ToolMapForPawns` debug action require `IsColonist` — a bridge-spawned pawn, even faction PlayerColony, does not qualify
- ✅ ToolMap debug actions DO honour the bridge's x/z, even ones reading UI.MouseCell() (2026-09-02, BENCH)
- The debug menu's `Actions\Spawn Pawn...\<kindDef>` does not reliably spawn that kindDef — use `jawa/spawn_pawn`
- 🔴 `logCount: 0` from a debug action can mean LOGGING IS OFF, not "the action never ran"
- `rimworld/click_ui_target` can report success and do nothing — drive the real OS mouse
- VEF Dialog_NewFactionSpawning windows stack after a donor-free save load
- 4. Debug actions are the real surface

## [Pawns, factions, raids and combat](traps/pawns-factions.md)

- `jawa/list_pawns` returns `kind`, not `kindDef`
- 🔴 A parameter you PASS is not a parameter that SURVIVES — the raid faction is rewritten by ref
- ⚠️ Nothing on the bridge orders an ATTACK
- ⚠️ `jawa/list_pawns` cannot tell you what a pawn is HOLDING
- `jawa/destroy_batch` will not destroy pawns, and says so quietly
- Nothing reaches a `VehiclePawn`'s UI or its comps — four routes, four dead ends
- 🔴 `jawa/pawn_stats` — a stat that APPAREL moves must be read on a STRIPPED pawn
- 🔴 A raid census taken immediately after `jawa/fire_raid` reads ZERO — 2026-08-27, BUILD
- Doctrine-verify 2026-08-29: turret and explosion combat tests need three separate fixes, none of them the def
- 🔴 `jawa/set_faction_relation` CANNOT make a neutral faction hostile — 2026-08-27, BUILD
- 🔴 `jawa/pawn_get` nests everything in `pawns[0]` — 2026-08-27, BUILD
- 🔴 `jawa/set_faction_relation kind=Hostile` cannot make an ordinary faction hostile
- Killing a test pawn through the bridge — single damage calls lie
- Spawning pawns — `jawa/spawn_pawn` works; the `GenSpawn` routes NPE

## [The JawaBench companion: building, deploying, censusing, writing tools](traps/companion.md)

- Verifying a compiled-out tool: attribute names are UTF-8 blobs, not UTF-16 literals
- The companion DLL changes on every commit, by anyone, with no source change
- Fixed in the companion — one line each
- 🔴 `?.` guards the RESULT, not the CALL — the whole companion is dead at a main menu
- 🔴 Kill RimWorld BEFORE building the companion
- ⚠️ A docstring containing `jawa/world_*` made build.py report a phantom lost tool
- ⚠️ A bare `catch {}` in your own tool is the same bug you are hunting
- 🔴 A mod's own `[DebugAction]` methods do not surface through the bridge's debug-action tree
- JawaBench companion test grant expires
- Census the companion before you trust any `jawa/` call

## [Reading a result: defs, cells, instruments that are blind, denominators](traps/reading-results.md)

- `debugToolChanged: false` means nothing
- `ThingMaker.MakeThing` builds a wreck for any def whose framework wires it elsewhere
- The optimisation that made the number better made the picture wrong
- A field missing from the def dump is not proof the patch failed
- 🔴 A tool built to break a conflation can INHERIT that conflation from the API it reads
- A gate that greps "the source tree" greps the prose about it too
- Identify a thing by its accompanying signature, not by its own defName
- 🔴 An instrument can be blind to the exact branch that fails
- 🔴 The denominator is the population that EXERCISED the rule
- `rimbridge/list_logs` is a ring, not the log — a long session loses its startup lines
- An unasserted string-replace in a patch script is a silent no-op
- The instrument that settles "did my world edit land"
- `rimworld/get_ui_state` has no `currentMap` — do not ask it whether a map exists
- get_cell_info returns empty things + terrain None while the thing verifiably exists (2026-08-29)
- `get_cell_info` reports the FOUNDATION as `terrainDefName` (2026-09-02, BENCH)
- `jawa/get_defs` says "No def TYPE named 'X'" for a genuinely-loaded custom Def subclass
- `jawa/get_defs` cannot read everything a def holds
- `jawa/mod_settings_field` does not fire the mod's WriteSettings side effects
- FlowWorks reads that mislead
- `jawa/power_net` units
- Bridge and live-game traps
- Dumping the game process
