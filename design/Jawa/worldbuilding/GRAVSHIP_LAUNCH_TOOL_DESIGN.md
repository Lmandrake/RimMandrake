# Programmatic gravship launch — companion-tool design (research 2026-09-09)

Deep-source finding from the overnight sitting. The naive bridge path to flying a
gravship (fuel the tanks, click the pilot console, pick a tile) is unbuildable via the
bridge — it requires unpaused time (colonist labour) and every second of unpaused time
mutates/destroys staged state (measured: colonists minify+haul bridge-placed tanks, loose
fuel is hauled off, an extended run lost the whole colony). And the launch UI runs a
GPU-render cutscene that wedges under automation. This document is the design for a
companion tool that sidesteps all of it, grounded in the 1.6 source.

## The mechanism (read at source, RimWorld 1.6 Odyssey)

The launch UI (`CompPilotConsole.cs:125`) calls
`Find.GravshipController.InitiateTakeoff(engine, tile)`. That method
(`WorldComponent_GravshipController.cs:107`) is **entirely GPU-render/cutscene driven** —
`gravshipCapturer.BeginGravshipRender` → callback → camera pan → `BeginTakeoffCutscene`
(a `timeLeft` countdown ticked by `WorldComponentUpdate` using real frame `Time.deltaTime`).
Under bridge automation with the window unfocused, the render capture may never complete →
wedge. This is exactly the skill's documented hazard.

**But the real work happens render-free in `TakeoffEnded()` and the utility layer:**
- `GravshipUtility.GenerateGravship(engine)` (`GravshipUtility.cs:367`) — builds the
  `Gravship` WorldObject and **despawns every ship thing + pawn into it**. No render.
  Sets `Current.Game.Gravship`. This is the clean "lift-off" primitive.
- `GravshipUtility.TravelTo(gravship, oldTile, newTile)` (`:351`) — `SetFaction`, sets
  `gravship.Tile`/`destinationTile`, `Find.WorldObjects.Add(gravship)`. No render. Creates
  the traveling world object headed at the destination.
- `GravshipUtility.ArriveNewMap(gravship)` (`:485`) — generates the target map (via
  `GetGenSteps(gravship)`) and places the ship. Called by the traveling object on arrival.
- `DebugSettings.ignoreGravshipRange` (`CompPilotConsole.cs:80`) bypasses the fuel/range
  gate entirely — so **no fuelling is needed**.

## The tool: `jawa/gravship_launch`

Params: `targetTile` (int), `validateOnly` (bool, default true), `abandonOrigin` (bool).
Sequence when applying:
1. `engine = GravshipUtility.GetPlayerGravEngine_NewTemp(map)` — null-guard, must be spawned.
2. Validate: `targetTile` in range; not the current tile; a land tile.
3. `var gravship = GravshipUtility.GenerateGravship(engine);` (guard null).
4. `if (abandonOrigin && !mapHasGravAnchor) GravshipUtility.AbandonMap(map);`
5. `GravshipUtility.TravelTo(gravship, takeoffTile, targetTile);`
6. Land immediately (skip travel time): `GravshipUtility.ArriveNewMap(gravship);`
   — the one UNVERIFIED call. It MAY reference cutscene-only state
   (`gravship.capture`, `bakedIndoorMasks`, set only on the render path). **Must be
   tried on a SCRATCH copy first**, wrapped in try/catch with full logging; if it NREs on
   `.capture`, the fallback is to set those fields to safe defaults or let the traveling
   object arrive naturally over world-ticks (a few unpaused ticks, far less exposure than
   the colonist-labour path).
7. `GravshipUtility.generatingGravship = false;` cleanup; report the new map's tile + a
   pawn/thing census as the success proof.

## Test plan (never on the frozen canonical)
- PROVE: restore `Saves_archive_2026-09-09/EXPERIMENTAL_shipcrewed` as a scratch, run
  `gravship_launch{targetTile:17007, validateOnly:false}`, then census the new map: engine
  present + PlayerColony, 5 Founders aboard, tile==17007.
- LIES: `ArriveNewMap` could NRE on cutscene state and leave the ship in limbo (despawned
  from origin, not placed) — hence scratch-only until proven, and a save immediately before.
- Companion build: add `jawa/set_fuel` too (set `CompRefuelable` directly) as a smaller,
  independently-useful tool for any future fuelling need.

## Status
Design only — NOT built. Blocked on: (a) the world is FROZEN (2026-09-09) so a real launch
needs an unfreeze; (b) `ArriveNewMap`'s cutscene-state dependency needs one scratch test
cycle to resolve. Best built in a focused session with the owner awake to react to a wedge.
The canonical start currently has the ship at the origin map; the scenario fiction
("Get it off the ground") even supports the PLAYER flying it as the opening beat, so this
is a refinement, not a blocker.
