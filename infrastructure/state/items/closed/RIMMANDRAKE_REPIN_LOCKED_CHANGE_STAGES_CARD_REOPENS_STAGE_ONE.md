# RIMMANDRAKE_REPIN_LOCKED_CHANGE_STAGES_CARD_REOPENS_STAGE_ONE

Found 2026-11-14 by the detached helper RIMMANDRAKE_SIT_PYRELANDS_OWED_EXAM_AND_JUDGE_LOCKED_FIRST. Refusal record:
`design/concepts/Pyrelands/version/evidence/exam_and_judge_refusal_2026-11-14.json` (clause `stale_root_reopens_stage_1`).

**Problem.** A Design Version locked by his word (`version/VERSION.json` state `locked`) can still be changed by his own
card (Pyrelands, 2026-11-14 "Drop the sentence", commit f71693d77a: root, tree, sheet, scenes). The Designer stage machine
cannot tell that from new design input: `designer_stage.stale_stage` returns `(1, ['root'])`, so the next `open_run`
reopens stage 1 (Argue the idea), discards the accepted stage 1-3 results, and `chain_stages` re-runs stages 1, 2, 3 before
the exam he ordered ("they still owe it. One exam and one coverage judge pass each on the locked tree, no loop"). Three
Designer rework runs on a locked tree is the loop he ruled out.

## spec

A `designer_stage.py` verb (e.g. `repin --source OWNER:<tsn> <dir>`) that, for a concept whose
`version/VERSION.json` is `locked`, rewrites the accepted results' `inputs` to the current `inputs()` hashes when the
cited OWNER event exists and names the concept's item or its ADVANCE item; it records a `locked_change` history row and
refuses with no OWNER source, a non-OWNER source, or an unlocked version. The exam (stage 4) is then the open stage.

## verify

Acceptance test (a selftest on a fixture copy of `design/concepts/Pyrelands`, ext4 scratch, never /tmp):
1. Before the verb: `DS.stale_stage(fixture, st)` returns `(1, ['root'])` (watched on the base 2026-11-14 9:40 PM PST on the
   real concept: `stale 1 ['root']`).
2. `repin --source OWNER:1794721014843506307` on the fixture with VERSION.json locked: `stale_stage` returns `(None, [])`
   and `st['stage'] == 4`.
3. The same verb with `--source CONDUCTOR:<tsn>`, with no source, and with VERSION.json state `draft`: each refuses and
   leaves stage.json byte-identical.
Expected: 3 checks pass. Fails on base: step 2 cannot run (no verb).
