# The set-down judge on the 25 real set-downs: agreement with the Conductor's classes

Run at 2026-11-25 12:51 PST by `python3 src/RimMandrake/rimflow/set_down_calibration.py` (item `RIMMANDRAKE_TIGHTEN_SET_DOWN_CLASSES_ANY_TWELVE_LETTERS_PASS`). The cases and the rebuilt labels are in `set_down_cases.json` beside this file; each label is a reconstruction from the Conductor's counts, and `unsure` marks the two that the counts do not fix. A `could not judge` counts as a pass (the door passes it). The judge binds at most 3 disagreements of 25 (the Conductor's ruling).

**Measured: 21 of 25 agree; 4 disagree (cases 1, 10, 11, 16).** Longest call: 20 s; median: 14 s.
Within the bind rule: no.

`program` is filing_gate.decide on the same words (it binds now). `gate` is program and judge together: refuse when either refuses; in bold where it differs from the Conductor's class.

| n | class | Conductor's class | judge | agree | program | gate | the judge's missing part, or why it could not judge | s |
|---|---|---|---|---|---|---|---|---|
| 1 | no-tool | pass | REFUSED | **no** | pass | **refuse** | The run has the companion's C# source, a free game and restart access, so a missing bridge tool is its own to build, and the second reason (colony scenes retire | 14.2 |
| 2 | owner-act | refuse | REFUSED | yes | refuse | refuse | The set-down names no owner act: the cause is known and the fix is a plain label edit that the run already wrote a failing check for. Sorting the item onto the  | 13.3 |
| 3 | no-tool | refuse | REFUSED | yes | refuse | refuse | A missing scene is the run's to build unless the set-down shows why this run cannot, and it does not; a held game is not a missing tool, and the game_lock query | 13.9 |
| 4 | fix-unknown | refuse | REFUSED | yes | refuse | refuse | The cause is not unknown: the set-down names it (no TESTQ_ARCHMAGI=1, and a profile filter that admits only full-list). Calling the fix a 'routing design choice | 13.9 |
| 5 | fix-unknown | refuse (unsure) | REFUSED | yes | refuse | refuse | No experiment tested the bystanders' cause: the lead theory (a social fight) and the claimed Player.log reading have no command behind them. The pause stops new | 16.9 |
| 6 | owner-act | refuse | REFUSED | yes | pass | refuse | The set-down names its own fix (b) that keeps every bar, so no bar has to be made looser; a call of the Conductor is not one of the owner's five acts, and a cho | 15.9 |
| 7 | fix-unknown | refuse | REFUSED | yes | refuse | refuse | The cause is known (the judge reads only the contract, not the scene's final PASS/FAIL line), and the set-down offers a choice between two known fixes; that is  | 14.7 |
| 8 | fix-unknown | refuse | REFUSED | yes | refuse | refuse | The cause is known and named (the judge reads only the contract), and the set-down offers two known fixes, so this is a choice between known fixes, not an unkno | 15.2 |
| 9 | no-tool | pass | could not judge | yes | pass | pass | the transcript of the filing run could not be found | 0.0 |
| 10 | fix-unknown | pass | REFUSED | **no** | refuse | **refuse** | The set-down names its own next experiment: time each step inside apply_rows (fresh /proc snapshot, tree signature, corpus refresh, borrower re-walk) on one dry | 12.9 |
| 11 | fix-unknown | refuse | PASS | **no** | refuse | refuse |  | 19.0 |
| 12 | owner-act | refuse | REFUSED | yes | refuse | refuse | The stated reason is a Conductor decision, and a call of the Conductor is not one of the owner's five acts. The run did not show that visit 13 is live, and it d | 20.4 |
| 13 | other-mod | refuse | REFUSED | yes | refuse | refuse | The fault is in shared pipeline code (rimflow/model.py), not in another mod, and nothing in the digest shows that this run may not edit it. The set-down itself  | 18.3 |
| 14 | fix-unknown | refuse | REFUSED | yes | refuse | refuse | The cause is known: a stale marker from a run that has ended, with the game lock FREE. The set-down names two known fixes and says it tried neither. A choice be | 11.8 |
| 15 | fix-unknown | refuse | REFUSED | yes | refuse | refuse | The set-down says outright that the run never looked for the cause: it found the check's source, src/RimMandrake/FlowWorks/validation.py, and then filed instead | 9.3 |
| 16 | fix-unknown | pass (unsure) | REFUSED | **no** | refuse | **refuse** | The digest shows no experiment aimed at the cause of the 619 unread cells, so the cause is unknown only because it was never searched; it was not shown unknown  | 13.4 |
| 17 | other-mod | pass | PASS | yes | pass | pass |  | 13.9 |
| 18 | owner-act | pass | PASS | yes | pass | pass |  | 10.3 |
| 19 | fix-unknown | pass | PASS | yes | refuse | **refuse** |  | 19.2 |
| 20 | fix-unknown | refuse | REFUSED | yes | refuse | refuse | The cause is known and the set-down names a choice between two known fixes, which is not an unknown cause; and fix (b), a lapse rule in maturation_rescue.py wit | 13.6 |
| 21 | fix-unknown | refuse | REFUSED | yes | refuse | refuse | No experiment aimed at any row's cause was run. The set-down only sorts the symptoms from the result file, and it names live experiments that this run could hav | 16.9 |
| 22 | fix-unknown | refuse | REFUSED | yes | refuse | refuse | No experiment aimed at the cause was run: the theories (the trap or the blood on the centre cell refusing the filth, the plan's scar kind and size) are named bu | 14.5 |
| 23 | fix-unknown | refuse | REFUSED | yes | refuse | refuse | No theory of the cloud's cause was tested: the run only saw it in pictures. Its own acceptance test names the experiment it had the tools to run: a lone EMP bla | 12.8 |
| 24 | other-mod | refuse | REFUSED | yes | refuse | refuse | The fault is in ExplosiveKnockback, the very mod this run works on, so other-mod is false. The set-down names a known fix, its files and its acceptance test, al | 14.0 |
| 25 | other-mod | refuse | REFUSED | yes | refuse | refuse | The work belongs to ExplosiveKnockback, the mod this run is driving, so other-mod does not hold, and the digest shows the run had the proof build, the game and  | 15.2 |
