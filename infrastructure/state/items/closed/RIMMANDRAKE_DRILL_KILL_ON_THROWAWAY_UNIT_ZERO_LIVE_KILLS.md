## spec
Filed 2026-11-18 about midnight PST by the detached run on `RIMMANDRAKE_ENACT_PAGE_BEFORE_CODE_CONTROL_STORE_IS_PILOT`, as step 4 of that item: owed by the owner's
card of 2026-11-18 (`standing_rulings.md` §A boundary page before pipeline code). Not from a review finding.

Run the kill path for real, once, and keep the drill as a script (design `design/specs/2026-11-18-review-growth-cycle/01-design.md` sections 5.4 step 3 and 6 step 5;
promise kill-verified-dead on `design/specs/2026-11-18-pipeline-control-surface/boundary.md`). By the evening of 2026-11-18, 0 of the 15 live stops on the store's books had
used `--kill` [measured by the analyst, `D:\ClaudeWork\rimmandrake\conductor\control_review_rounds_real_or_treadmill_20261118.md`],
while four reviews argued about that path.

The drill (`src/RimMandrake/rimflow/control_kill_drill.py`, to be written) starts a throwaway `rm-probe-drill-*` unit with
a child process in real systemd through `launch_unit`, on a store of its own (`RM_CONTROL_DB`), never the live one. It
runs `pipe stop <unit> --kill` and prints one line: `DRILL PASS <unit> killed in <N> ms; N processes gone; run recorded
killed`, or `DRILL FAIL` with the cause. When systemd cannot be reached it prints `DRILL UNMEASURED` and exits 3: that
is not a pass. A drill failure is a broken promise: red test first, then the fix, in the same run.

## refs
file: src/RimMandrake/rimflow/control.py
file: design/specs/2026-11-18-pipeline-control-surface/boundary.md

## criteria
- `python3 src/RimMandrake/rimflow/acceptance/control_kill_drill_accept.py` exits 0.
- The drill's printed line is on this item as a note, with its milliseconds [measured].

## verify
python3 src/RimMandrake/rimflow/acceptance/control_kill_drill_accept.py   # exit 0
Acceptance test: watched failing on a6aac8a6fc7c: the drill script does not exist. Expected: 1 pass.
