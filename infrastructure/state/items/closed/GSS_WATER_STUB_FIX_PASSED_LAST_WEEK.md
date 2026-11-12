## spec
found-by: BENCH bridge run (2026-10-23, run 1 driver 3, row 1.18, HEAD 1f37da7100 deployed, 14-mod list fw_gss_sitting).
Class: MOD (proof says MOD; cause not isolated). REGRESSION: a prior PASS now FAILs.
Repro: `python.exe -I src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live --only matrix` (loads site calm =
RM_TestSite_calm_v2). Scene MX_F60_T15_S0 (Cybertek, 1 cord/connection, slack 0, no tangles; board bbox 10,10..34,20;
builds PowerConduit 14, WaterproofConduit 2, Battery 1, Heater 1 -- all survived) FAILs:
stubs expected 2 got 0; cord_edges expected 2 got 1; node_types expected {battery 1, consumer 1, stub_water 2} got
{battery 1, consumer 1}; strands expected [2,2] got 1. The other 29 matrix scenes, determinism and log budget PASS.
Last PASS: northstar/proof_all_20261016T192502.json ("graph ok: 2 edges, 2 strands, 1 nets"), which ran on tier
gimmesomeslack (no FlowWorks) and site RM_TestSite_calm_v1. Candidates: FlowWorks co-loaded (water / conduit terrain),
the calm v1->v2 site, or a GSS change since 2026-10-16. Not isolated here (no mod fixes on a bridge run).
Evidence: `D:\ClaudeWork\rimmandrake\scratch\br1_gss\gss_A.json`, `Transient/bridge_run_1_20261023/gss_A.log`.
Done when: MX_F60_T15_S0 PASSes on the fw_gss list (and the cause is named: which of the three candidates).
