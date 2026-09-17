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

A review shot exists to answer one question — *does this look right?* — and it
only does that if the frame shows the subject and nothing fighting it. Every
recurring failure of this task is the subject being **obscured or destroyed**
before the shutter: spawned inside rock, slaughtered by a raid between two bridge
calls, lost in fog or midnight, or off-frame because the camera stayed on the
colony. So the whole method is: **make the scene clean and still, then capture.**

This skill drives the live game. Read `skills/rimbridge/SKILL.md` for the
protocol and, before your first write, `skills/rimbridge/references/silent-failures.md`
— `success:true` never proves the game changed, and that is doubly true here
where the proof is a picture.

🔴 **From WSL, bridge scripts run under `python.exe`, not `python3`** (the bridge
binds Windows loopback). Screenshots land in
`.../RimWorld by Ludeon Studios/Screenshots/`; copy to `Transient/` and view them
— **a screenshot is a cache, not an observation** until you have actually looked.

## 🔴 Python is fast and cheap; you are slow and expensive — push work into the script

The bridge answers Python in milliseconds; every call *you* issue as the model is
a slow, costly round trip. So **do not hand-drive the bridge call-by-call.** Put
the sequence into `stage_review.py` (or a sibling script) with a flag that
specializes it, run it once, and spend your turn LOOKING at the result — not
issuing spawns and screenshots one at a time. A biome review is ~50 bridge calls;
that should be one Python invocation and one screenshot you read, not fifty
turns of yours.

**You are authorized to grow these scripts whenever it saves round trips**
(owner, 2026-09-17) — add options, add whole new capabilities, as long as you
(1) document the flag in the script's `--help`/docstring and (2) record it here in
the skill. A new `--two-pass`, a `--biome` preset, a batch mode that walks a list
of biomes end-to-end: build it, don't hand-crank it. When you catch yourself
about to issue the same three bridge calls a third time, that is the signal to
put them behind a flag instead.

## The helper does the whole clean-stage in one call

`src/RimMandrake/Utils/stage_review.py` composes every step below with the
read-backs and the traps already handled. Prefer it; drop to manual calls only
when a scene needs something it does not cover.

```bash
# art review — animals SPACED in a legible row on verified grass, midday, shot + save:
python.exe src/RimMandrake/Utils/stage_review.py --map 1 \
    --kill-hostiles --clear chunks,filth \
    --spawn "RUT_FireHawk:1,AA_Barbslinger:1,Anooba:1,Gizka:1" \
    --at 40,235 --spread 12 --terrain RM_FE_Ground --layout grid \
    --frame 30,228,160,16 --shot pyre_artgrid --save PYRELANDS_REVIEW

# ruled default capture in ONE call — midday-clear shot THEN signature-weather shot:
python.exe src/RimMandrake/Utils/stage_review.py --map 1 \
    --kill-hostiles --clear chunks,filth \
    --spawn "RUT_FireHawk:1,Anooba:1,Gizka:1" --at 40,235 --spread 12 \
    --terrain RM_FE_Ground --daylight \
    --frame 30,228,160,16 --shot pyre --two-pass RM_FE_Weather_AshFall \
    --save PYRELANDS_REVIEW
#   -> pyre_clear.png (midday) + pyre_ashfall.png (signature), one invocation
```

`--layout grid` (default) spaces each kind on its own verified-open cell —
**legible for art review**. `--layout cluster` piles counts around one point —
**dense herd vibe, but tall pawns overlap and hide each other, so never use it to
judge one creature's art** (owner, 2026-09-17). That art-vs-vibe split is the
single most important framing choice you make.

Everything after this line is *why* each step is there — read it so you can stage
by hand when the helper falls short, and so you understand what the flags do.

## 1. Clean first — kill hostiles, then clear the ground

**Order matters: remove ALL hostiles BEFORE spawning subjects.** A generated map
often arrives mid-raid with dozens of raiders (measured: 118 across Pirate +
PirateYttakin on one quicktest, "Raid: The Ohnaka Gang" stacking down the alert
column); if you spawn subjects into that and time so much as twitches, they are
killed or scattered before you frame them. `--kill-hostiles` clears every one.

🔴 **The kill mechanism, three traps deep** (all cost real shots):
- Select hostiles by the **`hostile` boolean** from `jawa/list_pawns`, never a
  faction-name guess — no substring catches Pirate *and* PirateYttakin *and*
  Ohnaka Gang.
- The pawn id field is **`id`, not `thingId`** (`thingId` comes back null). Pass
  `id`.
- `T: Damage To Death` only targets **player colonists** — hostiles cannot be
  reached that way and the call reports success having done nothing. Use
  `jawa/damage {thingId:<the id>, damageDef:"Bomb", amount:9999}`, which works on
  any faction. (The param is confusingly named `thingId` but wants the `id`.)
- **Sweep until stable at 0** — mechanoids survive one bomb. Read the count back;
  don't trust one pass.

Player colonists (your map anchor, §3) and wild animals are never touched.

Then clear what the subject would collide with:
- **Rosters / biomes:** `--clear chunks,filth` — loose rock and ash drifts that
  clutter the frame. (`src/RimMandrake/Utils/rimbench/clear_chunks.py` is the
  standalone read-back-proven version.)
- **Structures / gravships:** `--clear buildings,chunks` over the build rect
  first. The map's own ruins and rock **interact** with what you place —
  foundations refuse on existing floor, walls merge, a designator queues against
  existing work — so a structure test on un-cleared ground is testing the
  collision, not your build. Clear the footprint AND a margin around it.

`--clear` takes `chunks,filth,buildings,plants,items`; `--clear-rect x,z,w,h`
scopes it (default whole map). Buildings/plants are destructive — that is the
point when testing a structure, but say so.

## 2. Pause discipline — still scenes don't die

**Stage and shoot PAUSED.** An unpaused map resolves combat, wanders animals out
of frame, ages plants, and burns daylight while you read a screenshot — and
because each bridge call is a separate round trip, real frames pass *between*
your spawn and your capture. That gap is where "I spawned twelve and the census
shows three" comes from: they died or fled in the seconds between calls.

- `set_time_speed 0`, then **verify** it (read `ticksGame` twice — the call can
  report a speed and leave the game paused, or vice versa). The helper's `pause()`
  returns whether ticks actually held.
- **Unpause only in bounded bursts, for a stated reason**, then re-pause before
  capturing: to let plants grow in, weather settle, or ash drifts accumulate
  (§4). `step_game_ticks` in ≤2000-tick chunks (a bigger step frame-times out);
  a timeout is connection-fatal, so open a fresh socket and poll, never retry on
  the dead one.

## 3. Keep the map alive — colonists make it a home map

A map generated at a tile via `jawa/world_tile_map_generate` is a non-home
**Settlement** map, and the engine **culls non-home maps once you step time** —
so a scene you stepped for daylight or drifts vanishes, and `jawa/set_current_map`
then refuses with "No loaded map has uniqueID N". The fix (owner, 2026-09-17):
**spawn a few colonists on it** — `jawa/spawn_pawn faction:"PlayerColony"` — which
makes it a player home map that is never auto-culled. Then you can step and pause
freely. (This is also recorded in memory as `generated-map-culled-unless-home`.)

- `jawa/set_current_map {mapId}` switches `Find.CurrentMap` AND hides the world
  layer, so screenshots and current-map tools (spawn, list_pawns, take_screenshot)
  act on the right map. It refuses an unknown id and prints the loaded maps —
  read that list rather than guessing.
- Spawn **subjects** wild: `faction:"none"` (no combat, no fleeing). `faction:""`
  errors; the default is a hostile faction, which gets your subjects killed near
  a colony.

## 4. Placement — verify every cell is open and the right terrain

**A subject drawn inside rock, water or a wall is the number-one review defect.**
Never spawn across a fixed row that can cross gravel/rock/buildings — that was the
bug that produced animals standing on bare stone. Instead:

- **Verify each target cell** with `get_cell_info`: not water, not a building/wall,
  and (for a biome) on the terrain family you expect (`--terrain RM_FE_Ground`).
  In RimWorld the *plants* are the grass, not the terrain — soil terrain is where
  the dense grass grows, so a "lush grass" shot means spawning on the soil rows.
- **grid layout** places each kind on the next verified-open cell `--spread`
  apart. **cluster layout** spawns all counts at one verified anchor and lets the
  engine pop them into adjacent free cells — good for a herd, bad for art (§ the
  helper).

**Make them face the camera.** A subject faces wherever the sim last pointed it,
so an art shot photographs backs and flanks unless you turn them. `--face south`
(the helper) calls `jawa/set_pawn_rotation {dir:"south", lockRotation:true}` on
every pawn — **south is the front view toward the camera** — and locks the pose
(`debugRotLocked`) so they hold it while you frame. north/east/west are there for
a specific angle. Drafting and moving a colonist also induces a facing, but this
is the direct control and it works on wild animals too. (A downed/laying pawn
won't visibly turn — stand it up first.)

## 5. The shot — light, weather, fog, UI, frame

Default capture, owner-ruled: **midday + clear first, then the biome's signature
weather.** The clear midday pass shows true colour and density; the signature
pass (ashfall, blackrain, cinderfall…) shows the mood that defines the biome.

- **Time of day:** step toward midday (`--daylight`) so colour reads — a dawn or
  dusk shot reads muddy and undersells density. This is why the map must survive
  stepping (§3).
- **Weather:** `jawa/weather_set {weather, lockWeather:true}` forces and holds it;
  `--settle N` runs N ticks so drifts/effects build before the shutter.
- **Fog:** `jawa/set_fog unfog` the frame first — **a subject in unvisited fog
  photographs as black nothing.**
- **UI:** `jawa/clear_ui` before every shot — the dev log window sits exactly
  where the camera centres and has eaten many shots.
- **Frame:** `rimworld/frame_cell_rect {x,z,width,height,paddingCells}` zooms to
  fit a rect. It has been seen not to move the camera on its own, so the helper
  jumps to the rect centre first, then frames, then reads `get_camera_state` back.
- **Avoid structures in a biome/art frame:** a colony or ruin in shot pulls the
  eye and changes the read. Frame a patch away from built areas; that is why the
  helper spawns the roster in open ground you chose, not where the colony landed.
- **take_screenshot appends `.png` itself** — pass a bare name or you get
  `x.png.png`.

## 5a. When a colonist must DO a job for the test

Some tests need a pawn to actually *perform* an action — build a structure,
operate a bench, haul, plant. RimWorld will silently never do the job unless the
pawn can reach it and is fit to work, so a "nothing happened" result is usually
the pawn, not the mechanism. Owner's checklist, 2026-09-17:

- **Put a HEALTHY colonist right next to the job.** Distance + a partial path =
  the job never starts. `prep_worker()` spawns a fresh `PlayerColony` colonist at
  the job cell rather than hoping a distant one walks over.
- **Fully satisfy the pawn** — food, rest, recreation, mood, and health. A hungry,
  exhausted, or mentally-breaking pawn abandons the job or collapses mid-test.
  Top up every need (`jawa/pawn_need` to 1.0, `pawn_refresh_needs`) and heal
  (`jawa/pawn_health healAll`) before letting time run.
- **Remove all hostiles for the duration** (§1) — a raid interrupts the job and
  kills your worker. This is the same clear-first rule, for the same reason.
- Then unpause in a bounded burst (§2) to let the job resolve, and re-pause to
  inspect. Confirm the job's *result* (the built thing, the moved item), not that
  the pawn was "working".

## 6. Save one keeper per biome

Per the owner's standing "review options as savegames" ruling, after a biome is
staged nicely, **save it** (`--save <NAME>`) so he can walk it, zoom it and read
tooltips himself later. 🔴 **Verify the save landed** by stat-ing the named file
in the Saves folder — `rimworld/save_game` has written the CURRENT slot instead
of the name given, so trusting the returned path can overwrite a keeper. The
helper stats `Saves/<name>.rws` and reports its size. Keepers stay until the
owner says delete; name them per biome (`PYRELANDS_REVIEW`, `SCALD_REVIEW`, …).

## 7. Reset cadence for a biome-by-biome campaign

Testing every biome in turn, the reset rule is simple (owner, 2026-09-17):

- **If you changed files** (a def, a biome XML, an assembly): the running game
  holds the old defs in memory — **restart the game** so they parse at startup,
  then re-stage. Deploying to the Mods folder is not enough on its own. Use
  `skills/rimworld-load-round` and `modlist_swap.py`; the combined review list
  loads in ~80 s.
- **If you changed nothing on disk** (just moving to the next biome): **reload or
  regenerate** — re-tile the current tile to the next biome and
  `world_tile_map_generate` a fresh map, or reload the clean base save. No
  restart needed.
- **Reload to reset.** A staged map accumulates test damage, dead raiders, moved
  pawns. To start the next biome clean, reload the base save (or regenerate the
  map). **Do NOT nurse the map's contents** — this is scratch. When a step warns
  about "losing items from the game", ignore it: it is a throwaway review map and
  you reload to reset anyway. (The campaign save is untouchable; a review map is
  not the campaign — always say which map a shot came from.)

## 8. The scripts this composes

| script | does |
|---|---|
| `stage_review.py` | the one-shot clean-stage this skill is built around |
| `rimbridge_client.py` | connection (`resolve_endpoint` scrapes host/port/token from Player.log) |
| `rimbridge_lineup.py` | spawn one of every pawn kind in a framed grid — the roster line-up |
| `rimbench/clear_chunks.py` | clear every loose chunk, read-back proven |
| `rimbench/scatter.py`, `place.py` | organic distribution maths for natural-looking placement |
| `rimbench/render_terrain.py` | offline terrain→PNG when you want a map render, not a screenshot |
| `game_focus.py` | `preflight()` — turn on Run-in-background or every game call times out |
| `system_screenshot.py` | OS-level desktop capture (`python.exe`), for when you need the whole screen incl. dialogs, not the game's own shot |
| `modlist_swap.py` | swap to the minimal/review list and back before/after a load |

## 9. When a shot still comes out wrong — the checklist

Before concluding the subject looks bad, rule out the frame:
- camera on the **right map**? (`get_camera_state` mapId; `map_info` mapBiome)
- frame on the **subject**, not the colony? (jump to rect centre first)
- **unfogged**? **UI cleared**? **paused** so nothing moved?
- **daylight**, or is it just dark?
- subjects actually **on the terrain**, not in rock? (`get_cell_info`)
- did they **survive** to the shutter? (`pawn_get` count == what you spawned)

Only when all of those are clean is what you see the subject's real appearance.

## Keeping this skill honest

When a new staging trap costs you a shot, add it here (or, if it is a bridge-API
silent failure, to `skills/rimbridge/references/silent-failures.md` and link it).
When you find yourself writing the same multi-step bridge dance across several
reviews, fold it into `stage_review.py` rather than teaching the dance again.
