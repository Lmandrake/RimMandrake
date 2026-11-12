# GSS_WATER_STUB_FIX_PASSED_LAST_WEEK — done statement

Item: GSS matrix scene MX_F60_T15_S0 (waterproof-conduit water stubs) read 0/2 stubs on the fw_gss list (FlowWorks
co-loaded, deep swim on) on 2026-10-23 after PASSing 2026-10-16 on the gimmesomeslack tier. Fix landed (4b01d06994,
SnapshotBlock.Of; built c29007b6b66e). Owed: criterion A1 (GREEN-MIN), the live proof.

- **A1 (GREEN-MIN):** on the fw_gss list (`modset_builder.py --tier fw_gss_sitting`: FlowWorks + GimmeSomeSlack +
  Biomes + VEF core + all five DLC, FlowWorks deep swim on), `proof_all.py --live --only matrix` scene MX_F60_T15_S0
  PASSes: stubs 2, cord_edges 2, node_types {battery 1, consumer 1, stub_water 2}, strands [2,2].
  Evidence: the proof_all result JSON row `MX_F60_T15_S0` = PASS with those counts, the run's tier recorded as
  fw_gss_sitting (ModsConfig active list parsed at run time), the deployed GimmeSomeSlack DLL matching the built
  source (`.srchash`), and FlowWorks deep swim confirmed on (its Mod Settings value read at run time).
- **Cause named:** candidate 1, FlowWorks co-loaded (R12 deep swim makes WaterDeep walkable; the cord adapter read
  walkable as ground before water). Already recorded on the `implemented` event; the live PASS on the fw_gss list
  with the fix, against the 2026-10-23 FAIL on the same list without it, is what confirms it.
- **No regression in the run:** the other matrix scenes on the same run PASS (or any non-PASS is classified MOD, SITE
  or HARNESS and filed).
