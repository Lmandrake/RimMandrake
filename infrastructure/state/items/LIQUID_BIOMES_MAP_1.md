# LIQUID_BIOMES_MAP_1 — four liquid biomes, represented on the frozen world

Owner, 2026-09-06: *"there need to be four liquid biomes: A boiling ocean, two saline brine
seas, and one for use in a large propane-based lake on this side (we need to represent
this on the map)."*

## spec
- Reconcile with `terminator_sea.md` ("the three seas"): which existing sea defs are the
  boiling ocean and the two brine seas, and what each needs to become a distinct liquid
  biome def (waterBodyType, terrain, fish/fauna, the boiling-lift spec's scald water).
- **The propane lake gets worldmap tiles** under Umbra (the antistellar cap): a liquid
  biome def (`RUT_`/`RSW_` per the tier grammar) — MEASURED today: 332 of the 360 tiles
  at arc ≥165 are `AB_PropaneLakes`; the lake proper is a subset to rule with the owner
  by render (`worldview.py`) before painting.
- 🔴 The ancient war lab sits beneath the lake surface, over the Impact Site (owner);
  its placement rides the propane sheet and the lab item, not this one — but the lake's
  tile set must leave it a home.
- Anti-bullseye: the cap is a disc, not a ring; document the measured sector coverage.
- Save/re-freeze per the standing worldmap-repair procedure; back up Saves keepers.

## verify
Four liquid defs exist and resolve; the propane lake reads back from the live world on
its ruled tiles; the CSV re-count matches; render reviewed by the owner.
