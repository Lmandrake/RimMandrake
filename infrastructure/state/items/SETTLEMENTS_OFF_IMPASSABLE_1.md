# SETTLEMENTS_OFF_IMPASSABLE_1 — three holdings sit where a caravan cannot go

## spec

🔴 **OWNER, 2026-08-21: "Move them to the nearest valid tile."** Asked as move vs
show-me-first vs accept; he chose move.

`w9_run_2026-08-21_0143.md` lint reports **`settlementsOnImpassable: 3`** out of the 72
settlements stage 5 created. A settlement on impassable terrain cannot be reached by
caravan and behaves oddly in quests and raids that assume a route.

**Move each to the NEAREST valid tile**, not to a convenient one. These are authored
holdings with names, factions and prose behind them — a settlement that jumps a region
changes what it means.

⚠️ **Fix the CSV, not just the world.** `world/ASHKARR_WORLDMAP_settlements.csv` is the
source that stage 5 imports; a bridge-only move is undone by the next `w9_run --apply`.
Both, or the fix does not survive.

⚠️ **Re-check `settlementsWithNoRoad` after moving.** The 01:36 dry run reported 16 of
those; the 01:43 applied run no longer lists it, so the roads stage fixed most. A moved
settlement can strand itself off the road network again.

🔑 **Report which three they are and why each was invalid** — the owner declined the
show-me-first option, so this item owes him that in its closing note instead. If any of
the three reads as deliberate (a cliff eyrie, a crater fortress), say so rather than
moving it silently.

## verify

- Name the three: settlement, faction, old tile, new tile, distance moved.
- Post-move lint reports `settlementsOnImpassable: 0`.
- `settlements` count is still **72** — a move is not a delete.
- The CSV and the live world agree; re-running stage 5 is a no-op rather than a re-move.

## criteria

Seventy-two holdings, all reachable, all still where their prose says they are.
