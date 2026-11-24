# Agent work that plain Python can do: the census

Item `RIMMANDRAKE_FIND_AGENT_WORK_THAT_PYTHON_CAN_DO_TOKEN_FREE`. Written 2026-11-23 by a detached Opus run. The
one-page summary is `one_page.md` beside this file. The scripts are in `census/`.  This is a proposal: nothing was
built, filed or changed.

Each number is tagged `[measured]` or `[guess ~N%]`. UNMEASURED means that the instrument could not see. Spend is in
weighted tokens (`weighted_v2`, 1 = one uncached Opus 5.5 input token). M = million. "The week" is the 7 days to
2026-11-23 7:56 PM PST.

## 1. What already exists, and what it answers

| file | what it answers for this question | what it leaves open |
|---|---|---|
| `design/specs/2026-11-22-clean-house-advice/advice.md` | Which systems are duplicated; one program must decide each next act. A different reading of "deterministic" | It does not list the jobs inside a run |
| its `debate/plan.md` | Build nothing by default; fix each stop at its cause; report on 11-29 and 12-06 | The same. This page proposes nothing that the plan forbids: each candidate below waits for the Conductor |
| `design/specs/2026-11-19-incident-news-and-program-routes/boundary.md` | Five repeat alarms are answered by a program; an aged clock is not news. **Built.** Not repeated here | The other Operations jobs (section 4) |
| `design/specs/2026-11-21-crystallize-rule-files/results.md` | Rule text got 4% shorter; a line that restates a tool can be deleted after the tool is watched | Rule text, not work |
| `design/specs/2026-11-12-ticket-preflight-before-any-token.md` | 96 checks on a ticket before a run starts. Partly built (`ticket_preflight.py`). It covers "checking that a record has its parts" at the ticket doors | Work inside a run |
| `design/RimMandrake/pipeline_diagnosis_20261116.md` | Why mods stop (limits with no release) | Not a job census |
| `design/specs/2026-11-22-pipeline-single-source-sweep/` | Facts that have many homes. Six groups were built | Code against code, not agent against code |
| `design/specs/2026-11-20-context-kept-not-reloaded/`, `design/specs/2026-11-21-live-sitting-context-burn/` | What a run pays to load and reload its context | The acts after the load |

No file held this census `[measured: each file above was read, by headings and the parts named]`. So steps 2 and 3 below
are new.

## 2. How this was measured

- **Transcripts.** All 1,935 Claude transcripts changed in the week on this machine were parsed; 1,908 have a priced
  turn. Each model turn was weighed with `MODEL_PRICES` and given to the act that the turn's tool call performs.
  Duplicate turns (resumed sessions) were removed: 36.7M. Total: **1,718.7M** `[measured]`.
- **Check on the instrument.** The 731 detached run records of the week sum to 1,373.8M; their transcripts sum to
  1,336M before duplicates and 1,300M after `[measured]`: 3% and 5% apart. 50 of the 731 records have no token figure.
- **Act classes** come from fixed rules on the command text. A turn that does two things goes to the first rule that
  matches, so each class has an error. Three classes were caught too high and corrected (raw ledger reads fell from
  61.8M to 15.5M with a strict rule; "PIL" first matched PILOT; "pure" landing turns were first counted with compound
  commands). An earlier progress note on the item says 62M for ledger greps: that figure is wrong, 15.5M is right.
- **Records read.** For each role, at least three run timelines (each tool call in order). They are named in section 5.
- **Not seen:** Codex and GPT tokens (image generation, GPT consults) are not in these transcripts: UNMEASURED; the
  Codex usage records would measure them. Runs on SteveDesktop and the Macs: UNMEASURED. A saving is never measured
  before the build. Each saving below is a guess on a measured pool.

## 3. Where the week went

By role `[measured; the role of a run is read from its launch record and item name, so about 5% of items may be in the
wrong row: guess]`:

| role | sessions | weighted tokens | share |
|---|---|---|---|
| List items: machinery and other work (most launched by hand, 60 by the List Pipeline) | 407 | 600.0M | 35% |
| Text rewrites (biome and sea designs, skills, rule docs) | 195 | 204.1M | 12% |
| Conductor window | 136 | 193.7M | 11% |
| Mod fixes and traces launched by item | 114 | 179.2M | 10% |
| In-game driver | 28 | 114.1M | 7% |
| Conductor window's subagents | 169 | 102.0M | 6% |
| In-game fixer and steward runs at stage in_game (tick launched) | 58 | 76.8M | 5% |
| Designer, and the Designer cleanse reviewers | 89 | 38.9M | 2% |
| Offline build | 33 | 32.8M | 2% |
| Blind challenge judge | 20 | 31.8M | 2% |
| Art work (redraw, generate, stage) | 15 | 26.8M | 2% |
| Operations role | 97 | 18.0M | 1% |
| Items whose name starts ROUTE or CONFIRM and were not tick launched (some are not steward work) | 9 | 16.3M | 1% |
| Conductor role, quick checks | 49 | 14.0M | 1% |
| Coverage and art calibration judges | 184 | 23.9M | 1% |
| Steward and walk brief at pre_human or preflight | 8 | 6.9M | 0.4% |
| Judge (coverage, look), live | 6 | 10.9M | 1% |
| Art judge (arteval auto-judge) | 50 | 3.1M | 0.2% |

Launched by: the Conductor by hand 532 runs, 1,062.7M; tick at in_game 88 runs, 165.4M; List Work 60 runs, 77.9M;
tick at offline_build 23 runs, 32.1M `[measured]`.

By act (all roles) `[measured]`:

| act | turns | weighted tokens | share |
|---|---|---|---|
| Run offline tests | 10,407 | 181.2M | 10.5% |
| First context load of a run | 1,898 | 157.5M | 9.2% |
| Read a file | 10,855 | 157.3M | 9.2% |
| Inline Python that reads | 6,973 | 131.9M | 7.7% |
| Search | 7,948 | 120.4M | 7.0% |
| Live scene or bridge call | 5,601 | 114.6M | 6.7% |
| Stage record tools | 5,932 | 94.9M | 5.5% |
| Inline Python that writes (edits) | 2,934 | 90.9M | 5.3% |
| Land (publish, commit, sync) | 5,428 | 90.0M | 5.2% |
| Ledger writes | 4,357 | 81.6M | 4.7% |
| Text only (talk) | 2,786 | 59.8M | 3.5% |
| State reads (pipe, units, accounts) | 3,106 | 51.5M | 3.0% |
| Git reads | 3,129 | 45.4M | 2.6% |
| Game lock and game state | 1,497 | 28.9M | 1.7% |
| Waits | 1,649 | 27.6M | 1.6% |
| Build and deploy | 1,324 | 24.0M | 1.4% |

Seven of these acts are paperwork around the work: land, ledger, stage tools, state reads, game lock, waits, build and
deploy. Together they cost **398.5M, 23% of the week** `[measured by the act rules]`. That is the pool. Most of the rest
is reading, testing, editing and talk.

The kinds of work that the brief named, tested:

| kind | found? | where |
|---|---|---|
| Copy fields from one file to another | yes | driver rows, walk brief, SUMMARY, steward items |
| Check that a record has its parts | partly built | preflight, `judge_certificate`; the steward re-reads it |
| Choose the next act from a state | mostly built (`mod_next`, `list_pipeline`) | the stage confirm is still an agent |
| Parse a log or a result table | yes, large | rows, test tables, run results, ops status |
| Write a report that a template could write | yes | incident acks, stage confirm, some wakes |
| Re-derive a fact that a tool prints | yes, large | `--help` (51.3M), `show` cut by hand (39.1M), raw ledger reads (15.5M) |
| Copy last time's scripts and change the names | yes, not named before | driver visits, blind cycles, sittings |
| Poll a job | yes | waits (43M) |

## 4. The jobs, role by role

M = MECHANICAL, X = MIXED, J = JUDGEMENT. "Exists" says if code for the job exists. Load is the measured figure of the
week where the act rules could see it; UNMEASURED means that only a split of compound turns would show it. Risk names
the concrete case that a program would get wrong.

### In-game driver (28 sessions, 114.1M)
Read: Pyrelands visit 6 run 2, FlowWorks visit 8, GimmeSomeSlack visit 3 run 2 (whole timelines).

| job | in → out | class | the program, and does it exist | load | risk |
|---|---|---|---|---|---|
| Open the visit: claim, sync, stage, last visit's summary, folder skeleton | stage record, last visit → visit folder | M | `visit.py open M`: makes the folder, copies nothing, prints the plan. Not built | part of 41.6M | A new mod has no last visit: the program must say so, not copy another mod's |
| Choose the checks | commit delta → list | M | `rerun_relation.py` exists and is used (348 turns) | UNMEASURED | It errs to "run again" by design |
| Get a game: lock, tier, deploy, launch, readiness | tier → a live game | M | `game_instance.py`, `modset_builder.py`, `deploy_custom_mods.py` exist; nobody calls them as one | 18.2M | The wrong mod list gives a green scene on the wrong build; the loaded receipt must be read back |
| Run scenes one after another | list → rows | M | Each visit copies `runner.sh` and `make_rows.py` from the last visit by `sed` (4 to 26 lines change). `scene_runner.py` exists for C# scenes only | 7.7M copied scripts | A scene that dies must leave a row that says COULD NOT LOOK |
| Wait for scenes | runner log → finished | M | `waitfor.py` exists; each wait is capped by the 10-minute call limit | 6.9M | A hung game looks like a long scene |
| Repair a wrong check, classify a failure | log, code → fix | J | stays | large | A program cannot say if the mod, scene or environment spoiled the run |
| Plant a fault and show red, then green | fault patch, test → two readings | X | `maturation.py red-seen` runs it; the agent writes the patch | 14.0M (all roles) | An equivalent mutant reads green and means nothing |
| Rows, SUMMARY, polish and strange records | component verdicts → JSON and prose | X | `make_rows.py` per visit; a shared one is not built | 20.7M | The strange row's class and the "why" are judgement |
| Crop pictures and contact sheets | screenshots → one picture | M | inline PIL each time; two sheet tools exist for other uses | 3.2M | Which part to crop is judgement; the cut is not |
| Look at pictures | picture → what it shows | J | stays | 3.1M | — |
| Exit: build match, next, advance ask | rows → exit state | M | `build_match.py`, `maturation.py next` exist | in stage tools | Covered by the program already |
| Lease renew, ledger notes | clock → events | M | Agents run `modledger.py append … lease.renew` | 7.5M (all roles, often with other work) | A hung run would keep its lease; tie it to process life, as the game lock does |

### In-game fixer, and mod fixes and traces (172 sessions, 256M)
Read: HOLD_FLOWWORKS_PIT_PRISONERS (two sessions), TRACE_FLOWWORKS_MOAT_SWIMMERS, TRACE_PYRE_FIREHAWK.

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Find the cause in code and logs; design the fix; choose the experiment | J | stays | most | — |
| Set up a sitting (`b.py`, `shot.py`, `exp.py`, `run.sh` written again in each run) | M | `bridge_call` and the `rimbench` scripts exist; a fixed sitting kit is not built | 18.0M of throwaway scripts (all live and judge roles) | An experiment that the kit cannot express; keep the free script |
| Read the failing row and its evidence (`rows.jsonl`, scene JSON) | M | a query command: `visit.py row M CHECK`. Not built | part of 24.7M | Rows of old shapes |
| Read the item's history and fold notes into a context | X | launcher pastes it (section 6, rank 6) | 41.9M `show`, all roles | A long item; the packet must not be cut silently |
| Before and after test of the fix | M | `red-seen` exists for planted faults; parent-against-fix is done by hand with `git show` or a worktree | 19.5M red/green turns | A test that needs a build, or a file that the parent lacks |
| Publish, note, close | M | section 6, rank 1 | 74.6M (all roles) | — |

### Offline build (33 sessions, 32.8M)
Read: FINISH_SLACK_ICON_LAMP, AUTOBUILD_GIMMESOMESLACK_FOUR_BARS, WIDEN_PYRE_LONE_FIRE.

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Write the code and the test | J | stays | most | — |
| Read which bars are left | M | `maturation.py brief`, `next` exist | UNMEASURED | — |
| Regenerate the test table and wait for it | M | `make_test_table.py` exists per mod | part of 43.0M waits | Full regeneration is long; the wait is the cost |
| Check the deciders are red when they must be | X | `red-seen` exists | 14.0M (all roles) | Equivalent mutants |
| Certificate | M | `maturation.py certificate --run` exists | in stage tools | — |

### Blind challenge judge (20 sessions, 31.8M)
Read: Pyrelands cycle 5, FlowWorks cycle 4, ExplosiveKnockback cycle 6, Graffiti cycle 2.

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Read the design, the bars and the code; think of a hole | J | stays | most | — |
| Write lane-1 cases and the planted faults | J | stays; a program cannot know a good fault | — | — |
| Run lane 2: rerun every decider, plant each fault, log red or green | M | `rerun_offline.py` and `plant_faults.py` exist 17 times in 17 cycles, a new copy each time | 6.4M copied scripts | A generated fault that the judge did not choose would weaken blindness; only the runner moves, never the faults |
| Census of kernels, settings and rows with inline Python | M | a query command, not built | part of 24.7M | — |
| File the tickets and write SUMMARY | X | template from the fault rows; the hole text stays with the judge | 3.1M records | A program could file a wrong class; the judge names the class |

### Judge (coverage, look), calibration judges (190 sessions, 34.8M)
Read: the live coverage judge run of the Pyrelands exam retake (36 turns), five art calibration runs turn by turn
(Danglemaw, Dewblade twice, DecayDrake twice), and the turn counts of 60 coverage judge runs (most are 3 turns, 100k to
250k each `[measured]`). The arteval auto-judge runs are one turn each. 

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Give the verdict | J | stays | 10.9M live | — |
| Rank the calibration cases to re-run after a brief change | X | the runner runs all cases when the hash changes. A finer rule could skip cases whose section did not change; not built | 23.9M calibration `[measured]` | A brief edit can change a case that a text diff says is untouched. I do not propose it (`_why`: the calibration is the only proof of the judge) |
| Crop, zoom and measure the pictures (each art judge finds a Python with PIL and writes its own crops) | M | the stager makes the zooms, the alpha, size and outline numbers, and lists them in `subject.json`. Part built (`scale` and play-zoom pictures are staged); the crops are not | part of 14.3M art calibration (99 sessions) | A judge that wants another crop; leave it the tool |
| Start cost of one-turn judges | M | a run with fewer loaded tools. Not agent work, so not ranked | 17.3M of starts in misc runs | — |

### Steward: confirm, road back, pre_human, preflight (39 runs, 25.4M)
Read: CONFIRM_GIMMESOMESLACK_VISIT_THREE, CONFIRM_PYRELANDS_CYCLE_FOUR, ROUTE_GIMMESOMESLACK_VISIT_ONE,
ROUTE_PYRELANDS_CYCLE_THREE, STEWARD_EXPLOSIVEKNOCKBACK_PRE_HUMAN.

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Confirm the exit (12 runs): read rows, table, SUMMARY; say the exit is met; advance | X | `build_match` and `next` compute the exit; `maturation_dispatch.py:1896` says "the program never advances: the steward's confirmation stays a hand step". Move: the program advances when each row counts, no row is unclassed, and each strange row has a class | 5.4M | The steward also judges looks (it ran a blind look judge) and can find a wrong check. Keep those as a judge run only when a row asks |
| Road back (19 runs): read failed rows, file an item for each, advance to an earlier stage | X | Rows are classed by the driver; the program files a skeleton item for each MOD row with check, row, evidence, expected class, then moves the stage | 13.2M | Two rows with one cause make two tickets; the agent joins them. The program can list same-cause rows by check family |
| Pre_human walk brief (8 runs) | J, with a filled template | `walk_brief.md` is a template; the list of open tickets and last rows is data | 6.9M | "What I noticed first" is judgement |

### Designer and the cleanse (89 sessions, 38.9M)
Read: Warscar, TheForge and Contagion reviewer runs, one exam retake (the Designer's own role run).

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Review a proposal; verify a fix | J | stays | 35.8M cleanse reviewers | — |
| Check that each owner quote is in its named source; that each path, def and id exists | M | `designer_stage.py check`, `citations_lint.py` and the owner-quote check exist; a program run over the proposal before the review is not built | part of search 12.9M | A quote that was joined or corrected by rule |
| Exam retake: launch readers, score, close | M | `exam_retake.py`, `designer_stage.py` exist; the readers are judgement | 0.5M per retake | — |

### Operations (97 sessions, 18.0M) and quick checks (49, 14.0M)
Read: Operations sessions 951770a7, 580daa95, 27965b23, b8ca2bdc and 12 result texts; Conductor sessions 41470598,
312e50f2, 421ce59c and 12 result texts.

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Decide that a repeat alarm has not changed | M, part built | `incident.py` `program_answer`: 5 routes. 18 program routes and 61 role routes exist | Operations 47 runs 11.7M and Conductor 40 runs 9.8M ended in an ack | A step inside a band that is a real start of a fault |
| Find what a metric is: read `ops_watch.py`, series, `told.jsonl`, past acks | M | an incident packet built by the program, with the metric's definition and last readings. Not built | 9.2M of 1,048 turns | The definition line can go stale; take it from the code |
| Find the cause of a new alarm, fix it | J | stays (24 Operations runs, 4.7M, ended in a fix) | 4.7M | — |
| Write the ack, the plan, the trigger line | X | fill the row from the packet; the plan stays | 3.4M | A plan that names no new act is worth nothing |
| Fold overdue hand acts, note a steady state | M | `maturation_hands.py` exists | UNMEASURED | Wrong item folded |

### Conductor window (136 sessions, 193.7M) and its subagents (169, 102.0M)
Read: sessions ef311d37 (all 232 turns), aab6064a, 8c581a3a.

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Wake: owed list, handoff, words, pipe, locks | M | `seat_restart.py words`, `queue --owed` exist; the window opens and cuts them by hand | 20.8M | A pasted wake that is long costs on each later turn; keep it short |
| Read a run's result after a wake | M | the wake file carries the unit, state and path only; the window opens the `.out.json` with ad hoc Python, 408 turns | 11.2M + 4.2M of report turns | The result text can hold what he must see; the packet must not cut it silently |
| State reads (pipe, locks, accounts, MATURATION_NOW) | M | commands exist; a standing block in the wake is not built | 18.6M | A stale block must carry its time |
| Launch helpers; write briefs | X | `detached_helper.py launch` exists | 6.3M + 2.0M | — |
| Talk to him; decide; open pages | J | stays | 33.6M | — |
| Record his words and ledger writes | X | his words go in as he typed them | 14.0M ledger, 1.3M open page | — |

### List Pipeline: Shape, Work, Verify, Launch, View, Audit
Verify, Launch and View are programs today `[measured: list_pipeline.py is tokens-free and `MOVED_BY` says program]`.
Work 60 runs, 77.9M, read: FIX_STAGE_REVIEW_MIDDAY, CORRECT_SPRITE_SKILL, REWRITE_SKILL_QUESTS. Shape runs of the
week whose brief opens with the Shape text: 0 of 731 records `[measured]`, so there was no Shape load to read. Audit: the follow-through audit is a timer (`rm-follow-through`), its agent load UNMEASURED.

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Work: read the item, do it, run its check, land, close | X | the Work brief lists five shell steps; the landing and close are M | part of 77.9M | The need can be wider than the check; the brief says so |
| Shape: split the item, write a check with its "fooled by" line | J | stays; `list_effect.py check` already refuses a check that never fails | 0 runs this week | — |
| Verify: run the check on main | M | built | 0 | — |
| Audit | J | stays; counting is code | UNMEASURED | — |

### Text rewrites (195 sessions, 204.1M) and art work (15, 26.8M)
Read: RECHECK_THESUMP, RECHECK_BLUEDESERT, REWRITE_CHILL_SEA, REWRITE_SKILL_QUESTS; LIQUID_PUMP_REDRAW,
REDRAW_STEPPED_PIT, JUDGE_PYRE_ULLAI.

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Read the sources, choose the words | J | stays | 35.7M file reads | — |
| Find every source; flatten JSON; drop repeats; list what was read | M | each run writes `flat.py`, `dedupe.py`; a source packet is not built | 35.6M of inline scripts that write (mixed with edits) | A source that the search misses, so the run trusts a partial list |
| "Lose nothing" check | M | exists for rule files; per-file variants each time | 11.2M tests | — |
| Generate and judge a picture | J (Codex pictures, Codex spend UNMEASURED) | pre-checks exist (`validate_sprite.py`) | 26.8M Claude side | — |
| Crop, compose, compare | M | inline PIL; `thing_contact_sheet.py` exists for another use | 12.6M (all roles) | — |
| Stage in the game for a look | X | `stage_review.py` exists | UNMEASURED | — |
| Install the art | M | `art.py install` exists | — | — |

### Small or rare roles (classed from the role file or the run name; no run record read: the load says why)

| role | jobs | class | load in the week |
|---|---|---|---|
| Fable rescue (`fable_rescue.md`) | find why a mod is stuck; redesign | J; its setup, waits and landing are ranks 1, 2 and 7 | 2 runs, 19.8M `[measured]` |
| Test Pilot (`rm-testpilot`) | live sitting, one change at a time | J; the sitting kit (rank 2) is the M part | inside the fixer rows: UNMEASURED apart |
| Criteria fixer (`criteria_fixer.md`) | reword one acceptance clause | J | UNMEASURED |
| Code review (`code_review.md`) | read code for a broken promise | J; `code_review_status.py` does the record | 668 tool calls, 11.1M (all roles, part of compound turns) |
| Findings judge (`rm-findings-judge.timer`) | decide an outcome for each new finding | X; folding is code (`findings_fold.py`), the outcome is J | UNMEASURED |
| Art prompt writers (regen prompt, departures) | rewrite a generation prompt | J | 14 runs, 1.1M `[measured]` |

## 5. Ranked candidates

Each saving is a guess on a measured pool. Two rows can share turns, so the sum is not the total. My net figure for the
ten together: about **120M a week, 7% of the week** `[guess ~50%]`. The calculation counts a removed turn at its own cost
(average 15k to 30k). It does not count the smaller gain of a shorter context after it, nor the small cost of the pasted
text. A packet of 3,000 tokens that stays for 60 turns costs about 9,000 weighted tokens (0.05 each turn) plus its first
load of about 6,000. One turn that it removes costs 15,000 to 30,000.

| rank | candidate | pool `[measured]` | saved in a week `[guess]` | build |
|---|---|---|---|---|
| 1 | One landing-and-closing command | 74.6M pure landing turns (4,408 turns, 907 runs, median 4 a run) + 34.4M refused-publish repairs (420) | ~35M ~60% | medium |
| 2 | A visit kit and a cycle kit | 41.6M driver turns that are setup, waits, records + 9.5M copied cycle scripts and records | ~22M ~55% | large |
| 3 | Filled commands in the brief | 51.3M `--help` turns (2,807); 23.0M of these on ledger, stage, launch, lesson and publish verbs | ~20M ~50% | small |
| 4 | One test call: parent, fix, planted fault | 123.3M test turns (6,085); 37.8M run one test and write nothing; 19.5M are red/green | ~20M ~50% | medium |
| 5 | Conductor wake carries the result and the state | 54.8M (11.2 + 4.2 + 18.6 + 20.8) | ~18M ~55% | small |
| 6 | Item packet at launch | 41.9M `show` (39.1M cut by hand) + 15.5M raw ledger reads | ~15M ~50% | small |
| 7 | One long wait in place of many | 43.0M wait turns (2,260); 7.9M are direct repeats (501) | ~12M ~60% | small |
| 8 | Program advances, road back, walk-brief data | 25.4M in 39 steward runs | ~10M ~50% | medium |
| 9 | Incident packet, and program routes for steady incidents | 37.8M in 194 run records; 21.5M ended in an ack | ~10M ~50% | medium |
| 10 | Lease and progress note by program | 14.3M progress notes (484) + 7.5M lease renewals (202, often mixed) | ~8M ~55% | small |

Below ten: one query command for the table, rows and stage record (pool 24.7M, about 8M, shares 8.5M with rank 2); a
picture helper for crops and sheets (pool 12.6M live and art roles, plus the art calibration crops, about 6M); a source packet for text rewrites (pool 35.6M, about 8M, but
the rewrite wave is nearly over); a pre-review check of quotes and ids for the cleanse (about 4M).

### The ten, with what moves and what a program gets wrong

1. **Landing and closing.** A `finish` command takes the paths, the subject, the evidence and the item. It commits,
   publishes, retries a race, writes the note, closes the item and prints one line. Form refusals (pathspec, usage,
   "nothing to publish": 215 cases, 14.7M) are repaired inside it. It stops for a red check (77 cases) and a content
   conflict (54). `./publish` and `cli.py close` exist. Risk: an agent may close work that is not finished, because
   the command makes it easy. Keep the close check (`list_effect`, `--live`) in the path.
2. **Visit and cycle kits.** One `visit.py` opens, launches, runs scenes, writes rows and the SUMMARY, makes the sheets.
   One `cycle.py` runs lane 2 over the judge's fault files. The agent then repairs checks, judges looks and classes
   strange rows. 17 of 17 cycle folders hold their own `rerun_offline.py` and `plant_faults.py` `[measured]`; visit
   scripts differ from the last visit by 4 to 26 lines of 40 to 151 `[measured: Pyrelands 5 to 7]`. Risk: a kit that
   hides a death; and the drift between mods (each mod's entry point differs).
3. **Filled commands.** The launcher pastes the exact commands of the run (file, note, close, verify, red-seen, lessons),
   filled in, made from `argparse` at launch. `maturation.py brief` already does part. Risk: the text goes stale; make it
   from the parser, never by hand. Watch if agents still ask `--help`.
4. **One test call.** A command runs the named test on the parent tree and the working tree, plants the given fault, and
   prints the failing lines. `red-seen` does the planted half. The agent chooses the test and the fault. Risk: a test
   that needs the built DLL reads the wrong tree; the command must print which build it read.
5. **Conductor wake.** The run-end wake file carries the result's last message whole (the transcript has it), and the
   window gets one state block (locks, pipe line, accounts) at wake. Then a window reads a run's result without a turn
   (408 turns a week). Risk: long results grow the window's context; cap by relevance, never by cutting text. A result
   with a decision for him must not be treated as routine.
6. **Item packet.** The launcher runs `show`, folds the notes into state, last run, linked items and the last commits,
   and pastes it. `modledger` already builds such a packet for mods. Risk: a packet that omits the one decisive note; it
   must say what it left out and print the command that shows it.
7. **Long waits.** A `claude -p` run ends with its turn, so a wait blocks in a call with a 10-minute limit. Raising the
   limit (the `BASH_MAX_TIMEOUT_MS` setting; not set in `settings.json` or `claude_bounded.sh`
   `[measured]`) makes one turn serve a longer wait. It must stay under 59 minutes: of 18 gaps over 59 minutes in detached runs, 17
   rebuilt the whole prompt cache, about 895k each, and twelve 10-minute waits cost about 290k `[measured, scan2.pkl]`. So
   the saving is about 8M `[guess ~40%]`, not 12M. The effect of this setting in a detached run is untested: try it on
   one run first. Risk: a hang that a 10-minute call would have caught. `waitfor.py` must carry its own timeout and
   liveness check.
8. **Stage confirm and road back.** The tick advances when the exit program reads "met" with no unclassed row, files a
   skeleton for each MOD row, and wakes a steward only for a look, a joined cause or a wrong check. It reverses a
   decision in `maturation_dispatch.py` ("the program never advances"). So it needs the Conductor's word. Risk:
   advancing a mod on rows that are wrong in the same way (the check was wrong): the steward found such cases.
9. **Incident packet.** The program writes the metric's definition, the readings, the owner of the cause and what the
   last run wrote; a route table answers "steady, expected" for more than the five routes. The clock to clear and the
   five bands stay as decided. Risk: a slow rise inside a band (named in the boundary page as accepted).
10. **Lease and progress.** The lease lives with the process (the game lock does this). The progress note every 20
    minutes is written from the run's own last message and commits. Risk: the theory and the reading in a progress note
    are judgement; keep the note at the end of an experiment, and let the program do only the 20-minute "alive" line.

## 6. What stays with agents, and why

- Finding a cause, designing a fix, naming a hole in a test, judging a picture, reading a design text. The input is
  open and the answer has no test.
- The class of each failure (MOD, SITE, HARNESS, ENVIRONMENT, COULD NOT LOOK). A wrong class moves a mod. A program may
  list the facts beside it.
- The choice of a planted fault. A fault that a program writes tests only what the program knows.
- Talk with the owner, and every one of his five acts.
- Reading the prose of a ticket and deciding if it is worth doing.

## 7. What I could not look at

- Codex and GPT tokens; runs on other machines; the calls made by a Claude window on the Macs.
- The real saving of a candidate: UNMEASURED until built. A cheap first test exists for ranks 3, 5, 6 and 7: launch five
  runs with the change and five without, and compare `--help`, `show`, wait and result-fetch turns per run. The scripts
  in `census/` count those acts (`p3.py`, `p6.py`, `cond.py`).
- The quality of the role rows: a run is put in a role by the name of its item; about 5% may be wrong `[guess]`.
- Jobs inside compound commands: the act rules give a turn to one act, so acts that share a turn with work are
  under-counted (`publish` in 4,022 commands, only 2,312 with the word PUBLISHED in the first lines of output).
