# TESTER_PROMPT_TUNE_REJECTS_MOST_GOOD_WORK

Filed (BENCH): ralph_a `TESTER.md` rejects 23/30 known-good candidates (tier-A 5/8) while catching 3/9 planted
defects, no better than chance. Tune before day 1 of the architecture trial, or every arm's throughput is throttled by
tester noise. Day-0 prep for `design/RimMandrake/architecture_switch_harness_2026-10-29.md` §4.2.

## verify
- L0: the tuned TESTER.md re-run on the same frozen calibration set (the 30 known-good and 9 planted-defect
  candidates, unchanged): known-good acceptance and planted-defect catch rate each reported with their interval.
- L0: the tuned tester beats the old one on both rates, or the item says which rate it trades and why; a tester no
  better than chance on planted defects is not done.
- The calibration set and the scoring are not edited to pass; run by an agent other than the tuner.
- Stopping point: finish (before trial day 1).

## criteria
- A1 L0: re-run on the unchanged calibration set, both rates reported with intervals
- A2 L0: planted-defect catch rate better than chance, known-good rejection below the old 23/30
