# RIMMANDRAKE_BUILD_CLEANSE_APPLY_PROGRAM_PLAN_APPROVED_NO_TOOL

## spec

WHY: the owner approved the 23 Designer Cleanse proposals as THE PLAN (2026-11-17 9:04 PM PST; `design/concepts/CLEANSE_PLAN_OWNER_2026-11-17.md`). `design/specs/2026-11-16-designer-cleanse-and-bar-definition.md` section 4 "Applying a proposal" names a program that writes the new tree, sheet and next-version file from a proposal; it was never built (`designer_cleanse.py` has no apply verb).

BUILD: `python3 src/RimMandrake/rimflow/designer_cleanse.py apply <Mod> [--write]`, in `designer_cleanse.py` only (plus its selftest).
- Default is a dry run: print, per file under `design/concepts/<Mod>/`, what would be created, replaced or removed, and one closing verdict line `APPLY <Mod> WOULD_WRITE n files` or `APPLY <Mod> REFUSED <cause>`; write nothing.
- `--write` does it, inside the concept folder only, and prints `APPLY <Mod> WROTE n files`.
- REFUSE, each with its own cause word and non-zero exit, writing nothing: no proposal; `converge.json` missing or not converged; `result.json` not applyable; `check` fails; an `owner_marks.md` exists whose marks the proposal does not yet reflect (a marked id whose fate in `census.json` differs from his mark: cause `OWNER_MARKS_NOT_FOLDED`, naming each id); the mod is Pyrelands.
- It never files tickets, never launches anything, never touches `mod_owner_hold.json`, a pipeline state file or any source under `src/RimMandrake/<Mod>/`. Filing the proposal's tickets is a later ticket.
- The Design Version written is 0.1.0 for the kept parts; the moved parts land in the concept's next-version file as 0.2.0.
- Read how the stage machine and `concept_tree.py` read a concept folder BEFORE choosing what to write: an applied concept must load in `designer_stage.py` status without error. Say in the report which files those readers need and that you loaded one applied concept through them.
- "Could not look", "failed", "zero" and "empty" stay different outcomes in every return value and line.

FILES: `src/RimMandrake/rimflow/designer_cleanse.py`, `src/RimMandrake/rimflow/selftest_designer_cleanse.py`. No refactor. Apply nothing to a real concept in this ticket: the dry run on the 23 is the Conductor's next step.

## verify

Acceptance test (builder writes the cases FIRST and watches them fail on base, where the verb does not exist; say so in the report): `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_designer_cleanse` green, with new cases on fixture concepts in a temp dir covering: dry run writes nothing (tree hash unchanged); `--write` writes only inside the concept folder; each refusal cause above, one case each, each leaving the tree unchanged; a proposal with zero moved parts; a proposal with zero kept parts refused; an applied fixture loads through the stage reader. Each new guard is shown red on a deliberately broken input.
