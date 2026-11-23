## spec

Design Version: FlowWorks 0.1.0 (current, a Problem against the locked bars). Filed by the FlowWorks ticket sweep of 2026-11-22
(RIMMANDRAKE_SWEEP_FLOWWORKS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE), which merged these older tickets into this one, one
cause or one file group. Each old ticket's prose is in `infrastructure/state/items/closed/<ID>.md` and its history in
`rimflow show <ID>`; read the one you work on to its end before you build.

FlowWorks validation harness: seven rows red or blind for harness reasons (hose gate on SteveDesktop, rain E6, site hold, slime rows tier, fuel moat mod, sticky limitless, W8 edge on canary).

## merged tickets

- `PROOF_HOSE_FIX_GATE_RED_ON_STEVE` (proposed): hose_live_rows (30 rows) has never measured: on SteveDesktop the proof_hose_live driver spends ~1010 s in its offline gate, csharp_selftest (Utils/selftest_flowworks_stock.py, the C# SelfTest) reads red, and it refuses to go live (testq J20261104T044740Z-1f9b9a, sheet summary.drivers on the runner). That selftest also times out / fails / is UNMEASURED in recent nightlies. Make the gate's C# step pass on the runner (or run it once per build outside the live driver) so the hose rows measure
  - sweep reading: hose_live_rows (30 rows) never measured: proof_hose_live offline gate (selftest_flowworks_stock.py C# SelfTest) red/timeout on SteveDesktop, testq J20261104T044740Z-1f9b9a; driver still in validation.py and testq owed_register.json; no later fix recorded
  - its check: python3 src/RimMandrake/Utils/selftest_flowworks_stock.py (green within its timeout)
  - files: `src/RimMandrake/FlowWorks/validation.py`, `src/RimMandrake/Utils/selftest_flowworks_stock.py`, `src/RimMandrake/Utils/testq/owed_register.json`
- `FLOWWORKS_RAIN_DIAGNOSE_E6_OUT_OF_SYNC` (proposed): SteveDesktop core_live_rows E6_rain_fills_unroofed FAILs 7x (10-28..10-31, latest 10-31T10:03Z, 0 passes since): rain leaves S4_band/S1_ladder/S1_deep/E6_open cells at 0 vs expected 1; earlier runs also 'pulse-0 vector != oracle (out of sync)'. Diagnose mod vs oracle. Evidence: findings_fold.md table, 7 findings FLOWWORKS_E6_RAIN_FILLS_UNROOFED_FAILS_*
  - sweep reading: core_live_rows E6_rain_fills_unroofed FAILed 7x on SteveDesktop 2026-10-28..31 (0 passes; rain leaves cells at 0 vs 1, 'pulse-0 vector != oracle'); never diagnosed; the water model was reworked since (8734f51181, 2026-11-13), so a rerun decides whether it still fails
  - its check: FlowWorks validation.py core_live_rows: E6_rain_fills_unroofed PASS on a fresh run
  - files: `src/RimMandrake/FlowWorks/validation.py`
- `HARNESS_REPAIR_CAUSE_E0B6DA41_2` (proposed): harness fault, no verdict (testq J20261122T032751Z-ba092d.a1, FlowWorks): site_hold: could not hold the site quiet -- not a verdict on the mod: site hold raised
  - sweep reading: repeat site_hold sighting 2026-11-22 (J20261122T032751Z-ba092d) after the 2026-11-04 fix 0194c06c6e; 28 FlowWorks chains held without a verdict (bottle_revert, fire_*, toggle_*, dig_finds...), modcheck 303 PASS/72 NOT_RUN
  - its check: the same job re-run yields a verdict on every held chain
  - files: `src/RimMandrake/Utils/testq/testq.py`
- `THIRST_FIX_SLIME_ROWS_NEED_BIOMES_TIER` (proposed): SITE (probable): thirst/T15_slime_effects FAIL (job J20261026T060806Z-09152f): red pawn drank RM_SlimeRedShallow with no hediff/memory; red/green/white hediffs live in mandrake.rm.biomes, absent from the 11-mod flowworks tier (thirst_live.py DEBUG note); fix = stage the biomes tier or mark owed
  - sweep reading: thirst_live T15/T16 slime rows FAILed live (latest 2026-10-31, 0-1 passes since); probable SITE (slime terrain needs Biomes tier) but unsettled; inv_slime is a 0.1.0 bar
  - files: `src/RimMandrake/FlowWorks/northstar/thirst_live.py`
- `FUEL_MOAT_WIRE_EMPIRE_PURSUIT_NOT_INVITED` (proposed): testq FlowWorks/fuel_moat_astrofuel utinni_blast_summons_raid + astrofuel_detonation_off_burns UNMEASURED every run: RimUtinni Empire Pursuit is not on the FlowWorks test list (Type not found: RuthlessPursuingMechanoids.FuelBlastInvestigation); compose it for this chain or retire the row from the FlowWorks sheet
  - sweep reading: Unfixed: no commit names it. extensions.py:3244 still probes RuthlessPursuingMechanoids.FuelBlastInvestigation in the component utinni_blast_summons_raid (line 3360), so the row reads UNMEASURED on any list without RimUtinni Empire Pursuit. The checker is wrong for its list: compose the mod in, or retire the row
  - files: `src/RimMandrake/FlowWorks/northstar/extensions.py`, `src/RimMandrake/Utils/modcheck/required_checks.json`
- `BODY_CLASSIFY_FIX_STICKY_OFF_NEVER_FORMS` (proposed): FlowWorks: edge pond W6 classified with stickyLimitless OFF never forms a body (S5 regression, was PASS 2026-10-24T02:48)
  - sweep reading: S5_sticky_limitless FAILed once live (run4 2026-10-25, W6 limitless=None), PASSed on run5 replay; never re-run on validation_v2 --live --fresh-map; setting still exists (RM_LiquidStock.cs, validation.py:47)
  - its check: validation_v2 --live --fresh-map: S5_sticky_limitless PASS twice running
  - files: `src/RimMandrake/FlowWorks/Source/RM_LiquidStock.cs`, `src/RimMandrake/FlowWorks/validation.py`
- `RIMMANDRAKE_DIAGNOSE_FLOWWORKS_W8_EDGE_NOT_LIMITLESS_ON_CANARY` (proposed): FlowWorks core_live_rows S3_classification FAIL on SteveDesktop (J20261121T212809Z-40a0e0, the driver-cure canary): [MOD] 'W8 (edge) not limitless: {}'. First red of this signature. Diagnose mod vs site vs oracle. Acceptance test: none, live-only row; the oracle is S3_classification reading PASS on a steve-targeted run of core_live_rows.
  - sweep reading: core_live_rows S3_classification FAIL on SteveDesktop 2026-11-21 (J20261121T212809Z-40a0e0) [MOD] 'W8 (edge) not limitless: {}', first red of the signature, undiagnosed; no later commit cites it
  - its check: S3_classification reads PASS on a steve-targeted run of core_live_rows, or the red is classed SITE/ORACLE with the cause
  - files: `src/RimMandrake/FlowWorks/northstar`

## his words (as recorded on the merged tickets)

- none recorded on these tickets

## verify

Acceptance test: none as one command, harness repairs; each row is seen FAIL on a planted fault and PASS on the build (each merged ticket above names its check).

## criteria

- Each merged ticket above is fixed with its check passing (red first where it is a fix), or dropped with its evidence.
- No locked 0.1.0 bar is loosened or edited by this work.

## refs

item: PROOF_HOSE_FIX_GATE_RED_ON_STEVE
item: FLOWWORKS_RAIN_DIAGNOSE_E6_OUT_OF_SYNC
item: HARNESS_REPAIR_CAUSE_E0B6DA41_2
item: THIRST_FIX_SLIME_ROWS_NEED_BIOMES_TIER
item: FUEL_MOAT_WIRE_EMPIRE_PURSUIT_NOT_INVITED
item: BODY_CLASSIFY_FIX_STICKY_OFF_NEVER_FORMS
item: RIMMANDRAKE_DIAGNOSE_FLOWWORKS_W8_EDGE_NOT_LIMITLESS_ON_CANARY
