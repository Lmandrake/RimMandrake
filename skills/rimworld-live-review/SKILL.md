---
name: rimworld-live-review
description: >-
  Stage a live RimWorld scene through the bridge so a human can LOOK at it and
  judge it — a biome's plant density and colour, a creature roster's art, a
  built structure or gravship, a xenotype line-up — and capture screenshots (and
  keeper savegames) that show the subject cleanly. Use this whenever the task is
  "show me / let me see / screenshot / review in game / does this look right /
  walk this biome / check the art in world", whenever staging pawns, animals,
  structures or terrain for a picture, and above all when a review shot keeps
  coming out wrong — subjects spawned in rock, everything dying between calls, a
  midnight-dark or fogged frame, the camera on the wrong map, the shot framed on
  the colony instead of the subject. This is the "make it look right and capture
  it" skill; rimworld-debug-testing is the separate "does the mechanism work"
  skill. Reach for this before hand-rolling spawn/screenshot bridge calls.
---

# Live review: stage it clean, then look

A review shot answers one question — *does this look right?* A good shot shows the subject and nothing that fights the
subject. In every recurring failure, the subject was **obscured or destroyed** before the
shutter. Four examples:

- the subject spawned inside rock;
- a raid killed the subject between two bridge calls;
- fog or midnight hid the subject;
- the camera stayed on the colony, so the subject was out of frame.

So the whole method is: **make the scene clean and still, then capture.**

This skill drives the live game. Read `skills/rimbridge/SKILL.md` for the protocol. Before your first write, read
`skills/rimbridge/references/silent-failures.md`. `success:true` never proves that the game changed. That rule matters
twice as much here, because the proof is a picture.

🔴 **From WSL, bridge scripts run under `python.exe`, not `python3`**, because the bridge binds Windows loopback.
Screenshots land in `.../RimWorld by Ludeon Studios/Screenshots/`. Copy them to `Transient/` and view them. **A
screenshot is a cache, not an observation**, until you have looked at it.

🔴 **No walkthrough map or review save reaches him until you have looked at every station** (owner, 2026-10-22:
*"No walkthrough maps unless you've zoomed in on every station and stared at the screenshot for potential issues
related to the mod, ok? Typical graphics problems, connections, making sure each graphic objects is recognizable as
what it is"*). At each station:

1. Take a tight zoomed capture (`screenshot_cell_rect`, rootSize ~6) and Read it.
2. Check what the mod draws:
   - Does each part render?
   - Does every connection meet (hose into reel, pipe into fitting)?
   - Does anything run under a building, or draw over a thing that belongs on top of it?
   - Is each object recognisable as what it is?
3. Fix or remove a broken station. Then tell him in one line what you caught.

On the 2026-10-22 FlowWorks walk, checks of the framing alone missed exactly these faults. A naive Opus judge may do the
staring. The rule is `standing_rulings.md` §Nothing reaches the owner unread.

## This vs a review sheet — and why neither verdict is final

A quick game load on a SMALL mod list, staged with this skill, is a standing review tier, not a fallback (owner
ruling, first art walk, 2026-09-14).

- Use the live scene for questions of zoom level and scale. There the live scene beats a sheet. The pattern: a trimmed
  list (MINIMAL + content mods + overrides), a quicktest map, a spawn of each batch, a walk.
- Use a sheet for a side-by-side comparison and for a check against canon.

⚠️ **Neither verdict is durable on its own.** The owner said "call those done" of creatures that he saw in game. When he
saw the same creatures on a sheet, he reversed that verdict to rerender. Bolotaur and Gualaar both went that way in one
sitting (2026-09-15). So a shot that reads fine in the moment does not close the review. Before you call a batch of
creatures finished, serve the sheet too.

More traps for this section: [references/traps.md](references/traps.md) § This vs a review sheet — and why neither verdict is final.

## 🔴 Python is fast and cheap; you are slow and expensive — push work into the script

The bridge answers Python in milliseconds. Each call that *you* issue as the model is a slow, costly round trip. So
**do not hand-drive the bridge call-by-call.**

- Put the sequence into `stage_review.py`, or into a script beside it, with a flag for your case.
- Run the script once. Spend your turn on the result: LOOK at it.
- A biome review is ~50 bridge calls. Those calls make one Python invocation and one screenshot to read, not fifty turns
  of yours.

**You are authorized to grow these scripts whenever it saves round trips** (owner, 2026-09-17). You may add options and
whole new capabilities, on two conditions:

1. Document the flag in the `--help` text or docstring of the script.
2. Record the flag here in the skill.

For example, build a new `--two-pass`, a `--biome` preset, or a batch mode that walks a list of biomes end-to-end.
Do not crank such work by hand. The signal is this: you are about to issue the same three bridge calls a third time. Put
them behind a flag instead.

**A scene for a mechanism mod comes from the mod's own proof script**, never staged by hand. Use the script's
`prepare_site`, its dry plot (a plot with no water source beside it) and its control cases. The reason: a hand-staged
scene shows something that the proof never reproduces. Then the owner judges a scene that nobody can rebuild.

- Validate the site in the script first (water/source margin:
  `skills/live-debugging-proof-harness/references/lightspeed-authoring.md` §4).
- Before the capture, pause, verify the pause, and read the state of the subject back.
- To capture pawns after you step time, use `settled_shot` (`rimbench/shotsettle.py`, §2).

## Minimum Force (owner, 2026-11-23)

> **Use the least force that makes a scene affordable and reliable, and that leaves to the mod every decision the scene
> claims to test.** Whatever the force steps past is outside that scene's evidence.

The ladder, from most force to least, for "a raider crosses a covered pit":

1. Teleport the raider onto the cover.
2. Give the raider a path over the cover.
3. Build a corridor with no other way, and put bait beyond the pit.
4. Put a ring of pits round a base, and let a natural raid come.

Say which step the scene uses, and in one line why not a lighter one. Trying every lighter step first is not required. A
scene that shows a mechanism says which of the mod's decisions its force steps past. The scene shows nothing about those
decisions. The kinds of live scene and the seven outcomes of a run: `skills/live-debugging-proof-harness/SKILL.md` §The
scene contract.

## The helper does the whole clean-stage in one call

`src/RimMandrake/Utils/stage_review.py` composes every step below, with the read-backs and the traps already handled.
Prefer the helper. Make manual calls only when a scene needs something that the helper does not cover.

```bash
# art review — animals SPACED in a legible row on verified grass, shot + save:
python.exe src/RimMandrake/Utils/stage_review.py --map 1 \
    --kill-hostiles --clear chunks,filth \
    --spawn "RUT_FireHawk:1,AA_Barbslinger:1,Anooba:1,Gizka:1" \
    --at 40,235 --spread 12 --terrain RM_FE_Ground --layout grid \
    --frame 30,228,160,16 --shot pyre_artgrid --save PYRELANDS_REVIEW

# ruled default capture in ONE call — midday + clear shot THEN signature-weather shot:
python.exe src/RimMandrake/Utils/stage_review.py --map 1 \
    --kill-hostiles --clear chunks,filth \
    --spawn "RUT_FireHawk:1,Anooba:1,Gizka:1" --at 40,235 --spread 12 \
    --terrain RM_FE_Ground --daylight \
    --frame 30,228,160,16 --shot pyre --two-pass RM_FE_Weather_AshFall \
    --save PYRELANDS_REVIEW
#   -> pyre_clear.png (Clear, 10-14 h) + pyre_ashfall.png (signature), one invocation
```

`--layout` is the most important framing choice that you make, because it picks art or mood:

- `--layout grid` (the default) puts each kind on its own verified-open cell. The grid is **legible for art review**.
- `--layout cluster` piles the counts around one point. The cluster gives the mood of a dense herd, but **tall pawns
  overlap and hide each other, so never use it to judge one creature's art** (owner, 2026-09-17).

The sections below say *why* each step is there. Read them to understand the flags, and to stage by hand when the
helper falls short.

## 1. Clean first — kill hostiles, then clear the ground

**Order matters: remove ALL hostiles BEFORE spawning subjects.** A generated map often arrives mid-raid, with dozens of
raiders. One quicktest measured 118 across Pirate + PirateYttakin, and "Raid: The Ohnaka Gang" filled the
alert column. Suppose that you spawn subjects into a raid and time moves at all. Then the raiders kill
or scatter the subjects before you frame them. `--kill-hostiles` sweeps every hostile pawn, up to six
rounds, and reports how many are left.

🔴 **The kill mechanism, three traps deep** (each trap cost real shots):

- Select hostiles by the **`hostile` boolean** from `jawa/list_pawns`, never by a guess at the faction name. No substring
  catches Pirate *and* PirateYttakin *and* Ohnaka Gang.
- The pawn id field is **`id`, not `thingId`**. `thingId` comes back null. Pass `id`.
- `T: Damage To Death` targets **player colonists** only. On a hostile, the call reports success and does nothing. Use
  `jawa/damage {thingId:<the id>, damageDef:"Bomb", amount:9999}`, which works on any faction. The parameter has the name
  `thingId`, but it wants the `id`.

**Sweep until the count is stable at 0.** A mechanoid survives one bomb. Read the count back. Do not trust one pass.

The sweep never touches player colonists (your map anchor, §3) or wild animals.

Then clear what the subject can collide with:

- **Rosters and biomes:** `--clear chunks,filth` removes loose rock and ash drifts, which clutter the frame. `chunks`
  destroys rock and slag chunks only, with a read-back. A chunk that shares its cell with another item stays, and the
  report counts it (`left_beside_items`). `items` destroys every loose item, chunks included.
  `src/RimMandrake/Utils/rimbench/clear_chunks.py` is the standalone version for the whole map. That version also takes
  an item that shares a cell with a chunk.
- **Structures and gravships:** first run `--clear buildings,chunks` over the build rect. The map's own ruins and rock
  **interact** with what you place. A foundation refuses to go on an existing floor. Walls merge. A designator queues
  against existing work. So a structure test on ground that is not clear tests the collision, not your build. Clear the
  footprint AND a margin around it.

`--clear` takes `chunks,filth,buildings,plants,items`. `--clear-rect x,z,w,h` limits the clear to a rect (default: the
whole map). A clear of buildings or plants is destructive. For a structure test that is the purpose, but say that you did
it.

More traps for this section: [references/traps.md](references/traps.md) § 1. Clean first — kill hostiles, then clear the ground.

## 2. Pause discipline — still scenes don't die

**Stage and shoot PAUSED.** While you read a screenshot, an unpaused map moves on. Combat resolves, animals wander out of
frame, plants age and daylight passes. Each bridge call is a separate round trip, so real frames pass *between* your spawn
and your capture. That gap explains "I spawned twelve and the census shows three". The missing animals died or fled in the
seconds between the calls.

- Call `set_time_speed 0`, then **verify** the pause: read `ticksGame` twice. The call can report a speed and leave the
  game paused, or the opposite. The helper's `pause()` returns whether the ticks held.
- **Unpause only in bounded bursts, for a stated reason**, and re-pause before the capture. Such reasons are: let plants
  grow in, let weather settle, let ash drifts accumulate (§5).
- Prefer a stepped advance to an unpause. `B.ticks(n)` / `jawa/safe_advance` runs many ticks per frame inside a frame
  budget.
- A raw `step_game_ticks` is one tick per frame. Keep it in ≤2000-tick chunks, because a bigger step frame-times out.
- A timeout is fatal to the connection. Open a fresh socket and read the state back. Never retry on the dead connection.
- Before you advance more than 30,000 ticks, read `design/RimMandrake/debug_process.md` § "A long clock advance".
- After you step time on a paused game, pawns are still drawn at their old spots. Call `settled_shot`
  (`src/RimMandrake/Utils/rimbench/shotsettle.py`) for the capture. The function pauses, snaps every pawn to its real
  cell with `jawa/settle_tweens`, shoots, and proves that no tick passed.

## 3. Keep the map alive — colonists make it a home map

The engine **culls a non-home settlement map once you step time**. Then the scene that you stepped for daylight or drifts
is gone. `jawa/set_current_map` then refuses with "No loaded map has uniqueID N". Two things that you can arrange
keep the map (`Settlement.ShouldRemoveMapNow` holds the full list):

- **The settlement belongs to the player.** Then the map is a home map. On a tile with no map parent
  (a settlement, site or camp), `jawa/world_tile_map_generate` by default makes a settlement of the player (parameter
  `faction`). On a tile
  that already has a **Settlement** of another faction, the map is not a home map. Read `parentFaction` in the reply.
- **A living colonist stands on the map.** The fix for a non-home map (owner, 2026-09-17) is to **spawn a few colonists
  on it**: `jawa/spawn_pawn faction:"PlayerColony"`. While one lives, the engine does not cull the map. Then you can step
  and pause freely. The map does not become a home map, whatever the heading of this section says.

🔴 **Three more ways that a generated settlement map bites in one sitting:**

- The defenders include **turrets**. Before you call hostiles cleared, sweep `BuildingArtificial` by faction too, not just
  pawns.
- A **dead colonist** does not keep a non-home map. The engine culls the map when its last colonist has died, as it culls
  an empty one. A downed colonist keeps the map only while the colonist lives.
- The pause is what keeps the map alive between your calls. So keep the game paused except while you step time on
  purpose (2026-09-18).

⚠️ **If a map was already culled/orphaned before you noticed** (2026-09-14):

- **Before** you step time again, re-faction the Settlement object itself with `jawa/world_objects_set` (`ids=`,
  `defName: PlayerColony`).
- Or fall back to a save and a load. A reload is the reliable way to make an orphaned map current again.

Two calls for the map and its subjects:

- `jawa/set_current_map {mapId}` switches `Find.CurrentMap` AND hides the world layer. So screenshots and current-map
  tools (spawn, list_pawns, take_screenshot) act on the right map. The call refuses an unknown id and prints the loaded
  maps. Read that list; do not guess.
- Spawn **subjects** wild: `faction:"none"` (no combat, no fleeing). `faction:""` errors. The default is a hostile
  faction, which gets your subjects killed near a colony.

🔴 **A freshly-generated map can render stale, and that alone can invalidate a verdict.**
`jawa/world_tile_map_generate` now finalizes the map itself: regions, rooms and draw meshes. Read
`mapFinalize.failedSteps` in its reply. Did a step fail, or did another tool change the map after that call? Then call
`jawa/map_commit` before you judge a picture (`BRIDGE_MAPGEN_STALE_FINALIZE_1`).

🔴 **And some generated maps render PURE BLACK, with no known bridge fix** (2026-09-19).

- Two repairs did not help: `jawa/refresh_rect` over the whole map + `map_commit`, and the vanilla debug action
  `Actions\Regen All Map Mesh Sections`.
- The cause is not fog and not night. The control that proves it: on the same connection, switch to a map that you
  entered normally (`jawa/set_current_map`). That map renders fine seconds later.
- `jawa/colony_found` does **not** generate a map; its own response says so. So no known bridge route enters a
  tile-generated map the way a player does. `jawa/settlement_attack` (only in a companion DLL that was built
  with `build.py --gm`) sends a caravan into another faction's settlement. Whether a map entered that way renders is UNMEASURED.
- Is the bar of a review "see it on screen", on a map that the bridge authored from a tile? If the map renders black,
  the review is **blocked** until a companion tool takes that entry path. Say so. Do not ship a black screenshot as a
  negative result.

## 4. Placement — verify every cell is open and the right terrain

**A subject drawn inside rock, water or a wall is the number-one review defect.** Never spawn across a fixed row that can
cross gravel, rock or buildings. Such a row once put animals on bare stone. Instead:

- **Verify each target cell** with `get_cell_info`. The cell holds no water and no building or wall. For a biome, the cell
  is on the terrain family that you expect (`--terrain RM_FE_Ground`).
- In RimWorld the *plants* are the grass, not the terrain. Dense grass grows on soil terrain. So for a "lush grass" shot,
  spawn on the soil rows.
- **grid layout** places each kind on the next verified-open cell, `--spread` apart.
- **cluster layout** spawns all counts at one verified anchor, and the engine pops them into adjacent free cells. The
  cluster is good for a herd and bad for art (§ the helper).

**Make them face the camera.** A subject faces wherever the sim last pointed it. Unless you turn the subjects, an art shot
photographs backs and flanks.

- `--face south` (the helper) calls `jawa/set_pawn_rotation {dir:"south", lockRotation:true}` on every pawn. **South is
  the front view toward the camera.** The call also locks the pose (`debugRotLocked`), so the pawns hold it while you
  frame.
- north, east and west are there for a specific angle.
- If you draft and move a colonist, the colonist turns too. `set_pawn_rotation` is the direct control, and it works on
  wild animals.
- A downed or laying pawn does not visibly turn. Stand the pawn up first.

More traps for this section: [references/traps.md](references/traps.md) § 4. Placement — verify every cell is open and the right terrain.

## 5. The shot — light, weather, fog, UI, frame

The default capture, owner-ruled: **midday + clear first, then the biome's signature weather.** The clear midday pass
shows true colour and density. The signature pass (ashfall, blackrain, cinderfall…) shows the mood that defines the
biome.

- **Time of day:** shoot at midday so that colour reads. A dawn or dusk shot reads muddy and undersells density.
  `--daylight` reads the local hour (`jawa/glow_at`), jumps the clock forward to 10–14 h and reads the hour back. An
  hour that it cannot read stops the run. The jump simulates nothing, so it needs no safe colony and culls no map. But
  filth and loose ash age by the jump (under a day; §8b). `--two-pass` does the same without the flag.
- **Weather:** `jawa/weather_set {weather, lockWeather:true}` forces the weather and holds it. A new weather is fully in
  after 4,000 ticks. `--two-pass` forces `Clear` and runs those ticks before its `_clear` shot. With `--two-pass`,
  `--weather X` names the weather of that first shot.
  `--settle N` runs N ticks, so drifts and effects build before the shutter.
- **Fog:** first run `jawa/set_fog unfog` on the frame. **A subject in unvisited fog photographs as black nothing.**
- **UI:** call `jawa/clear_ui` before every shot. The dev log window sits exactly where the camera centres. That window
  has eaten many shots.
- **Frame:** `rimworld/frame_cell_rect {x,z,width,height,paddingCells}` zooms to fit a rect. The call has been seen
  not to move the camera on its own. So the helper jumps to the rect centre first, then frames, then reads
  `get_camera_state` back.
- 🔴 **`frame_cell_rect` does not zoom IN past the current zoom.** On the owner's full list the root size 24 gives a
  ~149-cell-wide view. So a shot "framed on X, only X on screen" holds half the map. Call `set_camera_zoom` with the
  `sizeRange.min` value first, then frame. An 11-mod test list hid this fault, because its camera mod starts zoomed in
  (2026-10-11).
- **Don't over-zoom on a pawn.** `jump_camera_to_cell` + `rootSize: 11` (the "Closest" zoom) draws any
  forbidden-item icon at full-screen size. The icon and its red forbidden-X overlay fill the frame instead of the animal.
  Before you shoot a specific pawn, back off to `rootSize` ~14–18 (2026-09-19).
- **Avoid structures in a biome/art frame.** A colony or ruin in shot pulls the eye and changes the read. Frame a patch
  away from built areas. For that reason the helper spawns the roster in the open ground that you chose, not where the
  colony landed.
- **take_screenshot appends `.png` itself.** Pass a bare name, or you get `x.png.png`.
- ⚠️ **`rimworld/take_screenshot` silently ignores `x`/`z`/`zoom`.** The call records those args and does not refuse them.
  So three shots asked for at different framings can come out identical. Frame with a camera tool (`frame_cell_rect` /
  `jump_camera_to_cell`) FIRST, then shoot. Look at the PNG before you send it, not just at the tool's "success"
  (2026-09-18).
- ⚠️ **`rimworld/clear_log` empties the debug log but does NOT close the window.** If that window is in the frame, close
  it with `jawa/window_list_close typeName=EditWindow_Log`.
- **To face a pawn at the camera, use `jawa/set_pawn_rotation dir:south lockRotation:true`** (§4). Most vanilla animals
  are static when idle. Only a creature that carries `PawnRenderNodeProperties_Spastic` (the Toughspike template) jiggles
  an appendage on its own when idle (2026-09-17).

More traps for this section: [references/traps.md](references/traps.md) § 5. The shot — light, weather, fog, UI, frame.

## 5a. When a colonist must DO a job for the test

Some tests need a pawn to *perform* an action: build a structure, operate a bench, haul, plant. When the pawn cannot reach
the job or is unfit to work, RimWorld silently never does the job. So a "nothing happened" result is usually
the pawn, not the mechanism. The owner's checklist, 2026-09-17:

- **Put a HEALTHY colonist right next to the job.** With distance and a partial path, the job never starts.
  `prep_worker()` in `stage_review.py` spawns a fresh `PlayerColony` colonist at the job cell, so no distant
  colonist has to walk over.
- **Fully satisfy the pawn**: food, rest, recreation, mood and health. A hungry, exhausted or mentally-breaking pawn
  abandons the job or collapses in the middle of the test. Before you let time run, top up every need (`jawa/pawn_need`
  to 1.0, `pawn_refresh_needs`) and heal the pawn (`jawa/pawn_health healAll`).
- **Remove all hostiles for the duration** (§1). A raid interrupts the job and kills your worker. The clear-first rule of
  §1 has the same reason.
- Then unpause in a bounded burst (§2) to let the job resolve, and re-pause to inspect. Confirm the *result* of the job
  (the built thing, the moved item), not that the pawn was "working".

## 6. Save one keeper per biome

The owner's standing ruling is "review options as savegames". After you stage a biome well, **save it** (`--save <NAME>`).
Then he can walk it, zoom it and read tooltips himself later.

🔴 **Verify the save landed**: stat the named file in the Saves folder. `rimworld/save_game` has written the CURRENT slot
instead of the given name. So if you trust the returned path, you can overwrite a keeper. The helper stats
`Saves/<name>.rws` and reports its size.

Keepers stay until the owner says delete. Name them per biome (`PYRELANDS_REVIEW`, `SCALD_REVIEW`, …).

## 7. Reset cadence for a biome-by-biome campaign

When you test every biome in turn, the reset rule is simple (owner, 2026-09-17):

- **If you changed files** (a def, a biome XML, an assembly): the running game holds the old defs in memory. A deploy to
  the Mods folder is not enough on its own. **Restart the game**, so that it parses the files at startup, then re-stage.
  Use `skills/rimworld-load-round` for the restart. Load the mod's small list: `modset_builder.py --tier <tier> --apply`
  (run while the game is down). The tier is in `design/concepts/<Mod>/version/small_list.json`. If the mod has no such
  file, choose a tier from `modset_builder.py --list`.
- **If you changed nothing on disk** (you only move to the next biome): **reload or regenerate**. Either re-tile the
  current tile to the next biome and `world_tile_map_generate` a fresh map, or load the pre-staging save. No restart is
  necessary.
- The **pre-staging save** is a save that you make yourself, on the mod list that runs now, before you stage anything on
  the map. No save of that kind ships with this skill. Make it with `rimworld/save_game` under a name of your own, and
  verify that it landed (§6). Load it with `python.exe src/RimMandrake/Utils/live_site.py --save <NAME>`. A keeper (§6)
  holds a staged scene, so it is not a pre-staging save.
- **Reload to reset.** A staged map accumulates test damage, dead raiders and moved pawns. To start the next biome clean,
  load the pre-staging save or regenerate the map. **Do NOT nurse the map's contents**, because the map is scratch. When
  a step warns about "losing items from the game", ignore the warning: the map is a throwaway review map, and you reload
  to reset anyway.
- Never write over a canonical world save (`infrastructure/state/CANONICAL_SAVE.md`). Every other save is disposable, but
  a save that waits for his review stays until he rules. Always say which map a shot came from.

## 8. The scripts this composes

| script | does |
|---|---|
| `stage_review.py` | the one-shot clean-stage this skill is built around |
| `stage_xenotype_grid.py` | the naked-races grid: pawns of each XenotypeDef side by side (`--per`, default 3), stripped, faced south |
| `rimbridge_client.py` | connection (`resolve_endpoint` finds host/port/token: the caller's value, the environment, then Player.log or the named game's own, then a default) |
| `rimbridge_lineup.py` | spawn one of every pawn kind in a framed grid — the roster line-up |
| `rimbench/clear_chunks.py` | clear every loose chunk, read-back proven |
| `rimbench/shotsettle.py` | `settled_shot()`: a paused capture that draws each pawn at its real cell (§2) |
| `rimbench/scatter.py`, `place.py` | organic distribution maths for natural-looking placement |
| `rimbench/render_terrain.py` | offline terrain→PNG when you want a map render, not a screenshot |
| `game_focus.py` | `preflight()` — turn on Run-in-background or every game call times out |
| `system_screenshot.py` | OS-level desktop capture (`python.exe`), for when you need the whole screen incl. dialogs, not the game's own shot |
| `modset_builder.py` | `--tier <tier> --apply` swaps to a small list before a load; leave the list on the tier that serves your work |

More traps for this section: [references/traps.md](references/traps.md) § 8. The scripts this composes.

## 8a. Four live param/name traps this cost, 2026-09-20

Each of the four returned something that looked like progress, and each wasted a staging pass.

- 🔴 **There is no `get_cell_info` under `jawa/`.** The tool is **`rimworld/get_cell_info`**.
  **`rimworld/get_cells_info`** takes a rect of up to 1024 cells in ONE call. A call with the wrong name made every cell
  read as blocked. So the grid placed nobody and reported a tidy list of "NO CELL" rows.
- 🔴 **`jawa/set_pawn_rotation` takes `pawnId`, NOT `pawn`**, while `jawa/pawn_gear` takes `pawn`. The first grid was never
  rotated; it faced south by luck. Never assume that two tools in one family name the pawn the same way.
- 🔴 **`jawa/take_screenshot` takes `fileName`, not `name`.**
- 🔴 **`jawa/set_fog` takes `action` + `rect:"x,z,w,h"`**, not `mode`/`x`/`z`/`width`/`height`.

**The unknown-parameter guard of `rimbridge_client` caught all four.** Without the guard, the bridge DISCARDS the bad
keys, runs on defaults and returns `success: true`. ⛔ Never pass `check=False` to silence the guard.

⚠️ The guard RAISES. A helper that wraps calls in try/except turns the raise into a quiet failure of one call. So make the
wrapper print the reason, or a whole staging step fails invisibly.

Two more traps of this kind are in §5 (2026-09-18). `rimworld/take_screenshot` ignores `x`/`z`/`zoom`. An emptied
debug log leaves its window open. Never trust the screenshot call's own framing args. Look at the PNG before you send
it, because a "cleared" log window can still cover your frame.

## 8b. `sky_glow_set` does not survive to the shutter

`jawa/sky_glow_set` forces `CurSkyGlow`. The next `SkyManagerUpdate()` overwrites the value; the tool's own return
says so. MEASURED 2026-09-20: shots taken with and without the call had **identical mean brightness** (62.6 / 74.4 /
79.8 on both passes).

**Get light from the CLOCK, not the glow.** `jawa/time_set_ticks` jumps `TicksGame` and simulates nothing: no incidents,
no needs, no map culling. So the call is safe on a staged scene where `step_game_ticks` is not. Two limits:

- If something time-dated (filth, ash) is in frame, the call is not safe. The jump ages that thing by the whole jump
  (`skills/rimbridge/references/silent-failures.md`, which says: set the clock before the map exists).
- The call is REFUSED while any loaded map holds a spawned free colonist, unless you pass `timeException=true` (and say
  `why`). So the call refuses beside the colonists of §3.

2500 ticks = 1 game hour. Read the local hour (`jawa/glow_at`, or one test shot) and offset from there.

⛔ **And do not post-brighten a COLOUR review.** The purpose of the shot is to judge hue, and a corrected exposure destroys
the hue. If the scene is too dark, move the clock or change the ground. Say which one you did.

## 8c. A one-pawn-per-species grid is a SAMPLE, not a palette

🔴 A grid of one pawn per species is the most misleading thing to hand someone for a colour review. A xenotype
usually carries SEVERAL skin genes, and each pawn rolls exactly ONE. MEASURED 2026-09-20: Abednedo carries 9, Ithorian 6,
Bith 5. Only Ugnaught, Nelvaanian and Umbaran carry exactly 1, so a single pawn is an honest sample of only those three.
Spawn **4+ per species in a labelled column**. If you do not, the reviewer rules on one random draw and believes that the
draw is the species.

## 8d. A line-up the owner must RECOGNISE — his five corrections (owner, 2026-10-06)

The 2026-10-06 xenotype grid failed review on all five counts. `stage_xenotype_grid.py` now does each one. Each one
applies to any line-up of species, creatures or kinds:

1. **Label by what he recognises: the race or species, never the pawn's random name.**
   *"you should have labeled each of them by the Race I'm supposed to recognize, not by
   random names."* Rename every subject (`jawa/set_pawn_identity single=<race>`) and pin a `jawa/review_label` above it.
2. **Face the camera.** *"they are looking away from the camera."* DRAFT the subjects and let a few ticks pass (*"If you
   allow some time to advance, they will look at the camera. Because they are drafted"*). THEN call
   `set_pawn_rotation dir=south` and check the read-back. In one run the ticks alone left a whole grid facing north, so do
   both.
3. **Remove everyone first.** *"there are at least two or three individuals not part of this set that should have been
   removed"* and *"Just remove everyone first... get rid of them."* BEFORE you spawn, use `jawa/clear_area
   dryRun=false` over the whole frame. That call is the dev menu's own Clear area, and it removes pawns. ⛔
   `jawa/damage Bomb 9999` does NOT remove drafted colonists (MEASURED 2026-10-06, three runs). `destroy_batch` never
   touches pawns. A second run on the same site without a clear stacks pawns on the first.
4. **Hold them in place.** *"all of them should have been drafted so they stayed in one
   place."* The draft in item 2 also does this.
5. **Stand a standard human beside them for comparison.** *"they should be next to a
   standard human for comparison."* A Baseliner goes first in the grid.

⚠️ `rimworld/start_debug_game_ready` can time out at 30 s and leave the OLD game running. Prove a fresh map:
`ticksGame` is near 0 AND no subject from the last run is there. Or restart the game, which takes under a minute on a
small test list. Save the finished line-up as a keeper.

When you refer to an image, **open the image for him** (`powershell.exe Start-Process '<windows path>'`). Never hand him a
bare link. Read the image yourself first.

## 9. When a shot still comes out wrong — the checklist

Before you conclude that the subject looks bad, rule out the frame:

- Is the camera on the **right map** (`get_camera_state` mapId; `map_info` mapBiome)?
- Is the **world** view down? `jump_camera_to_cell` can report success with the WORLD view still up, so the "shot" is the
  planet and not the map. First call `jawa/world_view {show:false}` and read `get_camera_state.mapId` (2026-09-18).
- Is the frame on the **subject**, not the colony? Jump to the rect centre first.
- Is the frame **unfogged**? Is the **UI cleared**? Is the game **paused**, so that nothing moves?
- Is it **daylight**, or is the shot only dark?
- Do the subjects stand **on the terrain**, not in rock (`get_cell_info`)?
- Did the subjects **survive** to the shutter (`pawn_get` count == what you spawned)?

Only when all of these are clean do you see the subject's real appearance.

More traps for this section: [references/traps.md](references/traps.md) § 9. When a shot still comes out wrong — the checklist.

## Keeping this skill honest

- When a new staging trap costs you a shot, add it here. If the trap is a silent failure of the bridge API, add it to
  `skills/rimbridge/references/silent-failures.md` and link it.
- When you write the same multi-step bridge sequence across several reviews, fold it into `stage_review.py`. Do not teach
  the sequence again.
- Old lines and their evidence are in [references/history.md](references/history.md).
