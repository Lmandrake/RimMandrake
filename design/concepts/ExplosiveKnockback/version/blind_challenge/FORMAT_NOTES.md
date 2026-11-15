# Blind challenge (Stages 4 and 5): format notes from the first run

Written by the cycle-1 blind agent on Explosive Knockback 0.1.0, 2026-11-14, for the next three mods. These are
proposals from one run (n = 1), not rules.

## The record, one folder per cycle

```
version/blind_challenge/cycle_<N>/
  SUMMARY.md                 one page: counts per lane, fixes with shas, tests edited, unsettled, exit judgement
  lane1/<Blind>.cs|py        the blind agent's own tests (kept: the next judge reruns them)
  lane1/run_lane1.py         one command; --kernel <file> runs them against any kernel (planted faults reuse it)
  lane1/lane1_rows.jsonl     one row per test: id, bar(s), kind (fixed|random|sweep|info|not_kernel), verdict
                             (PASS|FAIL|INFO|UNSETTLED), cases, detail (a failing random case carries its seed and its
                             shrunk form)
  lane2/rerun_offline.py     reruns every kind=offline test of test_table.json, compares with runs_today
  lane2/reruns.jsonl         one row per test: result, recorded_result, last, recorded_last, match
  lane2/planted_faults.json  the faults: id, file, old, new (exact one-occurrence text), bars
  lane2/plant_faults.py      plants each in turn, runs the deciders + lane 1, restores byte for byte, proves the tree clean
  lane2/planted_results.jsonl  per fault: which suites went red; baseline first; tree_clean_after last
  lane2/faults.json          refusal records: id, class Problem|Polish, bar, criterion, evidence[], would_pass,
                             smallest_fix, verdict_on_criterion, status (PENDING|FIXED <sha>|NOTED_FOR_CONDUCTOR)
  lane2/fixes.jsonl          per Problem fixed: fault id, red (command, rc, line on the old code), green (same on new), sha
  tests_edited.json          every test file the fixer changed: path, why, before/after hash
```

## What each lane really needed

- **Lane 1** needed: `sheet.md` (the bars in words, the delegated numbers), `tree.json` (each leaf's oracle: it carries the
  exact expected numbers, e.g. rat 5 / colonist 3 / muffalo 2), `plan.md` (where a number came from, e.g. "1.6x the person
  kernel"), the kernel file, and the settings file for **defaults and slider ranges** (the sweep is pointless without the
  ranges). It also needed the def patch with the per-type forces (fire 0.5): "settings as shipped" must include it.
  It did **not** need `scenes.json` (82 kB) or `VERSION.json` beyond the version number.
- Lane 1 could not decide 8 of 29 leaves offline (flight, hose, gas clumps, cover, fetching, Harmony scope, teleport
  trace, the walk): those rows are written `UNSETTLED` with the reason, so the absence is a decision.
- **Lane 2** needed: `test_table.json` (`tests.*.command`, `runs_today`, `kind`, `partial`, `known_red`; `bars.*.proves_at`
  and `offline_decides`), the game-side code that **calls** the kernel (this is where both Problems were: the kernel was
  right, its callers were short of the bar), and the journal's open-question list (to avoid judging questions the owner
  holds). The proof scenes (2 400 + 860 lines) were not needed offline.

## Boring enough for a program next time

1. **Reruns**: `rerun_offline.py` is generic over any mod's `test_table.json`. It should become the steward's tool.
2. **Planted faults**: the plant/run/restore/prove-clean loop is generic; only `planted_faults.json` is mod-specific, and
   most of it is mechanical (flip a comparison, drop a factor, swap an order, change a default). A program can
   propose the list from the kernel (every `<`/`<=`, every `Math.Max`, every default literal); the agent adds the
   meaning-bearing ones (the rule each bar states).
3. **Lane 1's harness** (random grids, shrinker, row writer) is reusable across mods with a kernel; the properties are not.
4. **The exit check** below.

Traps met: (a) the harness killed mid-fault left the fault in the tree: restore on signal, and prove `git diff --quiet`
after; (b) lane 1's own baseline had a FAIL, so "caught" must mean *a new failing row*, not a red exit code; (c) the
builder's kernel selftest copies into a machine-wide staging folder before locking: run planted faults with
`WINBUILD_ROOT` set to a private folder; (d) the recorded `last` line was truncated or taken from stderr, so a rerun
compare must accept a recorded prefix and compare verdicts first.

## Making the exit test machine-checkable

The exit is "every offline bar green, no Problem found". From the record a program needs:

- `test_table.json` bars with `proves_at` in {2, 4-5} (the offline bars) and their `decides`; a fresh rerun of each
  decider (`reruns.jsonl`, not `runs_today`, which may be stale) with `result == PASS`.
- `faults.json` with no fault of class `Problem` whose status is not `FIXED <sha>`; and for each FIXED one a `fixes.jsonl`
  row whose red rc is non-zero on the parent sha and green rc is zero on the fix sha (`red`/`green` one run
  `{on, cmd, rc, line}` or a list of them; a later row for the same fault replaces an earlier one).
- `lane1_rows.jsonl` with no `FAIL` (an `UNSETTLED` row is not a failure of this stage; it is owed to Stage 6), or,
  since lane 1 stays as recorded (blind, before the fixes), each of its FAIL rows PASS in `lane2/lane1_rows_after_fix.jsonl`,
  lane 1 rerun at the fix sha with no FAIL.
- A `kind: record` decider has a `command` (`src/RimMandrake/rimflow/record_check.py`: the event is still there, its line's
  hash unchanged) and is rerun like any other; `not_rerunnable` never meets the exit.
- `tests_edited.json` present (possibly empty) so the next judge is shown every weakened test.
- `planted_results.jsonl` ending in `tree_clean_after: true`.

One judgement stays human-or-agent: whether a fault is a Problem or Polish. Everything else above is a file check.

## Two things the guards on fix-in-place did not foresee

- **A fix can need bar text.** The smallest honest fix for "goods fly about 1.6x" was a Mod Setting, but a new saved
  setting turns a builder test red until a locked scene's action names it, and the fixer may not edit scene text. Cycle 1
  shipped a constant and wrote the slider up for the Conductor. Next time, say in the brief which way to go.
- **The blind order works, and it is where the Problems came from.** Both code Problems were seen first in lane 1 (an INFO
  row: "nothing in the kernel or settings makes goods fly farther"; a sweep reasoning about the cap scale), then confirmed
  in lane 2 by reading the callers. Lane 1 alone could not have called them: the kernel was right; its callers were short.

## Cost of this run (for budgeting)

About $9 of a $20 bound [measured, the session's budget line]. Lane 1 landed at 21:37 PST; the second, complete
planted-fault loop ended at 21:56 (43 faults x 8 suites, under 15 minutes); the fixes landed at 22:00 and the record at
about 22:05 [measured from commit and file times]. Lane 1's own start time was not recorded: record it next time.
