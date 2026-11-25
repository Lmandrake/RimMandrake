# Codex code reviews of six pipeline files with no page, counted by the reader (2026-11-24 evening)

Run: `RIMMANDRAKE_FEED_CODEX_THIRD_LANE_NINETY_SIX_LEFT_IDLE`. Six read-only Codex reviews under
`src/RimMandrake/rimflow/roles/code_review.md`, with one change: the file has no boundary page, so its page is its own
docstrings and comments. Prompts and raw answers: `D:\ClaudeWork\scratch\codex3\reviews\<file>\`.

The question this record answers: does Codex obey the brief's significance rule? Before this run it was UNMEASURED.

## The count

"Significant" is the reader's call by the brief's rule. "Shown" is a test that went red on the old code and green
on the fix, run by the reader. A wrong test is shown when it is fixed.

| file | findings | Codex: Problem | reader: significant | shown | landed |
|---|---|---|---|---|---|
| `src/RimMandrake/Utils/boundary_check.py` | 2 | 1 | 1 | 1 | f52ea9665a |
| `src/RimMandrake/Utils/owner_queue.py` | 6 | 5 | 5 | 5 (4 red, 1 wrong test fixed) | f52ea9665a |
| `src/RimMandrake/Utils/scene_fake.py` | 4 | 3 | 0 | - | - |
| `src/RimMandrake/Utils/testq/gaps.py` | 3 | 3 | 3 | 3 | f609d765a9 |
| `src/RimMandrake/Utils/art_eval/runner.py` | 4 | 4 | 4 | 4 (3 red, 1 missing test added) | c525f87ccf |
| `src/RimMandrake/Utils/scratch_reap.py` | 3 | 2 | 2 | 2 | 86096dded |
| **all six** | **22** | **18** | **15** | **15** | |
| first three reviews read | 12 | 9 | 6 | 6 | |

- Codex called 3 findings Problems that the reader judged not significant: the three `scene_fake.py` ones. Each is
  true (the fake's replies differ from the wire page), but Python reads neither field, so no verdict, record or gate
  comes out wrong.
- Codex called 1 finding polish that was a real red on main: `selftest_boundary_check.py` failed because
  `design/specs/2026-11-24-live-gate-on-pipeline-host/boundary.md` was not in `PAGES`. Fixed at 1a3ca1df11.
- Every finding Codex returned with a full trace and a call site that the reader judged significant was shown true.
  So Codex is accurate about what is true, and it is generous about what is significant: 18 called, 15 kept (83%).

## Polish (one line each; nobody fixes these)

- `scene_fake.py:281` session bind acknowledged without storing the group or returning `bound` (Python reads neither).
- `scene_fake.py:297` a closed run's status reply says `rows: 5` for six records and omits `values` (Python rebuilds both).
- `scene_fake.py:266` two sessions opened in one process share the id `g1`.
- `scene_fake.py:302` not handled: a run on the fake's newer hand stays live after `jawa/run_until cancel`.
- `owner_queue.py:416` not handled: `write_view()` raises if its own directory setup fails.
- `scratch_reap.py:2951` `--sanity` creates the state directory when it does not exist.
- `testq/gaps.py` a FAILed chain whose FAIL rows belong to two items gets no fix pick (the plan names it); a per-row
  retest would need `brake_release.canary_request` to keep row keys.
