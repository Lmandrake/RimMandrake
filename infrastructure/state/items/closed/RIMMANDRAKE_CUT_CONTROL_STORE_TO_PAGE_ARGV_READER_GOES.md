## spec
Filed 2026-11-18 about midnight PST by the detached run on `RIMMANDRAKE_ENACT_PAGE_BEFORE_CODE_CONTROL_STORE_IS_PILOT`, as step 4 of that item: owed by the owner's
card of 2026-11-18 (`standing_rulings.md` §A boundary page before pipeline code). Not from a review finding.

Cut `src/RimMandrake/rimflow/control.py` to its boundary page, once, by one run (design `design/specs/2026-11-18-review-growth-cycle/01-design.md` section 6 step 4; the
page: `design/specs/2026-11-18-pipeline-control-surface/boundary.md`). Where the page puts an input outside ACCEPTS, refuse it by name and delete its handling. A launch names
its unit as a field of its spec, so the reader of `systemd-run`'s own options (`_sr_unit`, `SR_VALUE_OPTS`, written
2026-11-18 to answer a review claim and then faulted itself) goes. All 9 launch call sites are ours and use one form
[measured, `00-problem.md` of that design].

🔴 Not before one fresh reader that did not write the page has read it and its holes are settled: the Conductor
launches that read. One run at a time edits `control.py`. Prefer deleting code. `control.py` is live for every launch:
run its selftests and `./pipe show` after the landing, and revert the landing first if a launch check goes red.
No Codex or GPT review of the result (his stop of 2026-11-18 8:22 PM PST stands).

## refs
file: src/RimMandrake/rimflow/control.py
file: design/specs/2026-11-18-pipeline-control-surface/boundary.md

## criteria
- `python3 src/RimMandrake/rimflow/acceptance/control_cut_to_page_accept.py` exits 0 (4 checks).
- `run_selftests.py --only selftest_control` is GREEN and `./pipe show` answers after the landing.
- Every promise on the page still has its passing test; no promise was dropped to make the cut.

## verify
python3 src/RimMandrake/rimflow/acceptance/control_cut_to_page_accept.py   # exit 0
Acceptance test: watched failing on a6aac8a6fc7c: 3 of 4 checks fail. Expected: 4 pass.
