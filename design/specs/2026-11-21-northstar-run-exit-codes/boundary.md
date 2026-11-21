# BOUNDARY: the exit code of `northstar_driver/cli.py run`, Design Version 0.1.0

Code: `src/RimMandrake/Utils/northstar_driver/cli.py` (`cmd_run`, `open_or_refuse`). Tests: `src/RimMandrake/Utils/northstar_driver/selftest_run_exit_codes.py`, one `t_<promise>` each. Item: `RIMMANDRAKE_REPAIR_PYRE_TABLE_LIVE_COMMANDS_THAT_NEVER_START`.

Readers of this exit code: `judge_certificate.red_seen` (a red run is rc != 0, checked against a no-fault start probe), each Stage 6 driver that runs a test table's live command, and `northstar_bar_proof.py`.

## ACCEPTS
- **a-mock-or-live-session.** `--mock` runs on the in-memory game; otherwise the bridge endpoint comes from `rimbridge_client.resolve_endpoint` (CLI > env `GABP_SERVER_PORT`/`GABP_TOKEN` > a named game's own > Player.log).

## DOES NOT SURVIVE
- **bridge-dies-mid-run.** A bridge that is reached and then drops raises out of the run as before (exit 1 with a traceback); only a bridge never reached is a refusal.
- **only-this-page's-scope.** The rest of `cli.py` (preflight, running-list, judge and record subcommands) has no page here.

## PROMISES
- **clean-run-exits-0.** A run whose bars are all green exits 0 and writes its results file. Tested by `t_clean_run_exits_0`.
- **dirty-site-is-refused.** A run whose preflight refuses the site exits 2, runs no bar, and writes a results file whose `bars` is empty. Tested by `t_dirty_site_is_refused`.
- **unreachable-bridge-is-refused.** A live run that cannot reach the bridge (no token, connection refused, timed out) exits 2 with one `REFUSED  cannot reach the bridge` line naming the cause, never 1, and writes no results file. Tested by `t_unreachable_bridge_is_refused`.
