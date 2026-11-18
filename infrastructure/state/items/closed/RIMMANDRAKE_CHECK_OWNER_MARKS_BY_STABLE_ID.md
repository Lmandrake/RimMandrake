# RIMMANDRAKE_CHECK_OWNER_MARKS_BY_STABLE_ID

## spec

WHY: the owner approved the 23 Designer Cleanse proposals as THE PLAN (2026-11-17 9:04 PM PST). On Abyss and TheRot he
marked five capabilities, and those marks were folded into the two proposals at baaea8888a. The Conductor decided that
those two stay approved once a fresh review passes (OWNER.jsonl tsn 1794983843500059966). The apply program's
owner-marks guard parsed his markdown table, and it failed in every review round:
- bold headers and no outer pipes were skipped;
- "a letter that is not a fishery" matched the fishery mark;
- the fishery rule flipped between rounds.

This ticket replaces that parsing with a check by stable capability id against a machine-readable plan. It is its own
module and does not touch designer_cleanse.py. The apply command (RIMMANDRAKE_WRITE_CLEANSE_APPLY_ATOMIC_HOLD_UNTOUCHED)
will call it.

THE PLAN FILE: `design/concepts/CLEANSE_PLAN_OWNER_2026-11-17.json` (landed with this ticket's filing):
- `mods.<Mod>.approve`: "digest" (approved as it stood) or "fresh_review" (Abyss, TheRot).
- `approved_digest`: designer_cleanse.proposal_digest of `cleanse/` at a6f989bcda.
- `marks`: {census row id: "keep" | "next_version" | "drop"}.
- `excluded.Pyrelands`.

CONTRACT: new `src/RimMandrake/rimflow/cleanse_plan.py`.
- `plan_check(repo, mod, plan=None)` returns {"answer", "mod", "ids" (sorted list), "path"}. `answer` is one of:
  - PLAN_MISSING: no plan file.
  - PLAN_MALFORMED: not JSON, an unknown mark word, or an unknown approve kind.
  - EXCLUDED: Pyrelands.
  - NOT_IN_PLAN: the mod has no entry in the plan.
  - MARK_ROW_MISSING (ids): a marked id has no census.json row. Rows match by `id` only, never by text.
  - MARK_NOT_FOLDED (ids): the row's fate is not in the mark's class. keep = designer_cleanse.KEPT;
    next_version = "next_version"; drop = "recommend_retire".
  - CHANGED_SINCE_APPROVAL: approve "digest", and the current proposal_digest differs from approved_digest.
  - AWAITING_REVIEW: approve "fresh_review", and converge.json is not (applyable True, open [], digest = the current
    proposal_digest).
  - APPROVED.
  - COULD_NOT_LOOK (path): plan, census.json or converge.json exists but cannot be read.
- Order: reads first, then plan, then exclusion, then marks, then approval.
- It never reads owner_marks.md or any markdown.
- CLI `cleanse_plan.py check (<Mod> | --all) [--repo R] [--plan P]` prints one `PLAN <Mod> <ANSWER> [ids|path]` line per
  mod. Exit: 0 when all are APPROVED, 4 when any is COULD_NOT_LOOK, else 1.
- Do not change designer_cleanse.proposal_digest. Import it.

FILES: `src/RimMandrake/rimflow/cleanse_plan.py`, `src/RimMandrake/rimflow/selftest_cleanse_plan.py` (temp fixtures only;
it passes from a copy holding only src/RimMandrake/{rimflow,Utils,contracts}).

ACCEPTANCE TEST, written first and watched failing on base bab5b4087c (origin 3eb4de4094 at fetch):
`design/specs/2026-11-17-cleanse-apply-split/tickets/case_owner_marks.py`
- Its input kinds:
  - live --all: 21 APPROVED, Abyss and TheRot AWAITING_REVIEW.
  - Pyrelands; a mod not in the plan; BlueDesert unedited and with a census row removed.
  - TheRot: without a marks file; with pleasure_brew refated; with a current, a non-applyable or a stale converge.
  - Abyss: the fishery row removed, or renamed to warning_letter; fold_lamp and heat_observation refated; vine_turning
    under every KEPT fate.
  - a contradicting, bold-header or unreadable owner_marks.md (ignored).
  - census, converge or plan unreadable; plan missing; non-JSON; an unknown mark word; a --plan alternate; the sparse
    selftest.
- Base read: exit 1, `cases read 59; wrong 59 (worst: live --all); limit 0` (no module).
- Satisfiability: a 60-line reference sketch, NOT landed, read `cases read 62; wrong 1`. The one wrong was the missing
  selftest.

## verify
```
python3 design/specs/2026-11-17-cleanse-apply-split/tickets/case_owner_marks.py
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_cleanse_plan
python3 src/RimMandrake/rimflow/cleanse_plan.py check --all
```

## criteria
- C1 L0: case_owner_marks.py exits 0 and prints `wrong 0`, every case read.
- C2 L0: `run_selftests.py --only selftest_cleanse_plan` is green.
- C3 L0: the diff touches only cleanse_plan.py and selftest_cleanse_plan.py, and `check --all` prints 23 lines.

## refs
new: src/RimMandrake/rimflow/cleanse_plan.py
new: src/RimMandrake/rimflow/selftest_cleanse_plan.py
file: design/concepts/CLEANSE_PLAN_OWNER_2026-11-17.json
file: design/concepts/CLEANSE_PLAN_OWNER_2026-11-17.md
file: design/concepts/Abyss/cleanse/census.json
file: design/concepts/TheRot/cleanse/census.json
file: src/RimMandrake/rimflow/designer_cleanse.py
file: design/specs/2026-11-17-cleanse-apply-split/tickets/case_owner_marks.py
sha: baaea8888a
