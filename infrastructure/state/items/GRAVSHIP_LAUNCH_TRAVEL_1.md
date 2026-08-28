# GRAVSHIP_LAUNCH_TRAVEL_1 — lift, fly, land, and none of it undoable

Row 2 of 5 split out of `BRIDGE_TOOLS_HARD_BLOCK_1`.

## spec
`GravshipUtility.GenerateGravship` → `TravelTo` → `ArriveNewMap` / `AbandonMap`.

🔴 **Four calls that between them DESTROY one map and CREATE another.** Nothing here is undoable
from the bridge, and there is no dry run the engine offers.

## The precondition the engine will not check for you
Fuel comes from `TryGetPathFuelCost`. ⛔ **A tool that skips that check strands the ship** — the
launch succeeds and the vessel cannot arrive. Check it, report the number, and refuse when short.

## What it must do
- `dryRun` defaulting **true**, like `jawa/fire_raid`, reporting the fuel cost and the target tile
  without moving anything.
- Assert the identity of what is being launched and where it is going — same rule as
  `jawa/world_tile_import`'s `expectTiles`. A wrong tile id here costs a map.
- Say what state the game is in if it fails between `TravelTo` and `ArriveNewMap`.

## verify
Build clean; then on a SCRATCH quicktest map only — never the campaign — launch and arrive, and
read back the new map's tile with `jawa/map_info`.

## criteria
- [ ] Fuel checked and reported before launch; short fuel refuses.
- [ ] `dryRun` defaults true.
- [ ] The halfway state is named in the result.

---

# BUILT 2026-08-28 by BENCH — awaiting the down-window deploy, then the live proof

Owner promoted to v1 and handed to BENCH ("let's see if you can do it").

**Four tools written into `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchGravshipTools.cs`,
compiled clean, all four verified present in the built DLL by `build.tool_surface`
(surface 240 → 244, MEASURED):**

- `jawa/gravship_status` (read) — engines, fuel, cooldown, missing components, and the
  three in-flight states: cutscene / travelling / **landing-marker pending** — the named
  halfway state the spec demanded.
- `jawa/gravship_launch_check` (read) — every vanilla gate reproduced argument-for-argument
  from `CompPilotConsole.StartChoosingDestination_NewTemp` + `Building_GravEngine.CanLaunch`
  (fuel path at the engine's own `FuelUseageFactor`, layer-adjusted range, signal jammer,
  same-tile GravAnchor rule, `IsValidTileForNewSettlement(forGravship:true)`).
- `jawa/gravship_launch` (GM-gated) — **dryRun defaults TRUE**; refuses on any gate; sets
  `LaunchInfo` like the vanilla dev gizmo (a null launchInfo NREs at landing);
  `ConsumeFuel` then `InitiateTakeoff`, exactly the confirmed-launch closure. Reports
  `originMapWillBeDestroyed` and the async state chain.
- `jawa/gravship_land` (GM-gated) — resolves the stranded-at-marker state via
  `marker.BeginLanding`; optional move is bounds-checked and flagged caller's-risk.

## criteria
- [x] Fuel checked and reported before launch; short fuel refuses — in both check and launch.
- [x] `dryRun` defaults true.
- [x] The halfway state is named in the result (`nextState`) and readable (`gravship_status`).
- [ ] LIVE: `prove_gravship.py` on a scratch quicktest (next window; the script authors a
      minimal ship, exercises the refusal path, launches, catches the marker state, lands,
      and asserts the new map's tile == target). Def names in it verified against the dump
      (`SmallThruster`, `ChemfuelTank`, `PilotConsole`, `GravEngine`); the set-fuel debug
      action walk and `jawa/world_neighbors` arg shape are best-effort and may need one
      interactive fix.

Deploy rides DOWN_WINDOW_ASSEMBLY_DEPLOY_1 (game held up all night by FOUNDRY).
