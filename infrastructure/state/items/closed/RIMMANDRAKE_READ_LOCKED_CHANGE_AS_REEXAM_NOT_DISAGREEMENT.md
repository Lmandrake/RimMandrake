# RIMMANDRAKE_READ_LOCKED_CHANGE_AS_REEXAM_NOT_DISAGREEMENT

## Defect
MATURATION_NOW listed "Pyrelands: files disagree: VERSION.json says locked; stage.json still says ready at Designer
step 4 (Exam)" (earlier the same day: "blocked at Designer step 5 (Lock)"). Both files were right: his card changed the
locked 0.1.0 (`designer_stage.py repin` writes a `locked_change` history entry and voids the stale stage's exam), so the
Designer retakes stage 4 on a version that stays locked. `maturation_now.disagreements()` did not know that state.

## Fix
A stage.json whose history holds a `locked_change` with no Designer `lock` after it is the re-exam of a locked change,
not a disagreement. A `lock` after it, then a non-locked status, disagrees again. No writer was wrong; no file repaired.

## Acceptance test
`python3 src/RimMandrake/Utils/selftest_maturation_now.py` -> `ALL PASS`. Its p7 checks "a locked change back in the
Designer is not a disagreement" (FAILED on base 0c28b2596e, watched) and "a Designer lock after the locked change, then
not locked: they disagree again"; a mutant that ignores the later lock turns the second red (watched).
