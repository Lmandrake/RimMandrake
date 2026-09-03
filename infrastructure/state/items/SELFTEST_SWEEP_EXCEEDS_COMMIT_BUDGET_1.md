# SELFTEST_SWEEP_EXCEEDS_COMMIT_BUDGET_1

The CLAUDE.md "Tools" block tells every seat to run, before a commit:

    for f in $(find src -name selftest_\*.py); do python3 "$f" || echo "FAIL $f"; done

That loop is serial and unbounded, and the sweep is now slow enough that a
Bash-tool invocation of it hits the 120 s timeout and is **truncated** — it prints
only the FAILs it reached before the kill, so a green-looking partial run is
indistinguishable from a real all-pass. Measured this the hard way tonight
(2026-09-03, BENCH): the first sweep timed out at 120 s having reached only 2 of 25
selftests' failures; a clean re-time gave the numbers below.

## measured (25 selftests, one machine, 2026-09-03)

    TOTAL ≈ 112 s serial — and that UNDERCOUNTS: selftest_cli.py did not finish
    inside a 60 s cap, so the true serial total is ~150 s+.

    slowest:
      >60 s   selftest_cli.py          (rimflow/) — NOT hung: 87 end-to-end cases,
                                        each spawns a fresh python subprocess; cost
                                        is interpreter startup ×87, not logic
      29.4 s  selftest_one_path_seam.py
       5.9 s  selftest_concurrency.py
       4.5 s  selftest_check_canon.py
      (the remaining 21 are ≤2 s each)

Two tests own ~90 s+ of the wall time; the other 23 are ~15 s combined.

## fix options (pick one — this is a decision, not a prescription)

1. **Parallelise the sweep** (smallest change, no test edits): a runner that fans
   the 25 out with a per-test timeout and a pass/fail summary. Wall time drops to
   roughly the slowest single test. Could live as `src/RimMandrake/Utils/run_selftests.py`
   and replace the CLAUDE.md loop line.
2. **Make selftest_cli.py in-process** (biggest single win): 87 subprocess spawns →
   call the CLI entry in-process, or convert to pytest. Removes ~60 s by itself.
3. Both.

## spec
Make "run every selftest before commit" actually run every selftest inside a normal
tool timeout, and make a truncated/failed run visibly distinct from an all-pass.
Update the CLAUDE.md Tools line to whatever the new invocation is (superseding the
raw `for` loop in place, per the superseding-a-doc rule).

## verify
The full sweep completes well under 120 s and prints an explicit "N/N passed"; a
deliberately-broken selftest shows up as a named FAIL in that summary, not as
silence.

## criteria
No seat can get a partial sweep that reads as green. The two slow tests no longer
dominate wall time.
