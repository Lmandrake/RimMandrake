# Findings curation: keeping what the test runs learn (design pass, 2026-10-29)

Status: DESIGN ONLY. Nothing here is built or switched on, and no role file is changed. It answers the owner's refusal
of the "born as items, no lobby" proposal (ledger item `FINDINGS_REDESIGN_BORN_AS_ITEMS_NO_LOBBY`, an Innovator
proposal of 2026-10-29). The roles named here are the ones in RimFlow v3 (`design/RimMandrake/rimflow_v3_2026-10-26.md`):
the **Conductor** talks to him, the **Producer** decides what is built and when, **Operations** keeps the machine
running, the **Arbiter** rules a feature done, the **Auditor** re-checks closed work and turns repeat errors into rules,
the **Innovator** proposes big changes, the **Dispatcher** (a program) wakes and feeds the agents, and **FOUNDRY** is
the one autonomous builder.

## 1. What he asked, verbatim

> "Those findings are growing context and memory. We absolutely don't want to lose that. It should be a periodic
> Foundry job to do this. That's why Foundry isn't merely a queue: this is part of the thinking. What do we keep, what
> is actually work, what can be retired to longer term memory, etc. Please do an Opus 5.5 design pass on the right way
> to do this provided out v3 design, or argue that other agents should own that job. Provide three trade-off options
> to consider." (owner, 2026-10-29, ledger note on `FINDINGS_REDESIGN_BORN_AS_ITEMS_NO_LOBBY`)

So the questions are: what each finding becomes, how often that is decided, who decides, what it costs, and how we
prove nothing was lost.

## 2. What a finding is today (measured 2026-10-29 from the ledger shards)

**Where they come from.** 146 finding events are in the ledger. 127 of them are type `UNTRIAGED`, and all 127 were
written by one program: the test-queue ingest (`src/RimMandrake/Utils/testq/ingest.py`), which turns every FAIL row of
a finished test job on SteveDesktop (the second machine that runs game tests) into one finding. Its own comment says
"a human or seat decides MOD/SITE/HARNESS" (is the mod wrong, the test map wrong, or the test machinery wrong). No
role does. The other 19 are older hand-filed ones (16 `modcheck-failure`, 2 `conflict`, 1 `HARNESS`).

**What one looks like.** A name such as `FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_D77D50` (mod, test row, then six hex
characters of the job id), the run it came from, a severity the ingest always sets to `medium` (so severity carries no
information), and one line of at most 160 characters, e.g. *"dig_finds/cut_turns_up_local_find FAIL on SteveDesktop:
ExpectationFailed: the dig job never finished"*. The full evidence (the result sheet) stays on SteveDesktop.

**Volume.** 35 on 10-26, 28 on 10-27, 53 on 10-28, 11 by 14:00 on 10-29. None has ever been turned into an item
(0 of 127 named as an item or spawned from), which matches the Operations watch number `flow.untriaged_findings`.

**A sample of 20 (random, seed 7)** sorts into:

| Kind | In the sample | What it really is |
|---|---|---|
| The same quarry failure: "the dig job never finished" | 5 | one problem, reported again on every run |
| Thirst rows (tank fill order, routine salt, dehydration) | 5 | 3 distinct rows, each repeated |
| Other FlowWorks rows (sticky water, every-cell oracle, grate, pit drowning, fill-in) | 5 | possibly real mod bugs, each seen once or twice |
| Test machinery: "diptych could not be composed (No module named 'PIL')", "case missing from the SelfTest output" | 3 | harness faults, not mod faults; two share one root cause |
| Lane health: "the vanilla canary was red" | 2 | the test machine itself was unhealthy; Operations' business |

**The repetition is the main fact.** Strip the job-id suffix and the 127 findings are **50 distinct failures**. The top
one, the quarry dig job, is 23 findings (27 with its twin row `finds_off_none`). New distinct failures per day were
26, 7, 16 and 1: the stream of *new* things to think about is far smaller than the stream of findings.

**The pool holds real signal nobody saw.** The quarry item (`FLOWWORKS_QUARRY_DIGGING_1`, "canals uncover local
materials") stands at `validated` while the test machine has recorded 26 failed and 41 partial runs against it and
only 3 passes. Thirst items marked `done` (`THIRST_ROWS_HARDEN_FALSE_PASS_ROUTES`, `TESTQ_SWEEP_WIRE_FLOWWORKS_DRIVERS`)
have failing rows filed after them. This is exactly the memory he does not want to lose. It is not lost from disk (the
ledger is append-only) but lost from attention, which is worse because it looks safe.

**The same problem one level up.** The lessons inbox (`infrastructure/state/lessons/`, one file per lesson, meant to
be folded into skills and then deleted) holds **1,087 unfolded lessons**; its README says it was last drained
2026-09-23, and 22-210 arrive per day. The Auditor's weekly pass owns that fold in v3. So "retire to long-term memory"
cannot mean "move it to the lessons inbox": that is a second waiting room, nine times bigger. The memory homes that
are actually read are the **skills** (`skills/`, about 41, loaded by agents when a topic comes up), the **facts**
(`infrastructure/state/facts/`, 42 files, "unbudgeted, never dropped"), the **ledger history of an item**, and the
**rules and checks** (a pre-screen flag, a selftest, an `ops_watch` rule, a hook). The auto-memory folder
(`/home/mandrake/.claude/projects/-home-mandrake-rm-bench/memory/`, 152 files) is read only by windows opened in the
BENCH clone, so FOUNDRY never sees it; it is not a shared home.

## 3. What a finding can become

Every finding ends in exactly one of five outcomes, each written down as a ledger event that names the finding.
Nothing is ever deleted: the finding event stays in the ledger forever; "retired" means decided, not erased.

| Outcome | When | Where it lands |
|---|---|---|
| **New work** | a real problem no open item covers | a new item spawned from the finding (`rimflow spawn --from <finding>`, an existing verb); the Producer orders it |
| **Merged into an item** | an open item already owns this problem, or this is a repeat of a failure already decided | a note on that item with the count, first and last seen; if the item is already `done` or `validated`, a regression item caused by it instead, because a passed item that still fails is the most valuable thing in the pool |
| **Long-term memory** | the finding teaches something general (e.g. "SteveDesktop's Python has no PIL, so every picture row fails as HARNESS") | a line in the skill that owns the topic, a fact file, or a rule spec for the Auditor; never the lessons inbox; the event records the file and the line |
| **Routed** | it is about the test machine, not the game (red canary, refused pull) | Operations' existing lane item (`STEVE_LANE_MONITOR_PAUSE_FINDINGS`, the standing item those failures are already filed under) |
| **Retired with a record** | the row has since passed on later runs, the cause was fixed by a known commit, or its item was dropped | the event carries the reason and the proof (the passing runs or the sha) |

Building block shared by all three options: one new ledger verb (for example `rimflow triage <finding> --as
work|merge|memory|route|retire --into <item or path> --why`), and the Operations watch counts "findings with no
outcome yet" instead of "findings that are not items". Today there is no way to record merge, memory or retire at all,
which is part of why the pool only grows.

## 4. Who should own it under v3

He suggested FOUNDRY. The v3 design supports that for the core of the job, with one honest amendment.

- **For FOUNDRY.** Deciding what a failure *is* (mod bug, bad test map, broken test machinery, already fixed) is
  engineering diagnosis. Since the v3 cutover (2026-10-28) FOUNDRY owns `src/`, all FlowWorks, the test harness,
  deploys and acceptance at every level, so it is the only role that can read a result sheet and a commit history and
  say which. Any other owner would end up filing "please diagnose" tickets to FOUNDRY, which is the hand-off the
  Innovator was trying to remove. His point that "Foundry isn't merely a queue" also fits v3: FOUNDRY's turn is fed by
  the Dispatcher, and a periodic curation ticket is just another ticket it is fed.
- **The amendment: FOUNDRY must not be the only check on itself.** Most failing rows are against work FOUNDRY (or
  BENCH before the cutover) built. Retiring a finding as "flaky" or "already fixed" is the maker grading its own work,
  which v3 measured as unreliable (0 defects in 2,744 FlowWorks self-reviews; 13 in one week once reviews were
  independent). So the **Auditor samples the retirements and merges**, as it already samples closes. That is the v3
  separation of duties, not a new rule.
- **What stays with others.** The Producer still decides the order of the work the curation creates (FOUNDRY files
  it, it does not rank it). Operations gets the lane-health findings. The Auditor still owns turning a *repeat* into an
  enforced rule; curation hands it the repeat with its count.

## 5. Option A: a daily FOUNDRY curation ticket over the whole pool

**Why.** It is his suggestion taken literally and the quickest way to get the pool read: a ticket the Dispatcher
files once a day, worked by FOUNDRY in a fresh window with full judgment on every finding.

**How it runs.** Each morning, after the overnight test runs land, the Dispatcher files one curation ticket. FOUNDRY
reads every finding with no outcome yet, groups them itself, decides each one's outcome (§3), writes the events and
the memory lines, and commits once. The first run clears the existing 127.

| | Gains | Costs |
|---|---|---|
| Build | about half a day: the triage verb, the schedule entry, the watch count | none beyond that |
| Tokens | none spent on building machinery | FOUNDRY reads every repeat. ESTIMATE 150-300k tokens a day at 30-50 findings a day (3-6k each with evidence), growing with the number of test rows; the backlog run is another ~400k |
| Risk | full judgment on everything; nothing is folded by a program that might fold wrongly | the repeats crowd out thinking (23 copies of the quarry failure is 23 reads); curation competes with building for FOUNDRY's day; when the queue is busy the ticket slips and the pool grows again; only the Auditor's sample stops a self-serving retirement |

## 6. Option B: a program folds the repeats, FOUNDRY judges only what is new (recommended)

**Why.** The data says most of the pool is repetition (127 findings, 50 distinct failures, one of them 27 times), and
repetition needs counting, not thinking. Let a program do everything that is mechanical and reversible, and spend
FOUNDRY's judgment only on new failures, contradictions and memory.

**How it runs.**
1. **No-AI sorting, after every ingest** (run from the Dispatcher's measure list, like `ops_watch`). Each finding gets
   a signature: mod, test row, and the failure text with run-specific numbers and file names removed. A "standing
   failures" table keeps, per signature: first seen, last seen, count, the items it was filed under, the raw texts,
   and when that row last passed (read from the test queue's done records, which list every row, not just failures).
   The program does only four things on its own, each recorded as an outcome event a person can undo:
   - a repeat of a signature already decided is **merged** into that decision (count goes up, no new thinking);
   - a red canary or refused pull is **routed** to Operations' lane item;
   - a row that has **passed 3 later runs in a row** is **retired** with those runs as the proof, and comes back
     automatically if it ever fails again;
   - a failing row under an item marked `done` or `validated` is flagged as a **contradiction** and goes to the top
     of the next curation.
2. **A daily FOUNDRY curation ticket over the residue**: new signatures, contradictions, and signatures still failing
   after 3 days. FOUNDRY diagnoses each one (mod / test map / test machinery), decides work, merge or memory, and
   commits once. On the last four days that is 1-26 signatures a day instead of 11-53 findings.
3. **A weekly memory sweep** (same ticket, Friday): FOUNDRY reads the standing table for patterns that are general
   (the PIL fault, "dig job never finished" across runs) and writes them into the owning skill or a fact file, or
   hands a repeat to the Auditor as a rule candidate.
4. **The Auditor's weekly pass** samples the week's retirements and program merges, judged by a helper that did not
   make them; a wrong one is a defect against the curation, and a wrong merge rule gets a ticket.

| | Gains | Costs |
|---|---|---|
| Build | the signature table also makes "how often does this row fail?" answerable for everyone, and gives the Producer and the Conductor a real list of standing failures | 1-2 days: signature function, table, four rules, selftests, the triage verb, watch counts; and the sorting program must itself be reviewed by a non-maker before it is trusted |
| Tokens | ESTIMATE 40-120k a day (only new or stuck signatures, ~5-10k each with evidence) plus ~100k for the weekly sweep; it scales with new problems, not with test volume | the no-AI step costs nothing in tokens but adds a scheduled program to keep alive |
| Risk | judgment goes where it matters; a quarry-style contradiction surfaces the next morning instead of never; a retirement needs proof, and comes back by itself if wrong | a too-loose signature could merge two different bugs into one (the worst way to lose something): mitigated by merging only identical cleaned text, keeping every raw text, and the Auditor's sample; a too-strict signature only makes noise. A flaky bug that passes 3 times hides until it fails again, then it returns |

## 7. Option C: one weekly memory pass, owned by the Auditor

**Why.** This is the honest case for another role. His real worry is memory, and v3 already gives the Auditor the
two memory duties it has: folding lessons into skills each week, and turning repeat errors into enforced rules. The
lessons inbox (1,087 unread) is the same unread pile as the findings pool, nine times larger. One keeper of all
memory, who never built the work it is judging, would fix both at once.

**How it runs.** The Auditor's Monday pass takes findings and lessons together: what is work (filed for the Producer),
what is a repeat (its own rule), what goes into a skill or fact, what is retired. Where it cannot tell a mod bug from a
harness fault it files a "diagnose" ticket for FOUNDRY.

| | Gains | Costs |
|---|---|---|
| Build | small: a widened weekly duty, no new program | it changes the Auditor's role file and its weekly budget |
| Tokens | one pass a week, so no daily cost | ESTIMATE 0.5-1M tokens a week (the 1,087-lesson backlog, roughly 400-700 new lessons a week, plus the findings) in a role whose weekly pass already carries unfinished duties forward |
| Risk | independence: no maker curates its own failures; lessons get a keeper at last | a real bug waits up to a week (the quarry contradiction would still sit for days); the Auditor lacks the engineering context to diagnose, so many findings bounce back to FOUNDRY as tickets, which is the hand-off the Innovator wanted gone; the biggest pass in the system is also the one most likely to be "carried" every week, and then the pool grows again |

## 8. Recommendation

**Option B.** Most of the pool is repetition that a program can fold for free and with proof, so FOUNDRY's thinking
is spent only on what is new or contradicts a "done", and nothing is ever deleted.

Two notes that go with it, whichever option he picks:
- The lessons inbox has the same disease at nine times the size. Option B does not fix it; it only refuses to feed it
  (curation writes straight into skills and facts). It deserves its own decision.
- Until the sorting program has been reviewed by a non-maker, its merges and retirements should be advisory (written,
  but also listed for FOUNDRY's daily ticket), the same way the Arbiter started advisory.

## 9. How we know nothing is lost

"Lost" here means unread and unacted on, since the ledger never forgets. Five checks, all no-AI except the last:

1. **Conservation.** Every finding has exactly one outcome event, or is pending. Each day the watch records filed,
   decided by kind (work / merge / memory / route / retire) and pending, and the age of the oldest pending finding.
   The target: oldest pending under 2 days, and filed = decided + pending, exactly. A mismatch is an alarm.
2. **A canary finding.** Once a week a planted, labelled test finding with a known right answer is filed. If it has
   no correct outcome by the next curation, the curator is not reading, whatever the counts say. (A count that reads
   zero is a broken instrument until a probe like this proves it can see.)
3. **Memory lands where it is read.** An outcome of kind memory must name a file and line that exist and contain the
   finding's signature, in a skill or fact file, not the lessons inbox. A program checks this daily.
4. **Retirements that come back.** A retired signature that fails again reopens itself and is counted. The share of
   retirements that come back within 14 days is the curation's error rate for retiring; a rising rate is an alarm.
5. **The Auditor's sample.** Each week a non-maker helper re-judges a random sample of retirements and merges, blind
   to the curator's reasons. Wrong ones are defects against the curation, and any later bug report or owner complaint
   that matches a retired signature counts as an escape.

## 10. Sources

- The refused proposal and his words: `python3 src/RimMandrake/rimflow/cli.py show FINDINGS_REDESIGN_BORN_AS_ITEMS_NO_LOBBY`;
  innovations list `design/RimMandrake/innovations.md`.
- Roles: `design/RimMandrake/rimflow_v3_2026-10-26.md` §2-3; `infrastructure/agents/FOUNDRY.md`;
  `src/RimMandrake/rimflow/roles/auditor.md` (weekly pass, lessons to skills, repeats to rules);
  `src/RimMandrake/rimflow/roles/producer.md` (backlog hygiene); all six roles enabled in
  `src/RimMandrake/rimflow/dispatcher_schedule.json` on 2026-10-29.
- Where findings come from: `src/RimMandrake/Utils/testq/ingest.py` (docstring and the `finding` call); the count:
  `src/RimMandrake/Utils/ops_watch.py` `c_flow`.
- Counts in §2: computed 2026-10-29 from `infrastructure/state/ledger/events/*.jsonl` (146 finding events, 127
  `UNTRIAGED`, 50 signatures after stripping the job suffix, 0 spawned); the quarry item's history from
  `rimflow show FLOWWORKS_QUARRY_DIGGING_1` (70 verify events: 26 fail, 41 partial, 3 pass); lessons from
  `infrastructure/state/lessons/` (1,087 files plus README; 22 so far on 10-29, 210 on 10-26).
- Token figures are ESTIMATES from finding counts times a per-read guess, not measured burn; Operations' economy pass
  can replace them after a week of whichever option runs.
