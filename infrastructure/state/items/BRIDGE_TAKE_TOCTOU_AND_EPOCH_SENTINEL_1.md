# BRIDGE_TAKE_TOCTOU_AND_EPOCH_SENTINEL_1 — two smaller bridge findings

Code review, 2026-09-02, alongside the ledger-forgery fix (`102516c6`).

## spec

Both in `src/RimMandrake/rimflow/cli.py`.

**1. `bridge take` is TOCTOU.** The world is read once near the top of `cmd_bridge`
and `model._apply` has no state guard for the `bridge` verb, so two simultaneous
takes both succeed and the `infrastructure/state/BRIDGE` mirror can name a different
window than the ledger's last event. `bridge who` re-derives and repairs it — but
only if someone already doubts the answer, and the whole point of the file is to be
believed at a glance.

⚠️ Fix carefully. This system's stated design errs toward ALLOWING a take, never
toward mutual lockout (owner, 2026-09-02) — a guard that turns a race into a refusal
would be worse than the race.

**2. `_epoch`'s `0.0` sentinel is unguarded in `_distress`.** `_epoch` returns `0.0`
for an unparseable timestamp, which is 1970. `_idle_seconds` converts that to `None`
deliberately, but `_distress` uses `_epoch` directly (~lines 425 and 460): one
malformed `ts` anywhere yields an age of ~495,000 hours and forces a distress score,
silently reordering the queue.

## verify
- Two `bridge take` calls racing against one throwaway ledger leave the mirror and
  the ledger's last event agreeing.
- A ledger containing one deliberately malformed `ts` does not move any item's
  distress score.

## criteria
The BRIDGE mirror cannot disagree with the ledger after concurrent takes, and no
single bad timestamp can promote an item.
