# SteveDesktop work that plain Python can do: the census

Item `RIMMANDRAKE_STUDY_STEVEDESKTOP_WORK_SETUP_AND_TRACKING_WE_MESS_UP`. Written 2026-11-23 by a detached Opus run. The
one page is `one_page.md` beside this file. Scripts and their first output: `census/`. This is a proposal: nothing was
built, filed or changed.

Tags: `[measured]` or `[guess ~N%]`. UNMEASURED: the instrument could not see. Spend is weighted tokens (`weighted_v2`),
M = million. "The window" is the 21 days to Mon 2026-11-23 8:30 PM PST. "The week" is its last 7 days. Times are local
Pacific unless they end in Z. An **asked job** is one that an agent, the visit feed or the retired Relentless tick asked for. A
**filler job** is one that the lane queues for itself when it has nothing else.

## 0. Does the owner's claim hold?

His claim: "we frequently mess up getting its work configured properly and remembering to track it." **Both halves hold.**

| | 21 days | last 7 days |
|---|---|---|
| jobs that ended | 954 | 289 |
| jobs that did not finish DONE | 293 (31%) | 64 (22%) |
| of them, our own setup faults (section 2) | 150 | 56 |
| asked jobs | 248 | 61 |
| asked jobs that a setup fault killed | 94 (38%) | 16 (26%) |
| asked jobs that ran to the end and measured nothing | 43 | 14 |
| asked jobs that gave at least one PASS or FAIL row | **79 (32%)** | **29 (48%)** |
| filler jobs that gave at least one PASS or FAIL row | 492 of 706 (70%) | 170 of 228 (75%) |

`[measured: census/kinds.py; 0 done records unreadable]`. Jobs
that we ask for fare far worse than jobs that the program asks for. Quarantined jobs are in these counts (275 of 954).

Tracking: of 165 asked jobs that were kept, **62 have their id in no ledger event after they ended** (46 only from the
RUNNER program, 57 from a seat) `[measured: census/ledger_after.py]`. The check is strict: a seat that wrote the result
without the id is not seen. It is a floor on what is traceable, not proof that nobody read. Looser check (items, design,
git, 8,570 transcripts): 10 visit jobs and 6 quarantined jobs have their id nowhere on this machine after they ended
`[measured: census/tracked_mentions.py]`.

## 1. How work gets to SteveDesktop today

| # | step | who | reads | writes | class |
|---|---|---|---|---|---|
| 1 | Decide that a check goes to SteveDesktop | **agent** by hand; or the visit feed (program, since 2026-11-22); or the filler (program) | test table, `testq` blocks, coverage | nothing | MIXED: whether the check is worth running is judgement; whether the lane can run it is mechanical |
| 2 | Give a check a route (`testq` block) | program (`testq_blocks.py`) derives; agent applies | test table, the mod's modcheck suite | `test_table.json` | MECHANICAL for a modcheck chain; JUDGEMENT to write a new chain |
| 3 | Submit: choose selector, profile, tier, deploy list, sha, `--for-item`, lane, priority | **agent** (`testq.py submit`, 24 flags); program for feed and filler | its own memory, `--help` (51 of 143 submit calls were help text `[measured]`) | `pending/<job>.json` | MECHANICAL: every value but the purpose is a function of the item or check |
| 4 | Check the request before it queues | program (`testq.py submit`: schema, hold, deploy names, tier, plan, sha on main, retest rule) | repo | refusal text | built; gaps in section 4 |
| 5 | Stage the bridge companion for origin/main | program (`companion_stage.py`, each tick, since 2026-11-03) | dispatch clone | worker inbox, `companion_stage.json` | built; stages main's newest only |
| 6 | Copy registered site saves | program (`site_stage_step`, since 2026-11-22) | `test_site_saves.json` | Saves on both games | built; only registered saves |
| 7 | Admit one job per game | program (`testq.py tick`, each 60 s) | pending, pauses, fault windows | `running/` | built |
| 8 | Pull, pin sha, preflight, deploy, load, attest, run | program (`worker.py` on SteveDesktop) | runner clone, game | attempt folder, `modcheck.log`, result | built |
| 9 | Fetch the result, retry once on a machine death | program (tick) | worker outbox | `done/` | built |
| 10 | Write the result to the ledger | program (`ingest.py`) | `done/` | RUNNER events, findings, repair items | built for jobs that name an item; **two holes**: `--proofs` jobs and visit jobs (section 3) |
| 11 | Count the result where it decides something | **agent**, when one remembers (a driver copies a lane result into visit rows; a seat notes an item) | `done/`, ledger | `rows.jsonl`, note | MECHANICAL, **not built** |
| 12 | Triage a FAIL row | **agent** (daily findings judgment, STEVE_FILLER_MONITOR_FAIL_FINDINGS) | finding | classed finding | JUDGEMENT |
| 13 | Repair a harness cause | **agent**, from `HARNESS_REPAIR_CAUSE_*` (31 filed in the window, 5 open `[measured]`) | evidence | code | JUDGEMENT |
| 14 | Pause, resume, hold the lane | **agent** by hand; the fault monitor and periodic reboot by program | lane state | `paused.json` | MIXED: the reason is judgement; the end condition is mechanical |
| 15 | Own a stalled lane | program (`steward.py`) files an item, wakes a capped headless seat (20 wakes `[measured]`) | tick state | 50 `STEVE_LANE_UNSTICK_*` items in the window, 37 dropped `[measured]` | MECHANICAL, built; keyed badly (`RIMMANDRAKE_KEY_STEWARD_ITEMS_ON_CAUSE_NOT_FRESH_NAMES`) |
| 16 | Reboot, fault watch, audio driver check | program (`fault_monitor.py`, `preflight.py`) | probes | windows, reading | built |
| 17 | Take Steve1 or Steve2 by hand, outside the lane | **agent** over ssh (149 bridge events for the machine in the window, none of which the lane's counts see `[measured]`) | host lock | ledger bridge events | JUDGEMENT; results UNMEASURED by the lane |

So 10 of 17 steps are already plain Python. The messes sit at the joints where an agent still fills in values (1, 3, 11,
14) and where the program's answer is dropped (10, 11).

## 2. Where the setup goes wrong (Question 2)

One kind per not-DONE job, first rule that matches. Command: `python3 census/kinds.py`. `[measured]` unless tagged.

| kind | jobs (asked) | dates | concrete case | status today | class of the work |
|---|---|---|---|---|---|
| **Stale deploy**: the bridge companion was not built from the job's sources | 50 (48) | 11-03 to 11-23 | 15 in a row on 11-12; J20261124T013316Z-550722 | stager built 11-03; still 2 on 11-23: the inbox holds one file, and a newer main's companion replaced the right one before the job installed it (tick.log: right one staged 4:06 PM and 5:14 PM, replaced 4:14 PM and 5:39 PM; jobs sent 4:20 PM and 5:35 PM) `[guess ~85%]` | MECHANICAL: keep one staged companion per source hash; hold a job until its own is there |
| **Wrong game**: Steve2's job refused because Steve2's own kept game was up | 47 (10) | 11-23 only | 19 refusals in a row from 7:59 AM; 10 of them visit jobs | fixed 1072913ab0 at 2:50 PM; 11 h after the first; the ticket `RIMMANDRAKE_FIX_STEVE2_LOAD_PREPARE_REFUSES_RUNNING` still says open | MECHANICAL: stop after 2 of the same refusal |
| **Wrong mod list**: the list could not be written (stale marker, missing before-copy) | 26 (26) | 11-06 to 11-17 | 7 in a row on 11-12, GimmeSomeSlack tier | preflight moves the marker since 11-12; 1 since | built |
| **Wrong mod list**: the running load was not the composed list | 11 (6) | 11-04 to 11-22 | J20261104T074700Z-42d8eb: `ray1203.simplecamerasetting` not on that machine | detected before a row runs; 5 in the last 7 days | MECHANICAL: read the host's installed ids before the list is named |
| **Wrong map or save**, not DONE: no test map that the runner may use | 10 (2) | 11-06 to 11-13 | J20261113T114138Z-7ba5eb: "a colony, not a test map" | none in the last 7 days | built |
| **Wrong map or save**, DONE: at least one row says the site, map or biome was wrong | 66 (16) | 11-06 to 11-23 | J20261122T172224Z-ccc309: "could not make a Pyrelands site current (read RM_TheRot)", about 20 min of lane | site copy built 11-22; `RIMMANDRAKE_ROUTE_PYRE_TESTQ_OFF_STEVE_NO_SITE_THERE` open | MIXED: a program refuses a chain whose site save is absent; a person makes the site |
| **Wrong build**: a Steve2 result that checked Steve1's install | 13 DONE (5) | 11-23 | J20261124T001426Z-9581b9 said FRESH, the game loaded an older companion | fixed 3bfaf78cd0 at 4:35 PM (`RIMMANDRAKE_FIX_STEVE_TWO_LANE_READING_STEVE_ONE_INSTALL`). The 13 results still stand. Whether a row in them is wrong is UNMEASURED: the deployed DLLs of that day would settle it | MECHANICAL: ask the running game what it loaded (`jawa/running_mods loadedOf=ours`) |
| **Runner clone could not update** | 5 (2) | 11-03 to 11-20 | J20261103T192538Z-5e2c71: empty git objects after a power loss | pauses the lane; the repair is by hand | MECHANICAL: the four commands stand in the RUNBOOK |
| **Wrong contract**: the worker's result shape was refused | 1 (0) | 11-12 | J20261112T183712Z-caa4c9 | fixed | built |
| **Wrong selector** by the agent | 1 named; more in refusals | 11-13 | J20261113T054726Z-9995ee: "wrong selector (--item); resubmitted as --proofs" | of 143 submit calls, 24 gave no job id: 17 refused by the tool (retest rule, pilot route, deploy name, tier), 7 for other reasons (timeouts, background, a traceback) | MECHANICAL |
| **Check that this lane cannot run** (needs a driver, a proof build or a result made elsewhere), sent anyway | 28 DONE (7) | 11-03 to 11-23 | J20261124T030115Z-135064 | chains stay in the rotation; `RIMMANDRAKE_ROUTE_TESTQ_PROOF_BUILD_JOBS_TO_STEVE` open | MIXED |
| **Missing package, or no route to the bridge from the wrong python** | 23 DONE (10) | 11-06 to 11-23 | `No module named 'lxml'` 16 rows, UtinniPatches; proof line with `python3` not `python.exe` | one lesson and one package at a time (numpy, Pillow 11-23) | MECHANICAL: a check at preflight of the packages and the interpreter that the script imports |
| **Kept game was spoiled** (dead colonist, site not quiet) | 33 DONE (16) | 11-04 to 11-23 | J20261124T035514Z-a16591, every row UNMEASURED | the kept game goes on to the next job | MECHANICAL: stop the kept game after "dead colonists", as the canary rule does |
| **Planned rows that never ran** (NOT_RUN) | 55 DONE (25) | 11-04 to 11-23 | J20261124T033119Z-dd4fed: 12 of 16 rows NOT_RUN | counted honestly as NOT_RUN | a consequence, not a cause |
| **Jobs that never started** | 8 cancelled + 47 + 5 + 1 refused above, + 17 cancelled duplicates | 11-10 to 11-23 | 17 duplicate reruns made in one second by `ingest.py` on 11-12 (cancelled the same day); 2 cancelled for "companion not on SteveDesktop" | built | MECHANICAL |
| **A job submitted on the wrong machine's queue** | no count | 11-12 | lesson `20261112T060309Z`: a submit on SteveDesktop wrote a local queue that nobody reads | fixed 780f797c48; how many before it: UNMEASURED (that queue is gone) | built |

Not setup, for scale: the game crashed or never got ready while loading 74 (48 of them inside quarantine), the game process
vanished under the job 15, harness read faults 45, red canary 2, stopped from outside 6 `[measured]`. The load crashes and
the canary belong to SteveDesktop's register fault (`infrastructure/state/facts/steve_fault_diagnosis.md`).

**Results from inside a machine-fault window that were counted.** 55 windows, 252 of 504 hours `[measured]`. Last one
ended 2026-11-21 9:46 AM, before the audio driver went off for good. 275 jobs were quarantined. 162 DONE jobs inside a
window were **kept** (143 under his ruling of 2026-11-12, "stop the quarantine process and run the validation anyway", 19
released) and no window job was kept without its tag `[measured]`. They put **157 verdicts on the ledger** (74 + 8 pass,
35 + 8 fail, 23 + 9 partial), and **none of those 157 ledger lines names the window** `[measured: census/windows.py]`; a
control found that 248 verdicts outside windows join the same way. The tag is in the done record. The ledger reader cannot
tell. That was not a mistake of setup: he ordered the runs. The missing words on the line are the mistake.

**Kinds with no case found in the window:** a job run on the wrong sha (the worker pins it) and a job that ran on another
game's bridge by accident. "No case found" here means that the result records hold none; a case that no tool records
would be UNMEASURED.

## 3. Where we forget to track it (Question 3)

**Results that nobody counted.**

1. **Every visit-feed job (32).** 22 DONE, 10 REFUSED; 12 of them had 163 PASS and 3 FAIL rows. `visits.py`: **0 of the 32
   job ids are in any visit folder**, and of 1,819 rows in `rows.jsonl` of all visits, **1** has `game: stevedesktop`. The
   summaries of Pyrelands visits 6 and 7 say "SteveDesktop was not used". The rows format accepts `stevedesktop`. So a lane PASS
   drains the feed, and the visit then runs the same check again on an Arch game. (`measured`; the 3 FAIL rows did reach
   the filler host as findings.)
2. **Every `--proofs` job (59 in the window, 12 since 2026-11-18).** `ingest.py:425` returns (a retired reader) `skipped: ... relentless_game reads
   its verdict`. That reader, `relentless_game.py`, is retired: deleted 2026-11-18 (b28e0d6975). Since then a proofs result reaches the ledger
   only if the submitter writes it: 9 of 12 have a note from a seat, 3 have none `[measured]`. Example:
   J20261123T120620Z-d74bbd (FAIL, `RIMMANDRAKE_RUN_ROT_GIANTS_CLICK...`) is in no ledger event after it ended.
3. **348 jobs `skipped: the job names no item`** (filler and visits). The PASS rows of those update only `coverage.py`
   (`gaps.py` reads them to order the filler). A FAIL row reaches `STEVE_FILLER_MONITOR_FAIL_FINDINGS` or an item (57 jobs made findings `[measured]`). Nothing else is counted.
4. **9 ingest errors, 2026-11-05 to 11-06:** the name bank refused `HARNESS_REPAIR_CAUSE_..._2`, so the repair item was
   never filed for that sighting `[measured]`. Retired with the bank; no later case.
5. **Fixed but open:** `RIMMANDRAKE_FIX_STEVE2_LOAD_PREPARE_REFUSES_RUNNING` (proposed; code fixed at 2:50 PM). Its Operations
   author guessed the wrong cause ("command line unreadable") because Operations had no access to SteveDesktop's process
   list `[measured: the item text]`.

**Idle time** (`census/idle.py`, `idle_why.py`):

| measure | value |
|---|---|
| Steve1, lane job running | 155.3 of 504 h (31%) |
| of which asked work | 46.4 h; filler 114.2 h |
| Steve2 (lane since 2026-11-23 2:56 AM) | 10.0 of 17.6 h, 2.7 h of it the 47 refusals |
| Machine unreachable (steward state) | 28.3 h; machine down windows 12.7 h |
| Lane PAUSED | 229.2 h |
| Lane BRAKED (a filler brake) | 54.1 h |
| Days when Steve1 ran under 1 hour of lane work | 7 of 21: 11-07, 11-08, 11-15 to 11-19 |
| **Hours when an asked job waited and nothing ran** | **149.9 h**, 142.7 of them while PAUSED |
| Asked jobs that waited over 24 h | 28 (longest 76.5 h) |
| Since the audio driver went off (2026-11-21 1:20 PM) | Steve1 busy 39.3 of 55.2 h (71%) |

Why paused: the CPU soak 66.3 h (his order); the Artisan looper, Codex and Claude Whittle (retired) hosts 79.6 h (the machine was in
use outside the lane); fault monitor 23 h; **a pause with no end date 49.3 h** (2026-11-15 6 AM to 11-17), a probe after the
load crash that nobody resumed, escalated to him once (it waited on an in-person BIOS visit). Whether work that Steve1 could take was
waiting then: no job was queued `[measured zero]`; whether a visit check could have gone is UNMEASURED (no feed existed
before 11-22). Two routes to the other game do not exist: while Steve1 is held, its queued jobs do not go to Steve2 or ArchSmall.
A pause covers the whole machine.

**What could go to SteveDesktop:** 43 of 443 live checks of 6 mods carry a `testq` block (Pyrelands 33 of 38, FlowWorks 10 of
32, GimmeSomeSlack 0 of 206, LeaningScrub 0 of 79, ExplosiveKnockback 0 of 56, Graffiti 0 of 32) `[measured: test_table.json]`.
Steve2 takes "any free game" work in principle and is empty of routes in practice. Open items: `RIMMANDRAKE_TAG_GSS_LIVE_CHECKS_FOR_STEVE_NONE_OF_203_CAN_GO`,
`RIMMANDRAKE_ROUTE_TESTQ_PROOF_BUILD_JOBS_TO_STEVE`.

## 4. What plain Python can take (Question 4)

| candidate | class | what the code does | does it exist? | risk |
|---|---|---|---|---|
| **A. Count lane results.** Turn each DONE visit job into rows of the open visit's `rows.jsonl`; verify the item of a `--proofs` job | MECHANICAL | Map chain to check by the `testq` block; write verdict, game, sha, unit with the fields of `build_match.py identity`; replace the retired, dead `relentless_game` route by `rimflow verify` | half: ingest does it for item jobs; the row writer is missing; the proofs route is dead | a row on another build counts; keep the build match as the door, and "could not look" as its own word |
| **B. One-line ask.** `testq.py ask ITEM` (or `ask MOD --check C`) fills profile, tier, deploy, sha, item, lane; refuses in words when the lane cannot run it | MECHANICAL | Reads the item's live-proof lines, the test table, the tier; checks sha on main; checks the site save, `python.exe`, packages, proof-build need; holds as pending until the companion is staged | parts: submit checks, preflight, `testq_blocks derive` | it asks a check that the mod does not need; purpose stays with the agent |
| **C. Stop on a repeat.** Two of the same refusal or INVALID note on one game stops that game and opens one item with the two worker logs | MECHANICAL | `repeat_guard.py` already holds one chain after an INVALID of class TEST or DELIVERY; it reads neither REFUSED nor the game, so each new chain set met the same wall | yes, half: it did not see the 47 | a transient refusal stops a game; a program then retries once after 30 minutes, not an agent |
| **D. Pause with an end.** `pause` demands `--hours` or a readable end (unit ended, item closed); the tick resumes when it is met; while paused, jobs of lane `any` go to the other free games | MECHANICAL | reads the end condition each tick; writes why it waits | partly: `pause --hours` exists and is not forced; a no-hours pause escalates | resumes onto a machine under test; the condition names the unit that must be gone |
| **E. Host facts file.** Before a job: installed package ids, python packages, site saves, zoom mod, free disk, read from the machine each hour; submit and the list builder read the file | MECHANICAL | one ssh read into `steve_host.json` with age; an old reading is UNMEASURED | no; today each is learned by a failed job | a stale file refuses good work; stale reads as unknown, never as absent |
| **F. Spoiled kept game.** After "dead colonists" or "site not quiet", the worker stops the game | MECHANICAL | same as the red-canary rule | yes for canary and wounded maps only | one more cold load (about 8 min) per case |
| **G. Window on the ledger line.** `ingest.py` adds the fault-window id to the verify and finding text | MECHANICAL | one string; backfill as notes is optional | `fault_window` tag exists in the record | none named |
| **H. Wait and wake.** A submitter waits with one command that returns the rows; the tick notifies the submitter's item | MECHANICAL | `testq.py wait JOB`; note on the item at the end (exists for item jobs) | partly: `show`, hand loops, `waitfor.py` | hides a hung job; it must read the heartbeat |
| **I. Steward items by cause** | MIXED | see `RIMMANDRAKE_KEY_STEWARD_ITEMS_ON_CAUSE_NOT_FRESH_NAMES` | open item | a wrong key merges two stalls |
| Class a FAIL row as mod, check or scene; find a harness cause; write a new chain; decide a site | JUDGEMENT | none | - | a wrong class moves a mod |

## 5. The load (Question 5)

Claude turns whose tool call is SteveDesktop work, 7 days to 2026-11-23 8:30 PM, by fixed rules on the command text
(`census/tokens.py`). All turns on this machine: 1,716.6M `[measured]`.

| act | turns | weighted tokens |
|---|---|---|
| Reach the machine over ssh | 334 | 5.32M |
| Read a job or the lane | 275 | 4.14M |
| Set up (companion, mods, deploy, install, game) | 112 | 2.13M |
| Wait for a job | 111 | 1.83M |
| Submit a job | 52 | 0.93M |
| Lane control (pause, resume, cancel) | 55 | 0.77M |
| **Subtotal: setup, submission, waiting, reading, control** | 939 | **15.1M** (0.9% of the week) |
| of which in fault and audio diagnosis runs | | 3.9M |
| **Routine remainder** | | **11.2M** (0.65%) |
| Machine fault work | 183 | 3.20M |
| Lane code and page work | 1,114 | 23.68M |
| Ledger or note text that names SteveDesktop | 436 | 11.78M (an upper bound: the turn did other things too) |
| Other text that names it | 844 | 13.72M (mostly reading; the rules cannot split it) |

Total with a SteveDesktop word in the command: 67.4M, 3.9% `[measured]`. The setup and reading turns that name no SteveDesktop
word (a driver that reads a copied result) are UNMEASURED; a split of each turn by its result text would measure them.
Each class rule matches the first rule; a turn that does two things goes to one class, error UNMEASURED.

**Runs on SteveDesktop itself:** the model analysis could not see them. `tokens.py` ran there over ssh: 36 transcripts
changed in the 7 days, 0 unreadable, 0.5M in all, 0.04M of it SteveDesktop work `[measured]`. Codex and GPT on either machine: UNMEASURED (no Codex meter in these records).

**What it means:** the tokens are small. The loss is game time and trust: 94 asked jobs gone to setup, 149.9 h of asked
work waiting, 163 PASS rows counted nowhere. And the 23.7M a week of lane code work is the price of fixing one cause after
another by hand.

## 6. The changes, ranked

Prevention is counted on the past 21 days, and only where the fault is not already fixed on main. Gains are guesses.

| rank | change | failures prevented | tokens saved in a week | build | risk |
|---|---|---|---|---|---|
| 1 | A: count lane results | all visit-feed results (22 DONE jobs, 163 PASS rows in 2 days) and every proofs job with no seat note (3 of 12 since 11-18) `[measured]`; saves Arch game time for those checks `[guess ~55%]` | 1.5M `[guess ~40%]` | medium | a row on another build |
| 2 | C: stop on a repeat | 81 jobs: 38 of the 47 Steve2 refusals, 43 others `[measured: census/repeats.py, runs of one note in a row on one game, less the first two]` | 1M `[guess ~40%]` | small | a transient refusal |
| 3 | B + E: one-line ask and host facts | of 16 asked setup deaths in the last 7 days, about 8 still have a live cause (list, companion race, sync) `[guess ~50%]`, plus about 14 asked and 12 filler jobs a week that measured nothing `[measured]` | 3M, from 51 help calls, waits and wrong selectors `[guess ~45%]` | large | asks a needless check |
| 4 | D: pause with an end | 49.3 h with no end and the 142.7 h asked work waited under a pause `[measured]`; about half could have run on another game `[guess ~40%]` | 0.3M `[guess ~40%]` | small | resumes under a soak |
| 5 | F: stop a spoiled kept game | 33 jobs in 21 days had at least one such row, 13.5 lane hours in them `[measured]`; about 15 jobs `[guess ~40%]` | 0.5M `[guess ~35%]` | small | one more cold load |
| 6 | G: window on the ledger line | 157 unmarked verdicts on the ledger `[measured]`; the fault is off since 11-21, so its use now is the past | 0 | small | none named |
| 7 | H: wait and wake | waits 1.8M and part of 4.1M reads | 1.5M `[guess ~45%]` | small | hides a hung job |

The rows overlap, so the gains do not add up. Together: about 6M a week `[guess ~40%]` of 15.1M. Change 1 and 2 are the first
pair to try: small to medium, they touch the two counted halves of his claim.

## 7. What this study could not see

- Codex and GPT tokens on either machine.
- Results that an agent read and acted on without the job id in any file. `ledger_after.py` is a floor.
- Steve2 before 2026-11-23 2:56 AM: it had no lane. Use of either game by hand is in no lane record.
- The exact cause of each NOT_RUN row.
- The queue on SteveDesktop that a submit used before 780f797c48.
- The saving of any change before it is built.

## 8. Open items cited, not repeated

`RIMMANDRAKE_ROUTE_TESTQ_PROOF_BUILD_JOBS_TO_STEVE`, `RIMMANDRAKE_ROUTE_PYRE_TESTQ_OFF_STEVE_NO_SITE_THERE`,
`RIMMANDRAKE_TAG_GSS_LIVE_CHECKS_FOR_STEVE_NONE_OF_203_CAN_GO`, `RIMMANDRAKE_KEY_STEWARD_ITEMS_ON_CAUSE_NOT_FRESH_NAMES`,
`RIMMANDRAKE_FIX_STEVE2_LOAD_PREPARE_REFUSES_RUNNING` (fixed, open), `RIMMANDRAKE_KEY_TESTQ_SKIP_CACHE_ON_INPUTS`,
`RIMMANDRAKE_CACHE_TESTQ_DONE_READS_TICK_OUTRUNS_HEARTBEAT`, `RIMMANDRAKE_MEASURE_STEVE_NOTHING_HOURS_ON_SETTLED_JOBS_ONLY`,
`RIMMANDRAKE_FIX_STEVE_WORKER_STALE_INDEX_LOCK_BEFORE_PULL`, `RIMMANDRAKE_FIX_STEVE_LANE_WORKER_AND_GAME_STOPS`,
`OPS_STEVE_FEED_IDLE_LANE_HURP`, `STEVE_LANE_MONITOR_PAUSE_FINDINGS`, `STEVE_FILLER_MONITOR_FAIL_FINDINGS`,
`RIMMANDRAKE_SORT_OLD_STEVEDESKTOP_TICKETS_IN_ONE_PART`.
