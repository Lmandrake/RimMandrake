# CANAL_FILL_FRONT_TRACE_MOUTH_STAYS_DRY

Class: HARNESS (traced 2026-10-12, offline-MEASURED). Not a leak, not a dead feed: water races, so a dead-end D=1 channel fills
from its FAR END back and the mouth is wet only once the run is full. See "Root cause (2026-10-12)" below. extension_proof dry half, chain `plot_C` row `canal_fill_front`, has FAILed in all three
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

## Root cause (2026-10-12)

Live 2026-10-12 (Transient/bench_live_20261012/ext_dry.json, plot_C): 3 pulses fired, body stock 300 -> 297.081238, mouth F=0.
- MEASURED offline: SelfTest case `CANAL_FILL_FRONT_TRACE_MOUTH_STAYS_DRY_dead_end_fills_from_far_end` (FlowKernelFuzz.cs,
  production RM_FlowKernel, 60-cell LIMITED body stock 300 beside a dead-end 1x10 D=1 channel): after 3 pulses the channel reads
  mouth->end `0000000111`, 3.000 debited, 3 levels in the channel, ledger balanced; after 10 pulses `1111111111`, stock 290.
- Mechanism (RM_FlowKernel.ResolveComponent): recipients run deepest-first then nearest-source-first; the mouth takes 1 level from
  the source, then the next recipient pulls that level on (PickDonor: an equal-depth BRIMMING donor may give, MayFlowBetween
  allows source-hop 1 -> 2), and so on down the run in the same pulse -- the designed "water near-instant" race (FL-2 /
  THICK_LIQUID_CREEP_1 left water untouched). One debit per pulse through a single D=1 mouth.
- INFERRED: 297.081238 = 300 - 3 whole levels + refill accrued on pulses 2-3 (Refill skips a full body, so pulse 1 accrues
  nothing; ~0.04/pulse for a 60-cell body). The fraction is refill, not a sub-level debit. recededCount 1 = floor(297/5) = 59.
- Fix (HARNESS, extensions.py plot_C): canal_fill_front now passes when the CHANNEL took liquid and the levels in it equal the
  body's debit within 1 unit (a debit that lands nowhere still FAILs); canal_holds_only_channel skips the 3 painted source
  cells beside the mouth (they read D=4 F=4 by design and would have FAILed the ring scan once this row stopped blocking it).
  No kernel or DLL change. Notes: Transient/canal_mouth_2026-10-12.md.

NEXT: BENCH re-runs `extension_proof.py --live --site dry --chains plot_C_limitless_canal` and reads canal_fill_front PASS with
"levels in channel == debit"; then the item can close.
