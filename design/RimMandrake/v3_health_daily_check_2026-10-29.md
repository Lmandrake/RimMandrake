# v3 health: the daily check (spec, 2026-10-29)

Item: `V3_HEALTH_BUILD_DAILY_PULSE_DAY_ONE`. Written by a BENCH design helper (Opus); FOUNDRY builds.
Owner, 2026-10-29: "1, 2, 3 - should be a daily check performed by a responsible party all the time (could be Ops,
could be Arbiter). Everything but 4. Switching off agents is a good idea later when we show that at least a nominative
system is functional for awhile." By card the same day: **Operations owns all of it**; the Auditor's weekly re-check
guards Operations grading its own usefulness.
Owner, later the same day: "I also suspect Operation may need to sample more often than once a day. I think perhaps
there are dumb monitors that are running all the time that feed into real-time dispatch as well as Operation
assessment?" Yes: that is the shape below.

Day-one evidence (hand-made, what this automates): `D:\ClaudeWork\rimmandrake\conductor\v3_health_2026-10-29.md`.

## 0. What this is, in one screen

Every day we want to know whether RimFlow v3 is alive, useful, better than v2, and what it costs. Today one agent
answered that by hand in about an hour, and four of the answers were UNMEASURED. This spec turns that into:

- **Programs that measure all the time.** `ops_watch.py` already runs every 15 minutes with no AI, and the Dispatcher
  reads its output on every tick. We add four small pieces to that same pass: tag counts of his messages, a trace of
  each role's output, the timing of planted faults ("drills"), and one rebuilt page.
- **One cheap AI step, checked by a program.** Telling "keep going" from "this is broken" in his messages needs reading.
  A Haiku tagger does it hourly; a program checks every tag it writes and its agreement with the 10-26 censuses.
- **Operations judges, it does not gather.** It reads the page in its existing 07:30 and 19:30 runs and when a health
  alarm wakes it. No new role run, no helper, no new schedule slot.
- **Nothing new reaches the owner** except the page, which Operations has read before he does, and the existing
  weekly v3-vs-v2 note.
- Part 4 (switching roles off to see what breaks) is deferred by his ruling.

## 1. Who does what, and how often

| part | what measures it | cadence | what judges it | AI cost |
|---|---|---|---|---|
| 1 message tags | `owner_tags.py extract` (no AI) finds new messages; `owner_tags.py tag` (Haiku) tags them | extract every 15 min (inside the ops_watch pass); tag hourly (own timer) | program checks every batch; Operations reads the daily numbers | Haiku only |
| 2 drills | `health_drill.py plant` (no AI) from a fixed catalogue; ops_watch collector `health.drill.*` looks for the catch | plant: daily timer 06:10 local, at most the rate in §3.4; catch check every 15 min | Operations, weekly in the Monday 07:30 run | none |
| 3 output trace | ops_watch collector `health.trace.*` (no AI) | every 15 min | Operations at 07:30 and on `ROLE_*` alarms | none |
| 5 page | `v3_health_page.py` (no AI), last step of the ops_watch pass | every 15 min; one dated copy kept per day | Operations reads it at 07:30 and stamps it read | none |
| alarms | ops_watch `targets` with `"for": "Operations"` | every 15 min, edge-triggered | Operations alarm run (existing trigger) | existing alarm run |

Everything a program writes goes under `D:\ClaudeWork\rimmandrake\v3_health\` (scratch: programs read it), except the
page, which a human reads (it stays there too, at a stable path, because Operations and the owner both read it every
day; it is not Transient).

The Dispatcher already reads `ops_watch/status.json` every tick. The new `health.*` keys land in the same file, so the
Dispatcher can use them later (for example, not launching a role whose last three runs were RUNNING-UNUSED) with no new
plumbing. Using them for dispatch decisions is NOT in this spec; that would be a loosening or tightening for the owner.

## 2. Part 1: tagging his messages (feeds the kill test)

### 2.1 What the kill test needs, and the trap in it

The v3 kill test (`design/RimMandrake/rimflow_v3_2026-10-26.md` §6) uses two numbers from two different censuses:

| KPI | baseline | target | where the baseline came from |
|---|---|---|---|
| keep-going messages/day | 31 | ≤26 | friction census (`D:\ClaudeWork\rimmandrake\orch_record\friction_census.md`): typed messages only, from seat transcripts, 10-05..10-26; categories b (unstick) + g (session driving) + h (status pull) = 40% of ~78/day, from a **hand-labelled sample of 140** |
| failure-signal share | 27.5% | ≤25% | frustration census (`D:\ClaudeWork\rimmandrake\csuite\frustration_census.md`): every "## Lukas" block in `conversations/*.md`, 10-02..10-27, 2,114 messages **including 685 card answers**; any of B, R, S, O, L, C; **every message read** by one Opus reader |

Two facts follow, and the design is built around them:

1. **The 31/day is too noisy to test against 26.** 40% from n=140 has a 95% interval of about ±8 points, so the
   baseline is somewhere between ~25 and ~37 a day. A drop to 26 is inside that. The per-message hand labels of the
   140 were not saved (`sample2.json` holds 70 texts with no labels), so they cannot be re-scored either.
2. **The two KPIs use different denominators and sources.** One counts typed messages only, per day; the other is a
   share of all blocks including card answers. The tagger must reproduce each census's own ruler, not one blend.

So: **the kill test compares the tagger against the tagger.** Once calibrated (§2.4), the tagger re-tags both
baseline windows. Those re-tagged numbers become the instrument's baseline, printed beside the original 31 and 27.5.
The targets keep their meaning as relative drops (31 → 26 is −16%; 27.5% → 25% is −2.5 points). Open question 1.

### 2.2 Tags

Each message gets one or more of three tags, or none:

- **keep-going**: he is driving the machine rather than the work: unsticking or "keep going", session and orchestration
  driving (wake, handoff, N subagents, AFK), status pulls ("any cards for me?", "is the sheet open?"). Friction
  categories b + g + h.
- **failure-signal**: something failed that he had to notice: broken or stale thing (B), repeat or already ruled (R),
  should have known (S), obvious fix he had to suggest (O), slow (L), ceremony (C). Frustration union.
- **direction**: the work he wants to do: a new goal, design, question, review pick, approval. Friction a + e.

The tagger also writes the frustration sub-letter (B/R/S/O/L/C) and the friction letter (a..i), because those are what
the gold sets carry. A message can be keep-going and failure-signal at once ("why is this still stale? continue").

### 2.3 Where the messages come from

`owner_tags.py extract` reuses the two extractors the censuses used, so the rulers match:
`src/RimMandrake/Utils/sim/friction_census.py extract --since <last>` (seat transcripts, `origin.kind=human`,
timestamps, card answers kept apart) for keep-going/day, and the `## Lukas` rule of
`src/RimMandrake/Utils/sim/owner_msgs_extract.py` on `conversations/*.md` for the share. A message is keyed by
sha1(seat, session, timestamp, first 80 chars) so a re-run never double-counts. The day is his local day (PDT/PST),
from the message timestamp, not the conversation file's name (a session that crosses midnight would otherwise be
mis-dated). Output: `v3_health\tags\messages.jsonl` (append-only).

### 2.4 The tagger and its mechanical check

Model: **Haiku**, by `infrastructure/agents/Agent_Policy.md` ("haiku ... classification"), and allowed there only
because a program catches it. Read the alias from `ANTHROPIC_DEFAULT_HAIKU_MODEL`; name no account in code.

One call tags up to 40 messages. The prompt is fixed text in the repo (`owner_tags_prompt.md`, sha256 pinned in the
program like `v3_vs_v2_rules.json`; a changed byte refuses to tag until re-calibrated). It holds the tag definitions
from 2.2 and 24 fixed examples drawn from the frustration census.

Every batch is checked by the program before a single tag counts:

1. **Shape.** Exactly one row per message id sent; no id invented; tags only from the enum; letters consistent with the
   tags (a B letter needs failure-signal). Any miss: the whole batch is rejected and retried once, then left UNTAGGED.
2. **Evidence.** Each tag carries a quoted cue; the program checks the cue is a verbatim substring of the message. A
   tag whose cue is not in the text is dropped and counted (`cue_miss`).
3. **Stability.** A random 15% of each day's messages are tagged a second time in a different batch order. Disagreement
   above 15% marks the day ESTIMATE-LOW (shown, never used by the kill test).
4. **Coverage.** A day's figures are reported only when ≥95% of its messages are tagged; otherwise UNMEASURED with the
   count missing.

**Calibration: how agreement with the 10-26 censuses is proven.** This is a gate the build must pass, and it re-runs
weekly (Sunday 05:00, before the Monday verdict):

- **Failure-signal, per message.** The frustration census labelled all 2,114 messages (`csuite\tags.txt`; a message
  absent from it is NONE). Freeze a stratified gold set of 400 (all six letters represented, ~1/3 card answers), never
  used as prompt examples. Bar: failure-signal precision ≥0.80 and recall ≥0.75 against the census, and the tagger's
  share on the full 2,114 within ±2.5 points of 27.5%. The census reader's own self-agreement was 87.5% on 40, so
  ~0.8 is close to the ceiling a second reader could reach.
- **Keep-going, aggregate only.** The friction hand labels are lost, so per-message agreement cannot be proven. Two
  steps instead: (a) a one-off Opus gold pass labels a fresh random 300 of the friction window's 1,638 messages with
  the friction letters (a "nobody catches it" job, so Opus by the ladder; about 150k weighted tokens, once); the tagger
  must reach keep-going precision ≥0.80 and recall ≥0.75 on it; (b) the tagger's keep-going share on all 1,638 must
  fall inside the hand sample's 95% interval (about 32%-48%). If (b) fails while (a) passes, the hand sample was the
  outlier and the tagger's number stands, flagged as such on the page.
- The calibration writes `v3_health\tags\calibration.json` (date, prompt sha, model id as reported by the API, each
  agreement figure with n). The ops_watch `v3.keep_going_per_day` and `v3.failure_signal_share` points read it:
  - calibration passed within 8 days → **ESTIMATE** with "AI-tagged; agreement p/r on n" in the point's `why`;
  - failed or older than 8 days → **UNMEASURED** with the reason.
  They are never MEASURED: a model's reading is an estimate with a known error rate. That conflicts with the done
  line on `OPS_KPI_MEASURE_OWED_VTHREE` ("MEASURED ... from a deterministic instrument"); open question 1.

Output points (replacing the `U()` placeholders in `ops_watch.c_v3` for these two keys):
`v3.keep_going_per_day` (7-day mean, his local days, typed only), `v3.keep_going_today`,
`v3.failure_signal_share` (7-day, all blocks incl. cards), `v3.direction_per_day`, `v3.owner_msgs_per_day`.
`accepted_per_day` stays with `OPS_KPI_MEASURE_OWED_VTHREE`; this spec does not build it.

## 3. Part 2: planted faults (drills)

### 3.1 The idea

A program plants a fault we know about, at a time we record, of a kind one named role is supposed to catch. We then
time how long that role takes, or whether it catches it at all. That measures each role's real usefulness instead of
its claimed usefulness. The Arbiter's trial on 10-28 already did this once by hand (a deliberate fake close, which the
Arbiter caught and the Auditor's pre-screen waved through).

### 3.2 The catalogue

`src/RimMandrake/Utils/health_drill_catalogue.json` lists each drill class: what is planted, the catcher (one role
or program), what counts as a catch, the deadline, and the line of the catcher's role doc that makes it the catcher's
job. A class whose catcher doc does not say it is that role's job is refused by the program (the drill would measure a
duty nobody has). Starting classes:

| class | planted | designed catcher | caught when | deadline |
|---|---|---|---|---|
| FAKE_CLOSE | an item closed with a sha that does not touch the files its note claims | Arbiter (next batch); Auditor pre-screen as second | a verdict or ledger note/file naming the item as FAIL or defect | 48 h |
| VALIDATED_BUT_FAILING | an item at `validated` followed by RUNNER verify `fail` events (the QUARRY pattern) | Auditor (pre-screen + daily audit) | an Auditor note, finding or filed item naming it | 48 h |
| STALE_DOING | an item in `doing` with an expired lease and no event for 5 days | Producer (daily list) | the Producer drops, re-plans or flags it | 48 h |
| DEAD_FINDING | a RUNNER finding citing a real-looking failure, left untriaged | whoever owns the findings pool once `FINDINGS_FOLD_BUILD_QUARRY_SAID_IT_23X` lands (program folds, FOUNDRY judges) | the fold or FOUNDRY names it | 72 h |

Deferred until a catcher exists: **LAPSED_PERMISSION** (a grant past its expiry; catcher would be the grant monitor of
`COMPANION_GRANT_WIRE_LAPSES_AT_BEDTIME`, unbuilt). When it lands, the drill is a decoy grant entry for a decoy
subject, never a real grant: a drill may never change what any real work, the game or the bridge can do.

**Never planted:**
- any class **Operations** catches: ops_watch alarms and flags, a silent or blind collector, token-talk drift, runway or
  budget anomalies, a role NOT-RUNNING. Operations is the planter (by the owner's card) and knows every drill; it must
  never be timed against one. The program refuses a catalogue entry with catcher Operations, and a selftest proves it;
- any class whose failure path ends at the owner (a stale `needs owner`, a re-asked ruling, a card): if the catcher
  misses it, it reaches him. That breaks "nothing reaches the owner unread";
- anything touching the game, the bridge, deploys, art, real grants, or another seat's real items.

### 3.3 Marking plants so they never reach the owner or corrupt a metric

- **Sealed registry.** Each plant is recorded in `D:\ClaudeWork\rimmandrake\v3_health\drills\registry.jsonl`: id,
  class, planted time, catcher, deadline, every ledger event it wrote. Nothing in the repo names a live drill.
- **One filter, used everywhere.** `src/RimMandrake/Utils/drills.py is_drill(item_id)` reads the registry. Every
  metric program drops drill items and drill-caused items: ops_watch (flow, production, testing), `v3_vs_v2.py`,
  `rimflow_metrics`, `audit_prescreen.py`'s statistics (its flags still fire: that is the catch), the friction tools.
  The v3_vs_v2 rule file is untouched (the filter is input cleaning, not a rule change), and its verdict prints
  "drill items excluded: n".
- **Owner surfaces.** Every program that renders for the owner (morning cards, RimPulse, HUMAN.md, blind_view's owner
  lines) drops drill items through the same filter. A drill never carries `needs owner` (refused at plant time).
- **Ledger hygiene.** Drill items are real ledger items (the catchers read the ledger, so they must be). At reveal
  they are dropped with `--why "drill <id>: planted <t>, caught by <role> after <h> h"` and so leave the counts.

### 3.4 Keeping them invisible to the catcher

- Names are minted through `rimflow namecheck` from ordinary subject words in the lanes the catcher sees, not from a
  "DRILL" word. Times are random inside the catcher's window, never on a clock slot.
- The registry lives outside the repo; role instructions name it as off-limits the way token figures are; the
  existing token-talk scanner gains the registry path as a term, so a role run that reads or mentions it raises
  `DRILL_PEEK` and that drill is voided (not counted either way).
- Operations never writes a live drill id anywhere but its own item's notes, and only after reveal. The page shows open
  drills as a count only.
- Rate: at most **2 plants a week**, at most one open per catcher, one class per week in rotation. Small enough that
  the catchers' real work and the metrics are not distorted, large enough for ~8 timings a month.
- **The seat the events are written under is open question 2.** A catcher that sees seat `DRILL` on a close is not
  being tested. A drill written as seat FOUNDRY or RUNNER is invisible but means the ledger holds events under a
  seat that did not write them, marked only in the sealed registry.

### 3.5 Timing and cleanup

Every 15 min the ops_watch collector `health.drill` reads the registry and the ledger since each open drill's plant
time and checks for the catch rule. It records `caught_by`, `caught_after_h`, or `overdue`. At catch or at
deadline + 24 h, `health_drill.py reveal` (no AI): drops the drill item and any item whose caused-by chain starts at
it, writes the reveal note, appends the result to `drills\results.jsonl`, and closes the registry row. A drill whose
reveal fails stays OPEN in the registry and raises `DRILL_CLEANUP_STUCK`. A selftest proves a full cycle leaves no
open item, no needs-owner and no metric change on a fixture ledger.

Results feed the page: per catcher, drills caught / planted and median hours to catch, over 4 weeks.

## 4. Part 3: output tracing

### 4.1 What it answers

For every component (the six roles, the Dispatcher, testq, seat restart, the bridge grant): did it run when it should
have, what did it produce, and did anyone act on what it produced? Verdict per component per day:

- **WORKING**: ran, and at least one output was acted on by another role or seat within 72 h.
- **RUNNING-UNUSED**: ran and produced, and nothing it produced was acted on within 72 h.
- **NOT-RUNNING**: a scheduled slot passed (+45 min grace) with no launch, and no hold explains it (band, off switch,
  daily cap). A held slot is HELD, shown with its reason, not NOT-RUNNING.
- **UNMEASURED**: the trace cannot attribute outputs to the run, or a source is stale. Never read as zero.

### 4.2 How the program sees it (no AI)

- **Ran?** `dispatcher\state.json`, `journal.jsonl` (launch, done, held, missed) and `dispatcher\roles\rm-role-*.json`
  run records, against `dispatcher_schedule.json`'s slots.
- **Produced?** Ledger events written during the run. Today every role run writes as seat BENCH, so a role's events
  cannot be told from the interactive BENCH seat's. **Build step 1** fixes this: `rimflow cli` stamps
  `role_unit` from the `RM_ROLE_UNIT` environment variable that `role_launch.py` already sets on every run. Until that
  lands, attribution by run time window is ESTIMATE. File outputs named in the run record (verdicts.jsonl,
  `conductor\log.md`, Operations' `owner\OP-*.md`) count too.
- **Acted on?** A later event by a different seat or role on the same item id, or on an item spawned from it
  (claim, start, close, supersede, drop, a note citing it), or a later event citing a produced file's id
  (an Arbiter verdict id, an `OP-` id, an `RR-` replan id). Citation of a file by path alone is ESTIMATE.
- The day-one rows that needed judgment ("arguably WORKING for n=1") are exactly what Operations judges: the program
  gives the mechanical verdict; Operations may overrule it in its note, with a reason, and the page shows both.

Output: ops_watch points `health.trace.<component>.verdict` (as a number code plus label), `.runs_24h`,
`.outputs_72h`, `.acted_72h`, `.missed_unexplained`, and `v3_health\trace\<date>.json` with the evidence ids. The
existing `role:<R>:overbudget` alarms are not duplicated.

## 5. Part 5: the standing "how is v3" page

`D:\ClaudeWork\rimmandrake\v3_health\index.md`, rebuilt by `v3_health_page.py` at the end of every ops_watch pass,
with a dated copy `v3_health\days\<date>.md` kept once a day at 07:00 local. One screen, four layers, every number
tagged MEASURED, ESTIMATE or UNMEASURED (the point's own mark, copied, never upgraded):

1. **Running?** One row per component from part 3: verdict, last run, next slot, held reason. Plus the Dispatcher
   tick age and failed timers, copied from the ops_watch digest.
2. **Useful?** Part 3's WORKING/RUNNING-UNUSED per role over 7 days; drill catch rate and median time per catcher
   (part 2); untriaged findings; accepted items/day (UNMEASURED until `OPS_KPI_MEASURE_OWED_VTHREE`).
3. **Better than v2?** The latest row of `v3_vs_v2\history.jsonl` (standing, PROVISIONAL until four settled weeks,
   the counterfactual's mark) and the §6 success-test KPIs from ops_watch series: keep-going/day and failure share
   (part 1), test hours catching nothing, process-commit share, each with baseline, target and 7-day trend. The kill
   test line: "can fire / cannot fire (which input is UNMEASURED)".
4. **At what cost?** Weighted tokens per role per day against its cap (run records), the v3_vs_v2 cost ratio, process
   share, and **this check's own cost** (tagger tokens, Operations' share of its runs).

Reuse, not duplication: the page reads `ops_watch\status.json` and the series, `v3_vs_v2\history.jsonl` and
`weeks\<end>.json`; it measures nothing itself. It is a renderer like the digest. Layer 4 carries token figures, so it
is Operations' and the owner's only: a blind copy `index_blind.md` without layer 4 is written for the token-blind roles,
by the same allow-list rule as `digest_blind.md`.

**Read before he sees it.** Operations' 07:30 run reads the page first (after `digest.md`, which it already reads),
checks every number marked MEASURED that moved more than its band against its series, and stamps
`v3_health\read_stamp.json` (time, page hash, anything it overruled). The page's header says "last read by Operations
at <t>" and, if the page changed materially since, "not yet read". That is how a standing page meets "nothing reaches
the owner unread".

## 6. Alarms (so Operations wakes instead of waiting)

New ops_watch `targets`, all `"for": "Operations"` (kept in `alarms.json`, never filed as ledger items: no commits,
and no drill id ever reaches the ledger by an alarm). They use the existing edge-triggered run_alarms (file once per
new crossing, clear after 4 clear passes). The existing Operations alarm trigger runs one alarm run for all open
alarms, at most one per `alarm_run_gap_s`.

| tag | key | bar | why it matters |
|---|---|---|---|
| ROLE_NOT_RUNNING | `health.trace.*.missed_unexplained` | > 0 | a scheduled slot passed with no launch and no hold to explain it |
| ROLE_UNUSED_STREAK | `health.trace.*.unused_days` | ≥ 3 | a role produced for three days and nobody acted on any of it |
| DRILL_UNCAUGHT | `health.drill.overdue` | > 0 | a drill passed its deadline uncaught |
| DRILL_PEEK | `health.drill.peeks` | > 0 | a catcher read or named the sealed registry |
| DRILL_CLEANUP_STUCK | `health.drill.reveal_failed` | > 0 | a drill item could not be removed |
| TAGGER_STALE | `v3.tagger_age_h` | > 3 | tags stopped arriving: the kill-test inputs go UNMEASURED |
| TAGGER_DRIFT | `v3.calibration_ok` | = 0 | the weekly calibration failed its bar |
| KILL_TEST_FIRES | `v3.kill_test` | = 1 | after the first full v3 week: keep-going 7-day mean not below the re-tagged baseline AND accepted items not risen (only when both inputs are not UNMEASURED) |
| HEALTH_PAGE_STALE | `health.page_age_min` | > 60 | the page renderer died |

KILL_TEST_FIRES is a hand-up, not a decision: Operations writes it to the owner by its owner-only route
(`ops_watch\owner\OP-*.md`, read back) because stopping v3 is his.

## 7. Cost: tokens and commits

All token figures are ESTIMATE (weighted tokens, `role_launch.TOKEN_WEIGHTS`), sized from today's run records.

| part | daily tokens | basis |
|---|---|---|
| 1 tagger | ~60k Haiku-weighted/day | ~110 messages/day (78 typed + cards), 3 batches/day at ~7k in and ~1.5k out each, plus the 15% repeat |
| 1 calibration | ~70k Haiku-weighted/week (~10k/day) | 400 + 300 gold messages, weekly |
| 1 gold pass | ~150k Opus-weighted, once | 300 friction-window messages labelled by Opus at build time |
| 2, 3, 5 | 0 | programs |
| Operations judging | ~+40k at 07:30, ~+15k at 19:30 (~55k/day) | one screen of page plus the trace rows it overrules; inside its existing 450k/550k caps and 1.65M daily cap, no new run |
| alarm runs | 0 new on average | health alarms share the existing one-alarm-run-a-day budget; a day with a health alarm and another alarm still runs once |
| Auditor re-check | ~+30k/week | the weekly re-check of Operations' trace overrulings and drill reading (its own budget) |

**Total ≈ 70k Haiku + 55k Opus weighted per day**, about 3% of Operations' 1.65M daily cap for the Opus part. Haiku's
list price is roughly a fifth of Opus per token (ESTIMATE from the published price sheet, not a meter reading).

**Commits.** Daily running adds **no routine commits**: everything writes under `D:\ClaudeWork`, and the health alarms
stay out of the ledger. Ledger events come only from drills (about 3 events at plant, 2 at reveal; at 2 drills a
week, ≤4 small commits a week, riding the Dispatcher's existing ledger publish where possible) and from Operations'
notes on its own item, which it writes today anyway. The build is about **7 commits**, one per build step, all
`src/RimMandrake/Utils/` and so counted as process by `process_regex`: a one-time bump against a 7-day share already at
72.4%. The build should land in one or two days rather than drip, so it moves one week's share, not three.

## 8. Build order with L0 checks

Each step is one commit with its selftest (`run_selftests.py --only <test>`). L0 = a selftest on fixtures, no live
system.

1. **Role run stamping.** `rimflow cli` writes `role_unit` from `RM_ROLE_UNIT` on every event when set.
   L0: an event written with the variable set carries it; without it, the event is byte-identical to today's.
2. **Output trace collector** (`health.trace.*` in ops_watch). L0: on a fixture schedule, journal and ledger, a role
   with a run and an acted-on output is WORKING; with outputs and no reaction for 72 h, RUNNING-UNUSED; a missed slot
   with no hold, NOT-RUNNING; a slot held by band, HELD; events without `role_unit` and no run window, UNMEASURED.
   Re-run on the real 10-28..10-29 data must reproduce the day-one table's verdicts for the Producer (WORKING), Arbiter
   and Auditor (RUNNING-UNUSED); a differing row is listed for Operations to judge, not silently accepted.
3. **Page renderer** (`v3_health_page.py`). L0: every number on the page carries one of the three marks; a fixture
   point marked UNMEASURED renders as UNMEASURED, never 0; the blind copy contains no word from the token-talk terms;
   the page measures nothing (it imports no collector).
4. **Message extract** (`owner_tags.py extract`). L0: on the census inputs, extraction reproduces 1,638 typed messages
   for 10-05..10-26 and 2,114 blocks for 10-02..10-27; a second run adds 0 rows; a session crossing midnight files
   each message under its own local day.
5. **Tagger + checks + calibration** (`owner_tags.py tag`, `calibrate`). L0 (no model call): a fixture model reply
   with a missing id, an invented id, an unknown tag, or a cue not in the text is rejected or dropped exactly as §2.4
   says; a changed prompt byte refuses to tag; a day under 95% tagged is UNMEASURED. L1 (one live run, the gate): the
   calibration bars in §2.4 pass on the frozen gold sets, and `calibration.json` is written. Until it passes, the two
   ops_watch points stay UNMEASURED.
6. **Drills** (`health_drill.py`, `drills.py`, catalogue, `health.drill.*` collector). L0: a catalogue entry with
   catcher Operations, or with `needs owner`, or touching game/bridge/deploy paths, is refused; on a fixture ledger a
   plant, a catch event and a reveal leave no open item, no needs-owner line, and identical flow and production
   figures to the same ledger without the drill; an uncaught drill raises DRILL_UNCAUGHT at its deadline and not
   before; a role run text naming the registry path raises DRILL_PEEK. Not switched on until open question 2 is
   answered.
7. **Alarms and role text.** The §6 targets in `ops_watch_rules.json` (Operations proposes; the owner's rule that
   Operations does not edit targets alone stands, so FOUNDRY writes them under this item); `roles/operations.md`
   gains a "v3 health" section: read `index.md` at 07:30 after the digest, stamp it, judge trace overrulings, weekly
   drill reading on Mondays; `roles/auditor.md` gains the weekly re-check of those. L0: each new target fires on a
   fixture crossing and clears after 4 clear passes; the Operations trigger names a health alarm.

Order rationale: 1-3 give a running page with no AI at all (most of the value, zero tokens). 4-5 add the kill-test
inputs. 6 waits on the owner. 7 wires it all to Operations.

## 9. Open questions for the owner

1. **Kill-test ruler.** The 31/day baseline came from a hand sample too small to detect a drop to 26, and an AI
   tagger can only give an ESTIMATE, never the "deterministic MEASURED" that `OPS_KPI_MEASURE_OWED_VTHREE` asks for.
   Proposed: the tagger re-tags the baseline windows, the kill test compares tagger to tagger as relative drops
   (−16% keep-going, −2.5 points failure share), and the two KPIs count as ESTIMATE with their calibration figures.
   Yes, or keep 31 and 27.5 as fixed numbers?
2. **Drill seat.** A drill must look like ordinary work to its catcher. May the drill program write its ledger events
   under the seat the fault would really come from (FOUNDRY for a close, RUNNER for a verify), marked only in a sealed
   registry and removed at reveal? If not, drills use a visible seat and measure much less.
3. **Who drills Operations?** Operations plants, so nothing tests whether Operations catches its own class of faults
   (a blind collector, a missed slot). Leave that untested for now, or have the Auditor plant one Operations drill a
   month?
