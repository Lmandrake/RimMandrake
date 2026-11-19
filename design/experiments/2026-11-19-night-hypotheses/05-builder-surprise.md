# Replay: does a builder's own report say where a later check finds a fault?

Item: `RIMMANDRAKE_REPLAY_TWO_MORE_HYPOTHESES_SURPRISE_AND_LARGE_READS`. Tests the hypothesis
`RIMMANDRAKE_AUDIT_ON_SURPRISE_ONLY_PREDICTION_SEALED_FIRST` in `00-hypotheses.md`, in the form the Conductor's
brief gave it: an outside check is worth most where the builder's closing report admits a slip, a doubt, an
untested part or a surprise, and worth little where it does not.

## For the owner

(PENDING: written after the counts.)

## Written before measuring (2026-11-19, 2:48 AM PST)

- **Population.** Every detached run whose record (`D:\ClaudeWork\rimmandrake\dispatcher\detached\*.json`) was
  launched on or after 2026-11-17 00:00 PST, finished, with a readable result text. One run is one row.
- **The mark, from the report alone.** A fixed list of word patterns over the run's result text, in four kinds:
  UNTESTED (untested, UNRUN, not tested / run / verified, could not verify, did not test), SLIP (my mistake, I
  missed, I broke, first attempt failed, had to redo, corrected), DOUBT (not sure, unsure, uncertain, unclear,
  might not, a `[guess` tag), SURPRISE (surprise, unexpected, turned out, contrary to). **FLAGGED** = any kind hits.
  A stricter mark, **FLAGGED-STRICT** = UNTESTED, SLIP or SURPRISE (no bare hedges), is reported beside it. The
  patterns live in `tools/builder_surprise.py` and are not changed after the first count.
- **What happened next, within 48 hours of the run's end** (clipped at the moment of measuring; the window each row
  had is reported). Three outcomes, kept apart:
  - **FAULT FOUND**: a later act found a fault in this run's work. Candidates come from the ledger (later events on
    the same item by anyone but this run, and items filed that name it or are `caused_by` it), the Conductor log
    (entries naming the item, except this run's own end lines), later runs' reports that name the item, and later
    commits that touch the files of this run's closing commit. A candidate must hold a fault word; each candidate
    is then judged by hand, **without seeing the run's mark**, as fault or not.
  - **LOOKED, NOTHING FOUND**: one of those later acts exists, and none was judged a fault.
  - **NOTHING LOOKED**: no later act of any of those kinds.
- **FOR the hypothesis:** among runs that were looked at, the fault rate of FLAGGED runs is at least twice that of
  unflagged runs and at least 15 points higher, and unflagged runs show a fault rate of 15% or less.
- **AGAINST:** the two rates are within a factor of 1.5, or unflagged runs fail more often, or more than half of
  all faults sit in unflagged runs.
- **TOO SMALL to say:** fewer than 5 faults in all, or fewer than 10 looked-at runs in either row. Then I say so
  and claim nothing.
- **Sanity probe.** Two cases are known to be faults before counting: a "23 of 23" claim that a later experiment
  showed was 16 of 23, and a first close that failed a selftest. If the instrument does not find both, it is blind
  and the counts are not reported as a measurement.
