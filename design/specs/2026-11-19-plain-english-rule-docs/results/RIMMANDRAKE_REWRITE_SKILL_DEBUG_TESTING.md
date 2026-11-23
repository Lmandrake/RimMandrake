# Result: `RIMMANDRAKE_REWRITE_SKILL_DEBUG_TESTING`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimworld-debug-testing/SKILL.md`. Run 2026-11-23.

Base: `51cb1feb3f35543efca7ecad2340b04f7522b72e`
Also: skills/rimworld-debug-testing/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 28,834 | 31,878 |
| words in linted prose | 3,973 | 4,567 |
| STE violations per 100 words | 4.33 | 2.10 |
| sentences over 20 words | 66 | 32 |
| flagged lines (mechanical) | 36 | 26 |
| lines that a cold reader cannot act on (hand count, by the writer) | 10 | 0 that this run could resolve; 2 listed under "Could not determine" |

The long sentences that stay, by kind. Owner quotes or set phrases in quotes: the 2026-08-30 and 2026-09-25 quotes, the
two examples and the two model answers of §8, the suspended rule. Sentences that hold a command, a path or a code name: the
driver lock, the `CLAUDE.md` pointers, `COLD_LOAD_RUN_SHEET_*`, the trimmed-tier line. Two short sentences that the lint
joined at a bold lead or a closing quote mark: most of the others. Four fit no kind, by one to three words: the boot to the
menu, the biome census lead, the cold-load choice and the string-heap line.

## What stays byte for byte

The front matter (`description` included), every heading, every owner quote.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "quicktest", "tier" | what each is | one sentence at first use |
| "It exceeds the 30-second client timeout" | how to avoid it | the client default is named; the two parameters are given |
| "check nobody is mid-audit" | how to check | `game_lock.py query` |
| "Destroy it by starting another" | the menu step | named above it |
| "one game is shared by both windows" | which game | four games, and the pointer |
| "a since-deleted worldgen sweep script" | which script | history file |
| "biome-purity census", "headless COUNT" | what each counts | one clause each |
| "user-string heap" | what it is | one clause |
| "the false-pass field" | which plan holds it | §7 is named |
| "BTD, SWX, Outer Rim" | what they are | three mods with the same species |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy without READYWAITS_UNIFY_ONE_HELPER, the 78.5 s, `guy762_Head_rodian` and the 119,904 | 2 lost (the id, the 78.5 s). Check 1 did not see the other two. |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 4 lost, exit 1 |
| check 1 | the final rewrite, with `--also` | 73 items, 0 lost |
| check 2 | the final rewrite, with `--also` | 167 spans, 0 lost |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | PASS; 19 of 19; GREEN, 12 cases |
| `selftest_skills_by_work`, `selftest_guiding_prose`, `selftest_skills_registered_or_listed`, `selftest_validate_skills`, `selftest_game_names_prose`, `selftest_retired_era_gone` | final text (`selftest_skills_registered_or_listed`: before the last repairs) | PASS |
| `selftest_testpilot_sim` | the changed citations | all checks passed |

Names: no person is named in either text. The reader found no mod, tool or creature name lost.

## What the meaning read found

One fresh Opus reader (rm-judge, model opus) read both texts without the writer's reasoning. It found 13 REAL and 18
TRIVIAL items. It found the headings, the front matter and each owner quote unchanged. Seven of the 13 were changes of meaning
that the settled rows below make on purpose, and the repo supports them. The other 6:

| finding | repair |
|---|---|
| the three fixed content faults read as the cause of the two failures | the MonoMod cause is back beside its failure; the text says that no link was found |
| "never judge it by the call's own success" | four conditions for an answered call; `wait_ready` for a timed-out call |
| the owner announcement narrowed to ArchBig | any game on his machine |
| "nothing else shows the culprit" | the difference shows the rewrite; add one mod at a time to find the mod (`RM_PyrelandsDensityEnforcer.cs`) |
| "the v1 gate is history" | removed |
| "a quicktest does not need ArchBig" | "a quicktest on a tier" |

The same reader then read the repairs twice (1 REAL and 8 TRIVIAL, then 0 REAL and 1 TRIVIAL). The REAL one was the start
conditions on a timed-out call. All are repaired. No reader read the last edit: the two call names in "Before you call
`go_to_main_menu` or `start_debug_game_ready`".

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| never quicktest on the full list / it worked there | a tier first; the full list only for the final verification pass | 1: `bridge_debugging_system.md` line 284 (2026-09-27); 2: owner, 2026-11-02 (`rimworld-load-round` §0). The application of his words on test lists to a quicktest is this run's inference. |
| `start_debug_game_ready` discards the map / it keeps the old map | `go_to_main_menu` discards it | 1: `prove_quicktest_world.py`, `validation_v2.py` |
| the shared wait is PLANNED, ~57 copies / it is built | built | 1: `await_lifecycle.py`; both items are closed |
| announce to seats, check who audits / the driver lock | the lock | 3: §The bridge is passed through one file |
| run when nobody is at the keyboard / his presence gates nothing | removed; the message to him stays and gates nothing | 2: owner, 2026-10-30 |
| one game for two windows / four games | four | 3 |
| "Test destructively" / canonical saves are precious, and a game he plays | both limits stated; his quote is untouched | 3: §Facts you cannot guess; `GAME_STATE_WORKFLOW.md` |
| a quicktest takes ~30 s / 5, 10, 78.5, ~90 s | a table of measured times | 1: `live_test_speed_assessment_2026-11-12.md`; 3 |
| the `JawaIonWeapons` heap is four bytes / 4,596 bytes | "an earlier build" | 1: the committed DLL, read this run |
| the flight quote of `CLAUDE.md` / its present text | the present text, and `jawa/pawn_flight` | 3; `flight.md` |
| batch consistency / the kinds of live test | a batch is the sample of one run; pointer added | 3: §A live test declares its kind |
| two screenshot traps / three; three shapes / four | the counts are fixed | 1: the text itself |
| the culprit was found by the diff / by bisection | bisection | 1: `RM_PyrelandsDensityEnforcer.cs` |
| a 25-minute slot / ~15 to 25 minutes | pointer to `rimworld-load-round` §0 | 5 |
| `DOC_BUDGET.md` / no such file | removed; its sentence stays | 4 |
| "add it" to this skill / only curation sessions edit a skill | `lessons.py add` | 3: §Skills |
| `testpilot_sim.py` cites lines of this skill, `rimworld-load-round`, `rimworld-deploy` and the proof harness | it cites sections now | 1: the line numbers moved |

## Could not determine

| line | question | who would know |
|---|---|---|
| "Do NOT issue the call again. You get a *second* map." | whether a second call during map generation makes a second map now, or answers "A game is already loaded." | a live run on ArchSmall |
| the crash of 2026-09-08 on the full list | its cause; no record names it | the session of that night |

## What this run did not test

- No live game was driven. Each bridge claim that the code does not decide stands as written.
- No measurement shows that an agent tests better with the new text.
- The trigger evals were not run, because the description did not change.
- The lesson `20261115T155545Z-BENCH-debug-despawn-genspawn-drafted-colonist-leaves.md` in the inbox was not folded in: the
  item covers the rewrite only.
