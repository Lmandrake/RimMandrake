## spec
Filed 2026-11-19 by the detached run on `RIMMANDRAKE_SHARE_PROBE_RESULT_TYPE_NINE_FILES_ROLL_OWN`, as step 5 of its brief. Not
from a review finding.

The files under `src/RimMandrake/rimflow` and `src/RimMandrake/Utils` that define their own `Unreadable` or `Unmeasured`
class answer through `src/RimMandrake/rimflow/probe_result.py` instead: their reads return `value`, `empty`,
`could_not_look(cause)` or `failed(cause)` (or let `NotAnswered` raise), and the file's own class goes.

The parent item counted 9 files; the scan reads 10 besides `control.py`, because it walks subfolders
(`Utils/northstar_driver/bars.py`) [measured 2026-11-19]: `boundary_check`, `findings_fold`, `heap_bisect`,
`northstar_driver/bars`, `running_now`, `scratch_reap` (Utils); `conductor_closeout`, `mod_owner_hold`,
`pipeline_control`, `pipeline_pause` (rimflow). `control.py` keeps its `Unreadable` (the store's raise inside `txn()`);
its systemd and cgroup reads moved in f5b06712b7a8. A file that is pipeline machinery owes its boundary page when it is
changed (`design/RimMandrake/standing_rulings.md` §A boundary page before pipeline code).

## refs
file: src/RimMandrake/rimflow/probe_result.py
file: design/specs/2026-11-19-probe-result/boundary.md

## criteria
- `python3 src/RimMandrake/rimflow/acceptance/own_unreadable_classes_gone_accept.py` exits 0 (1 check).

## verify
python3 src/RimMandrake/rimflow/acceptance/own_unreadable_classes_gone_accept.py   # exit 0
Acceptance test: watched failing on f5b06712b7a8: 10 files named. Expected: PASS.
