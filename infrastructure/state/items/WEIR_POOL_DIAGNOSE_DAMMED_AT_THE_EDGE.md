# WEIR_POOL_DIAGNOSE_DAMMED_AT_THE_EDGE (FlowWorks rivers; presumed SITE, untraced)

BENCH 2026-10-12, extension_proof `--live --site river` on river_site.py's tile 825 (TemperateForest, riverCount 2, current 3,582
cells), 23-mod pilot tier, export e8a4060321: `works.weir_arrest_and_pool` FAIL —
`RM_RiverWorksProofs.ProofWeirPool` returned `POOL cells=0 dropped=0 arrestedWet=True at=(108, 0, 12)`; the 8 later `works`
components were UNMEASURED (upstream failed). Evidence: `Transient/bench_live_20261012/ext_river.json`, `fw_ext_river.log`.

The weir arrested its water cell but `RM_Building_BankWeir.AddPoolCells` found no upstream cell at all. `SpawnWeir` takes the FIRST
bank-edge site `FindWeirSite` meets in `map.AllCells` order (lowest z first), here z=12 beside the south map edge; if the river enters
the map there, `Upstream()` has no in-bounds cell with a flow toward the weir. That would be a probe-site artefact (SITE), not the weir.
Not traced; the other reading (a real weir whose Upstream() never finds a neighbour) is a MOD bug.

NEXT: run ProofWeirPool with a weir site picked mid-river (or print Upstream()'s 8 neighbours' FlowDirAt at the chosen site) to decide SITE vs MOD.

## Diagnosis 2026-10-12 (BENCH night-fixes subagent, offline): NOT the map edge; C# fragility, not harness. Undecided SITE-vs-MOD only by one live print.

- The "weir at the map edge" reading is REFUTED. `FindWeirSite` (`src/RimMandrake/FlowWorks/Source/Rivers/RM_RiverWorksProofWorks.cs:24-69`) already skips
  a margin of `weirPoolLength + 4` = 12 cells (`RM_RiversSettings.cs:57`, default 8); z=12 is the FIRST row it allows, 8 pool cells fit above z=4.
  Prior runs pooled at that same row: `extension_result_20261006T003821.json` (76,0,12) cells=14, `...T020120` (106,0,12) cells=16, `...T025236` (35,0,12)
  cells=23. Only the pre-margin run (79,0,0) read cells=0 for the edge reason. The harness (`extension_proof.py`, `extensions_rivers.py`) passes no site: it just
  calls `ProofWeirPool(arg)` (arg is only "keep"), so there is no Python-side placement to move.
- Mechanism that fits: `RM_Building_BankWeir.AddPoolCells` (`RM_Weir.cs:524-551`) starts at `WaterCell` and breaks the moment `Upstream` (`RM_Weir.cs:553-590`) returns
  invalid. `Upstream` wants a neighbour whose QUANTISED 8-way flow dir steps exactly onto `cur`, else (only if `FlowDirAt(cur) >= 0`) the cell behind `cur`
  having any flow. The weir's `WaterCell` is by construction the bank-edge water cell (`RM_PlaceWorker_RiverWeir`, `RM_Weir.cs:69-97`: exactly 1 water + 1 bank),
  i.e. the slowest, noisiest lane; `flowDir` is built once from vanilla `waterInfo.riverFlowMap` (`RM_MapComponent_RiverCurrent.cs:EnsureGrid`). Tile 825's grid
  is `current=3582 fast=894 edge=2688` (75% edge-lane cells), the highest edge share seen. `FindWeirSite` only checks that the wet end HAS flow (`wetHasFlow`),
  never that an upstream exists, so a site whose edge flow points along the bank is accepted and then pools 0. Same river, 2 cells away, the sluice at (110,10)
  reads poolCount=3, so the river does flow there.
- Class: MOD-or-SITE both live in C# FlowWorks Source (another agent owns it now), so nothing is fixed here. Two candidate fixes: (a) make `Upstream` tolerant
  (accept a neighbour whose dir is within 1 of pointing at `cur`, or walk the lane inward); (b) make `FindWeirSite` require `AddPoolCells`-style upstream >= 1 so the proof
  lands on a poolable site. (a) is the player-facing one: a real weir on this river would also get no slack pool.
- NEXT: in `ProofWeirPool` append the 8 neighbours' `FlowDirAt` and `FlowDirAt(WaterCell)` to the result string, rebuild FlowWorks, rerun `python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live --site river` on tile 825; if no neighbour steps onto `WaterCell`, it is MOD (fix a); if upstream exists, re-open.
