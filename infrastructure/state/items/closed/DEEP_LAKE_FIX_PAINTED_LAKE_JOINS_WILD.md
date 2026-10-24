## spec
found-by: BENCH bridge run (2026-10-23, run 1, build fed77f423a, 14-mod tier). Class: SITE presumed (unproven) — the
script scores it MOD FAIL.
`python.exe src/RimMandrake/FlowWorks/northstar/deep_lake_proof.py <out> --fresh-map`, twice on two fresh quicktest maps:
- run 1 (`Transient/bridge_run_1_20261023/deep_lake.json`): painted 72x72 lake (PAINTED deep=4356 shallow=828) reads
  `BODY id=1 cells=1894 limitless=True truncated=False deepest=0` -> DL_lake_over_4000_is_limited FAIL, gradual_hollow FAIL,
  refill_restores_exact_shape FAIL, colonist rows UNMEASURED "no dry square past bed 4".
- run 2 (`deep_lake2.json`): `BODY id=2 cells=4000 limitless=True truncated=True deepest=0` -> lake_over_4000 FAIL,
  gradual_hollow FAIL (deepestDry 4, lakebedAbyss 0), shallow_dries_first PASS, refill PASS, colonist rows UNMEASURED.
- 2026-10-22 belt (`northstar/deep_lake_result_20261022T1200_belt.json`): cells=5184 limitless=False deepest=12, PASS.
drainableLakeMaxCells read live = 40000 (default), so not a leaked setting. RM_LiquidStock.cs:161-176 keeps a body truncated
(limitless) when the lake walk meets an owned body or an edge: presumed the painted rect touches the fresh map's own natural
water (body ids 1/2, deepest=0 = the wild lake's floor, not the painted one), i.e. SITE.
Fix: the proof must read back that the painted lake is ONE body of SIZE^2 cells before scoring (else UNMEASURED/SITE), and
pick/clear a site with no natural water within the rect + margin. If the read-back shows the rect isolated and the body
still truncates, it is MOD — refile. Item DRAWDOWN_DIAGNOSE_THIRTEEN_BEFORE_TWELVE A1 stays owed.
