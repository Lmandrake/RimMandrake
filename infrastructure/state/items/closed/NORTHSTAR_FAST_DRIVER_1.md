# NORTHSTAR_FAST_DRIVER_1 — ultra-fast Python driver for north-star validation

Owner (typed, 2026-09-30): "...Then use ultra fast python to drive the bridge to validate. Make it happen!"
Task context relayed by BENCH ("Yes. Write out comprehensive northatar plans for all three and ticket them
out as trials for full completion."); filed without the owner-said flag because that quote is not in this
session's transcript.

Built: `src/RimMandrake/Utils/northstar_driver/` — layered on `rimdrive.Session` (reconnect, verified pause,
litter sweep) and modcheck's `Suite`/`northstar` parser, not beside them. New: timed persistent transport
(one socket per run, optional pipelined `call_many`, UNPROVEN live), pre-flight site check that refuses a
dirty site, bar runner (PASS/FAIL/UNMEASURED per bar, `shows=` roll-up, JSON for modcheck), MockGame +
selftest. Invoke (live, Windows Python, repo-relative): `python.exe src/RimMandrake/Utils/northstar_driver/cli.py
preflight|run ...`; offline: `python3 ... run --mock --plan <plan.py>`.

Owed (NOT done — game was down):
- First LIVE preflight: response shapes (`get_game_info.devModeEnabled/godMode`, `list_windows`,
  `list_things` rect) are assumed and mirrored in the mock; a mismatch reads UNMEASURED by design.
- A live modal-listing tool: `rimworld/list_windows` is assumed absent -> `no_modal` is UNMEASURED until a
  window-listing tool exists on the bridge (JawaBench companion).
- Prove or reject pipelining (`--pipeline`) against the live bridge.
- Visual bars: judge hookup (`modcheck.judge`) so a visual must-show can reach PASS.
- Bridge lock from a python.exe process (rimdrive limitation) — take the lock from WSL first.
- Per-mod trial plans (design/RimMandrake/northstar_trials/) register `@bar` functions against this core.
