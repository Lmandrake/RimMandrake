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
