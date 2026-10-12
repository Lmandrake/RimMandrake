# CANAL_FILL_FRONT_TRACE_MOUTH_STAYS_DRY

Class: UNDECIDED offline (traced 2026-10-11, 7b9b1bb6a3) -- no-pulse-in-window suspected over a dead feed; see below. extension_proof dry half, chain `plot_C` row `canal_fill_front`, has FAILed in all three
2026-10-11 runs (extension_result_20261011T141116.json, ...T170309.json, BENCH Transient/bench_live_20261011/ext_dry.json):
the source is stocked 300/300 and adjacent to the dug channel, yet the mouth cell stays F=0 after 3 pulses.
New in the BENCH run: `tar_front_lags_water` FAILs 0/10 wet in the same shape (likely the same root).
Triage: Transient/bench_live_20261011/ext_dry_triage.md. Suspect: the source->channel feed in
RM_MapComponent_Excavation DoPulse (~1223-1285) with RM_StockMath.CollectComponent / RM_LiquidStock.BodyAt -- the body
report says formedByThisCall: true after the dig; if a dig after classification never re-seeds the component, it is a mod bug.
Note validation_v2's own X7 tar/water staircase rows PASS (fw_validation_v2.log), so the primitive works; the plot_C staging differs.

Trace (2026-10-11): the kernel cannot refuse a stocked cardinal source (RM_FlowKernel.PickDonor -> CanSupply -> TryDebit,
source feed fuzzed by selftest_flowworks_kernel_oracle), and classify-after-dig is harmless (BodyAt/FormBody). In all three
runs plot D's pond fed its mouth on its FIRST pulse while plot C (750 ticks) and C2 (1500 ticks with C) never moved: the
likelier cause is that no pulse ran in C's window (engine left off / nextPulseTick ahead), not a dead feed.
tar_front_lags_water 0/10 was HARNESS: tar gives every 6th pulse, a 3-pulse window held a giving pulse half the time.
Fix 7b9b1bb6a3: both rows read jawa/flowworks_engine_state + the body stock either side of the window
(_source_feed_verdict: engine off / no pulse = UNMEASURED with numbers; pulses ran and dry = FAIL with the stock);
the tar row waits one full stride. Selftest: northstar/selftest_canal_fill_front.py.

NEXT: BENCH runs `extension_proof.py --live --site dry` (plot_A..C2 at least) and reads canal_fill_front's verdict text; UNMEASURED "no pulse fired" -> trace what stalls the schedule; FAIL "never debited" -> MOD in the adapter (CanSupply/InputAllowed).
