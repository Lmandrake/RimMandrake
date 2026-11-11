# Evidence index

Original requirements: original-criteria.json, item-before.txt; parent fixture authorization: fixture-authorization.txt.

Production identities: content-publication-provenance.json, dependency-reconciled.json, deploy-biomes-plan.txt, deploy-LuminousPigment-plan.txt, VEF-type-provenance.json, tier-VEF-plan.txt; live-attempt7/artifact-inventory.json.

Primary trial: live-attempt7/live.json, live.calls.jsonl, live_driver.rc, session.json. Includes loaded roster/defs/flight reads, complete pool, real incident/schedule/arrival, full census/letters and before/after restoration data.

Process/tier: live-attempt7/preflight_offline.json, steam_launch_preflight_live.json and rc/assessment companions; actual_guard_before_drive.stdout, steam_route.jsonl, steam_launch_up.*, startup_log_gate.json, post_live_log_gate.json.

Cleanup: live-attempt7/cleanup_*; independently repeated final_actual_game_status.*, final_actual_guard.*, final_bridge_free.*. Fresh raw/source/host audit: final-verification.json; code: final_verify.py.

Preserved histories: live-attempt1 through live-attempt6; adapter-path-incident.json; final-audit-attempt6/; credential-redactions.json. Interrupted setup2 retains its original IN_PROGRESS session receipt and successful cleanup, not a passing status. Only credential values were removed from raw replies; no unsanitized copies retained.

Independent model calls: broaden_prompt.txt, broaden_raw.json, broaden_call.json; Test Pilot pilot1/broaden_* and addendum.txt. Inherited unchanged controls: offline-selftests-final.txt, kernel-run.json, kernel-raw.*. Original parent-stopped worker: run.jsonl*, parent-redirect.json.

Functional code: src/RimMandrake/HugeThings/northstar/passage_pool_driver.py (real driver), passage_pool_live.py (offline parser), selftest_passage_pool.py. Orchestration: session_control.py, live_session.py, steam_adapter/powershell.exe. No dependency source/build edits.
