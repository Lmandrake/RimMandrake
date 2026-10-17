# P12 build log — DEEP_WATER_BUILD_SWIM_OR_SINK (FOUNDRY offline builder, 2026-10-17)

Ruling R12 (owner 2026-10-17, by card): pawns may swim in water 2 m or deeper; non-water fluids keep the no-swim
refusal; deep water stops being a barrier for pits and trenches. No bridge, no game.

## Stage (a) — read docs, find the hooks
- status: DONE. Hook RM_Drowning.keepsHeadUp/PerCheck (P7). Vanilla (RimSage): Walkable/Standable/region type all come from
  PathGrid.CalculatedCostAt (terrain Impassable -> 10000 at its first line); PathGridJob refuses custom offset >= 10000;
  Pawn.WaterCellCost = race/gene value, else 1 while job.swimming (so the class must read race/gene directly);
  JoyGiver_GoSwimming needs Standable + IsWater. Natural non-water seas (propane, brine, scald) carry the Water tag:
  swimmability is by LiquidDef whitelist (fresh, salt, icy), not by tag.
- Decision (item step 1): passability by PATH GRID postfix, def keeps Impassable, so every def-level reader (roads, tiny
  islands, stockpile/fishing designators, deep scanner, BedLevels) keeps vanilla's answer.

## Stage (b) — swim math (Verse-free, SelfTest)
- status: BUILT. RM_SwimMath.cs: SwimClass None/Swimmer/Strong/Aquatic, Load, EnduranceFactor, Effective (sink < 0.1),
  CostFactor, Exhaustion/Recovery per check, KeepsHeadUp, PlanOffset/PlanCellCost.

## Stage (c) — wiring: passable deep band, path cost, drowning hook, animals, refusal, rescue, joy
- status: BUILT (DLL compiles). Swimming/RM_Swim.cs: PathGrid.CalculatedCostAt postfix (swim cost 60 or the creature's
  waterCellCost; impassable things/fences still close); CostToMoveIntoCell postfix (Moving/load factor); per-pawn offset
  grid (non-swimmer blocked, land animal +3000/square) composed into RM_Patch_PathFollower_PitRoute; CanReach veto for a
  non-swimmer to a lake square; items never spawn on / drop pods never aim at a swim square; RM_Drowning.keepsHeadUp set;
  ExitInReach reads natural water; RM_Swim.Tick (exhaustion hediff RM_SwimExhaustion, warning messages, tired undrafted
  swimmers head for footing, drowning on natural water by PerCheck); swim joy: refused liquids + deep only for rested swimmers.

## Stage (d) — settings
- status: BUILT. RM_SwimSettings (14): master deepSwimEnabled ON, swimOpenWaterEnabled OFF, humanlikesSwim, mechanoidsSink,
  swimPathCost 60, swimEnduranceHours 2, swimRecoveryHours 1, weight penalty 1.25 / slowdown 1.5, animalsAvoidDeepWater +
  cost 3000, swimWarnAt 0.7, tiredSwimmersHeadForShore, deepSwimJoyEnabled. WriteSettings re-applies on live maps.

## Stage (e) — tests
- SelfTest: 8/8 new Swim_* pass; whole run 527/530, the 3 FAILs are Lake_floors_* x2 + DeepBed_drawdown (another
  builder's uncommitted P11 work in this shared clone, not mine). Re-run in the scratch clone at publish.
- Scratch clone (/home/mandrake/rm/scratch/FOUNDRY/p12, origin + only P12's hunks): SelfTest 522/522 (514 + 8 Swim_*),
  again 522/522 on the tree rebased onto 34ffd701b. Exhaustion timeline: warned 1.40 h, under 2.00 h, dead 3.10 h.
  Weight table (person, 35 kg capacity): load 0 -> 2.00 h, x1.00 (73 ticks/square); 0.26 -> 1.36 h, x1.39; 0.46 (marine +
  rifle) -> 0.86 h, x1.69; 0.66 -> 0.36 h, x1.99; 0.74 -> SINKS. Towing a person counts 0.5 load.
- Oracle differential 3000/3000 x 7 modes PASS. vv_shipped_matrix --skip-ep: SHIPPED 0 everywhere; OFF_edgeSinks
  kernel_fuzz 142/2000 (known); VERDICT FAIL only on AUTHORED Thirst_slime_last_resort_ruled (known); forced-flag
  SHIPPED suite fails 24 (same count as P5/P7).
- run_selftests --only (FlowWorks python + Utils flowworks + settings): 15/17 then 16/17 after the review-map coverage
  row for RM_SwimExhaustion; remaining red selftest_settings_screens: FlowWorks rows all ok; FAILs are LeaningScrub,
  TheForge, ExplosiveGrowth, SWBestiary group counts (not FlowWorks, untouched).

## Stage (f) — publish + item notes
- status: DONE. The shared foundry clone held another builder's uncommitted P11 lake-floor hunks in the same files, so P12
  was staged blob-by-blob into a scratch clone, rebased onto origin, DLL rebuilt there: source 0e59ee10c + 520d16996,
  DLL 1e2dec39d. PUBLISHED 1e2dec39d.
- Notes: PIT_SUPERDEEP_COLLAPSE_1 and PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH (risk + recommendation); the item (verdicts).

## Defaults chosen (veto list; each has a Mod Setting)
- Passable deep band by the path grid, not the def (WaterDeep stays Impassable for every def-level reader).
- Scope: lakes, dug canals and pits; ocean and deep river water OFF (setting).
- Who swims: every person; land animals (detour +3000/square unless no other route); waterCellCost > 1 or water-seeker
  = strong (3x endurance); waterCellCost 1 or a swimming graphic = aquatic (never tires); mechanoids sink.
- Swim cost 60 a square (wading chest-deep 42; vanilla deep 300 unused); x Moving and x(1 + 1.5 load).
- Endurance 2 h unloaded person, x sqrt(body size) 0.5..2, x Moving, x(1 - 1.25 load); sinks under 10% (~72% load).
  Recovery 1 h on footing. Warn at 70% (message); undrafted/AI swimmers then head for the nearest footing; drafted obey.
- At exhaustion the head goes under and P7's one drowning rule runs (about an hour). Downed in deep water drown.
- Items never land in deep water; drop pods never aim there; a non-swimmer cannot reach a lake square.
- Swim joy: deep water only for a rested swimmer with an hour of endurance; brine, propane, boiling, poisoned, acid, tar,
  slime, oil refused everywhere (natural seas too, shallow brine included: a widening of the old refusal).

## Live proofs owed (P10, minimal list, no flyers, NOT run)
- A colonist swims across a 3 m lake and climbs out (ProofSwim "x,z" mid-lake: class/water/pathCost/headUp).
- A heavily armoured colonist tires, gets the warning message, heads for footing; drafted, is warned then goes under.
- A non-swimming land animal walks around a lake with a land route; a mechanoid is never routed in.
- A prisoner in a flooded sheer pit swims to the lip and cannot climb out.
- Regions/reachability after toggling the master off and on mid-game (WriteSettings re-reads every map's path costs).
- Perf: the path-grid postfix only runs on cells vanilla priced 10000; offset-grid rebuild on each swim-terrain change.
