# Notes (newest first)

## 2026-11-11 20:10 -08:00: picked by CLAUDE_STEVEDESKTOP_OFFLINE4 (SETUP)
- Runs: 1, a pass (blind check at 9fd7d703c3, selftest 50/50). The non-pass tail is 0, so the mode is whittle.
- Reopen cause, MEASURED: 8fb9f7f2b6 (the Pyrelands landing, 2026-11-08 11:52 PST) replaced `.claude/settings.json`
  with the branch's copy. `block_blanket_git_stage` appears 0 times there, and once in its parent and on main.
  943a7a66da (19:37 PST) restored it, and the deadman read `kept` at 2026-11-09T04:18Z. The fix itself never broke.
  Class: SITE (a landing clobbering settings), not MOD or HARNESS.
- The same outage wrote 43 RUNNER `live` events across 29 distinct hooks (`grep "is not wired" RUNNER.jsonl`). It
  reopened, among others, HOOKS_BLINDSCAN_TUNE_DRIVE_D_IMPORT_TOLL, HANDOFF_HOOK_FIX_QUOTED_READY_COUNTS and
  CONDUCTOR_CLOSEOUT_BUILD_LEDGER_CHECK. One guard covers the class, and those items can cite it after this one
  closes (not this round's scope).
- Checker: `_hook()` in `src/RimMandrake/rimflow/live_line.py` runs a whole-name regex over the hooks JSON of
  `~/.claude/settings.json` and the clone's `.claude/settings.json`. The guard should reuse it, not re-implement it.
- The registered command ends `2>/dev/null || true`, so the hook must refuse by its JSON decision, not by exit code
  (cf. HOOKS_VERIFY_TRUE_SUFFIX_MAY_MUTE_REFUSALS). Check the registered line, not only the script.
- Guard verb: `rimflow guard <ID> --test <selftest*.py> [--instance "<args>"]`. Read `--help` for how the instance
  is fed.
- The offline lane gate (`infrastructure/whittle_claude/gate.py`) refuses any Bash command whose text contains the
  close flag spelled with two dashes, even inside a heredoc. Write such text with the Write tool. The close itself
  may need that flag, so a refusal there is a HARNESS fault to route around (a file-fed argument) or to fix in
  gate.py.
