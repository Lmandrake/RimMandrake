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
