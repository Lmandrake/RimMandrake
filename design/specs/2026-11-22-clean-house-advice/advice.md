# Advice: how to clean house without a rebuild

For Mandrake. Written 2026-11-22, about 4 PM PST, by a Fable helper of the Conductor. Tree read: `b8b9d42af8`.

Each claim is tagged `[measured]` or `[guess ~N%]`. UNMEASURED means that the instrument could not see. Spend is in
weighted tokens (`weighted_v2`).

## Summary (one page)

**Why your studies did not come back.** They were written. Each of your 21 study requests since 2026-10-29 produced
a document or a build `[measured]`. Three reached you whole. Three reached you only as question cards. For twelve,
the ledger has no record that you saw the document. I searched the Conductor's transcripts for five of those: two
were never named to you, and three were named in one or two chat messages `[measured]`. The causes that fit:

- A helper writes the study and cannot speak to you. The Conductor is the only path back, and it is the busiest
  seat. Its delivery, when it happened, was a line in a busy chat. This is the Conductor's fault.
- A study closes when its file exists. Nothing records that you read it, and nothing measures later if it worked.
- Each study looked at one slice and ended as tickets or new machinery. So each cleanup made the thing larger.
- The system that a study advised was often retired within two weeks.

**The diagnosis.**

1. The redundancy is of one kind: a generic service (who holds a thing, what runs next, what a run spent, how to
   launch a worker, how to tell you) was built again by each run that needed it.
2. The generator is still on. Each failure is answered with an addition: a rule, a gate, a test, a ticket. Nothing
   has a path to removal. For each commit on a mod, 2.3 commits change machinery `[measured]`.
3. Nobody owns the architecture, and no page shows it.

**The common systems we really need: nine.** A work record. A mod state machine that decides each next act. One
runner that starts a worker with typed input and output. One lease library for "who holds X now". The game driver.
One check runner. One judge harness. One desk for you. One watchdog. A tenth, the door to a second model, belongs
outside this project. The mechanism of each is generic; only the policy is ours.

**The strategies.**

| name | what it is | verdict |
|---|---|---|
| Strangle | Replace each duplicate behind a fixed interface, with a proof. Today did this six times | The method |
| Core | A small state machine in plain Python owns every decision. An LLM run is a leaf worker | The destination |
| Adopt | Outside tools for the generic parts | Typed worker output now |
| Trial | Three days, outside the pipeline: our tick against an outside workflow library, on the same crash tests | Once, in week one |
| Freeze | No new machinery for 14 days, one architecture owner | Yes. It turns the generator off |
| Observe | Record for seven days what is really used. Park the rest | Yes, first |
| Thin line | One mod through every stage on the core path only | Yes. A mod keeps moving |
| Rebuild | Archive and build again | No. Four rebuilds in seven weeks made this |

**My recommendation.** Freeze, Observe and Thin line now. Strangle toward Core for two weeks. Run the Trial. Measure
on day 14 and decide again. The first three acts:

1. You correct one architecture page: the nine systems, one home each (section 3 is its draft).
2. A recorder goes on for seven days.
3. The freeze starts: nothing new enters the pipeline unless it replaces something or a run was voided for lack of it.

**Where I disagree with you.** The work was done; only the return failed, so the remedy is delivery, not more
studies. "Deterministic" must mean one program decides each thing, not more gates. "If you see it, do it" is right
for a mod and makes duplicates in machinery that has no map. A laboratory for "a new way every week" makes cruft:
for a fixed time, choose the factory.

**Your decisions** (section 7): the freeze; who owns the architecture; where experiments happen; the 990 idle
tickets; the study rule; typed worker output; the engine trial; the change to "fix it in the same run".

**So that a study cannot be lost again** (section 8): the run delivers its own study. It opens the one-page summary
on your screen and records the delivery. No seat is in the path. The study stays first in your daily digest until
you react or dismiss it.

GPT attacked the first draft. It found a counting error and argued for an outside engine harder than I do. Section
10 shows what I took and what I did not.

---

## 1. The past studies, and why they did not return

### How this was measured

- `python3 src/RimMandrake/rimflow/owner_rulings.py --last 0 --grep "<words>"` with the words consolidate, cruft,
  redundant, simplify, streamline, deterministic, single source, clean house, crystallize, generalize, re-invent,
  architecture, kludge, duplicate, unify, study, audit and others. It gave 120 of your rulings `[measured]`.
- A replay of the ledger (`model.read()`, 76,558 events, 9,714 items) for every item whose name holds one of 25 study
  words. It gave 461 items. I kept the ones about process and machinery `[measured]`.
- For each kept item: its filing, its close, its last notes, and the state of the tickets that it made.

"Reached you" means that the ledger has an event that shows it: a card answer, your words, or an item that says the
document was opened for you. What the Conductor said to you in its window is not in the ledger. So "no record" means
no ledger record. It does not mean "never". A check of five documents against the transcripts follows the table.

### The table

Dates are the ledger's date of filing. "Built" means the tickets or changes that the study named.

| date | what you asked | what was produced | reached you | what happened to its advice |
|---|---|---|---|---|
| 10-29 | Document the whole agent workflow of that time, then a skeptical GPT review and a risk report | The document, the GPT review, a risk response. Closed 11-01 | Yes, whole. You decided on 11-01 | Eleven or more tickets were filed. The pipeline that they repaired was retired 12 days later. Orphaned |
| 10-29 | Compare this elaborate system with a simple loop of one prompt. Simulate both. GPT checks | A design and a simulation in 45 minutes. The GPT check stayed owed. Dropped 11-01 | No record | The loops ran on three mods from 11-07 and were retired on 11-13. The comparison never gave a verdict |
| 11-01 | Design an agent that never forgets a trap twice, GPT review, build at top priority | Designed and built. Dropped 11-16 | Partly (you named it) | Retired on 11-13 with its pipeline |
| 11-01 | Make the architecture simulations compare on equal terms | Done in the same hour | No record | The simulations served a pipeline that is gone |
| 11-04 | (the Conductor's own) Enact the timer audit "finally read" | Timers pruned, closed 11-05 | No record | Built. The item's own name says the audit had waited unread |
| 11-07 | Spring clean: extract and promote skills from every agent, handoff and rule file | A report in `D:\ClaudeWork\rimmandrake\conductor\spring_clean_2026-11-07\REPORT.md`. Closed in three hours | No record | Partly. Ten promoted skills were still not exported when the item closed |
| 11-11 | Study an outside agent factory demo for what it means for us | `design/RimMandrake/warp_cloud_factory_study_2026-11-11.md` | No record | One adoption was filed. It was later dropped |
| 11-12 | List every validation scheme so that you can argue a stage ladder | 55 schemes listed. A stage map with rules | Yes, as three cards | Partly. The rules landed. The one clean-up of the nightly test run is still not started. That run was red on 29 of 29 nights |
| 11-15 | Find every time the Conductor stepped into the pipeline, and build that wisdom in | 134 interventions, 42 lessons, each with a state | No record | Mostly built in the same run |
| 11-16 | Review every pipeline door. Put the cheapest deterministic check at each | A design, a two-screen findings page "for the owner", nine tickets | No record. The helper wrote "LEFT OPEN: for the Conductor to relay the findings". The item was closed three days later by a run that swept the owed list for trash | Built. The six tickets that I checked are done |
| 11-16 | Deep design: join long-term mod holders with the pipeline. Three options | A design with three options, a build plan | Yes, whole. You picked | Partly. The per-mod ledger is built. The cut-over of the three pilot mods is still in work |
| 11-17 | After the account resets, fix every filed pipeline ticket and close every old-era ticket | Four faults fixed. A census of 205 pipeline tickets into lanes on 11-19 | No record | Not done. The item is open. The red-test lane is still in work |
| 11-18 | Find why the review of pipeline code never ends. Give options | A problem page, a design with three options | Yes, as cards (three decisions) | Built as the boundary-page rule. The calibrated review brief is still in work |
| 11-19 | Is the retirement of the old eras complete? | A census: not complete, 21 things remain | Yes. An item says the report was opened for you | Mostly built |
| 11-19 | Crystallize: merge the rule file against the rulings and the memory | Done in 30 minutes | No record | Built |
| 11-19 | Crystallize: sweep records, skills and lessons, and propose changes | A 360-line report with three candidate changes | No record | The item is still open. Ten lesson clusters were merged |
| 11-19 | Drain the project rule file to one line and one pointer for each rule | Done | No record | Built. The file is 732 lines today, larger than before the drain `[measured]` |
| 11-20 | Package the whole system and send it to GPT: why does the system still push back on me? | A GPT analysis with 15 ranked changes and ten contradictions between documents | Yes, as four cards | Not done. The item to carry it out is still "proposed". It has had no event since 11-21 |
| 11-21 | Review the repairs since the new pipeline. Find the few principles. Fix the form | Nine principles. Four general faults fixed in three runs | No record. The review file says "Questions for the owner: none" | Partly. The item is open and waits on another item |
| 11-21 | How do we compress the rule files that doubled in eight days? | 302 sections classed. 6,955 lines became 6,661 | No record | Done as asked, with a result of 4%. The files did not get smaller in any way that matters |
| 11-21 | One fast deterministic way to take and release a game | Built in under two hours, 14 promises tested | Reported at close | Built. This one is a clean success |
| 11-22 | Sweep the whole pipeline for things that should be one script | 12 candidates, eight groups | Reported at close | Six groups were built on the same day |

Counts `[measured from the table]`: 22 rows. 21 are your requests, and one (11-04) is the Conductor's own. All 22
produced a document or a build. 3 reached you whole (10-29 workflow, 11-16 holders, 11-19 eras). 3 reached you as
cards (11-12, 11-18, 11-20). 1 reached you in part (11-01). 2 were reported at close (11-21 lock, 11-22 sweep). 13
have no ledger record that you saw them; 12 of those are your requests.

### A check against the Conductor's transcripts

The ledger cannot see what the Conductor wrote to you in its window. So I searched the Conductor clone's transcripts
(`~/.claude/projects/-home-mandrake-rm-bench`, 4.9 GB) for the file names of five "no record" documents, and classed
each match by who wrote it `[measured]`:

| document | in a Conductor message to you | in tool calls only |
|---|---|---|
| Door study findings (11-16) | 2 messages | 8 |
| Outside factory study (11-11) | 1 message (and 2 of your own messages name it) | 10 |
| Spring clean report (11-07) | 2 messages | 40 |
| Crystallize sweeps report (11-19) | **0** | 14 |
| Principles review (11-21) | **0** | 12 |

So "no record" has two meanings. Two of five documents were never named to you. Three were named in one or two chat
messages, among the many messages of a working day. I did not read those messages, so I do not know if they gave the
findings or only the path. A limit: old transcripts may have been removed, so a zero for an old document is weaker
than a zero for a new one.

### Why they did not return

These causes fit the evidence. The evidence does not exclude others. One other reading: some studies were dropped on
purpose, because the system that they advised was retired (cause 5), and nobody said so to you.

1. **One path back, through one seat, with no record of delivery.** A detached helper writes the study and ends. Its
   note says "NEXT: the Conductor reads it with the owner". The Conductor window restarts its context several times
   each day. Nothing made "show him this document" an act that survives a restart until 2026-11-15, when the owed list
   was built. The door study of 11-16 shows that the owed list is not enough: the study was owed, and a later run
   closed it as trash. When delivery did happen, it was a line in a chat, and nothing recorded it.
   **This is a failure of the Conductor seat.** It is my seat's fault, not the helpers' fault.
2. **A study came back as cards.** A card is a narrow question with a recommended answer. Your own rule (ask only
   with evidence, and take the obvious answer) pushes the Conductor to shrink each study to its two or three real
   choices. That is right for decisions. It is wrong for a diagnosis. You answered the cards and never saw the page.
3. **Done means "the file exists".** No study item needed your reaction to close. No study named a number and a date
   to measure it again. So nobody, you included, could see that a study had failed. The rule-file compression is the
   example: it passed every check and removed 4%.
4. **Each study was a slice, and its output was additive.** The 21 studies made tickets, rules, gates, a census tool,
   a lint. Not one of them had the removal of machinery as its measure. The backlog that receives the tickets has
   1,962 open items, and 990 of them had no event in 14 days `[measured]`.
5. **The ground moved.** Between 2026-10-27 and 2026-11-13 the project had at least four pipeline designs (the third
   workflow version with its seats, the agent that never forgets, the one-prompt loops, the Maturation Pipeline)
   `[measured: design/RimMandrake/retired_eras_index_2026-11-18.md]`. The first four studies in the table advised a
   system that was gone within two weeks.
6. **The rate** `[guess ~60% that it is a cause]`. You filed 13 of the 21 study requests in the last four days. In
   the same days you filed between 11 and 33 owner items each day `[measured]`. A helper starts within minutes of each
   request. Each result then competes with the next request for the one path back. I did not measure how long a
   study waits or how long you need to read one, so this cause is an inference.

---

## 2. The diagnosis

### The size of the thing `[measured, tree b8b9d42af8]`

| what | count |
|---|---|
| Age of the repository | 101 days (first commit 2026-08-13), 44,600 commits |
| Mod code (C#) | 3,104 files, 717,109 lines |
| Pipeline core `src/RimMandrake/rimflow`, not tests | 202 Python files, 99,617 lines |
| Its tests | 291 files, 100,477 lines |
| Tools `src/RimMandrake/Utils`, not tests (mod tools, art tools and pipeline tools together) | 1,000 Python files, 344,128 lines |
| Their tests | 948 files, 172,550 lines |
| Test files named `selftest_*` in the whole tree | 1,781 |
| Hooks | 34 hook programs, 38 registrations, 10,465 lines with their tests |
| systemd unit files in the tree | 83. Installed timers: 30 |
| Role files that an LLM must follow | 21 files, 3,908 lines |
| The four rule files (root rule file, standing rulings, charter, roles) | about 6,700 lines |
| Sections in the root rule file | 48 |
| Lessons, facts, skills | 627 files, 255 files, 32 skills |
| Spec folders, boundary pages | 121, 78 |
| Ledger | 76,558 events, 9,714 items, 1,962 open |
| Mod versions that passed and have a tag | 1 (the tag rule began 2026-11-13) |

Files that the pipeline's own test list calls pipeline machinery: 168 `[measured by today's sweep]`. So the machinery
that decides is about 170 files. Around it stand about 1,000 tool files. Nobody knows how many of those still run.

### Where the last 30 days went

**Tokens** `[measured, with limits]`. Source: the 933 detached run records of the last 30 days in
`D:\ClaudeWork\rimmandrake\dispatcher\detached`, weighed by `role_launch.tokens_v2`. Total: about 1,771 million
weighted tokens. This is an upper bound, because 405 records are in the old unit and convert to an upper bound. 66
records have no figure.

| class | runs | weighted tokens | share |
|---|---|---|---|
| A mod (the launch names a mod, or the item names one) | 353 | 750 M | 42% |
| Machinery (the item name holds a pipeline word) | 307 | 559 M | 32% |
| Not classed by this rule | 273 | 462 M | 26% |

The 25 most frequent unclassed items are about half mod work and half machinery `[measured by reading the names]`.
So machinery took about 40 to 45% of detached-run tokens `[guess ~60%]`. In the week of 2026-11-16 alone, machinery
runs took at least 390 M. The Conductor windows and their subagents are not in these records: UNMEASURED.

**Commits** `[measured: git log --since="30 days ago" --numstat, classed by path]`.

25,484 commits in 30 days.

| class of commit | commits | share |
|---|---|---|
| Ledger or state files only (a note, a claim, a close) | 15,970 | 63% |
| Machinery (`rimflow`, `Utils`, hooks, rule and role files, skills) and no mod file | 3,949 | 15% |
| Design documents only | 3,288 | 13% |
| A mod and no machinery | 1,753 | 7% |
| A mod and machinery together | 524 | 2% |

For each commit that changed only a mod, 2.3 commits changed only machinery. In the last week (2026-11-16 to 11-22)
the ratio was 3.8 to 1 (761 against 198). Changed lines in 30 days: 1,076,000 in machinery paths against 733,000 in
mod paths. A limit of this count: `Utils` also holds mod tools and art tools, so "machinery" here is wider than the
pipeline.

Your sentence "it is getting hard to keep fixing rather than building" is measured: by commits the factory gets two
to four times the attention that the mods get, and the ratio is rising.

### The kind of redundancy

The duplicates are not copies of code. Each one is **the same generic service, built again by the run that needed
it**. Listed by function, with the evidence:

| function | the homes found | state today |
|---|---|---|
| "Who holds X" | Game driver (four records disagreed until 11-21), the owner's hold of a mod, a control act that switches a mod off, a ledger lease on an item, the clone pool, the account slot | The game lock has one home since 11-21. The others each have their own record and their own reader |
| "What does this mod do next, and may it run" | Five places. Three of them gave three different answers for one held mod on 11-22 `[measured by the sweep]` | One home built today |
| "Which account is live" | Seven parsers of one command's output | One home built today |
| "What did a run spend" | Four stores, three rules for the unit | One home built today |
| "Which model does this alias mean" | Three tables that did not overlap | One home built today |
| A place to keep state | The ledger, the control store, a stage record for each mod, the new per-mod ledger, a journal in prose, the detached run records, a spend file, a voids file, the test queue, an operations ledger, an art ledger, a card store, a list of hand acts | No merge is planned. The status page read "next" from journal prose until today |
| A launcher of a worker | The role launcher, the detached helper, the pipeline tick, a pilot launch, a hand run, the test queue's runner, in-window subagents | Not merged. 98 hand acts are on record. 71 of the first 96 were a person deciding what the tick decides `[measured]` |
| A list of things to do | The ledger queue, the owed list, the hand-acts list, the known-red list, 35 polish lists, a "needs Conductor" list, the lanes census | Not merged |
| A page that says what is happening | The pipeline page, the running page, the fleet page, the code page, `./pipe why`, the daily digest, the operations digest | Not merged. Two of them disagreed on 11-22 |
| A reviewer or judge | Clean-code status, the findings judge, the blind judge, the coverage judge, the examiner, the fresh reader, the GPT review, the art judge | One rule each. No shared harness |
| A gate | 34 hooks (three split a shell line three ways), launch checks, preflight, tree checks at publish, a pre-push hook that runs four guards a second time | Hook merge planned in the sweep |
| A check that it is alive | The deadman, the metronome, the operations watch, 30 timers. Two clocks are listed as live and are disabled | Partly |
| A second model | The sibling run found 16 homes of the Codex sign-in | In work today |
| Things the sibling repositories already have | A ticket store (Lodestar `ticket.py`), a handoff tool (Lodestar and MandrakeWorkflows `handoff.py`), a digest (Lodestar `digest.py`), a model and second-opinion router (Dispatch `delegate`), a role runner (MandrakeWorkflows `role_runner.py`), a wait tool (Machinist `waitfor.py`) | RimMandrake has its own of each `[measured by file name; the degree of overlap in behaviour is UNMEASURED]` |

### How much is load-bearing

UNMEASURED, and that is itself the finding. Today's sweep called 272 of 322 pipeline files "single home already" from
a keyword search only. Its dead-code scan found 48 dead lines, by name only. Nobody has recorded which files run in a
normal week. My estimate: the path that takes a mod from design to a pass uses fewer than 150 of the roughly 1,200
Python tool files `[guess ~50%]`. The Observe strategy (section 4) replaces this guess with a measurement in seven
days.

The parts that I judge load-bearing and not redundant `[guess ~75%]`: the game bridge and its companion tools, the
deploy and build tools, the ledger writer, the publish door, the game lock, the account switcher, the mod tools and
the art tools. These are specific to the work and each has one home.

### What keeps making new cruft

1. **A failure is answered with an addition.** The reflex is a new rule, gate, test or ticket. Your rulings feed it
   too: a ruling becomes a section of the rule file. The root rule file has 48 sections. At least nine of them exist
   to limit an earlier rule or gate (a gate must not refuse the Conductor; a fault of form must not stop work; a limit
   must name its danger; only the related checks run again; only five acts stay yours; ask only with evidence; touching
   code has a cost; the judge refuses flaws only; no agent is told its spend) `[measured by reading the file]`. A rule
   that corrects a rule is the mark of a system that only adds.
2. **Prose where a program must decide.** About 6,700 lines of rules steer control flow through an LLM that reads
   them each time. That reading is not deterministic. The 71 hand acts are its cost: a person did what the program
   should have decided.
3. **The fix is made by the run that hit the fault.** That run sees one fault and one file. It cannot see that the
   service exists elsewhere, because no page says so, and a search by keyword does not find it. Your user rule 8
   measured this: four of six "new" mechanisms already existed.
4. **Nobody owns the architecture.** The charter is a process rulebook. The 121 spec folders are 121 patches. No page
   lists the systems, their one home and their interface. So "does this exist already?" has no place to be answered.
5. **A new pipeline every two weeks, with removal done later.** Each of the four designs left names, paths, units and
   tickets. This document was written in a folder that is still named for a retired pipeline.
6. **Agents make building cheaper than reading.** A helper can write 500 lines with tests in 20 minutes. To find and
   understand the existing 500 lines costs more. The economic default is to build.
7. **Tests of machinery are machinery.** 1,781 test files need care too. The nightly run was red on 29 of 29 nights.
   Today's census of red tests found tests that guard retired things.
8. **Two purposes.** The stated purpose is a game and a laboratory. The laboratory is the reason for the four designs.
   That is a fair price for research. It is not a fair price for a factory that must be dependable.

---

## 3. The common systems that we really need

I argue from the work, not from what exists. To turn a mod design into a passed mod, the factory must do ten things:

1. know what work exists and in which state;
2. decide the next act for each mod;
3. start a worker on that act, with a brief, an account, a model and a workspace;
4. give the worker the one game or the one clone that it needs, and take it back;
5. put a build into a game and read the game;
6. run the checks that the change touches, offline and in game;
7. get a judgement of taste from a reader who did not make the work;
8. land the result and record it;
9. bring to you what only you can do, and tell you the rest;
10. notice when any of this has stopped.

That gives nine systems. A tenth is outside the project.

| system | its one job | its one home (proposed) | what maps onto it today | what dies |
|---|---|---|---|---|
| **Work record** | One append-only record of items, runs and each mod's stage. Every list and page is a view that a program builds from it | The ledger for items; the control store's run record for runs; the per-mod ledger for stages | Ledger, control store, stage records, mod ledger, detached records, spend file, voids file, hand-acts list, owed list, known-red list | Journal prose as state. The spend file. Each separate list becomes a view. "Next" and "waiting on" text typed by an agent |
| **Mod state machine** | A pure function: (stage record, holds, leases, last results) gives the next act and who does it. It is the only place where a stage moves | `rimflow/mod_next.py` with the tick as its only caller that acts | `mod_next.py` (new today), `maturation.py`, `maturation_dispatch.py`, `control.py`, the steward briefs | Role-file prose that tells an agent what comes next. Hand runs that repeat a tick decision. Every second reader of "may it run" |
| **Runner** | Start one worker: typed input, one account, one model, one clone, one spend stop. Return one typed result and one run record | One module made from `detached_helper.py` and `role_launch.py` | Both of those, the pilot launch, hand launches, the model tables, the account pick, the spend watchdog | Every other launch path. Result parsing by reading prose. The brief paragraphs that tell a helper how to publish or close |
| **Leases** | One library for "who holds X now": a named resource, a holder that is a process, since when, for what. It is free when the process ends | `rimflow/game_lock.py`, made general | Game lock, clone pool, account slot, item lease | Each private lock file and its reader. The glance file for the bridge |
| **Game driver** | Put a build into a named game, drive it, read it, capture it | The bridge, its companion tools, `deploy_custom_mods.py`, `winbuild.py`, the capture tools | The same | Little. This is ours and mostly has one home |
| **Check runner** | One table of checks for each mod. Each check names what it reads. After a change, run only the related checks. Three answers: pass, fail, could not look | The test queue and `run_selftests.py`, joined | Test queue, selftest runner, publish tree checks, nightly run, the per-stage validators, the known-red list | The nightly run as a separate thing. Tests that guard retired things. About 15 of the 55 validation schemes that nobody runs |
| **Judge harness** | One way to ask a fresh reader for a verdict: typed input, a calibrated brief, a typed verdict (pass, or the holes) | One module. Each kind of judge is a brief, not a program | Blind judge, coverage judge, examiner, fresh reader, findings judge, art judge, code review | Seven separate launch and parse paths |
| **Your desk** | One queue of what waits for you and one page of what happened. Each entry has a due time | One generated page and the daily digest, both built from the work record | Cards, card store, owed list, daily digest, operations digest, the pipeline page, the running page, the fleet page, `./pipe why` | Five of the seven pages. Any status text that an agent types |
| **Watchdog** | Notice that the tick, a run, a disk or an account has stopped. Reopen one fixed item | The deadman and the metronome | Deadman, metronome, operations watch, 30 timers | Most timers. Alarm rules that nobody acts on |
| *Second-model door* (outside) | One door to GPT, Codex and image generation | Dispatch | The 16 sign-in homes, the consult tools, the art requests | The local copies. Two sibling runs work on this today |

**Mechanism and policy.** In each system the mechanism is generic and the policy is ours. The stage ladder, the bars,
the judge briefs and the game tools are ours. How to record, launch, lease, run a check, call a judge, show a page and
watch a clock is generic. A generic mechanism must not be written again inside this project. It comes from a sibling
repository or from an outside tool, or it is written once here behind an interface that names nothing about RimWorld.
The game driver is the one system that is ours through and through.

**What this table is not yet.** It is a list of jobs and homes. It is not an architecture until each row also has a
contract. GPT pressed this point and it is right. The architecture page must add for each system:

- its one writer, and who may read;
- what it answers when it could not look, and when it failed;
- what happens when its process dies in the middle (which act is safe to do twice);
- how a result is tied to the build that it was made on.

Four things are missing from the table and belong on the page:

- **A hold is not a lease.** Your hold of a mod and a control act that stops a mod are policy. They must outlive any
  process. They are inputs of the state machine and live in the work record, not in the lease library.
- **One commit point.** The work record is three stores (items, runs, stages). One program, the tick, must write a
  run's result and the stage move that follows from it, in a fixed order that is safe to repeat. Today several
  programs write them.
- **Build identity.** Every result names the build that it read. The pipeline has this rule in part (evidence bound
  to one build). It belongs to the check runner's contract.
- **Workspace and landing.** A clone for a worker, and the publish door, are parts of the runner. They exist and
  mostly have one home.

**What is not a system.** Rule prose. After the state machine decides control flow, an LLM needs four kinds of text:
the purpose, the guiding principles of the game, one short brief for each kind of worker, and facts that it cannot
guess. My target: fewer than 1,500 lines for the first three `[guess ~50% that this is reachable in a month]`.

---

## 4. The strategies

Costs are `[guess ~40%]` and are in weighted tokens. They leave out your attention and the cost of an outage. For
scale: detached runs took about 60 M each day in the last 30 days. The present pipeline took nine days and at least
517 M of machinery runs to reach today's state `[measured]`. Today's seven consolidation runs cost 12.2 M together,
1.2 to 2.1 M each `[measured from their run records]`.

### Strangle: replace each duplicate behind a fixed interface, with a proof

What today did six times: name the fact, build its one home, replay recorded inputs through the old paths and the new
one, class each difference, plant faults, delete the old paths.

- **Buys:** low risk. Each step is small and can be reversed. The proof finds real bugs (today: a status page that
  guessed a run's stage wrong for 13 of 91 runs).
- **Costs:** about 1.7 M for each group `[measured today]`. The sweep saw one layer, by keyword. I expect 30 to 60
  more groups `[guess ~40%]`: 50 to 100 M, two to four weeks beside other work. The larger merges (launchers, stores)
  will cost more than today's small ones.
- **Risk:** it removes duplicates and leaves the generator on. At 375 single-case repairs in eight days, new
  duplicates arrive faster than proofs remove them. It also does not shrink the prose. A proof against recorded
  behaviour can also keep an old bug: each difference must be classed against what the fact should be, not against
  what the old code did.
- **In one week it works if:** each tracked fact has one home, each proof lists its classed differences, and no merged
  fact was repaired again.

### Core: a deterministic state machine owns every decision

Write down every decision of the pipeline (about 40, I estimate). Mark each one: a program decides it, an LLM judges
it, or you decide it. A program decides all control flow: what runs next, where, on which account, whether a result
counts, whether a stage moves. An LLM run is a leaf: typed input, typed output, no knowledge of the pipeline. Delete
each rule line that the program now decides.

- **Buys:** this is what "deterministic" can truly mean. The same state gives the same next act. Hand acts become
  defects with a fix. The prose falls because the program made it unnecessary, not because somebody compressed it.
- **Costs:** 60 to 120 M, three to five weeks. Much of it exists: the tick, the stage record, `mod_next.py`. The
  hard part is not the happy path. It is what happens when a run is killed, cancelled or done twice, and my figure may
  be low for that part.
- **Risk:** it becomes the fifth pipeline, built beside the fourth. The guard: the core is reached by Strangle steps
  on the existing files, each with its proof. That guard is a discipline, not a certainty. A second risk: judgement
  is forced into the program. Taste and design stay with an LLM or with you; only the routing is the program's.
- **In one week it works if:** a stage move survives a killed tick and a killed worker in a test (the same state
  gives the same next act, and nothing is done twice), and hand acts for each stage move fall.

### Adopt: outside tools for the generic parts

I checked current options on the web on 2026-11-22.

| candidate | what it would replace | my judgement |
|---|---|---|
| The Claude Agent SDK (Python). It gives structured output against a JSON schema, hooks in code, session resume and subagents | The runner's shell wrappers, the reading of results from prose, a part of the hooks | **Adopt in a small way.** Typed worker output is the largest single gain for determinism. Whether it runs under the subscription sign-in the way the command line does: `[guess ~70%]`, a one-hour check |
| A durable workflow library or engine: DBOS (a Python library; Postgres is its main store and SQLite is supported), Temporal (a server), Prefect, Restate, LangGraph (a durable graph runtime for agents) | The tick, retries, resume after a kill, the run record. We built these by hand: the void of a killed run, the relaunch of a run left open, the continue after a spend stop, the bundle of an orphan clone | **Not on my opinion, and not on GPT's: by the Trial below.** For it: durable execution is exactly the part that we keep repairing, and it matters on one machine too. Against it: our state machine is seven stages by about ten mods; an engine adds a store, a second failure surface and a migration; it removes no rule line and no gate, and those are most of the volume |
| Beads, an issue tracker for coding agents with a "ready work" query | The ledger queue | **Do not adopt.** It moved to a database backend in 2026 and reviewers call it heavier. Our ledger works. Its problem is 1,962 open items, and a new store does not close them |
| Your own sibling repositories: Lodestar tickets and handoff, Dispatch, MandrakeWorkflows role runner | The second-model door now. Later the handoff and lessons tools | **Adopt the door now** (in work). The others only after the Observe census shows what RimMandrake's own copies really do |

- **Buys:** less code that is ours to keep.
- **Costs:** 5 to 10 M for the SDK pilot, more if the sign-in or the sandbox needs work. A full move to a workflow
  engine would cost 80 M or more and two to three weeks.
- **Risk:** a migration is a rebuild under another name. A typed result proves the shape of an answer. It does not
  prove that the answer is true or that the worker's side effects are complete.
- **In one week it works if:** one worker kind returns a typed result that a program reads with no prose parsing, and
  a malformed, a cut-off and a doubled result each give "could not look", never a pass.

### Trial: three days, outside the pipeline, repair against adoption

GPT's strongest objection is that I dismiss an engine by argument. So measure it. In a scratch repository, write one
mod's stage loop (decide, launch a worker, read its result, move the stage) on one outside library. I would pick DBOS
with SQLite, because it is a library and needs no server `[guess ~60% that it is the best first candidate]`. Use fake
workers. Run the same five fault tests on it and on our tick: kill the tick in the middle of a move; kill a worker;
deliver a result twice; a worker that never ends; a restart of the machine.

- **Buys:** a result in place of two opinions. It also gives the fault tests that the Core strategy needs anyway.
- **Costs:** 5 to 10 M, three days, one builder. Nothing in the pipeline changes.
- **Risk:** a toy passes where the real thing would not. The trial can show that adoption is not worth it. It
  cannot alone show that it is.
- **It continues only if:** the library passes all five tests, our tick fails two or more, and the trial code that
  is ours is under a tenth of the size of the tick. Otherwise it stops, and the fault tests stay as tests of our tick.

### Freeze: no new machinery, one architecture owner, a deletion budget

For 14 days nothing new enters the pipeline: no gate, hook, rule section, timer, store, page, list or role. Three
exceptions: it replaces something in the same commit; a run was voided for lack of it; you order it. One seat owns the
architecture page and answers "where does this belong?" in minutes. Each week the machinery must lose more lines than
it gains.

- **Buys:** it turns the generator off. Nothing else here does. It is nearly free.
- **Costs:** 2 to 5 M each week for the owner seat. Some fixes wait.
- **Risk:** a pipeline defect stalls a mod while its fix waits for a home. The voided-run exception limits this, and
  it is also a hole: with 33 voids in nine days, many additions can pass through it. A second risk: the freeze is one
  more rule in a system with too many. So it must be a program: the publish door refuses a new pipeline file that
  names no system. That gate replaces the boundary-page reminder. It does not see machinery that is added inside an
  old file; the weekly diff, read by the architecture owner, must catch that. A third risk: the architecture owner
  becomes a new place where work waits.
- **In one week it works if:** the rule files did not grow, each addition that passed names what it replaced or the
  void that needed it, and no question to the architecture owner waited more than an hour.

### Observe: measure what is used, then remove what is not

For seven days a recorder notes each of our Python files that a process loaded (the modules at the end of each
process, for our paths only), each hook that fired and its verdict, each unit that started, and each rule section
that a refusal or a brief cites. The result is a census. A file is then parked (moved out of the path; git keeps it)
only when three things are true: nothing loaded it in seven days, no other file names it, and it is not on a short
keep list (disaster recovery, account failover, the monthly and the rare paths).

- **Buys:** it answers "how much is load-bearing" with a measurement. It needs no reading of code, so it is cheap. It
  attacks volume directly, and volume is why nobody can find the existing wheel.
- **Costs:** about 2 M and seven days of waiting. The parking: 5 to 10 M, and more if something must come back.
- **Risk:** seven days cannot prove that a thing is dead. A vital thing that runs once a month is parked. The three
  conditions and git limit this. A rule that nobody cites may still shape what agents do, so the census does not
  remove rule text by itself. The recorder is new machinery during a freeze: it is the one exception that I ask for,
  and it is removed after the census.
- **In one week it works if:** the census exists and names, with counts, the files, hooks and units that nothing
  used.

### Thin line: one mod through every stage on the core path

Pyrelands is the only biome mod that advances. Take it through its remaining stages with one rule: every act comes
from the state machine. Each hand act is recorded as a defect of the core and fixed in the core. Whatever machinery
the passage did not touch is suspect.

- **Buys:** you build while you fix. It gives the Core strategy a real test. It gives one number that you can feel:
  hand acts for each stage move.
- **Costs:** the mod's own work, plus each core fix that a hand act exposes. Those fixes are machinery spend and
  must be counted as such, not hidden in the mod's figure.
- **Risk:** one mod does not use every path (a flyer, a second game, an art pass). An easy stage would flatter the
  result.
- **In one week it works if:** Pyrelands moved one stage or more, with fewer interventions than its last move, and
  one planned kill of a worker during the move was recovered by the program.

### Rebuild: archive and build again (your rejected option, costed fairly)

Keep the mods (717,000 lines, the product), the game driver, and the ledger as history. Write a new factory core of
perhaps 5,000 to 8,000 lines from the architecture page.

- **Buys:** clean interfaces at once. About 300,000 lines of tools leave the working tree in one day.
- **Costs:** the present pipeline is the best measure: 517 M or more and nine days to reach a first passed mod, with
  mods stopped for most of that time. I expect 300 to 600 M and two to four weeks.
- **Risk:** high. The project has rebuilt its pipeline four times in seven weeks, and each rebuild left what you now
  call cruft. The 42 lessons from the Conductor's 134 interventions live in the old code as its odd cases. A rebuild
  meets each of them again, as failures.
- **The fair points for it:** those four rebuilds were not bounded and kept no oracle, so they do not price a
  careful one. A rebuild that keeps the history, the fixtures and the old code for comparison is possible. But that
  is the Core strategy, or the Trial if an engine is under it. The difference between Core and Rebuild is only the
  oracle: in Core, the old code and its recorded history prove the new code.
- **In one week it works if:** one replaced slice passes the old slice's recorded inputs and the five fault tests. A
  week cannot show more than a slice.

### The comparison

| | stops the generator | removes volume | raises determinism | mods keep moving | cost (M) | days | risk |
|---|---|---|---|---|---|---|---|
| Strangle | no | slowly | a little | yes | 50–100 | 14–28 | low |
| Core | partly | yes, prose | much | yes | 60–120 | 21–35 | medium |
| Adopt (SDK only) | no | a little | some | yes | 5–10 | 3–5 | low |
| Trial | no | no | gives the fault tests | yes | 5–10 | 3 | low |
| Freeze | **yes** | no | no | mostly | 2–5 a week | 14 | low |
| Observe | no | **much** | no | yes | 7–12 | 7 + 3 | low to medium |
| Thin line | no | no | shows it | **yes** | about 0 | 7–14 | low |
| Rebuild | no | much | unknown | **no** | 300–600 | 14–28 | high |

No single strategy fills the first three columns. That is why the recommendation is a set.

---

## 5. The recommendation

**Freeze, Observe and Thin line at once. Strangle toward Core for two weeks. Adopt typed worker output. Run the
three-day Trial of an outside engine in week one. Do not rebuild. Measure on day 14 and decide again.**

The reason for this order: the generator must go off first (Freeze), or every other step is undone at 375 repairs in
eight days. Volume must fall by measurement (Observe), or nobody can find the one home of anything. A mod must keep
moving (Thin line), or this becomes two more weeks of fixing in place of building, which is your complaint.

**What would change my mind.** If the Trial passes its three conditions, the day-14 decision is between Core on our
own tick and Core on the library, and I would then lean to the library for the durable part. If after 14 days the
interventions for each stage move have not fallen, Strangle toward Core is not working and a bounded replacement of
the tick (with the old one as oracle) is the next option, before any thought of a full rebuild.

### The first two weeks

| days | act | who | done when |
|---|---|---|---|
| 0 | You read section 3 and correct it. It becomes the one architecture page | You, 20 minutes | The page is landed with your corrections |
| 0 | The freeze starts. The publish door refuses a new pipeline file that names none of the nine systems | The Conductor, one fixer | A planted new file is refused; a replacement passes |
| 0 | The recorder goes on | One fixer | Its first day's list exists |
| 1–7 | Pyrelands moves on the core path. Each hand act becomes a fix in the state machine | The pipeline, the Conductor | Hand acts for each stage move are counted each day |
| 1–7 | Strangle, in this order: the launcher (one runner), the lists (views of the work record), the status pages (one page) | Opus fixers, one group each | Each group's proof passes and its old paths are deleted |
| 3–5 | Pilot: one worker kind (the blind judge) returns a typed verdict | One builder | A program reads the verdict with no prose parsing; a broken result reads "could not look" |
| 3–5 | The Trial: one stage loop on an outside library, five fault tests on it and on our tick | One builder, in a scratch repository | The three conditions are read: continue or stop |
| 7 | Read the Observe census. Park what nothing loaded and nothing names | The Conductor decides; a fixer parks | The tree is smaller by a measured count |
| 8–12 | The decision list for Core: every decision, and who decides it. Delete the rule lines that a program now decides | One Fable run, then fixers | The four rule files are below 5,000 lines |
| 8–14 | Leases: clone pool and account slot move onto the lock library | One fixer each | One reader for each "who holds X" |
| 14 | The measures table (below) is read against day 0. You decide: continue, change, or lift the freeze | You, with one page | Recorded |

### What stops now

- New studies of a slice. The next study is the day-14 measurement.
- A new rule section for one failure. The failure goes to the architecture owner, who names the system that must
  absorb it.
- A hand run on work that the tick owns, without a defect line against the state machine.
- Tickets filed from a study before you have reacted to the study.
- Compression of rule files by rewriting. Prose falls only when a program takes over its decision.

### What must never be built again without the architecture page

A lock or hold. A store or list. A launcher. A status page or digest. A gate or hook. A timer. A judge or review
loop. A parser of another tool's output. Each of these has one home in section 3. A change extends that home.

### The measures

One script prints them each week from the records. Nobody types them. Day-0 values are measured today.

**The measures that decide.** GPT's objection here is right: a count can fall because somebody hid the thing that it
counts. Lines fall by packing. Tickets fall by parking. Red tests fall by deletion. Voids fall by a new label. So the
deciding measures are costs of a fixed piece of real work, read from run records:

| measure for each accepted stage move of a mod | today | direction |
|---|---|---|
| Elapsed time from "may run" to "moved" | UNMEASURED | down |
| Weighted tokens, mod work and machinery work shown apart | UNMEASURED per move | down |
| Interventions: every launch, stop, release or state edit that the tick did not make, counted from run records and the control store, not from the hand-acts list | 98 hand acts on record in 9 days | down |
| Your minutes | UNMEASURED | down |
| Stage moves that were later undone | UNMEASURED | down |
| Planned kills that the program recovered with no hand (the five fault tests, weekly) | not run yet | 5 of 5 |

**The counts that warn.** They show the direction of volume. None of them decides alone, and each names how it can
mislead.

| measure | today | direction |
|---|---|---|
| Hand acts on the hand-acts list (misleads if recording stops) | 98 in 9 days | down |
| Voided runs each week (misleads if a void gets another label) | 33 standing voids in 9 days | down |
| Machinery share of detached-run tokens (misleads if mod spend grows and machinery spend does not fall) | about 40 to 45% | below 25% |
| Red tests on origin (misleads if a red test is deleted, not repaired) | today's census is in work | to zero, then an alarm |
| Open items, and items idle for 14 days (misleads after a bulk park) | 1,962 and 990 | down |
| Lines in the four rule files; sections in the root rule file (misleads if text is packed, not removed) | about 6,700; 48 | down |
| Net pipeline lines each week, added minus deleted (misleads the same way) | UNMEASURED until the commit split is automated | negative |
| Homes for each tracked fact (misleads if a fact is left off the list) | 1 for six facts since today | 1 for every fact in section 2 |
| Mod versions passed (misleads if a bar is made easier; the tag rule is nine days old) | 1 | up |

---

## 6. Where I disagree with you

1. **The work was done more than you think; the return was as poor as you think.** Every request produced a document,
   and the fixes of several were built without you. A built fix is not a returned study, so your complaint stands.
   But the remedy is delivery, not more studies.
2. **Your request rate may be part of the cause** `[guess ~60%]`. Thirteen study requests in four days produced
   thirteen documents and helper runs. I did not measure your reading time. If you agree that you cannot read one
   study each day, a limit of two open studies follows.
3. **"Deterministic" must not mean "more gates on form".** The project tried that. The result was 34 hooks and then
   five rulings to stop gates from refusing work. An independent check of a real invariant (one driver for each game,
   a result tied to its build) is good, and can even guard a faulty decider. A gate that judges the form of work is a
   second decider placed after the first.
4. **"If you see it, do it" needs a map first.** For machinery, a fix in the same run by the run that hit the fault
   is how five readers of one fact arise. During the freeze I would change it to: if you see it, fix it in its one
   home; if it has no home, give it to the architecture owner.
5. **"A new way every week" has a cost that you are now paying** `[guess ~65% that it is a main cause]`. Four pipeline
   designs in seven weeks is good research and bad plant engineering. The table in section 1 shows the direct cost:
   four studies advised a system that was then retired. That the experiments also caused the duplicates is my
   inference. Keep experimenting, but in a copy or a sibling repository, and bring a result into this pipeline only
   as a Strangle step.
6. **Routing everything generic through sibling repositories is not free.** Each one adds a boundary across
   repositories that a helper in a clone must reach. Do it for the second-model door, where the pain is proven. Do it
   for others only when the Observe census shows that the local copy is used and is a copy.
7. **Passing mods is the measure that matters.** One mod version has a pass tag. That count is unfair to the months
   before 2026-11-13, when the tag rule began, so I do not use it as a verdict on the project. I use it as the
   direction: any plan that stops mods for weeks to perfect the factory repeats the pattern.

---

## 7. Your decisions

| decision | options | gain | cost |
|---|---|---|---|
| **The freeze** | (a) 14 days, with the three exceptions. (b) No freeze; the architecture owner reviews after the fact | (a) The generator stops. (b) No fix ever waits | (a) Some pipeline fixes wait a day; your own new ideas for machinery wait too. (b) The growth continues while we clean |
| **Who owns the architecture** | (a) A standing Fable seat, one sitting each week plus short answers. (b) The Conductor. (c) You | (a) One seat with the whole in view and no other duty. (b) No new seat. (c) Your taste, directly | (a) About 2 to 5 M each week. (b) The busiest seat gets another duty; this is how studies were lost. (c) Your time, each day |
| **Experiments** | (a) For 30 days, pipeline experiments happen outside this pipeline. (b) As now | (a) The ground stops moving under the cleanup. (b) Full freedom | (a) A slower path from idea to trial. (b) Each new design orphans the last cleanup, as in section 1 |
| **The 990 idle items** | (a) Park them all in one act: out of every queue, reopened by name at need. (b) Continue the sweeps for each mod. (c) Leave them | (a) Every list becomes readable today. (b) Each item gets a judgement | (a) A good idea may sleep until somebody searches for it. (b) Five sweeps so far; about 1 M each, and weeks. (c) Lists stay unreadable |
| **The study rule** (section 8) | (a) The run delivers, with a limit of two studies in work. (b) The run delivers, with no limit | (a) No study is lost, and each one can be read. (b) You may ask freely | (a) A third request waits or replaces one. (b) The queue to you grows again |
| **Typed worker output** | (a) Pilot the Agent SDK on the blind judge. (b) Validate a JSON result with our own schema check, no SDK. (c) Not now | (a) Less code that is ours; hooks in code later. (b) No new dependency. (c) No change | (a) A one-hour check of the sign-in first; a dependency. (b) We keep the wrappers. (c) Prose parsing stays |
| **The engine trial** | (a) Run the three-day Trial in week one. (b) No trial; stay on our tick. (c) No trial; move to an engine now | (a) A measured answer, and five fault tests that we keep. (b) No distraction. (c) GPT's stronger position: stop repairing a home-built orchestrator | (a) 5 to 10 M and one builder for three days. (b) The question returns at the next void. (c) A migration during the cleanup, on opinion alone |
| **"Fix it in the same run"** | (a) During the freeze, machinery fixes go to the one home or to the architecture owner. (b) Leave the rule | (a) No new duplicate. (b) Fastest local repair | (a) A helper sometimes stops with a defect line and no fix. (b) The duplicates continue |

My picks: (a) for each row, and for typed output (a) if the sign-in check passes, else (b).

---

## 8. A standing mechanism so that a study cannot be lost

My first design made the study an owed item that only your reaction could close. GPT's objection was correct: that
guards the close, not the delivery, and it still leaves the Conductor in the path. The owed list (`rimflow/owed.py`)
already does that much, and the door study was lost through it. The better design takes the seat out of the path:

1. **The run delivers its own study.** A study run ends through one tool call, `deliver`. The tool refuses a document
   that does not open with a summary of one page (the answer, the first three acts, your decisions). It opens that
   document on your screen with `src/RimMandrake/Utils/show.sh`. It writes one ledger event, `delivered`, with the
   time and the full Windows path. A study run that ends without that event is reported as failed, by the same
   program that reports every run's end today. No seat must remember anything.
2. **Three separate records.** `delivered` (the tool, at the run's end). `reacted` (your words, a card answer, or
   your "seen": optional, and never needed to finish the run). `measured again` (item 5). Today all three are one
   "close", and that is why nobody could see which one was missing.
3. **It stays in front of you until you react or dismiss it.** Delivered studies with no reaction are the first
   lines of your daily digest, oldest first, each with its path and its age. "Seen" or "drop it" removes the line.
4. **No ticket before your reaction.** The study names at most three acts. Their tickets are filed after you react.
   A study that you dismiss files nothing.
5. **A second date.** Each study names one number and a date to measure it again. On that date a program measures it
   and puts both readings in your digest.
6. **A limit of two undelivered studies** (your decision in section 7). A third request shows the two that are in
   work and asks which one it replaces.

What it does not solve: a window that opens on your screen while you are away is a weak delivery. The digest line
covers that. A phone line would cover it better. The phone alarm route is retired and its replacement is your open
choice, so I did not design on it.

Acceptance test (not built in this run, because of the freeze that I recommend; it is the first exception that I
would ask for). On a fixture ledger and a fake `show.sh`: (a) `deliver` on a document with no summary is refused and
names the repair; (b) `deliver` on a good document opens it and writes `delivered`; (c) a study run that ends with no
`delivered` event is reported failed; (d) a delivered study with no reaction is the first digest line; (e) "seen"
removes it; (f) on the second date both readings appear. Six rows, each red on today's tree.

For this document: this run could not use that tool, because the tool does not exist. So this document depends on the
old path once more. The item that owes it to you exists
(`RIMMANDRAKE_BRING_HIM_THE_CLEAN_HOUSE_ADVICE_AND_BOTH_CODEX_STUDIES`: the Conductor puts this advice and the two
sibling studies in front of you). I did not open it on your screen myself, because you are in a walkthrough with the
Conductor now. Its second date: 2026-12-06, with the measures of section 5.

---

## 9. What I could not look at

- The Conductor's transcripts, beyond a search for five file names. I did not read what the Conductor said about
  each study, and I did not search for the other eight "no record" rows.
- Whether you read any document. No instrument records that.
- SteveDesktop: its units, clones and tools.
- The behaviour of the sibling repositories' tools against RimMandrake's own. I compared names, not behaviour.
- Which pipeline files run in a normal week. This is the Observe census.
- Spend inside the Conductor windows and their subagents.
- The outside tools beyond a web search on 2026-11-22. I ran none of them. Whether DBOS uses SQLite by default or
  only supports it: the sources disagree.
- Elapsed time, tokens and your minutes for each stage move. These are the deciding measures of section 5, and their
  day-0 values do not exist yet.

## 10. The skeptical review by GPT, and what I did with it

One consult, `gpt-6.1-sol` at high effort, on the first draft, with the order to attack it. Its full answer is kept
beside this file as `gpt_review.md`.

| GPT's objection | my judgement | what changed |
|---|---|---|
| The table has 22 rows, not 21, and the delivery counts are wrong | Correct | Counts repaired in section 1 and in the summary |
| A missing ledger record cannot show a missing delivery; the studies may have been delivered in the chat | Correct, and it could be checked | I searched the transcripts for five documents. Two were never named to you; three were named once or twice. Section 1 now says so |
| The causes are stated as proven | Correct | Section 1 says that the causes fit the evidence and names one other reading. The rate cause is marked as a guess |
| Nine systems are a shopping list: no writers, no failure contracts; a hold is policy, not a lease; "one work record" is three stores; build identity, workspace and landing are missing | Mostly correct | Section 3 has a contract list for the architecture page, moves holds out of the lease library, names the one commit point, and adds the missing parts. I kept the nine names: a list of jobs and homes is what an agent needs to answer "does this exist already?" |
| "Four ours, five generic" confuses mechanism with policy | Correct | Replaced by "the mechanism is generic, the policy is ours" |
| Costs are not calibrated; 1 M for each group is too low | Correct | I measured today's seven runs: 1.2 to 2.1 M each. Strangle is now 50 to 100 M |
| Observe: seven days cannot prove that a thing is dead; a start line is not module coverage | Correct | The recorder notes loaded modules. Parking needs three conditions. Rule text is not removed by the census |
| Freeze: the void exception is a hole; a file-name gate misses additions inside old files; the owner seat can become a queue | Correct | All three are now named as risks, with the weekly diff as the answer to the second |
| Thin line: "about zero" hides the fixes; an easy stage flatters | Correct | The fixes count as machinery; one planned kill is part of the signal |
| Rebuild is costed unfairly; a bounded replacement with an oracle is possible | Half correct | The fair points are added. A bounded replacement with an oracle is the Core strategy, so my verdict on a full rebuild stands |
| The dismissal of a workflow engine is weak: durable execution matters on one machine; the document missed LangGraph; DBOS can use SQLite | Correct about the weakness | The engine row now gives both cases. A three-day Trial with stop conditions replaces my opinion |
| Recommend to stop improving the home-built orchestrator and test a replacement | Not taken as the main plan | An engine does not stop the generator, and it removes no rule and no gate. Those are most of the volume. The Trial tests GPT's case at low cost. If it passes, I change my lean (section 5) |
| Most measures can be gamed | Correct | Section 5 now decides on the cost of a fixed stage move and on recovery from planned kills. The counts only warn |
| Several disagreements are straw men | Partly correct | Points 1, 2, 3, 5 and 7 of section 6 are reworded or marked as guesses |
| Section 8 guards the close, not the delivery; make the run deliver | Correct, and better than my design | Section 8 is rewritten around a `deliver` tool call and three separate records. I kept the digest line, which GPT called "more banners": a window that opens while you are away is not a delivery |

## Sources for the outside tools

- Pydantic AI, durable execution overview: https://pydantic.dev/docs/ai/durable-execution/overview/
- ZenML, Temporal alternatives for agent workflows: https://www.zenml.io/blog/temporal-alternatives.md
- Claude Agent SDK, structured outputs: https://code.claude.com/docs/en/agent-sdk/structured-outputs
- Claude Agent SDK, hooks: https://code.claude.com/docs/en/agent-sdk/hooks
- DBOS, Python programming guide: https://docs.dbos.dev/python/programming-guide
- Pydantic AI, DBOS integration (shows a SQLite system database): https://pydantic.dev/docs/ai/integrations/durable_execution/dbos/index.md
- Temporal, durable execution: https://docs.temporal.io/durable-execution
- LangGraph and Deep Agents (named by GPT; I did not check them): https://www.langchain.com/oss-overview
- Beads issue tracker: https://github.com/steveyegge/beads
- Thoughtworks Technology Radar, Beads: https://www.thoughtworks.com/radar/tools/beads
