## spec
Filed 2026-11-19 by the detached run on `RIMMANDRAKE_SHARE_PROBE_RESULT_TYPE_NINE_FILES_ROLL_OWN`, as step 5 of its brief. Not
from a review finding.

Switch `src/RimMandrake/Utils/could_not_look_lint.py` at `./publish` from shadow to refusing. Since a439e73a7c97 it runs
as a shadow check in `src/RimMandrake/Utils/publish_tree_checks.json` (`"shadow": true`, `--shadow`): publish prints
its last line and refuses nothing. 299 places in 30 of 39 pipeline files sit on its counted allowlist
`src/RimMandrake/Utils/could_not_look_allowlist.json` [measured 2026-11-19 after f5b06712b7a8]; a count is a list of
places to read, not a count of bugs. Arming it: drop `shadow` and `--shadow` from its row; a NEW place then refuses a
publish. Before arming, the Conductor decides whether the 299 stay allowed as they are or some are read first.
The page's promise `lint-shadow-refuses-nothing` describes tonight's wiring, so arming changes the page: that is
next-version work for `design/specs/2026-11-19-probe-result/boundary.md`.

## refs
file: src/RimMandrake/Utils/could_not_look_lint.py
file: src/RimMandrake/Utils/publish_tree_checks.json

## criteria
- `python3 src/RimMandrake/rimflow/acceptance/could_not_look_lint_armed_accept.py` exits 0 (3 checks).

## verify
python3 src/RimMandrake/rimflow/acceptance/could_not_look_lint_armed_accept.py   # exit 0
Acceptance test: watched failing on f5b06712b7a8: 1 of 3 fails (the row is shadow). Expected: 3 pass.
