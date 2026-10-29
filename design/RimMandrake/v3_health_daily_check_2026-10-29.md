# v3 health: the daily check (spec, 2026-10-29)

Item: `V3_HEALTH_BUILD_DAILY_PULSE_DAY_ONE`. Written by a BENCH design helper (Opus); FOUNDRY builds.
Owner, 2026-10-29: "1, 2, 3 - should be a daily check performed by a responsible party all the time (could be Ops,
could be Arbiter). Everything but 4. Switching off agents is a good idea later when we show that at least a nominative
system is functional for awhile." By card the same day: **Operations owns all of it**; the Auditor's weekly re-check
guards Operations grading its own usefulness.
Owner, later the same day: "I also suspect Operation may need to sample more often than once a day. I think perhaps
there are dumb monitors that are running all the time that feed into real-time dispatch as well as Operation
assessment?" Yes: that is the shape below.
Owner, 2026-10-29, on drills (by card): the Auditor plants faults, including the ones Operations must catch; the
kill-test baseline is an Opus gold-labelling of the v2 week. His design for recording plants, and its revision, is §3.

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
| 2 drills | `health_drill.py plant` (no AI), the Auditor's program, plants blind from the Auditor's catalogue; `health_drill.py watch` (no AI, not in ops_watch) looks for the catch | plant: own timer, random minute, at most the rate in §3.3; watch every 15 min | the Arbiter referees each settled plant; Operations and the Auditor read results weekly | none |
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

## 3. Part 2: planted faults (revised 2026-10-29 to the owner's design)

### 3.1 His design, and what this section changes

By card, 2026-10-29: **the Auditor plants faults, including the ones Operations must catch.** His words the same day:
*"Planted faults should be added from outside the system (I would suggest Auditor by its very design). It is treated
as a very real fault, and recorded in a secret ledger that only Arbiter and Conductor are allowed to look in. Once the
experiment is over, it is post-modified to indicate it was a Plant so it never contaminates later processing, after
that information can no longer change behavior. Stats that are gathered should have parallel numbers that are
"corrected fault-free" that at first are simply equivalent but later get updated once faults are removed. Then in the
hidden register the fault is marked as repaired."*

The point is unchanged: plant a fault we know about, of a kind one named role should catch, and time the catch. That
measures each role's real usefulness, not its claimed usefulness (the Arbiter's 10-28 trial did it once by hand).

What his design gets right and is kept: plants look real, so they test the real path; a secret register; a reveal
that marks the plant so it stops mattering; two numbers for every statistic, equal until a reveal. Six things in it
needed working out. Each is below with how it is resolved:

| issue | resolution | where |
|---|---|---|
| The Auditor is itself a catcher (VALIDATED_BUT_FAILING; second line on FAKE_CLOSE). A planter that knows the plant cannot be timed on it. | The Auditor **owns** the catalogue and the rate; a program it owns plants **blind** on its own timer, outside every role run. The Auditor never learns which plant fired or when. | 3.2 |
| The Arbiter may read the secret, yet it is the designed catcher of a fake close. Reading the live register would void every Arbiter timing. | The Arbiter reads **settled** rows only (caught, missed or voided) and referees them. The Conductor alone reads **live** rows. | 3.2 |
| The real ledger is append-only, so a plant cannot be "post-modified". | The reveal is a new **appended, public, structured event**; projection rules make readers treat the revealed events as planted. Nothing is edited. | 3.5 |
| "Only Arbiter and Conductor may look": every agent runs as the same Windows user and can read any file. | The register is a **seal, not a lock**: unreadable by accident, and reading it on purpose leaves a trail that voids the peeker's drills. Named plainly as a limit. | 3.4 |
| A plant has real side effects: a FOUNDRY ticket spent on a fake, real code written to fix a fake, a plant reaching his screen. | Reveal **per plant, at its first catch** (not at the end of a long experiment); a fixed rule for code that "fixed" a plant; an owner gate in every owner-bound renderer. | 3.7, 3.8 |
| "Corrected" numbers would need the secret to compute. | They do not: they are computed from the **public reveal events only**, so before a reveal they equal the raw numbers by construction, and no metric program ever opens the register. | 3.6 |

### 3.2 Who plants, who knows, who catches

- **Planter: `health_drill.py plant`, owned by the Auditor.** The Auditor writes and maintains the catalogue (3.3),
  the rate and the safety refusals; that is the "from outside the system" part. The program runs on its own timer, not
  inside any role run (no `RM_ROLE_UNIT`), picks the class, the target window and the minute at random from the
  catalogue, writes the plant, and records it only in the sealed register. The Auditor's role text says it never reads
  the live register. So the Auditor can still be timed on the classes it catches: it knows the classes exist (its own
  role doc says so anyway), not the instances.
- **Live reader: the Conductor.** It is the only voice to the owner, so it must know what is fake in order to keep
  fakes off his screen (3.7). It is not timed as a catcher of anything. It uses the knowledge for that filter only:
  it never steers, delays, assigns or comments on work because it is a plant. If the owner asks about a plant item
  directly, the Conductor tells him the truth: he is outside the experiment, not a catcher.
- **Referee: the Arbiter**, on settled rows only. When the watcher (3.8) marks a plant caught, missed or void, the
  row becomes readable to the Arbiter, which confirms the mechanical verdict (was that note really a catch?) and rules
  on any real commit the plant drew (3.7). While a plant is live it is invisible to the Arbiter, so the Arbiter stays a
  fair catcher of fake closes. This narrows his "Arbiter may look" to "Arbiter may look once it is over"; open
  question 2 asks him to confirm.
- **Catchers: every role, Operations included** (by his card). Nothing about a live plant reaches Operations: the
  watcher is not an ops_watch collector, and nothing it writes for Operations names or counts a live plant (3.8).

### 3.3 The catalogue and the hard refusals

`src/RimMandrake/Utils/health_drill_catalogue.json`, written by the Auditor, lists each class: what is planted, the
catcher, what counts as a catch, the deadline, and the line of the catcher's role doc that makes it the catcher's job.
A class whose catcher doc does not say so is refused (it would measure a duty nobody has).

| class | planted | designed catcher | caught when | deadline |
|---|---|---|---|---|
| FAKE_CLOSE | a duplicate of a real, already-finished item, closed with a sha that does not touch the files its note claims | Arbiter (next batch); Auditor pre-screen second | a verdict or note naming the item FAIL or defective | 48 h |
| VALIDATED_BUT_FAILING | an item at `validated` followed by RUNNER verify `fail` events (the QUARRY pattern) | Auditor (pre-screen + daily audit) | an Auditor note, finding or filed item naming it | 48 h |
| STALE_DOING | an item in `doing` with an expired lease and no event for 5 days | Producer (daily list) | the Producer drops, re-plans or flags it | 48 h |
| DEAD_FINDING | a RUNNER finding citing a real-looking failure, left untriaged | the findings-pool owner once `FINDINGS_FOLD_BUILD_QUARRY_SAID_IT_23X` lands | the fold or FOUNDRY names it | 72 h |
| Operations classes | proposed by the Auditor; each acts only on a **decoy input** that ops_watch reads and nothing else does (for example a decoy source whose writer the planter pauses, so it goes stale) | Operations | its alarm or note names it | 24 h |

Deferred until a catcher exists: LAPSED_PERMISSION (a decoy grant for a decoy subject, never a real grant).

**Refused at plant time, by the program, each proved by a selftest:**
- anything touching the game, a save (canonical or not), the bridge, deploys, the Mods folder, `ModsConfig.xml`, art,
  real grants, or anything on the owner's screen (RimPulse, his desktop, the game window);
- anything in the repo but the ledger shards: a plant never commits code, defs or docs. A fake close cites an
  existing, unrelated sha;
- any change to another seat's real item: a plant writes events on items it filed itself;
- `needs owner`, a card, a re-asked ruling, or any path whose miss ends at the owner;
- a fabricated item with buildable content: a plant's item duplicates finished work or is process-only, so a catcher
  who "does the work" finds nothing to build (3.7);
- more than **2 plants a week**, more than **one live per catcher**, or a class used twice in a row.

### 3.4 The secret register: where it lives and how it is guarded

- **Where.** `D:\ClaudeWork\rimmandrake\v3_health\drills\sealed\` (outside the repo; nothing in the repo names a live
  plant). Two files: `live.bin`, sealed (encrypted with a key from a file whose path is read from the environment,
  set only on the planter's timer, the Conductor's launch and the watcher), and `settled.jsonl`, plain, which the
  Arbiter reads. A plain grep for an item id, class name or the word "plant" over `live.bin` matches nothing (selftest).
- **Row.** Plant id, class, catcher, planted time, deadline, every event it wrote as (seat, tsn) (ledger events have
  no id of their own; seat + tsn is their identity), the items it filed, and a status:
  `LIVE` → `CAUGHT` / `MISSED` / `VOID` → `REVEALED` → `REPAIRED`.
- **Tool guard.** `drills.py` is the only reader. `read_live()` refuses unless `RM_ROLE_UNIT` is the Conductor or the
  caller is the planter or watcher; `read_settled()` serves only settled rows. This stops an honest mistake. It does
  not stop a determined agent, which can read any file this Windows user can.
- **Tripwire.** The register path and the key-file path are terms in the existing token-talk scanner over every role
  run's transcript except the Conductor's. A hit raises `DRILL_PEEK`, voids every live plant that role catches, and is
  filed as a finding. So peeking is detectable after the fact, and a peek only spoils the peeker's own numbers.
- **What is not done, and why.** A separate Windows account with file permissions would make it a real lock. That is
  much more plumbing (another user, another environment, credential handling) for a threat (an agent deliberately
  hunting the register) that the tripwire already exposes. Revisit if `DRILL_PEEK` ever fires.

### 3.5 In the ledger: a real-looking plant, then a public reveal

- **Planting.** The plant is written as ordinary rimflow events under the seat the fault would really come from
  (FOUNDRY for a close, RUNNER for a verify): his "treated as a very real fault". The shards are union-merged
  (`.gitattributes`), so writing FOUNDRY's shard from another clone cannot conflict. The commit rides the ordinary
  ledger publish with an ordinary `ledger:` message. The cost is honest and temporary: until the reveal, the ledger
  holds events under a seat that did not write them.
- **The reveal (his "post-modified").** The ledger cannot be edited, so the reveal is an **appended event**, a new
  verb `reveal` written by the watcher under the Auditor's role unit: `{plant, class, catcher, outcome,
  caught_after_h, events: [(seat, tsn)...], items: [...]}`. It is structured, not a note, because readers must act on
  it and free text is not parsed. It is public: once a plant is over, nothing about it is secret, and its reveal is
  what makes every later reader correct.
- **Projection rule.** `model.planted(events)` returns the revealed events and items, plus every item whose
  caused-by chain starts at a revealed item. `model.corrected(events)` is the event list without them. `model.replay`
  itself is unchanged: the history stays true (those events did happen); a reader chooses the view.
- **Afterwards the plant can no longer change behaviour.** The watcher drops every planted and descendant item still
  open, with `--why "plant <id>: revealed"`, so it leaves every queue, list and lease. Every program that decides
  anything (the Dispatcher, the Producer's list, `audit_prescreen.py`'s statistics, `arbiter_pending.py`) reads the
  corrected view. The as-recorded view is kept for history and for the drill results.

### 3.6 Two numbers for every statistic: as-recorded and corrected

- **How they are made.** One function, `model.corrected()`, applied at the reader. The ledger readers today are
  `model.read()` (v3_vs_v2, blind_view, role_launch), `pulse_core.read_ledger()` (ops_watch and RimPulse),
  `testing_metrics.read_ledger()` and `mod_completion.read_ledger()`. Each metric gains the corrected twin by passing
  its events through it. A selftest lists every ledger reader under `Utils/` and `rimflow/` and fails if a metric
  reader does not route through it, so a new reader cannot silently skip the correction.
- **Equal until a reveal, by construction.** The correction uses only public reveal events, so before any reveal the
  two numbers are identical, and computing them reveals nothing about a live plant.
- **ops_watch.** Each ledger-derived point carries `value` (as-recorded) and `corrected`. Alarms fire on the
  as-recorded value: a plant must trip an alarm exactly as a real fault would. Trends, the kill test and the page use
  `corrected`.
- **History that was already written.** ops_watch series and `v3_vs_v2\history.jsonl` rows are never rewritten.
  When a reveal touches a past window, its corrected figure is recomputed from the ledger and **appended** as a
  correction row (`corrected_by: <plant id>`). Readers take the newest row for a window.
- **v3_vs_v2.** The rule file is untouched (the correction is input cleaning, not a rule change). Its verdict prints
  both numbers and "plants removed: n".
- **Blind surfaces** (`digest_blind.md`, `index_blind.md`, `blind_view`) show corrected numbers and the count of
  plants **settled** this week. They never show a live count: knowing a plant is out there would put the catcher on
  alert.
- **Cost is not corrected away.** Tokens and hours spent catching or handling a plant were really spent. They are
  removed from quality and flow counts but kept in cost, as a separate "drill overhead" line on the page.
- **A decision already taken on as-recorded numbers is not undone** (an alarm run that happened, a role the Dispatcher
  held). The drill result records it, so the Auditor can see whether plants are steering real work.

### 3.7 Real side effects, and how each is contained

- **A FOUNDRY ticket spent on a fake.** The catch is designed to be a judgement (a verdict, a note, a finding), not
  a rework claim. The watcher reveals within one pass of the catch (≤15 min) and drops descendants, so the window for a
  real claim is short. If one is claimed in that window, its cost is drill overhead. The fake close duplicates finished
  work, so even a reopened plant has nothing new to build.
- **A plant "fixed" by real code.** The reveal lists every commit that cites a planted or descendant item. The Arbiter
  rules on each: (a) it fixes a real gap the plant exposed (a check that should have caught it): **keep**, recorded as
  the drill's dividend; (b) it serves only the fake: **delete** it by the standing rule, fix every inbound reference,
  filed as a FOUNDRY item. Until every such commit is ruled, the row cannot reach `REPAIRED`.
- **Harm to the game, saves or his screen.** Not containable after the fact, so never allowed: refused at plant time
  (3.3). Plants live in the ledger and in decoy scratch inputs only.
- **A plant reaching the owner while it looks real.** Two layers. A program gate: every owner-bound renderer (morning
  cards, RimPulse, HUMAN.md, Operations' `OP-` relays, the Conductor's card builder) passes item ids through
  `drills.owner_gate()`, which holds anything citing a live planted or descendant item. A held line is left out, not
  reported missing. Then the Conductor, which reads the live register, checks anything it writes him by hand. A plant
  never carries `needs owner` (3.3), so the gate should seldom fire. Every hold is counted, and a hold is a design
  defect in that class.
- **A plant tripping another plant's catcher, or a real fault hiding behind a plant.** One live plant per catcher, and
  at most two a week. A real fault found while chasing a plant is real work and is filed as such.

### 3.8 Timing: per plant, not at the end of the experiment

- **The watcher**, `health_drill.py watch`, runs every 15 minutes on the planter's timer, not inside ops_watch
  (Operations is a catcher now). It reads the live register and the ledger since each live plant's planted time and
  applies the class's catch rule. Its outputs are the register itself and `drills\results.jsonl` (settled rows only).
- **A plant ends at its first catch, at its deadline, or at a peek.** Then: status `CAUGHT` / `MISSED` / `VOID`, the
  row moves to `settled.jsonl`, and the watcher writes the `reveal` event and the drops. It reveals per plant rather
  than at the end of a whole experiment because a plant that sits unrevealed for weeks keeps steering real work.
  The price: each reveal shows catchers what one plant looked like. Rotating classes and the low rate keep that small.
- **The Arbiter's referee pass** (in its next batch) confirms or overturns the verdict and rules on any commits.
  Then `REPAIRED` is set: all items dropped, corrected rows appended, commits ruled. A row revealed but not
  `REPAIRED` within 24 h raises `DRILL_CLEANUP_STUCK`.
- **The "experiment"** is a calendar window the Auditor sets in the catalogue (first one: 4 weeks from switch-on).
  Its end stops new plants and starts the results summary. It is not when plants are revealed: each one already was.
- **Results** feed the page: per catcher, plants caught / planted and median hours to catch, settled plants only,
  4 weeks. Operations reads them in its Monday 07:30 run, and the Auditor's weekly re-check reads them too.

### 3.9 Alternatives considered

| | how it works | gains | costs |
|---|---|---|---|
| **A. His design, literally** | The Auditor plants by hand and knows each plant; Arbiter and Conductor read the live register; plants revealed when the experiment ends | simplest; no blind planter | the Auditor and the Arbiter can never be timed, and they are the catchers of the two most important classes (fake close, validated-but-failing); plants sit live for weeks and steer real work |
| **B. Blind planter, split access, per-plant reveal (recommended, 3.2-3.8)** | as above | every role timed, Operations included; corrected numbers need no secret; a plant stops mattering within one pass of its catch | one new verb (`reveal`), a reader lint, a seal that is tamper-evident rather than a lock, and one narrowing of his access rule (Arbiter after settlement) |
| **C. Shadow overlay** | plants never enter the real ledger; they live in an overlay that only the catchers' reading tools merge in | no impersonated seat, no correction at all, no contamination possible | measures the reading tool, not the role: a catcher that reads git, raw shards or a file path never sees the plant; every reading tool needs the overlay |

Recommendation: **B**. It is his design with two changes: the Auditor plants through a blind program instead of by
hand, and the Arbiter reads after settlement instead of live. Both exist so that the roles he most wants measured can
be measured at all.

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
   (part 2, settled plants only; no live count is ever shown); drill overhead; untriaged findings; accepted items/day (UNMEASURED until `OPS_KPI_MEASURE_OWED_VTHREE`).
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
and no drill id ever reaches the ledger by an alarm). The `health.drill.*` keys are read from the watcher's
`drills\health.json`, which holds settled-plant counts only, so Operations, now a catcher, learns nothing live. They use the existing edge-triggered run_alarms (file once per
new crossing, clear after 4 clear passes). The existing Operations alarm trigger runs one alarm run for all open
alarms, at most one per `alarm_run_gap_s`.

| tag | key | bar | why it matters |
|---|---|---|---|
| ROLE_NOT_RUNNING | `health.trace.*.missed_unexplained` | > 0 | a scheduled slot passed with no launch and no hold to explain it |
| ROLE_UNUSED_STREAK | `health.trace.*.unused_days` | ≥ 3 | a role produced for three days and nobody acted on any of it |
| DRILL_UNCAUGHT | `health.drill.missed_7d` | > 0 | a plant reached its deadline uncaught (already revealed when this fires) |
| DRILL_PEEK | `health.drill.peeks` | > 0 | a role other than the Conductor read or named the sealed register (§3.4) |
| DRILL_CLEANUP_STUCK | `health.drill.unrepaired` | > 0 | a revealed plant was not `REPAIRED` within 24 h (§3.8) |
| DRILL_OWNER_HOLD | `health.drill.owner_holds` | > 0 | the owner gate held a line citing a live plant (§3.7): a defect in that class |
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
stay out of the ledger. Ledger events come only from drills (about 3 events at plant, one `reveal` plus the drops at reveal; at 2
plants a week, ≤4 small commits a week, riding the Dispatcher's existing ledger publish where possible) and from Operations'
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
6. **Drills** (`health_drill.py plant|watch`, `drills.py`, the `reveal` verb with `model.planted()` and
   `model.corrected()`, the catalogue). L0: every refusal in §3.3 fires (game, save, bridge, deploy, art, repo path,
   another seat's item, `needs owner`, rate); a plain grep of `live.bin` for a planted id matches nothing;
   `read_live()` refuses a non-Conductor role unit; before any reveal every metric's corrected value equals its
   as-recorded value; after plant, catch and reveal on a fixture ledger there is no open planted item, no needs-owner
   line, and corrected flow and production figures equal the same ledger without the plant; the reader lint fails on
   a fixture ledger reader that skips `model.corrected()`; `owner_gate()` holds a line citing a live plant and passes
   it after reveal; a role run text naming the register path raises DRILL_PEEK and voids that role's live plants.
   Not switched on until open question 2 is answered.
7. **Alarms and role text.** The §6 targets in `ops_watch_rules.json` (Operations proposes; the owner's rule that
   Operations does not edit targets alone stands, so FOUNDRY writes them under this item); `roles/operations.md`
   gains a "v3 health" section: read `index.md` at 07:30 after the digest, stamp it, judge trace overrulings, weekly
   drill reading on Mondays; `roles/auditor.md` gains the weekly re-check of those, ownership of the drill catalogue,
   and "never read the live register"; `roles/arbiter.md` gains the referee pass on settled plants (§3.2, §3.7);
   `roles/conductor.md` gains the live-register duty and its limit (filter for the owner only, §3.2). L0: each new target fires on a
   fixture crossing and clears after 4 clear passes; the Operations trigger names a health alarm.

Order rationale: 1-3 give a running page with no AI at all (most of the value, zero tokens). 4-5 add the kill-test
inputs. 6 waits on the owner. 7 wires it all to Operations.

## 9. Open questions for the owner

1. **Kill-test ruler.** The 31/day baseline came from a hand sample too small to detect a drop to 26, and an AI
   tagger can only give an ESTIMATE, never the "deterministic MEASURED" that `OPS_KPI_MEASURE_OWED_VTHREE` asks for.
   Proposed: the tagger re-tags the baseline windows, the kill test compares tagger to tagger as relative drops
   (−16% keep-going, −2.5 points failure share), and the two KPIs count as ESTIMATE with their calibration figures.
   Yes, or keep 31 and 27.5 as fixed numbers?
   **Answered by card 2026-10-29:** the baseline is an Opus gold-labelling of the v2 week. §2 is not yet revised to it.
2. **When may the Arbiter read the secret register?** Your design lets the Arbiter and the Conductor look. But the
   Arbiter is the designed catcher of fake closes, and an Arbiter that has read the live register cannot be timed on
   them. Proposed (§3.2): the Conductor reads live plants; the Arbiter reads each plant once it is settled and
   referees it. Yes, or give the Arbiter live access and leave fake closes untimed?
