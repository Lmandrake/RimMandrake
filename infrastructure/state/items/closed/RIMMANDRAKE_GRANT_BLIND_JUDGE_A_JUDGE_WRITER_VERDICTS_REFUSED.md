# RIMMANDRAKE_GRANT_BLIND_JUDGE_A_JUDGE_WRITER_VERDICTS_REFUSED

## spec

The GimmeSomeSlack blind cycle 5 run (run-1794814806, role blind_judge) was launched with `RM_MODLEDGER_WRITER=HOLDER.run-1794814806`.
`modledger.json` writers.HOLDER has no `finding.verified` or `finding.open`, and `modledger.py` refuses a HOLDER process
writing the `JUDGE.<run>` shard ("a holder never writes a judge's finding"). So the cycle's verdicts on the 17 claimed-fixed
findings (the steward's stated reason for opening the cycle) and its new findings could not be written to the mod ledger;
they are in `design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_5/SUMMARY.md` only. Separately, the holder lease
lapsed after 45 idle minutes because the run wrote rimflow notes but no modledger event; only DISPATCH can regrant it, so the
run's closing `session.checkpoint` was refused too (NO_CHECKPOINT expected).

Not fixed by the finder: the fix changes the ledger's fencing (which process may write a judge's verdict), a design call for
the Conductor. Options: launch a blind_judge run with a JUDGE.<run> writer (and its checkpoints as JUDGE notes), or let a
HOLDER whose lease role is blind_judge write finding.verified/finding.open; and say in the brief that any modledger append
renews the lease, so a run must append at least every 45 minutes.

## verify

Acceptance test: none yet, the design is the Conductor's; once chosen, a selftest that a blind_judge launch can append
`finding.verified` for a claimed_fixed finding and a holder-role launch cannot.
