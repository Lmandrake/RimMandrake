# TUSKEN_WATER_RAID_1 — the Deep Desert Tribes' signature: steal the water and vanish

Owner green-lit 2026-08-31 (tier 2). Spec by BENCH; machinery MEASURED from
1.6 source, and it OVERTURNS the 2026-08-14 finding — the steal-and-withdraw
behavior is mostly SHIPPED, not built from scratch.

## spec
Vanilla already composes attack→steal→leave: `LordJob_AssaultColony` takes
`canSteal:true` and attaches `LordJob_Steal`'s subgraph on
`Trigger_HighValueThingsAround`; `JobGiver_Steal` finds loot + exit and each
`JobDriver_TakeAndExitMap` job carries its raider off-map on completion (no
separate exit toil needed). What vanilla CANNOT do is care what it steals:
`StealAIUtility` scores `MarketValue × stackCount` over all haulables, with
a hardcoded value floor and no def filter.

**The build (small):**
1. `RUT_RaidStrategy_WaterRaid` (XML) → `RaidStrategyWorker_WaterRaid`
   (small C#, the confirmed extension point — all 18 live strategies wire
   this way) returning a `LordJob_WaterRaid`.
2. `LordJob_WaterRaid` composes SHIPPED toils, swapping in our
   `JobGiver_StealWater`: target selection restricted to a water-bearing
   def list (DBH water storage/containers, canteens, our own water items)
   with a value function of stored-water-first; a light harass posture
   (cover=true) instead of full assault — they fight to reach the water,
   not to kill.
3. Withdraw is free: found-nothing → `JobGiver_ExitMapBest` fallback is
   already in the Steal duty's think tree; loaded → TakeAndExitMap leaves.
   `Trigger_TicksPassedAndNoRecentHarm` bounds the visit.
4. Faction wiring: the strategy weighted onto the Deep Desert Tribes'
   arrival only; composition stays v1's light chiefless party.
5. Doctrine payoff: a raid you can DEFEND AGAINST by architecture (water
   deep, doors shut — Ishko smiles) rather than by killing; losses are
   property, not colonists — thematically the desert taxing you.

**Verify-first (two cheap checks before building):** (a) DBH water buildings'
`stealable` flag — a building marked unstealable needs the item-form target
(drawn water stacks) instead; (b) whether the closest-thing search's priority
function can be swapped without reimplementing it (source read left both
open).

## verify
Quicktest, spawn the raid via `jawa/fire_incident` with the strategy forced,
points explicit, read the REPLY's faction: PROVE raiders path to the water
store, EXPECT water gone + raiders exited + zero colonist-hunting behavior
logged; a map with NO water must produce harass-then-leave, never a stand-in
assault. LIES: vanilla's value-floor gate (`Trigger_HighValueThingsAround`)
silently converting the raid to plain assault on a poor colony — assert the
steal duty was actually assigned, not just that pawns left.

## criteria
The signature reads in play: they came for the water, took it, and left; the
owner watches one and rules the tempo.
