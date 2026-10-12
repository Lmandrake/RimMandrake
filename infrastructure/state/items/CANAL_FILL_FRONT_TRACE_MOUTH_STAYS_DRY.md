# CANAL_FILL_FRONT_TRACE_MOUTH_STAYS_DRY

Class: MOD, presumed (untraced). extension_proof dry half, chain `plot_C` row `canal_fill_front`, has FAILed in all three
2026-10-11 runs (extension_result_20261011T141116.json, ...T170309.json, BENCH Transient/bench_live_20261011/ext_dry.json):
the source is stocked 300/300 and adjacent to the dug channel, yet the mouth cell stays F=0 after 3 pulses.
New in the BENCH run: `tar_front_lags_water` FAILs 0/10 wet in the same shape (likely the same root).
Triage: Transient/bench_live_20261011/ext_dry_triage.md. Suspect: the source->channel feed in
RM_MapComponent_Excavation DoPulse (~1223-1285) with RM_StockMath.CollectComponent / RM_LiquidStock.BodyAt -- the body
report says formedByThisCall: true after the dig; if a dig after classification never re-seeds the component, it is a mod bug.
Note validation_v2's own X7 tar/water staircase rows PASS (fw_validation_v2.log), so the primitive works; the plot_C staging differs.

NEXT: replay plot_C on a fresh golden-site load with the body report read after each pulse; decide MOD vs staging.
