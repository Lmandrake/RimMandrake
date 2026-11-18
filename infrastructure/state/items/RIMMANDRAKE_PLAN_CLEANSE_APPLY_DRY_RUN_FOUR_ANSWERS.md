# RIMMANDRAKE_PLAN_CLEANSE_APPLY_DRY_RUN_FOUR_ANSWERS

## spec

WHY: the owner approved the 23 Designer Cleanse proposals as THE PLAN (2026-11-17 9:04 PM PST,
`design/concepts/CLEANSE_PLAN_OWNER_2026-11-17.md`). The apply program for them
(RIMMANDRAKE_BUILD_CLEANSE_APPLY_PROGRAM_PLAN_APPROVED_NO_TOOL) stopped after 3 Codex rounds (3 -> 10 -> 8 findings), and
the Conductor split it (OWNER.jsonl tsn 1794983843500059966). This ticket is ONLY the dry-run planner: it works out what an
apply would write and refuses what must not be applied. Writing is RIMMANDRAKE_WRITE_CLEANSE_APPLY_ATOMIC_HOLD_UNTOUCHED.
The owner-marks check is RIMMANDRAKE_CHECK_OWNER_MARKS_BY_STABLE_ID. Neither is in scope here.

FINDINGS carried (review 3 of attempt 3, `codex_lane/RIMMANDRAKE_BUILD_CLEANSE_APPLY_PROGRAM_PLAN_APPROVED_NO_TOOL.attempt3_fix_first/review.txt`), each a named case:
- F1 a Designer run open on the concept refuses (DESIGNER_RUN_OPEN), and the planned stage.json withdraws a queued job:
  status "blocked", running None, blocked_on non-empty (a "ready" job no longer stays queued at the old stage).
- F5 later_version.md: the moved ids go in ONE marked section, `<!-- cleanse:next_version begin -->` ...
  `<!-- cleanse:next_version end -->`, written exactly once (a re-plan replaces the section rather than adding another).
  Text outside the markers is kept verbatim. With zero moved ids, no later_version.md is planned.
- F6 check runs on every plan, a retry included. tree.json records `cleanse.old_leaf_ids` (the old tree's leaf ids,
  [] for a new tree), and a retry reads that record, so an old bar the proposal does not map refuses (CHECK_FAILED).
- F7 a file that exists but cannot be read (scenes.json, converge.json, any input) answers COULD_NOT_LOOK and names its
  path; it is never treated as absent. A converge.json that is `{}` or 0 bytes is CONVERGE_EMPTY, distinct from
  CONVERGE_MISSING and NOT_CONVERGED.
- F8 the selftest needs nothing under design/: it passes from a copy holding only src/RimMandrake/{rimflow,Utils,contracts}.

CONTRACT:
- `designer_cleanse.apply_plan(repo, mod)` returns a dict with:
  - `answer`: one of WOULD_WRITE / NOTHING_TO_APPLY / REFUSED / COULD_NOT_LOOK.
  - `cause` (a word), `path` (for COULD_NOT_LOOK).
  - `files`: {relpath under design/concepts/<Mod>/: full text}.
  It writes nothing anywhere, and the same inputs give the same `files`.
- CLI `designer_cleanse.py apply <Mod> [--repo R]`: per-file lines, then one closing line `APPLY <Mod> <ANSWER> [CAUSE]`.
  `WOULD_WRITE` closes `APPLY <Mod> WOULD_WRITE <n> files`.
  Exit codes: 0 WOULD_WRITE, 3 NOTHING_TO_APPLY, 1 REFUSED, 4 COULD_NOT_LOOK.
  `--write` answers `APPLY <Mod> REFUSED WRITE_NOT_BUILT`, exit 1, and writes nothing (the next ticket builds it).
- Refusal order:
  1. Reads come first: any unreadable input is COULD_NOT_LOOK.
  2. Then PYRELANDS, NO_PROPOSAL, ZERO_KEPT, CHECK_FAILED, CONVERGE_MISSING, CONVERGE_EMPTY, NOT_CONVERGED,
     STALE_CONVERGENCE (converge digest absent or not proposal_digest), RESULT_NOT_APPLYABLE, DESIGNER_RUN_OPEN,
     VERSION_DOWNGRADE (VERSION.json already above 0.1.0).
- Planned files always include tree.json, sheet.md, stage.json and version/VERSION.json, plus later_version.md when ids
  move.
  - tree.json: every bars.json bar is a leaf; `cleanse.digest` = proposal_digest; `cleanse.old_leaf_ids` as above.
  - VERSION.json: version "0.1.0", `proposal_digest`, `replaces` (the prior version or null).
  - The moved parts are 0.2.0 inside the next-version section.
- The materialized plan loads through concept_tree.load and designer_stage.status (status blocked); check_dir gives no
  refs; a re-plan over it answers NOTHING_TO_APPLY.
- Read how designer_stage.py and concept_tree.py read a concept folder before choosing the shapes. Do not change
  proposal_digest (the owner plan's 21 approved digests are pinned to it).

FILES: `src/RimMandrake/rimflow/designer_cleanse.py`, `src/RimMandrake/rimflow/selftest_designer_cleanse.py`. No refactor.
Apply nothing to a real concept.

ACCEPTANCE TEST, written first and watched failing on base bab5b4087c (origin 3eb4de4094 at fetch):
`design/specs/2026-11-17-cleanse-apply-split/tickets/case_plan_dry_run.py`
- Its input kinds:
  - K1 BlueDesert proposal only; K2 Cauldron old tree, stage ready; K2 with an unmapped old leaf; a K2 retry with an extra
    old leaf id.
  - K3 GelatinousSlime blocked; K4 LeaningScrub locked with later_version.md; Contagion; K5 a run open; VERSION 0.2.0.
  - converge missing / {} / 0 bytes / not converged / no digest / stale digest; result not applyable; no proposal.
  - zero kept; zero moved; scenes.json and converge.json unreadable; Pyrelands; a re-plan; the sparse selftest.
- Base read: exit 1, `cases read 67; wrong 44 (worst: K1 BlueDesert dry run (seam)); limit 0`. The CLI exits 2 there
  (argparse: invalid choice 'apply'). The 23 cases that read right on base are the no-write guards and the
  sparse-selftest guard, and they must stay right.

PRIOR ATTEMPT (reference only, not to be landed as is): commit 9bfba3fad2, patch
`/mnt/d/ClaudeWork/rimmandrake/conductor/codex_lane/RIMMANDRAKE_BUILD_CLEANSE_APPLY_PROGRAM_PLAN_APPROVED_NO_TOOL.attempt3_fix_first/patches/0001-designer-cleanse-safely-apply-approved-concept-propo.patch`.

## verify
```
python3 design/specs/2026-11-17-cleanse-apply-split/tickets/case_plan_dry_run.py
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_designer_cleanse
```

## criteria
- C1 L0: case_plan_dry_run.py exits 0 and prints `wrong 0`, every case read.
- C2 L0: `run_selftests.py --only selftest_designer_cleanse` is green, and the selftest calls apply_plan on temp fixtures.
- C3 L0: the diff touches only designer_cleanse.py and selftest_designer_cleanse.py, and proposal_digest is unchanged.

## refs
file: src/RimMandrake/rimflow/designer_cleanse.py
file: src/RimMandrake/rimflow/selftest_designer_cleanse.py
file: src/RimMandrake/rimflow/designer_stage.py
file: src/RimMandrake/rimflow/concept_tree.py
file: design/specs/2026-11-16-designer-cleanse-and-bar-definition.md
file: design/concepts/CLEANSE_PLAN_OWNER_2026-11-17.md
file: design/specs/2026-11-17-cleanse-apply-split/tickets/case_plan_dry_run.py
sha: bab5b4087c
