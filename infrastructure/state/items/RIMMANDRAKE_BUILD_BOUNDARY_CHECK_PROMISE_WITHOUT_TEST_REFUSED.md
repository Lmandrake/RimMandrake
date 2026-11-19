## spec
Filed 2026-11-18 about midnight PST by the detached run on `RIMMANDRAKE_ENACT_PAGE_BEFORE_CODE_CONTROL_STORE_IS_PILOT`, as step 4 of that item: owed by the owner's
card of 2026-11-18 (`standing_rulings.md` §A boundary page before pipeline code). Not from a review finding.

Build `src/RimMandrake/Utils/boundary_check.py` (design `design/specs/2026-11-18-review-growth-cycle/01-design.md` section 5.2): it reads a boundary page, finds for each
promise `some-name` the test function `t_some_name`, and prints `promises covered N of M`. A promise with no test exits
1 and is named. A page it cannot read exits 3 (could not look is never "0 of 0"). `./publish` runs it for every page
(register it in `src/RimMandrake/Utils/pipeline_tests.json`). About 150 lines [guess ~60%, the design's].

The first page is `design/specs/2026-11-18-pipeline-control-surface/boundary.md`. Its promises name today's tests in prose ("Tested by"). This item also gives each promise a
test function of its own name in `selftest_control.py`; two exist already (`t_his_hold_refuses_launch`,
`t_void_never_moves_a_stage`). Renaming or wrapping an existing test is enough where it already tests the promise. The
design's "each test ships with one broken stand-in it must reject" is wanted where it is cheap, and is not part of this
acceptance test.

## refs
file: src/RimMandrake/rimflow/selftest_control.py
file: design/specs/2026-11-18-pipeline-control-surface/boundary.md
file: src/RimMandrake/Utils/pipeline_tests.json

## criteria
- `python3 src/RimMandrake/rimflow/acceptance/boundary_check_accept.py` exits 0 (4 checks).
- `./publish` runs the check (a row in `pipeline_tests.json`).

## verify
python3 src/RimMandrake/rimflow/acceptance/boundary_check_accept.py   # exit 0
Acceptance test: watched failing on a6aac8a6fc7c: 4 of 4 fail, the tool does not exist. Expected: 4 pass.
