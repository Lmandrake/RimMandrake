# RIMMANDRAKE_CALIBRATE_JUDGE_STOP_RULES_WORDS_UNTIL_RUN

## spec

The owner picked "Stop rule in every judge brief (Recommended)" by card on 2026-11-19 (answered about 6:29 PM PST,
item `RIMMANDRAKE_ENACT_TOUCHING_CODE_COSTS_SEE_IT_DO_IT`). The picked description, word for word: *"Why: it hits the
measured cause. About a dozen briefs (auditor, ops alarms, blind judges, art and coverage judges, sweeps) each get a
look count and a 'good enough' level. Cost: each brief needs a calibration run, or the rule is only words. Recommended
with the next option: the data favours the pair."* The card stamped: "Owed: needs a calibration run".

The enacting run wrote the stop rules (the level that is enough, when to stop looking, the polish route that files no
ticket) and ran no calibration. This item owes the calibration runs: one source event, one ticket.

Briefs that now carry a stop rule, and their calibration state on 2026-11-19 (`refusal_contract.status`):

| brief | stop rule | calibration family today |
|---|---|---|
| `src/RimMandrake/rimflow/roles/auditor.md` | §When the audit is enough: steps 3 and 4 stop after five SOUND picks in a row | none: a family with planted cases is owed |
| `src/RimMandrake/rimflow/roles/operations.md` | Alarm runs: "When an alarm run is enough" | none |
| `src/RimMandrake/Utils/findings_judge_prompt.md` | step 2: worth the touch, "Enough: each signature …" | none |
| `design/RimMandrake/scene_look_judge_brief.md` | §When the look is enough, and when to stop | `scene_look_judge_brief`, UNTESTED |
| `.claude/agents/rm-judge.md` | §When the look is enough, and when to stop | none |
| `design/RimMandrake/art_judge_brief.md` | NOT YET WRITTEN, on purpose (below) | `art_judge_brief`, CALIBRATED |

Written without an acceptance check here, and why:
- `src/RimMandrake/rimflow/roles/conductor.md` §Review briefs: the stop rule for the blind-challenge judge briefs that
  the Conductor writes. No fixed brief file exists to calibrate; a template file would be the way to calibrate it.
- `src/RimMandrake/rimflow/roles/designer.md` (DesignerCodex filed 33, 26 open, churn report §8): a filing rule. A
  family hashing the whole 277-line designer.md would reset on every Designer edit. The churn re-run on 2026-12-03
  (tables 3, 4b and 4c of the report) measures it instead.
- The coverage judge's prompt lives in `src/RimMandrake/rimflow/coverage_judge.py` (code, family `coverage_judge`,
  UNTESTED). It already stops at the second `not_covered`; its polish route is owed in code, under its own boundary
  page.

**Why the art judge brief has no stop rule yet.** `art_judge_brief` was CALIBRATED on 2026-11-19 at 14:00:26Z (11
planted cases). Any edit resets it to UNTESTED by its hash, and then its verdicts have no consequence until a model
run (`refusal_contract.advisory`). So the edit and its calibration run go in ONE sitting, here. The text to add, after
§Checklist (per subject):

```
## When the look is enough, and when to stop

- Enough: every picture and facing that you were given has one verdict (KEEP, REDO or UNSURE) with its evidence.
  Then stop. Do not look for more.
- One full inspection, then one check of the repairs: a re-judge after a regen looks only at the REDO lines and
  raises something new only where the regen itself changed it. Never a third look (`standing_rulings.md` §The judge
  refuses flaws, not polish). The danger this count guards: a judge asked again never stops (Pyrelands stage 5 took
  nine recorded looks, 2026-11-17).
- A REDO quotes a violated constraint. A wish that no constraint states is a `proposals` line: it files no ticket
  and blocks nothing.
```

Work: write a calibration family (planted good and bad cases, `judge_cases`) for each brief in the table that has
none, add the art judge text, then run `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --model <family>`
per family. A brief that comes out FAILED is reported with its case results; never edit a case to pass.

## criteria

Acceptance test: `python3 design/specs/2026-11-19-touching-code-cost/acceptance_stop_rules_calibrated.py` prints
`PASS 7/7` and exits 0. Watched on the filing base (2026-11-19): `FAIL 1/7`, exit 1 (only the art judge brief's
current CALIBRATED status passes; it lacks the stop rule). A planted root with every brief CALIBRATED at its hash and
the art text added read `PASS 7/7`; the same root with one brief edited after calibration read FAIL.

## verify

Run the acceptance test. Also `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --no-run` lists each
family's status without writing.
