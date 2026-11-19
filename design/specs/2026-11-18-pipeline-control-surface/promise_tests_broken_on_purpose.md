# Each promise broken on purpose: does the test of its name go red?

Item `RIMMANDRAKE_BREAK_EACH_PROMISE_DOES_ITS_NAMED_TEST_FAIL`, run 2026-11-19 1:30–1:55 AM PST by a detached BENCH
helper. Page: `design/specs/2026-11-18-pipeline-control-surface/boundary.md` (23 promises, no SURVIVES section).
Tests: `src/RimMandrake/rimflow/selftest_control.py`. Design asking for it:
`design/specs/2026-11-18-review-growth-cycle/01-design.md` §5.2.

## For the owner

- We broke each of the 23 promises on purpose, one at a time, in a private copy.
- Then we ran the one test that has the promise's name.
- 16 tests went red. They caught the break.
- 7 tests stayed green. They did not catch the break.
- For 6 of those 7, a different test in the same file caught the break.
- For 1 promise, no test in the file caught the break. That promise is "every change is an act".
  The act can lose its "before" value and every test still passes.
- `boundary_check.py` said "23 of 23 covered". That count was not true for 7 of them.
- We filed one ticket to fix the 7 tests: `RIMMANDRAKE_HARDEN_PROMISE_TESTS_SEVEN_BREAKS_SLIPPED_PAST`.
- The ticket has a test that keeps all 23 breaks. On the base it failed with 7 slipped.
- **Fixed 2026-11-19** by that ticket: each of the 7 promises has a test of its own name. Now 23 of 23 breaks are
  caught by their named test [measured]. `control.py` was not changed: no new test was red on it.
- We did not change `control.py` or the tests in this run.

## Counts

- Promises on the page: **23** [measured]. Their named tests: 3 are tests of their own, 20 are an existing test given
  the promise's name.
- **RED 16, GREEN 7, UNMEASURED 0** [measured, twice: the scratch-clone harness and the committed acceptance script,
  `python3 src/RimMandrake/rimflow/acceptance/control_promise_breaks_accept.py`, exit 1 on the base].
- All 3 tests of their own went red. All 7 GREEN are renamed existing tests.
- Prior stated before the first break: about 6 of 23 GREEN `[guess ~55%]`. Measured: 7.
- The unbroken copy passed all 23 named tests first [measured]. After each break the copy was restored from the
  original and its sha256 matched (`c0ea2c57c9…`), 23 of 23 [measured].

## Table

| promise | the break (in a private copy of `control.py`) | named test | result |
|---|---|---|---|
| off-blocks-starts | `switch()` off cancels no unstarted run, and `condition()` re-checks no switch at start | `t_race` | RED |
| one-admission-point | `call_sites()` marks every systemd-run site routed | `t_sites` | RED |
| his-hold-refuses-launch | `blocking()` drops owner-layer rows | `t_his_hold_refuses_launch` | RED |
| three-named-stops | `escalate()` always finds nothing to do: a write-now order never becomes a kill | `t_stop` | RED |
| stop-reaches-the-agent | `hook()` returns exit 0 with the stop text (the agent is shown only exit-2 text) | `t_hooks_in_run_clone` | **GREEN** |
| kill-verified-dead | `_verdict()` does not count a survivor (`dead=False`) as a failure | `t_stop` | **GREEN** |
| kill-works-without-the-store | `stop()` re-raises Unreadable for a unit kill too | `t_review_claims_round_two` | RED (the test raised) |
| killed-run-needs-no-hand-step | `_finish_kill()` never calls `reap_detached()` | `t_kill_bookkeeping` | **GREEN** |
| stopped-run-spends-no-trial | `stop()` charges a live run's held trials instead of releasing them | `t_stop_review_fixes` | **GREEN** |
| look-charged-only-on-a-verdict | `settle()` charges the look whether or not the verdict is valid | `t_coverage_look` | RED |
| void-gives-back-once | `_account()` adds the voided quantity back to `available`: one void gives back twice | `t_look` | RED |
| void-never-moves-a-stage | `_stage_advanced_on_voided()` returns `[]` at once | `t_void_never_moves_a_stage` | RED |
| unreadable-store-launches-nothing | `launch_unit()` runs systemd-run with the payload when the store is unreadable | `t_unreadable` | RED (the test raised) |
| probe-never-lies | `_cgroup_pids()` reads a failed `systemctl show` as an empty cgroup | `t_review_round_four_p1` | **GREEN** |
| same-command-twice | `_idem_hit()` never finds an earlier act: a keyed command sent twice acts twice | `t_look` | **GREEN** |
| every-change-is-an-act | `_act()` records `before` as null on every act | `t_verbs` | **GREEN** |
| binds-at-once-from-any-clone | the `pipe` CLI suffixes the store path with a hash of its own folder | `t_clones` | RED |
| verbs-answer-in-a-second | `main()` sleeps 1.1 s before every verb | `t_verbs` | RED |
| queue-order-is-the-store's | `queue_apply()` returns the shipped order | `t_queue` | RED |
| counts-and-limits-are-adjustments | `_used()` freezes the count at the first adjustment's measured value | `t_accounts` | RED |
| a-test-never-touches-the-live-store | `test_process()` ignores `RM_UNDER_SELFTEST` and `RM_OWNER_HOLD_FILE` (live path made a decoy) | `t_stop_review_fixes` | RED |
| ended-run-is-recorded-ended | `hook_cmd()` does not fall through to the seat clones' `control.py` | `t_end_receipt_outlives_its_clone` | RED |
| reused-name-runs-again | `_admit()` never treats a `reuse_name` run as over | `t_reused_name_runs_again` | RED |

"The test raised" is RED the way `selftest_control.main()` counts it: an exception in a test is a failure.

## What each GREEN test checks instead

- **stop-reaches-the-agent**, `t_hooks_in_run_clone`: that the hook command names the run clone's `control.py` and is
  silent with no order; it never writes a stop order, so it never sees exit 2. Caught elsewhere by `t_stop`.
- **kill-verified-dead**, `t_stop`: kills real units, which die on SIGKILL, so no survivor ever reaches the verdict.
  Caught elsewhere by `t_stop_review_fixes` (a fake killer that reports a survivor).
- **killed-run-needs-no-hand-step**, `t_kill_bookkeeping`: calls `detached_helper.mark_killed` directly; control.py's
  kill path never runs. Caught elsewhere by `t_review_claims_round_three` (claim r3-5) and `t_review_round_four_p1`.
- **stopped-run-spends-no-trial**, `t_stop_review_fixes`: checks the dispatch-books half (`voids.jsonl`) and a kill
  with a survivor; it never reads a stopped run's store account. Caught elsewhere by `t_stop` and
  `t_review_claims_eight` (claim 7).
- **probe-never-lies**, `t_review_round_four_p1`: makes a store read fail inside `pipe off`; it never makes
  `systemctl show` fail. Caught elsewhere by `t_review_claims_eight` (claim 1).
- **same-command-twice**, `t_look`: sends a settle and a void twice, which are once-only by row state and the voids
  table, not by the idempotency key; it sends no keyed command twice. Caught elsewhere by `t_scope`,
  `t_owner_import`, `t_review_claims_round_two` (claim r2-7) and `t_accounts`.
- **every-change-is-an-act**, `t_verbs`: checks exit codes, at most 3 lines and speed; it never reads an act's
  `before`. **Caught by nothing**: the whole `selftest_control.py` passes under this break [measured].

"Caught elsewhere" is from the whole `selftest_control.py` run under each GREEN break [measured]. Three of the seven
(stop-reaches-the-agent, kill-verified-dead, same-command-twice) list the catching test on their "Tested by" line, and
the binding in `selftest_control.py` picked a different one; the other four list no test that catches their break.

## Limits of this measurement

- One break per promise. A promise with several clauses had one clause broken; RED says that clause is guarded, not
  every clause. Each break is the first or central clause; the choice is in the table.
- **binds-at-once-from-any-clone**: the break sits on the `RM_CONTROL_DB` branch, because `t_clones` pins that
  variable; a break of the live default path (a per-clone `DEFAULT_DB`) cannot be seen by that test at all.
- **a-test-never-touches-the-live-store**: the break also points the copy's `DEFAULT_DB` at a decoy, so the broken
  test could not write the live store. The live `control.db` mtime did not move during any break [measured].
- A first full pass read 6 GREEN: the `three-named-stops` break disables the kill, so its test unit
  `rm-probe-deaf1` (`sleep 300`) lived on and a later `t_stop` could not reuse the name, which turned the
  `kill-verified-dead` run red for that reason. Every break now starts with no `rm-probe` unit alive (the
  acceptance script does the same). The clean pass reads 7.
- Copy: a pool scratch clone of origin/main `fcd5241fb8` (same `control.py` and `selftest_control.py` bytes as this
  item's clone); logs were in `/tmp/bep/` (not kept).

## What the `before` break would have hidden

Under the `every-change-is-an-act` break (`_act()` stores `before` as null), `./pipe log` showed nothing wrong: it
prints id, revision, time, kind, scope and why, never `before`. `pipe undo` also worked: it reads the live switch,
adjustment and grant rows, not `before` [measured: no code reads `acts.before`]. So the loss was silent. What was
lost is the only record of the state a change replaced: a second `pipe off` or `pipe stop` overwrites the earlier
OFF row (its why, its act, his words); a grant replaces the account it changed; `pipe limit` replaces a limit. With
`before` null, the store and its `export_acts` file could not say what any of those were. `t_every_change_is_an_act`
now checks `before` (and who, when, why, after) on an off over an off, an on, a grant, two limits and a set.
