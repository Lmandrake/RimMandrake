# RIMMANDRAKE_CALIBRATE_JUDGE_STOP_RULES_WORDS_UNTIL_RUN

## spec

The owner picked "Stop rule in every judge brief (Recommended)" by card on 2026-11-19 (answered about 6:29 PM PST,
item `RIMMANDRAKE_ENACT_TOUCHING_CODE_COSTS_SEE_IT_DO_IT`). The picked description, word for word: *"Why: it hits the
measured cause. About a dozen briefs (ops alarms, blind judges, art and coverage judges, sweeps) each get a
look count and a 'good enough' level. Cost: each brief needs a calibration run, or the rule is only words. Recommended
with the next option: the data favours the pair."* The card stamped: "Owed: needs a calibration run".

The enacting run wrote the stop rules (the level that is enough, when to stop looking, the polish route that files no
ticket) and ran no calibration. This item owes the calibration runs: one source event, one ticket.

Briefs that now carry a stop rule, and their calibration state on 2026-11-19 (`refusal_contract.status`):

| brief | stop rule | calibration family today |
|---|---|---|
| `src/RimMandrake/rimflow/roles/operations.md` | Alarm runs: "When an alarm run is enough" | none |
| `src/RimMandrake/Utils/findings_judge_prompt.md` | step 2: worth the touch, "Enough: each signature …" | none |
| `design/RimMandrake/scene_look_judge_brief.md` | §When the look is enough, and when to stop | `scene_look_judge_brief`, UNTESTED |
| `.claude/agents/rm-judge.md` | §When the look is enough, and when to stop | none |
| `design/RimMandrake/art_judge_brief.md` | §When the look is enough, and when to stop (written 2026-11-23) | `art_judge_brief`, CALIBRATED 2026-11-23 on 14 cases |

Written without an acceptance check here, and why:
- `src/RimMandrake/rimflow/roles/conductor.md` §Review briefs: the stop rule for the blind-challenge judge briefs that
  the Conductor writes. No fixed brief file exists to calibrate; a template file would be the way to calibrate it.
- `src/RimMandrake/rimflow/roles/designer.md` (DesignerCodex filed 33, 26 open, churn report §8): a filing rule. A
  family hashing the whole 277-line designer.md would reset on every Designer edit. The churn re-run on 2026-12-03
  (tables 3, 4b and 4c of the report) measures it instead.
- The coverage judge's prompt lives in `src/RimMandrake/rimflow/coverage_judge.py` (code, family `coverage_judge`,
  UNTESTED). It already stops at the second `not_covered`; its polish route is owed in code, under its own boundary
  page.

Work: write a calibration family (planted good and bad cases, `judge_cases`) for each brief in the table that has
none, then run `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --model <family>`
per family. A brief that comes out FAILED is reported with its case results; never edit a case to pass.

## criteria

Acceptance test: `python3 design/specs/2026-11-19-touching-code-cost/acceptance_stop_rules_calibrated.py` prints
`PASS 6/6` and exits 0 (7/7 until the Auditor brief was deleted, 2026-11-23). Watched on the filing base (2026-11-19): `FAIL 1/7`, exit 1 (only the art judge brief's
current CALIBRATED status passes; it lacks the stop rule). A planted root with every brief CALIBRATED at its hash and
the art text added read `PASS 7/7`; the same root with one brief edited after calibration read FAIL.

## verify

Run the acceptance test. Also `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --no-run` lists each
family's status without writing.
