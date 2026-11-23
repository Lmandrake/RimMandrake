# RIMMANDRAKE_RETRY_SLACK_RELAY_SLICE_CHECK_RED_TWICE

Gimme Some Slack, a wrong check on the 0.2.0 path (found by the readiness list of
RIMMANDRAKE_OPEN_SLACK_NEXT_VERSION_SO_THREE_MODS_ADVANCE_TONIGHT, 2026-11-23).

## What happened

`SelfTest/SliceGateChecks.cs`, check "slice: an all-keys-changed re-lay held one Build N ms" (bound `SyncLayBoundMs`, 30 ms),
went red twice with no change to the lay:

- 2026-11-22: 32.1 ms (RIMMANDRAKE_STAGE_SLACK_SHORT_LOOK_AT_FOUR_CHANGES_THEN_HIS_PASS, PROGRESS note; called load noise; the
  second run passed);
- 2026-11-23 about 2:20 AM PST: 30.2 ms, 5695/5696, at load 13 on 14 cores, which made `proof_all.py --offline-gate` (T_GATE)
  read red on main (`/tmp/gss020_tgate.log`).

The check takes one wall-clock reading. The cold-build check beside it takes the best of up to 3 cold builds (`SliceBound`,
6f8bfb47c4) for the same reason. T_CORE and T_GATE decide bars (`no_stall_on_rewire` and others), so a false red is a wrong
verdict at a certificate or builder run on a loaded machine (test 1: a failure happened twice in ordinary operation).

## spec

The re-lay check takes the best of up to `SliceAttempts` (3) re-lays, each on a fresh builder warmed the same way. The
first re-lay's builder `b` keeps its state for the reuse checks that follow. The other checks on the first re-lay (bit-identical
end, no missing cord mid-re-lay) are unchanged.

## criteria

- Green: `python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py --no-export --perdig-only` passes on the fix.
- Red: `python3 src/RimMandrake/rimflow/maturation.py red-seen GimmeSomeSlack T_CORE --patch
  design/concepts/GimmeSomeSlack/version/evidence/fault_relay_slice_over_bound.patch` (a re-lay bound of 0.5 ms, which no
  re-lay meets) reads red after the retries.

## verify

Both commands under ## criteria, cited on the close.
