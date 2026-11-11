# Raw evidence index

All paths below are relative to this directory. Root artifacts preserve the first attempt; `attempt2/` preserves the second attempt and `attempt3/` the third attempt and `attempt4/` the rebuilt localized production artifact. These are raw data locations, not a verdict.

- `base.json`, `item_state.txt`, `quota.json`: clone/build/frozen-file identity and initial readings.
- `deploy_plan.txt`, `deploy_bytes.json`, `stamp_verification.json`, `source_manifest.json`, `source_snapshot/`: reviewed deployment plan, source/deployed hashes and first executed source snapshot. `failed_attempt1_source/` is that same failed-run source. The second/third executed script snapshots are in `attempt2/source_snapshot/` and `attempt3/source_snapshot/`.
- `original_settings_inventory.json`, `native_saved_Mod_HugeThings_RM_HugeThingsMod.xml`, `close_baseline.stdout`: prior game/Linux settings absence and XML actually written by native settings close.
- `baseline_process.stdout`, `baseline_fields.json`, `baseline_live.json`, `baseline_owned_layout.json`, `baseline_native_settings__clip.png`, `baseline_windows*.json`: baseline process, untouched settings, native UI draw and windows.
- `live_schemas.json`, `hover_schemas.json`, `tool_census.json`: actual live tool definitions and census.
- `baseline_preflight_*.json`, `adversarial_preflight_*.json`, `restore_preflight_*.json`: first-run raw preflight rows and explicit O02 applicability assessments.
- `adversarial_fixture.xml`, `adversarial_disk_before.json`, `adversarial_disk_first_read.json`, `adversarial_process.stdout`, `adversarial_live.json`, `ht_settings_adversarial_*.png`: first hostile disk/read/UI attempt. `adversarial_probe.rc` and its JSON preserve the failed UI comparisons. `live_attempt_1.json`, `attempt1_driver.*`, `attempts.md` retain its result and cleanup.
- `restore_launch_repair.*`, `restore_up.*`, `restore_delayed_*`: retained PowerShell adapter/process-list refusal and its repair. `finally_status.*` records the stopped-status return code 3; no receipt was relabeled.
- `attempt3_guard_free.stdout`, `attempt3_parent.stdout`, `attempt3_take.stdout`, `attempt3_guard_taken.stdout`: third lease and host identity.
- `attempt2/upgrade_live.json`, `attempt2/upgrade_probe.rc`, `attempt2/live_attempt.json`: second attempt display comparison failure and cleanup, with its other raw cold-load/UI data alongside.
- `attempt2_guard_free.stdout`, `attempt2_parent.stdout`, `attempt2_take.stdout`, `attempt2_guard_taken.stdout`: second lease acquisition and actual fresh host generation/parent identity.
- `attempt4/{adversarial,valid,upgrade}_fixture.xml`: exact hand-edited fixture bytes. The upgrade fixture omits the warning key.
- `attempt4/{arm}_disk_before.json`, `{arm}_disk_first_read.json`, `{arm}_process.stdout`, `{arm}_live.json`, `{arm}_live.startup.sanitized.txt`: file hashes, cold process identity, first untouched loaded fields, real UI layouts, exact label checks and credential-redacted startup logs. Arms are baseline, adversarial, valid, upgrade, restore; baseline/restore have no fixture. Baseline has UI captures too.
- `attempt4/ht_settings_{arm}_*__clip.png`: native window screenshots at each scroll position and trunk/wake tooltip screenshots, stored directly here by the game tool.
- `attempt4/{arm}_preflight_{offline,live}.json`, matching stdout/rc and `_assessment.json`: required rows for every cold process.
- `attempt4/live_attempt.json`, `attempt4/disk_restored_*.json`, `attempt4/finally_{down,status,release,lease,guard}.*`: per-arm result, all-field active restoration and disk restoration, game shutdown and actual host release.
- `display_preferences.json`, `owned_screenshot_cleanup.json`, `owned_full_screenshots_cleanup.json`: windowed/background preferences and removal of the one owned game-folder screenshot.
- `offline*.stdout`, `offline*.stderr`, `offline*.rc`: exact focused selftest runner receipts.
- `call_opus.py`, `broaden_prompt.txt`, `broaden_raw.json`, `broaden_stderr.txt`, `broaden_call.json`: fresh tool-disabled independent consultation input, output and process receipt.
- `pilot/broaden_prompt.txt`, `pilot/broaden_raw.json`, `pilot/broaden_call.json`: fresh tool-disabled Opus formatting diagnosis before the third attempt.
- `audit_final.py`, `final_audit.json`: final read-only reconciliation of raw results against actual files/source/deployment and restoration, with raw artifact hashes.
- `judge.last.txt`, `judge.events.jsonl`, `judge.spend.json`: independent Codex judgment transport.
- `workflow.stdout.txt`, `workflow.stderr.txt`, `workflow.receipt.json`: actual Whittle validate(cwd) output and return code.

- `parent_source_commit_verified.json`, `localization_committed.patch`, `parent_artifact_commit_verified.json`: actual parent commits and byte comparisons.
- `localization_winbuild.*`, `localization_dll_strings.json`, `localization_numeric_unchanged.json`, `localization_built_pair.json`: prescribed successful build, new/removed DLL literals, numeric prefix comparison and artifact hashes.
- `localization_deploy_plan.*`, `localization_deploy_apply.*`, `attempt4_guard_taken.stdout`: reviewed complete deployment plan, apply/readback and actual guard generation1399.
- `localized_source_manifest.json`, `localized_source_snapshot/`: all50 compiled inputs plus relevant final project/XML/functional/test source snapshots. The earlier `final_source_*` files preserve the prior artifact; they are historical.
- `pilot_localization/`: independent tool-disabled Opus diagnosis before attempt4. `offline_localization_gates.*` contains the passing exact focused test runner receipts; earlier localization parser failures are retained too.
- `../PARENT_JUDGE_PROMPT_AMENDMENT.md`, `base.json`, `audit_refusal_1_*`: original/current prompt amendment context and first final-audit refusal. STATEMENT and NOTES hashes remain unchanged.
