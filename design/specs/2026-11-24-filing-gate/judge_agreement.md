# The set-down judge on the 25 real set-downs: agreement with the Conductor's classes

Run at 2026-11-25 11:52 PST by `python3 src/RimMandrake/rimflow/set_down_calibration.py` (item `RIMMANDRAKE_TIGHTEN_SET_DOWN_CLASSES_ANY_TWELVE_LETTERS_PASS`). The cases and the rebuilt labels are in `set_down_cases.json` beside this file; each label is a reconstruction from the Conductor's counts, and `unsure` marks the two that the counts do not fix. A `could not judge` counts as a pass (the door passes it). The judge binds at most 3 disagreements of 25 (the Conductor's ruling).

**Measured: 20 of 25 agree; 5 disagree (cases 1, 10, 11, 16, 19).** Longest call: 26 s; median: 15 s.
Within the bind rule: no.

`program` is filing_gate.decide on the same words (it binds now). `gate` is program and judge together: refuse when either refuses; in bold where it differs from the Conductor's class.

| n | class | Conductor's class | judge | agree | program | gate | the judge's missing part, or why it could not judge | s |
|---|---|---|---|---|---|---|---|---|
| 1 | no-tool | pass | REFUSED | **no** | pass | **refuse** | The set-down shows that the bridge function is missing, but not that this run cannot build it. The run has the companion's C# source (JawaBench.BridgeTools/*.cs | 15.2 |
| 2 | owner-act | refuse | REFUSED | yes | refuse | refuse | The fix is known and in this run's own files: drop the material word from the stuffed def labels. A Conductor's choice of list is not one of the owner's five ac | 12.7 |
| 3 | no-tool | refuse | REFUSED | yes | refuse | refuse | The digest never ran game_lock.py, so the no-free-game claim is not shown. A missing scene is the run's to build, and the set-down does not show why this run ca | 14.5 |
| 4 | fix-unknown | refuse | REFUSED | yes | refuse | refuse | The cause is known and stated: the tick lacks TESTQ_ARCHMAGI=1 and archmagi_candidates filters by profile. That is not an unknown cause, and handing a routing c | 15.8 |
| 5 | fix-unknown | refuse (unsure) | REFUSED | yes | refuse | refuse | The cause is called unknown, but the run never tested its own lead theory (social fight), and the claim that Player.log records none has no command behind it, s | 19.6 |
| 6 | owner-act | refuse | REFUSED | yes | pass | refuse | Owner-act covers loosening a bar only when no fix that keeps every bar exists, but the set-down itself names fix (b), ReboundCells = min(floor(0.7 x left), flow | 16.7 |
| 7 | fix-unknown | refuse | REFUSED | yes | refuse | refuse | The cause is known and named in the set-down itself: the judge reads only the contract. The set-down offers a choice between two known fixes, which is not an un | 15.7 |
| 8 | fix-unknown | refuse | REFUSED | yes | refuse | refuse | The cause is known and the set-down names two known fixes, so a choice between fixes is not an unknown cause. The set-down also names a red-first test that this | 14.2 |
| 9 | no-tool | pass | could not judge | yes | pass | pass | the transcript of the filing run could not be found | 0.0 |
| 10 | fix-unknown | pass | REFUSED | **no** | refuse | **refuse** | The set-down names its own next experiment, timing each step inside apply_rows on one dry run, and nothing shows why this run could not do it. The digest has no | 13.0 |
| 11 | fix-unknown | refuse | PASS | **no** | refuse | refuse |  | 16.6 |
| 12 | owner-act | refuse | REFUSED | yes | refuse | refuse | The work is a Conductor call to re-pin and unlock, which is not one of the owner's five acts, and the one fact that could make it a valid wait (a live visit 13  | 14.6 |
| 13 | other-mod | refuse | REFUSED | yes | refuse | refuse | rimflow/model.py is the project's own pipeline in this clone, not another mod. The run found the fault, located its cause in bridge_gate, and drafted the test i | 18.1 |
| 14 | fix-unknown | refuse | REFUSED | yes | refuse | refuse | The cause is known: a stale marker that the guard cannot tell is not the owner's. The set-down offers a choice between two known fixes and says it tried neither | 12.7 |
| 15 | fix-unknown | refuse | REFUSED | yes | refuse | refuse | The run did no search for the cause: it says it did not read FlowWorks/validation.py, and the digest shows no experiment aimed at why the two P8 checks went red | 11.1 |
| 16 | fix-unknown | pass (unsure) | REFUSED | **no** | refuse | **refuse** | The digest shows no experiment aimed at the cause: the run named water, bridges and things on the cells as theories but never ran a test of any of them, so this | 14.8 |
| 17 | other-mod | pass | PASS | yes | pass | pass |  | 17.3 |
| 18 | owner-act | pass | PASS | yes | pass | pass |  | 12.0 |
| 19 | fix-unknown | pass | REFUSED | **no** | refuse | **refuse** | The set-down names its own deciding experiment: log Kernel() settings and the thing's state at each staging of a 53-check batch.py run, then classify the sighti | 25.5 |
| 20 | fix-unknown | refuse | REFUSED | yes | refuse | refuse | The cause is known and two fixes are named, so this is a choice between known fixes, not an unknown cause. Fix (b) is a code change to maturation_rescue.py that | 13.9 |
| 21 | fix-unknown | refuse | REFUSED | yes | refuse | refuse | The classes are guesses read off one result file; no experiment aimed at any row's cause was run. The set-down itself names the per-row live experiment as the n | 15.7 |
| 22 | fix-unknown | refuse | REFUSED | yes | refuse | refuse | No experiment aimed at the cause was run: the set-down names its own next step (log what the StartExplosion postfix decides over a few IED blasts, check the cen | 13.2 |
| 23 | fix-unknown | refuse | REFUSED | yes | refuse | refuse | The cause is unknown only because no experiment was run: the set-down names three theories and its own test, the run had the bridge and had already used jawa/ex | 14.0 |
| 24 | other-mod | refuse | REFUSED | yes | refuse | refuse | The fault is in ExplosiveKnockback, the very mod this run works on, so other-mod does not hold. The set-down itself names a known fix, with its files, pattern,  | 15.8 |
| 25 | other-mod | refuse | REFUSED | yes | refuse | refuse | The work is new proof lanes in ExplosiveKnockback, the same mod this run works on, so other-mod fails; the run had the bridge, the proof build and the plant pat | 17.6 |
