# NORTHSTAR_RESULTS_JOIN_1 notes 2026-10-06

## Formats

## Design

## Results
- proof_all_*.json (GSS/northstar/): mod, script, mode(live|partial), started, mod_hash (status.mod_hash of repo dir), env{running, running_sha256, assembly_matches, assembly_sha256}, rows[{id,status,class,detail,block}], blocks, aborted. 144 rows/full run, block "preflight" P1-P3.
- validation_v2_result_*.json (FlowWorks/northstar/): same identity keys, rows[{id,status,cls,detail}], summary, green, aborted. 59 rows; --mock run emits identical ids offline in 0.15 s.
- srchash: Assemblies/*.dll.srchash line "# dll: <sha256>".
- Manifest already mirrors checkout rows as validation.py chains: FlowWorks core_live_rows/<rid> (=CORE_LIVE_IDS), GSS live_battery/<rid> + proof_all_only_rows/<rid> (subset of 144).

## Design (done so far)
- Walk header `checkout: <script>` added to GimmeSomeSlack.md + FlowWorks.md (header block, above first `##`; NS current_hash verified unchanged).
- proof_all.py: DECLARED_ROWS + declared_rows() (144 ids = latest live run exactly; matrix ids from reduced spec). validation_v2.py: declared_rows() = clean --mock run ids (59 = live).
- required_checks.py: walk_checkout(), checkout_rows() (subprocess, avoids `validation` module-name collisions), _add_checkout(): mirrors marked checkout_row; unmirrored rows -> new check `checkout/<rid>` source checkout_row.
- Both latest results are STALE vs HEAD mod_hash (GSS c63d.. vs now c1fb..; FW f8d8.. vs 2af3..) -- independent of these edits (validation_v2 sits in northstar/, excluded from mod_hash; GSS source changed 2026-10-05 23:03).
- Report: judge_checkout() + checkout_results(); build_report joins (newer of summary/checkout judges checkout-fed checks); render lists checkout line per mod, STALE section, CHECKOUT DECLARED/no live result section. §2.4 doc amended (checkout_row source, stale-result taint, checkout-results paragraph).
- selftest_results_join.py: 24/24 GREEN.
## Results
- FlowWorks: read validation_v2_result_20261006T040914.json, STALE (f8d8 vs 2af3), 0 proven.
- GimmeSomeSlack: read proof_all_20261005T085243.json, STALE (c63d vs c1fb), 0 proven, 171 required (95 new checkout_row).
