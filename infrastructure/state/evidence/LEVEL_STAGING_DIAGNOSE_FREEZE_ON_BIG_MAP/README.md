# LEVEL_STAGING_DIAGNOSE_FREEZE_ON_BIG_MAP: evidence

These are verbatim copies, so the proof runs without `D:\ClaudeWork`.

- `tprof_T3.txt` comes from `D:\ClaudeWork\rimmandrake\live_wave3_20261026\tprof_T3.txt`. It is a `jawa/health_profile` capture from the live run of 2026-10-26: Archmagi full list, fresh 325 map (tile 96532, player Settlement), 100 rigs, FrameLegacy=0, FlowWorks c0517553c3. It covers one `maxLength` settings write. In that window a single paused frame took 90.5 s, inside `RM_MapComponent_Hoses.DrawAll` -> `EnsureLay` -> `LayFrom` (150 synchronous re-lays, mean 589 ms). This profile names the cause of the staging->lay freeze. Ledger: BENCH `verify` on HOSE_FRAME_FIX_CHOKES_325_BASIN_MAP, sha 5d0a747595.
- `perf_L0_timed.txt` comes from `D:\ClaudeWork\rimmandrake\live_round5_20261026\perf_L0_timed.txt`. It is the timed phase of `pipe_levelling_perf_proof` on the same kind of 325 map (tile 96532, player Settlement, 100 rigs, maxLength 80). FlowWorks fa833277f8 was deployed, and the lay-off-frame fixes 9dfb5c6dc9 + f3d78f0140 were in. Result: LEVEL_PERF_TICK_TIME and LEVEL_PERF_ALLOC PASS, links=100/100, so the proof completes on the 325 map. Ledger: BENCH `verify` on HOSE_LAY_FIX_GC_STORM_FROM_WORKER, config "fresh 325 map tile 96532".

That round still logged ~6 s frame stalls from worker lays. They belong to HOSE_FRAME_FIX_CHOKES_325_BASIN_MAP and HOSE_LAY_FIX_SYNC_RELAY_IN_DRAW, which are now done. The finding is written up in `design/validation_walks/RimMandrake/FlowWorks.md`.

## The proof, and its mutants

`python3 src/RimMandrake/FlowWorks/selftest_freeze_big_map.py` checks F1-F9: the profile row, the PASS rows with links=100, this README, and the shape of the fix in the source. DrawAll and the tick recheck ask deferred, EnsureLay defers before it can lay synchronously, LayLater lays only through the queue, and HoseLayQueue is compiled and self-tested. `mutants.sh` copies the files it reads and breaks one clause per run. `mutants_summary.txt` records each of the 17 mutants going red on its own clause, and an unmutated copy staying green.
