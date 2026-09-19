# QUEUE_DAILY_STALENESS_REVIEW_1 — built, tested, run clean against the real ledger

Daily staleness review: surface items idle in doing/blocked past N days, and
mis-tagged needs/for, so stalls stop rotting silently. `QUEUE_HEALTH_CHECK_1`'s
own closing line named this as real remaining scope if it "picks it up as a
recurring job rather than a one-off."

## 2026-09-05 (FOUNDRY, offline while BENCH held the bridge)

Built `src/RimMandrake/Utils/queue_staleness_review.py` +
`selftest_queue_staleness_review.py` (9/9 passing). Reuses `rimflow.model` for
all ledger reading — no ledger parsing reimplemented. Read-only: reports,
never mutates. `--blocked-days`/`--doing-days`/`--mistag-min` are flags, not
constants, with defaults calibrated against `QUEUE_HEALTH_CHECK_1`'s own
findings (documented in the script's own header).

Checks two honestly-derivable mis-tags: `for` naming a retired seat
(DECIDE/BUILD/CHECK/REP — orphaned instantly, not after N days), and
`needs: bridge`/`needs: game-up` idle while that exact window demonstrably
opened since. `needs: offline/deploy/harvest/owner` deliberately NOT checked —
no cheap ledger signal exists for them; the script's own docstring says so
rather than fabricating a proxy.

**First run found a real bug in itself**, not in the ledger: `item.blocked` is
a persistent flag a later `drop` does not clear, so the first version flagged
three items (`REFMATCH_THRESHOLDS_CALIBRATE_1`, `B55`, `FINAL_WORLD_PREP_1`)
that were correctly dropped back in August as if they needed attention today.
Fixed by adding the `item.open` check `render.py`'s own `view_sections()`
already uses (`item.blocked and item.open`), plus a regression selftest.
Caught by re-running the tool against the real ledger immediately, before
trusting its first output — see `[[grade-the-answer-not-the-exit-code]]`.

**Current real-ledger output (clean)**:
```
30 open doing/blocked items checked (27 doing, 3 blocked); 0 stale; 0 mis-tagged
```

## criteria
- [x] Recurring tool built (not a one-off hand census).
- [x] Reuses rimflow.model, no ledger-parsing duplication.
- [x] Thresholds justified against prior precedent, not arbitrary.
- [x] Selftest suite (9 cases) green, including a regression case for the
      dropped-while-blocked false positive found during this pass.
- [x] Run against the real ledger and result inspected by hand, not just
      "it ran without crashing" — the false positive above was caught this way.

Closing — the recurring job exists and runs clean. Whoever next runs it
regularly (a cron-style `/loop`, or just habit) owns deciding cadence; the
tool itself takes no action either way.
