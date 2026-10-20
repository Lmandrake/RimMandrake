# HOSE_REALFLOW_DIAGNOSE_SHORT_POUR_DRY_TANK

Class: MOD (presumed, untraced; could be a stale bar). `proof_hose.py --only realflow,save_load`, live, flowworks tier
(11 mods), FlowWorks DLL of ccf36a9af7. Same rows FAIL on the older DLL 84f0e4d79e (BENCH run 2026-10-19T05:20Z), so not new today.
Result: `Transient/live_session/20261018T233414/proof_hose_result.json`.

- NS_hose_carries_real_units / NS_hose_far_end_pump / NS_relay_chain_carries: one pump cycle (260 ticks after discovery)
  moves 8,594-8,899 tank units; the bar wants >= UNITS_PER_LEVEL (10,000 = 1,000 L since the litres migration cf4f24213d).
  Either the pump's per-cycle draw fell short of a level (MOD) or the bar is stale against a litres-era rate (HARNESS).
- NS_tank_feeds_hose: tank -> hose -> tank moved 0 units (perCycleCap 10,000, credits 0). This one is the strongest MOD lead.
- NS_tank_does_not_bridge_pipe_runs: second-run tank not built (secondRunTankBuilt false) - SITE/HARNESS presumed.

Bar: realflow rows PASS, or the bar is corrected from the pump's shipped per-cycle rate (RM_PumpMath) with the reason written here.
