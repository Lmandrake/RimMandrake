# RIMMANDRAKE_MEASURE_MATURATION_CONVERGENCE_PER_ROUND

## spec

Mods go round the Maturation Pipeline's judging stages and nothing measures whether they converge: MATURATION_NOW only
counts runs (2026-11-15: Pyrelands "Stage 3 has run 6 times", "Stage 4+5 has run 6 times", "Stage 6 has run 4 times";
Explosive Knockback 4 runs at each of two stages; no mod past Design Version 0.1.0). The owner's user-level rule on
Design Versions: "We need to allow our Design -> Build -> Debug -> Judge produce passes sometimes so we know the SYSTEM
works too." Ordered by the Conductor (harden order, 2026-11-15 12:45 PM PST, "Fix the process wherever it didn't work").

Build, with no model and no tokens, from records already on disk:
- per mod, per round of each judging stage: new, fixed, open; in-game rows pass / fail / unmeasured;
- one word per mod per stage by a stated rule: CONVERGING, FLAT, DIVERGING, or UNMEASURED where a record is missing;
- a table on MATURATION_NOW (new section), JSON for the tick;
- one behaviour: a DIVERGING stage puts a Needs Conductor line, with the numbers, in the Dispatch tick's reading. It
  pauses nothing and changes no bar.

Records read: Stage 3 `stage.json` coverage_rounds (and judge charges with no round: UNMEASURED rounds),
`coverage_fixes.json` claims; Stage 4+5 `version/blind_challenge/cycle_N/lane2/faults.json`; Stage 6
`version/in_game/visit_N/SUMMARY.md` Exit block.

## acceptance

`python3 src/RimMandrake/Utils/selftest_maturation_convergence.py` passes, and fails on the base commit: fixtures for a
falling, a flat and a rising stage, a missing round, an empty record and a malformed record (reads UNMEASURED, no crash);
the DIVERGING Needs Conductor line carries the numbers; MATURATION_NOW shows the table. Then the real table is run on
design/concepts and reported.
