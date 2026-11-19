# RIMMANDRAKE_HARDEN_PROMISE_TESTS_SEVEN_BREAKS_SLIPPED_PAST

Filed 2026-11-19 by `RIMMANDRAKE_BREAK_EACH_PROMISE_DOES_ITS_NAMED_TEST_FAIL` (one ticket for all its GREEN results,
as its brief asked). Evidence: `design/specs/2026-11-18-pipeline-control-surface/promise_tests_broken_on_purpose.md`.

## spec

`boundary_check.py` reads "promises covered 23 of 23" for the control store's page. Each of the 23 promises was broken
on purpose in a private copy of `control.py`, and the test of its name was run. For 7 promises the named test still
passed. Make each of these 7 named tests reject its break:

| promise | the break | named test today | what it checks instead |
|---|---|---|---|
| stop-reaches-the-agent | `hook()` returns exit 0 with the stop text | `t_hooks_in_run_clone` | hook path and silence; writes no order |
| kill-verified-dead | `_verdict()` does not count a survivor as a failure | `t_stop` | real units die on SIGKILL: no survivor |
| killed-run-needs-no-hand-step | `_finish_kill()` never calls `reap_detached()` | `t_kill_bookkeeping` | calls `detached_helper.mark_killed` directly |
| stopped-run-spends-no-trial | `stop()` charges held trials instead of releasing | `t_stop_review_fixes` | the dispatch-books half only |
| probe-never-lies | `_cgroup_pids()` reads a failed `systemctl show` as empty | `t_review_round_four_p1` | a failed store read, not systemctl |
| same-command-twice | `_idem_hit()` never finds an earlier act | `t_look` | settle/void twice (once by row state, not key) |
| every-change-is-an-act | `_act()` records `before` as null | `t_verbs` | exit codes, lines, speed; never `before` |

Six of the seven breaks are caught by some other test in `selftest_control.py` (named on the evidence page), so the
cheapest fix for those is often to bind the promise's name to that test or to give the promise a test of its own
that runs the catching check. `every-change-is-an-act` is caught by no test in the file: it needs a check that an
act's `before` (and who, when, why, after) are recorded. Change tests only; `control.py` keeps its behaviour.

Scope (Conductor's addendum, 2026-11-18 night): this ticket's acceptance test and nothing wider; no new guards.

## verify

Acceptance test, a runnable command, watched FAIL on the base (commit of this filing, 2026-11-19 1:51 AM PST):

```
python3 src/RimMandrake/rimflow/acceptance/control_promise_breaks_accept.py
```

- Base: 16 `REJECTED` lines, 7 `SLIPPED` lines (the 7 promises above), then
  `FAIL control_promise_breaks: 7 of 23 breaks slipped past their named test: ...`, exit 1 [measured].
- Pass: 23 `REJECTED` lines and `PASS control_promise_breaks: 23 of 23 breaks rejected by their named test`, exit 0.
  Expected pass count: 23 of 23. The 16 breaks caught today stay in, so a fix that weakens a test is seen.
- `COULD NOT LOOK` (exit 3) is not a pass: the unbroken copy fails a named test, a break no longer matches
  `control.py` exactly once (edit the break with the code, keeping what it breaks), or the copy failed. Seen on the
  base when the copy lacked `src/RimMandrake/contracts`.
- `--only <promise> ...` runs a subset (seen PASS, exit 0, on two promises caught today).
- Runs about 90 s; it starts real `rm-probe-` units through user systemd, as `selftest_control.py` does.

## criteria

- Each of the 7 named tests goes red under its break; the 16 that are red today stay red.
- Every named test still passes on the real `control.py`, and `selftest_control.py` passes whole.
- `boundary_check.py` still reads 23 of 23 for the page.

## refs

file: src/RimMandrake/rimflow/selftest_control.py
file: src/RimMandrake/rimflow/acceptance/control_promise_breaks_accept.py
file: design/specs/2026-11-18-pipeline-control-surface/promise_tests_broken_on_purpose.md
file: design/specs/2026-11-18-pipeline-control-surface/boundary.md
