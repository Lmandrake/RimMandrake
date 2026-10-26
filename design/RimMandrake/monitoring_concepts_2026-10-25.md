# RimMandrake monitoring concepts (2026-10-25)

Owner ask (verbatim): "consider the magnificent Lodestar Companion for things we might want to monitor on this system too. Then do several suggestions for an improved monitoring system, given Rimflow runs this system rather than Lodestar. Ticket monitoring, understanding which mods are being worked on, let's see many concepts on what we might actually benefit from tracking not just for fun but to inspire different choices and logic."

## 0. Data census (what exists today, measured)

Measured 2026-10-26 from the FOUNDRY clone through `model.read()` (the production reader: frozen file
plus every shard, content-deduplicated, canonical order). Every number below came from a script; the
reproducible part is `python3 src/RimMandrake/Utils/rimflow_metrics.py` (§D), whose 14-day output is
saved at `D:\ClaudeWork\rimmandrake\monitoring\metrics_14d_20261026.txt`.

**Volume.** 28,392 lines on disk fold to **28,385 events** (7 union-merge duplicates collapsed):

| File | Lines | First ts | Last ts |
|---|---|---|---|
| `infrastructure/state/ledger/events.jsonl` (frozen) | 10,890 | 2026-08-21 | 2026-09-24 |
| `events/FOUNDRY.jsonl` | 8,740 | 2026-09-24 | 2026-10-26 |
| `events/BENCH.jsonl` | 6,135 | 2026-09-24 | 2026-10-26 |
| `events/OWNER.jsonl` | 2,543 | 2026-09-24 | 2026-10-26 |
| `events/RUNNER.jsonl` | 84 | 2026-10-26 | 2026-10-26 |

4,886 items have been filed. The last 14 days hold 9,348 events. By writing seat (all time): FOUNDRY
13,643, BENCH 8,529, OWNER 3,972, BUILD 793, CHECK 726, DECIDE 541, REP 97, RUNNER 84.

**Verbs present** (count): note 5679, file 4843, close 2910, claim 2587, start 2450, game 1969, bridge
1583, lease 1336, verify 1291, implemented 981, needs 493, seat 478, reassign 474, block 370, capability
170, drop 146, reconcile 143, unblock 141, supersede 113, finding 88, reclaim 67, spawn 44, retarget 29.

**Fields present** (events carrying it): seat/event/ts on all 28,385; `id` 24,141; `tsn` 14,558 (only
from 2026-10-02 on, so 13,827 older events order by second only); `why` 5,078; `needs` 4,967;
`ownerSaid` 2,205; `evidence` 1,789; `caused_by` 1,552; `ranBy` 1,427 and `measured` 508 (on `game`
only); `token`/`expires` (leases) 1,336; `criteria` 981; `level` 884; `criterion` 804; `byCard` 611;
`override` 547; `perRuling` 221; `row` 156.

**Vocabularies.** `kind` is free text: **39 distinct values** (task 3057, bug 718, build 441, decision
143, design 101, check 99, fix 72, defect 57, ...). `target` is v1 4,814 and v2 29. `game` states: DOWN
637, UP 611, LOADING 478, GOING_DOWN 201, DEPLOYING 42.

**Absent, and what that costs.**
- **No `mod` field.** Which mod an item is about must be inferred from its id or title; the §D mapper
  places only 715 of the 2,150 items touched in 14 days (1,435 unmapped, 67%).
- **No effort, estimate or cost** (tokens, minutes) on any event. Budget comes from
  `src/RimMandrake/Utils/pulse/usage.py` (the plan's own usage endpoint), outside the ledger.
- **No session or agent identity below the seat.** Lease tokens carry a pid
  (`FOUNDRY.pid30372.21eb2f5b`), the only sub-seat trace.
- **No priority on events.** Rank is computed by `priority.py` and never recorded, so "how long did the
  top item wait" cannot be answered from history.
- **No explicit reopen.** Closed is terminal by design. Rework shows up only as a new item with
  `caused_by` pointing at a closed one.

**Replay health.** The fold collects **10 refusals** already in the file (e.g. a second `drop` on
`REFMATCH_THRESHOLDS_CALIBRATE_1`) and 0 tolerated unknown fields.

**Outside the ledger.** Git: **5,804 non-merge commits in 14 days**, checked against
`git rev-list --count`; 1,023 of them touch only the ledger. Mods with an `About/About.xml`: 76
RimMandrake, 21 RimStarWars, 33 RimUtinni (130). RimPulse (`src/RimMandrake/Utils/pulse/`) and the
telemetry daemon with Grafana (`src/RimMandrake/Utils/telemetry/`) already exist and are the natural
places to show any of this.

## A. What Lodestar Companion tracks, and what transfers

Read from `~/dev/Lodestar/companion/Model.swift` (the `Plots` struct is the list of everything the
face draws), `FaceAgents.swift`, `FaceTimelines.swift`, `FaceTiles.swift`, `Burning.swift`, and
`docs/companion/STYLE_GUIDE.md` §4-§8, `docs/companion/2026-10-22-bottleneck-answers.md`.

**Why a glance at it works.** Not the rows; the rules behind them:

1. *A healthy face is mostly unlit* (STYLE_GUIDE line 9). Light is spent only on what needs him. A
   glance answers "do I have to do anything?" before it answers anything else.
2. *Unknown is not zero* (§8). Unmeasured reads `--`, a hollow lamp bar means "cannot vouch", a red
   that went stale stays red with AS OF its age ("losing the monitor did not fix the fault").
3. *Stable scales* (FaceAgents.swift header: RSS ceiling 1600 MB raised only in 400 MB steps). Bars
   hold still so a change in the bar is a change in the world, not a rescale.
4. *Every row says it looked* ("0 URGENT · CHECKED 13:50"). An empty row with a timestamp is
   evidence; an empty row without one is a blind instrument.
5. *Motion budget*: at most two attention motions at once; a state change pulses 40 s then stops.
6. *Identity colour per project* threads every mark of a project together (the circuit contact).

**Rows, and whether each transfers to Rimflow:**

| Companion element (struct) | What a glance tells him there | Transfers? | Rimflow analogue |
|---|---|---|---|
| BURNING (`BurnPlot`, tiers red/amber/verify, due word) | which asks are his, how late | **Yes, already partly built** | RimPulse owner-only attention list; missing: tier + due word + VERIFY tier (agent says done, he has not looked) |
| AGENTS (`AgentSegment`: state waiting/running/idle/error, since, CPU/RSS, project burn/open) | who is working, who is waiting on him, heaviest hitter | **Yes, strongest transfer** | seats (BENCH/FOUNDRY/...) from ledger `seat`/`claim`/`start` events + Claude Code transcripts; "waiting" = seat with an open owner ask |
| ORDERS strip (`FocusCell`: burning/open per repo, overdue, unverified) | which project has work piling up | **Yes, re-keyed by mod** | per-mod open items (subject prefix / `mod` field) |
| GIT ACTIVITY 24H (`ActivityPlot`: 20-min columns stacked by repo colour) | where the hands were today | **Yes, re-keyed by mod** | commit paths under `src/RimMandrake/Mods/<mod>/` and design/ |
| BUDGET (`BudgetPlot`: fraction used, pace AHEAD/ON PACE/BEHIND, reset_at) | will we run out before reset | **Yes** | tokens/hour already in RimPulse; missing: pace against a weekly/plan cap |
| BEACONS (`BeaconsPlot`: one gem per standing risk, green/amber/red) | have any known failure modes re-fired | **Yes** | `infrastructure/state/facts/instrument_traps.md` + lessons: a beacon per trap that a grep of new logs/ledger notes can re-trigger |
| BEARING cadence (cycle length histogram, next due) | is the sense loop alive and on time | **Yes** | nightly selftests, code_review sweep, artpipe cycle: "last ran / next due / cycle length" |
| HOST panel (CPU / disk / mem / Claude share, `bottleneck-answers.md`) | is the machine the bottleneck | **Partly** | WSL host + the Windows game; "is RimWorld up / is the bridge held" matters more than CPU |
| BEARING HEALTH 24H (`BearingsPlot` ribbon) | collector errors over the day | **Yes, as instrument health** | a row per collector: last good read, age |
| DRAFTS, MEETINGS (mail/calendar) | replies ready, time to next meeting | **No** | nothing here sends mail or holds meetings |
| Renewal (`Renewal`: token expiry) | a credential about to lapse | **Small** | GenAI key expiry, if the env exposes it; otherwise drop |
| Privacy mode, Promise seals | screen sharing; commitments | **No** | single-owner local page |

What does **not** transfer is the hardware medium (lamps, breath, walnut): RimPulse is a web page
and phone widget. What transfers is the discipline: unlit when healthy, hollow when unmeasured,
fixed scales, every row timestamped, colour per mod.

## B. Monitoring concepts

Each concept below gives what it tracks, its source, one measured value (14-day window ending
2026-10-26 18:33Z unless it says otherwise), and the decision it would change. A concept that changes no
decision is decoration and is not listed.

**B1. Verify backlog (built, not yet accepted).** Tracks items in `built`/`validated`, how long since
`implemented`, and which levels are still owed. Source: `Item.built_at`, `owed_levels()`. Measured:
**521 items, median 16.8 d since built, 243 built items older than 7 d**. Owed levels: L2 327, L1 134,
L4 110, GREEN-MIN 67, L3 51, GREEN-FULL 7. Decision: this is the biggest number in the ledger. Before
offering new implementation work, `rimflow next` should prefer acceptance work when the backlog passes a
threshold, and L2 should be batched into cold-load runs (one load can pass many L2 criteria). It also
tells the owner whether "built" means anything yet.

**B2. Owner wait (needs=owner age).** Tracks open items whose `needs` is `owner` and how long each has
waited. Source: `needs` events, timeline via `replay(observe=)`. Measured: **48 open, median 3.2 d, 32
older than 3 d, oldest 45 d**. Waits that ended in the window: 70, median 1.6 d. Decision: this is
the BURNING row from Companion. Sort by age, show the due word, and stop agents filing more owner asks
on a subject that already has an old one waiting.

**B3. WIP age (time in current state).** Tracks every open item's age in its present state. Measured:
**doing 124 (median 23.4 d, 106 older than 7 d)**; proposed 720 (median 2.7 d, 252 older than 7 d);
ready 16 (median 17.5 d). Decision: a `doing` item older than a week is almost never being done. Sweep
it back to `ready` or drop it, so "doing" again means someone's hands are on it. FOUNDRY owns 80 of
the 124.

**B4. Lead and cycle time by kind.** Tracks filing to done, and first start to done. Measured: lead
**median 0.04 d (about 1 h), p90 2.4 d, n=1146**. Cycle (only items that were started): median
0.01 d, p90 3.6 d, n=286. By kind: bug median 0.01 d / p90 0.9 d (n=340); build median 1.1 d / p90
4.6 d (n=44); decision p90 39 d. Decision: sets honest expectations per kind ("a build takes about a
day, a decision can sit a month"). It also points at decisions as the slow lane, which is an owner-time
problem and not an agent problem.

**B5. Ceremony skip rate.** Tracks done items that never passed through `doing`. Measured: **751 of
1146 closed straight from `proposed`**, and 189 closed within 5 minutes of being filed. Decision: most
closes are receipts (file-and-close records of work already done). Either make that an explicit verb
(`rimflow did`), so the flow numbers stop counting receipts as throughput, or exclude them from lead
time. Otherwise B4 is mostly a measure of bookkeeping.

**B6. Flow balance (inflow against outflow).** Tracks filed against done + dropped + superseded per
window. Measured: **filed 1887, done 1146, dropped 32, superseded 32: net +677 in 14 days**. Decision:
the queue grows by about 48 items a day. While net is positive, a shift should spend a slice on
triage (drop or merge proposed items older than N days) instead of filing. The number says when to
stop.

**B7. Rework (follow-ups of closed work).** Tracks newly filed items whose `caused_by` points at an item
already `done`. This is the ledger's only reopen signal. Measured: **233 of 1887 filed (12%)** had a
cause that was already closed; 424 had any cause. Decision: per mod or per closing seat, a high share
means "closed too early" (close on a test that cannot fail). That should tighten the close gate for
that area, for example by requiring an L1 criterion.

**B8. Verify outcome mix.** Tracks `verify` results. Measured: **pass 419, partial 102, fail 65**
(11% fail). Decision: a rising fail or partial share on a seat or mod says its `implemented` claims are
optimistic, so more offline proof before calling it built. A zero-fail streak is a beacon to check
that the instrument can still fail.

**B9. Lease churn and lapse.** Tracks lease take/renew/release counts, items re-taken many times, and
open items whose lease lapsed without release. Measured: **take 467, renew 346, release 69**.
**166 open items hold a lapsed lease** (built 77, validated 49, doing 39). Top re-take:
`DIRTY_CODE_REVIEW_STANDING_LOOP_1` 56 times. Decision: release is written about 1 time in 7. A lapsed
lease on an open item is a seat that died mid-work, so these feed straight into B3's sweep. A standing
loop item re-leased 56 times should be a scheduled job, not a ticket.

**B10. Bounce (needs/reassign/retarget churn).** Tracks items moved between seats or needs repeatedly.
Measured: 227 items bounced at least once; **7 bounced 3+ times**, e.g.
`TANK_SOUTH_PORT_REDRAW_STUB_PEEKS_OUT` (4). Decision: a 3+ bounce is an item nobody can do as specified.
Escalate it for a rewrite of the spec, not another reassign.

**B11. Blocked age and blocker fan-in.** Tracks open blocked items, how long, and which blockers hold
the most dependents. Measured: **97 blocked, median 23.4 d**. Top blockers: `SUNSHADE_MIGRATE_MOVE_NOT_CHANGE`
holds 5, `BRIDGE_TPS_REVIEW2_FIXES_1` holds 4. Decision: work a blocker by its fan-in. Clearing one item
that unblocks 5 beats clearing 5 leaves. Show this to `priority.py` as a rank boost.

**B12. Mod heat (ledger and git).** Tracks which mods are being worked on, from item ids and titles
and from commit paths `src/<tier>/<Mod>/`. Measured, git: **FlowWorks 1233 commits**, then SWBestiary
156, UtinniPatches 152, Pyrelands 131, LeaningScrub 118. 108 of 130 mods were touched; **22 were not
touched at all**. Ledger: FlowWorks 310 items, Pyrelands 37, LeaningScrub 36, Contagion 28.
Decision: this is the Companion's ORDERS and GIT ACTIVITY row re-keyed by mod. It shows imbalance at a
glance (FlowWorks takes 21% of all commits). The cold list is the candidate set for "is this mod still
wanted, or is it a consolidation target" (MOD_CONSOLIDATION_PLAN).

**B13. Mapping coverage (instrument).** Tracks the share of items the mod mapper can place. Measured:
**67% unmapped** (1435 of 2150). Subject tokens like PIT (56), GSS (41), ART (40) and TESTENV (34) are
systems, not mods. Decision: either add an optional `mod` field to `file`, or teach the mapper a short
subject table. Until then, B12's ledger half is a lower bound and must say so.

**B14. Seat activity and bridge hold.** Tracks events and active hours per seat, last seen, and bridge
hold time. Measured: BENCH 4186 events over 198 active hours, FOUNDRY 2972 over 155, OWNER 2106 over
208. Bridge held: **BENCH 152.8 h, FOUNDRY 45.5 h, OWNER 12.2 h**. Longest single hold 36.8 h (BENCH).
Decision: a 37-hour hold is a forgotten lock, not a test. Auto-flag any hold over N hours with no bridge
calls, so the other seat stops waiting on a dead lock.

**B15. Cold-load spend.** Tracks game LOADING-to-UP transitions and durations from `game` events.
Measured: **175 loads in 14 days, median 2.0 min, p90 20.6 min, 22.5 h spent loading**, against 190.5
h UP. Decision: the p90 sits near a full-list load (about 25 min) and the median near a minimal-list one. Each full
load avoided is about 20 minutes, so count full-list loads per shift and push batching (one full load
per batch of L2 criteria, B1).

**B16. Provenance mix.** Tracks how filed items were authorised. Measured on 1887 filed: why-only
1388, ownerSaid 257, byCard 132, perRuling 54, **none 56**. Decision: an item with no provenance is
unexplained work. The 56 should be zero (a lint). The ownerSaid share per mod shows which areas the
owner is actually steering, against what agents generate for themselves.

**B17. Note thrash.** Tracks notes per item. Measured: 2020 notes over 863 items. Top:
`DIRTY_CODE_REVIEW_LOOP_CONTINUE_NOT_DONE` 41, `BIOME_SPRINT_PROVE_SCRUB_SETS_PACE` 32. Decision: an
item collecting 30+ notes is a log living inside a ticket. Split it, or move the log to a file and
keep the item for the decision.

**B18. Instrument health (the ledger watching itself).** Tracks replay refusals, tolerated fields,
duplicate lines collapsed, and the age of each collector's last good read. Measured: **10 refusals**, 0
tolerated, 7 duplicates. Decision: a new refusal is a seat writing against the rules, so page that
seat. A collector with no fresh read shows hollow, never zero (§A rule 2).

**B19. Budget pace** (outside the ledger). Tracks plan usage against the weekly allowance. Source:
`src/RimMandrake/Utils/pulse/usage.py`. Measured: `--` (not read here; it reads account tokens, and this
was an offline design pass). Decision: when AHEAD of pace, the shift picks cheaper work (offline L0
items, Sonnet-sized tasks); when BEHIND, it takes the heavy design items.

## C. Architectures

**C1. Derived projection over the ledger (a library plus CLI, no storage).** Each metric is a pure
function of `model.read()` folded once through `replay(observe=)`, the same pattern RimPulse already
uses for "to rule". It lives at `src/RimMandrake/Utils/rimflow_metrics.py`, and later perhaps as
`rimflow stats`.
- *For:* nothing new to keep consistent. Every clone computes the same answer (reader invariant). No
  verb is re-interpreted, so it cannot drift from the projection. A full replay of 28k events plus
  `git log` takes about 4 s wall.
- *Against:* no history of the metric itself. "Was the owner wait better last week" means replaying with
  `now` set to then, which works but costs a replay per point. Inferred fields (mod) stay inferred.

**C2. RimPulse panel fed by C1 (a live glance).** The pulse daemon (5 s loop) calls C1 at a slow
cadence (every 10 min, or on a ledger mtime change) and draws rows on the Companion discipline: unlit
when under threshold, hollow when the collector failed, AS OF on every row, fixed scales. Lives in
`src/RimMandrake/Utils/pulse/` as a new row group.
- *For:* this is where the owner already looks, and B1, B2, B3, B9 and B14 are glance questions ("do I
  have to do anything?").
- *Against:* panel real estate is the scarce resource. Only threshold-crossing metrics earn a lit row,
  and trends (B4, B6, B12) do not read well as a lamp. It adds load to a 5 s daemon unless cached.

**C3. Nightly digest plus time series (memory and trend).** A daily timer runs C1, appends one JSON
line per day to `D:\ClaudeWork\rimmandrake\monitoring\daily.jsonl` (a program reads it, so scratch),
and writes a one-page digest into the existing `pulse since` digest folder. Optionally it exports to the
telemetry store so Grafana draws B4, B6 and B12 as lines.
- *For:* trends and regressions become visible (net flow turning negative, acceptance backlog
  shrinking). It costs nothing at runtime, and the digest feeds the morning brief.
- *Against:* another timer to keep alive (it needs its own BEARING-style "last ran" row). A digest
  nobody reads is decoration, so it must surface only deltas past threshold.

**Recommendation:** C1 now (it is the foundation of the other two), then C2 for the four glance metrics,
then C3 when there is a question that needs a trend. They stack; none of them replaces another.

## D. Recommended first slice, with measured prototype numbers

**Slice: C1, the derived projection.** Built and committed as
`src/RimMandrake/Utils/rimflow_metrics.py`, with `src/RimMandrake/Utils/selftest_rimflow_metrics.py`
(a synthetic 10-event ledger with fixed answers: lead 26 h, cycle 24 h, queue wait 2 h, an open owner
wait of 44 h, a rework follow-up, alias and title mod mapping, `--` for an empty population; GREEN).
The selftest was seen failing once on a wrong expectation (net flow), so its checks can fail.

```
python3 src/RimMandrake/Utils/rimflow_metrics.py [--days 14] [--json] [--no-git]
```

Prototype numbers (14 days to 2026-10-26 18:33Z, full output at
`D:\ClaudeWork\rimmandrake\monitoring\metrics_14d_20261026.txt`):

| Metric | Value |
|---|---|
| Verify backlog | 521 items, median 16.8 d since built |
| Owner wait (open) | 48, median 3.2 d, 32 over 3 d, oldest 45 d |
| Doing older than 7 d | 106 of 124 |
| Open items with lapsed lease | 166 |
| Net flow | +677 (filed 1887, done 1146) |
| Closed without ever starting | 751 of 1146 from `proposed` |
| Rework share | 233 of 1887 filed follow closed work |
| Blocked | 97, median 23.4 d |
| Top mod by commits | FlowWorks 1233 of 5804 |
| Cold mods (no commit) | 22 of 130 |
| Ledger mod mapping | 67% unmapped |
| Cold loads | 175, 22.5 h loading (one-off probe, not yet in the script) |

**Why this slice first.** Four of its numbers are actionable today without any UI: the 106 stale
`doing` items and the 166 lapsed leases (a sweep), the 521-item acceptance backlog (re-weight
`rimflow next`), and the 48 owner waits (the BURNING list). It also exposed two schema gaps, no
`mod` field and receipts that look like throughput, which should be settled before any panel is
drawn on top.

**Owed next (not built here):** move the cold-load probe (B15) into the script; add a `--now` flag so
C3 can backfill a daily series; a RimPulse row group for B1/B2/B3/B9 (C2); decide on an optional
`mod` field on `file` (B13). The two new files are DIRTY under `code_review_status.py` until reviewed.
