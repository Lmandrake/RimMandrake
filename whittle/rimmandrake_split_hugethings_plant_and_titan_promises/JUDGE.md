# JUDGE: RIMMANDRAKE_SPLIT_HUGETHINGS_PLANT_AND_TITAN_PROMISES

Judge: CLAUDE_STEVEDESKTOP_OFFLINE5 (Relentless BUILDER_JUDGE seat), 2026-11-11. I did not read DONE.md or BROADEN.md.
Read: STATEMENT.md, NOTES.md, the item file, design/RimMandrake/hugethings_codex_2026-11-09/ANSWERS_OWNER.md
(answers 1-2), every file in evidence/ (all text; there are no images), the head of
src/RimMandrake/HugeThings/northstar/showcase_titan_live.py. I re-ran
`run_selftests.py --only src/RimMandrake/HugeThings/northstar/selftest_showcases.py --workers 1`: PASS 1/1, GREEN.

## A1 L0: implementation and specifications agree with the owner answer; focused offline checks pass. TRUE
- Owner answer 1 says two promises, each with its own demonstration. Answer 2 says the first demo is B: crossing, then
  death, then the crowd at the remains.
- evidence/a1_spec_split.txt (design/validation_walks/RimMandrake/HugeThings.md) has 4 plant must_show rows and 3 titan
  must_show rows. The titan rows are worded "first / then / then". cannot_show forbids `one_demo_for_both_promises` and
  `showcase_out_of_order`. That matches both answers.
- The code has separate drivers (showcase_plants_live.py, showcase_titan_live.py). The titan driver fixes
  order=["CROSSING","DEATH","CROWD"] and gates them: a phase that does not pass leaves every later phase UNMEASURED.
  The verbose output test_failed_crossing_gates_death_and_crowd shows that gate working.
- The offline checks pass: evidence/a1_selftest_showcases.txt is 3/3 GREEN, and my own re-run is 1/1 GREEN.
- Two notes, neither a disagreement. The spec is still DRAFT (not VALIDATED, no recorded hash). The offline tests run
  against a fake harness ("HARNESS fake preflight"), so they test the drivers' logic and say nothing about game
  behaviour. That is fine for L0.
- evidence/a1b_selftest_showcases_selection_probe.txt is byte-identical to a1_selftest_showcases_verbose.txt, so it
  adds nothing on its own.

## A2 L2: separate restored disposable-site demonstrations support both promises; titan showcase orders crossing, death, crowd. CANNOT TELL (not shown)
- evidence/ holds no live run of either showcase: no live_results JSON, no screenshots, no restore record, no per-phase
  start/end ticks. The newest code commit is "HugeThings showcases: review fixes before the first live run". That
  suggests neither demonstration has run yet.
- The PASS rows in the verbose files come from offline unit tests with fake inputs. They are not demonstrations.
- What would settle it: one restored disposable-site live run of each driver, with its raw results file and restore
  record. The plant run needs PASS on trunk-solid, cap-open, selection and door-seal-until-cut. The titan run needs
  CROSSING, DEATH and CROWD all PASS, in that order, with tick stamps showing the crowd arrives after the death. It
  also needs a couple of screenshots, so a still is not standing in for the crossing's motion.
- Staging: the titan driver records its own staging honestly (a spawned animal, a Goto order). That is acceptable for a
  showcase, but the judge must see it in the run record.

## Blank lines 3-5
These are empty bullets with nothing to judge.

## Overall
A1 is true. A2 is not shown at all, so the statement as a whole is not met. L4 feel stays with the owner in any case.

would show: no
