# Notes (newest first)

## 2026-11-11 19:58 -08:00 — picked by CLAUDE_ARCHMAGI_OFFLINE1
- Runs: 0 verify runs; nonpass tail 0. The item prose file is absent; the criteria live in the 2026-11-01 close reason
  (evidence `D:\ClaudeWork\rimmandrake\closeout_probe_2026-10-31\probe.txt`). The original fix is not in question.
- Cause of the outage: 8fb9f7f2b6 (2026-11-08 11:52 PST, Pyrelands lands on main) squashed the branch's
  `.claude/settings.json` over main's, dropping every PreToolUse/PostToolUse safety hook; 943a7a66da restored it at
  19:38 PST. The dispatch tree pulled the restore and the sweep marked it kept 2026-11-09 04:19Z. Classification:
  HARNESS/ops (a landing clobbered config), not the hook's code.
- The same outage reopened CONDUCTOR_CLOSEOUT_BUILD_LEDGER_CHECK (hook=conductor_goodbye.py), which owes a guard too.
  The same class guard serves it, but it is a separate item (one ticket at a time).
- Precedent: hook/unit guards on `selftest_live_retired.py --retired /dev/null` (LIVE_RESTORE_IM_BACK_HOOK).
- Instruments: `src/RimMandrake/rimflow/live_line.py` `_hook(name, settings)` is the deadman's own wiring check and
  takes a settings path; `src/RimMandrake/Utils/deadman_check.py` `promises()` lists the promises. Reuse them; do not
  write a second parser.
- No existing selftest checks hook promises against settings.json (`.claude/hooks/selftest_hook_registrations_refuse.py`
  checks that registrations can still refuse, not that promised hooks are present).
- Offline lane: no game is needed at any step.
