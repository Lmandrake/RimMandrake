# RimPulse redesign: what it shows, what you need from it, three better ways (2026-10-23)

FOUNDRY, offline design. No pulse code changed. Asked by the owner on 2026-10-23: *"Document the RimPulse
displays it chooses to show, and then capture all the sorts of ways a user needs to interact with Foundry and
Bench during and after a long development cycle (say overnight). Evaluate what SHOULD be reported on there.
[...] what's on there right now is strange and not useful. And these big glowing red errors are rarely
informative. package all that up and deeply design about it, then propose three better ways."*

**Evidence used** (all measured 2026-10-23 17:30 local):
- live feed `curl http://127.0.0.1:8765/api/now`: 112 rows, deployed code `pulse-deploy` at 3ceaf25
- `~/.local/state/rm-dashboard/metrics.jsonl`: 6618 records, 2026-10-08 20:58 to 2026-10-23 17:30, plus `pulse.py metrics`
- one Windows screenshot of the widget: `D:\ClaudeWork\rimmandrake\pulse_redesign\widget_crop.png`
- the 17:30 scheduled digest: `D:\ClaudeWork\rimmandrake\dashboard\digests\digest_2026-10-23_1730_scheduled.md`
- sources `src/RimMandrake/Utils/pulse/pulse_core.py`, `pulse.py`, `widget/index.html`, `systemd/`
- `design/RimMandrake/delegation_policy.md` §2 and §5; `infrastructure/agents/BENCH.md`, `FOUNDRY.md`

**A ruling this document runs into.** On 2026-10-22 you answered the card *"RimPulse surface: what should it
become?"* with **"Keep widget, fix defects only"**, recorded as *"No beacon, inbox or phone push"*
(`RIMPULSE_SURFACE_DECIDE_BRIEF_OR_BEACON`, closed). Today's request asks for redesigns. Proposals B and C
below reopen parts of that card. Only you can reopen it, so question Q1 asks you to.

---

## 0. The short version

- **What the screen showed at 17:30.** One red row, *"colony loss latched on unnamed row: GameEnder countdown
  started"*, shown twice (as a body row and as a strip pill). One "to rule" row, for a draft that is not ready
  to rule on. "to look at 0". Four folds (answered 1, recovered 1, failed 1, held back 25). Four sparklines.
  About 40% of the panel was empty, and the right edge (the done tally, the last lights) was off the screen.
- **The reds are almost never yours.** Over 15 days there were 119 red openings: 89 from telemetry (47 Windows
  low-memory, 39 *colony dead* and 3 *colonist hostile* on BENCH's throwaway test maps), 21 dead windows and 9 OOM kills.
  Red rows stayed open for a median of **129 s**, so most cleared before anyone could have read them. In 15
  days you never pressed ack or noise once (`pulse.py metrics`: *"alert precision UNMEASURED - no ack from the
  widget (his hand) yet"*). There were also 1416 amber "warn" openings, with a median life of 21 s.
- **What you value is barely there.** Review sheets: the sheet scanner reads only `Transient/biome_ffar`
  (`SHEETS_DIRS`, pulse_core.py:59), so art-eval shadow sheets never appear. Question cards: shown only while
  a window has a card open, and they vanish when that window closes. Rulings: 1 row, and it is premature.
  The audit of what agents decided for you does not exist anywhere: there are 295 delegated-verdict files for today
  and no digest was ever written (filed: `DELEGATED_DIGEST_FIX_NEVER_WRITTEN`).
- **What it lacks.** Anything about *outcomes* in words (it says "✓ 74" and lists item ids). Spend and
  limits. The game and mod-list delta. What will happen next. What you can undo.
- **Recommendation:** **A, "The Morning Paper"**, with C's one-line heartbeat as its live strip. Start by
  deleting the noise inside today's widget, which stays within the 10-22 card.

---

## 1. INVENTORY: every display RimPulse shows

Verdicts: **useful** (supports a decision you make), **noisy** (true but not yours, or too frequent to
read), **misleading** (suggests something false, or suggests you must act when you need not).

### 1a. Title bar (widget top)

| Display | Source / rule | Verdict | Evidence |
|---|---|---|---|
| `RimPulse` mark + ⟳ refresh | forces a re-collect (`pulse.py refresh`) | noisy | the daemon re-collects every few seconds anyway |
| Source lights: sessions, agents, ledger, hands, sheets, ... | `snap.sources[n].ok/stale` per collector | noisy | all green at 17:30; they fill the bar and push the window off-screen (screenshot) |
| freshness `connecting / Ns` | age of the last SSE message | useful only when bad | it matters only when it is stale |
| ‖ motion, ▾ collapse | local preferences | neutral | - |

### 1b. Body sections, top to bottom (`index.html` `render()`, lines 288-322)

| # | Display | Source and the rule that makes it appear | Verdict | Live evidence |
|---|---|---|---|---|
| 1 | **Red rows** ✖ + ack/noise buttons | every unacked `kind=red` row (sources in §1d) | **misleading** | the one red at 17:30 was a test map's colony loss, `recovery unknown`; you could do nothing about it |
| 2 | **to rule** section: seat asks (amber) | `~/.claude/sessions/<pid>.json` status=waiting plus the transcript's last AskUserQuestion; BENCH/FOUNDRY only | useful | a live card is the only truly blocking thing; none were up at 17:30 |
| 2b | **to rule**: "finished, idle, waiting for you" (amber_soft) | seat idle ≥60 s, no subagents, <2 h | misleading overnight | 197 openings in 15 d; an idle FOUNDRY is a stalled belt, not a request |
| 2c | **to rule**: ledger rulings | rimflow replay: open, needs=owner, not blocked, class `rule` (`owner_rulings`, `ask_class_raw`), under 14 days | useful in principle, wrong in practice | 1 row: `WATER_SCENES_S5_JUDGE_THIRD_DRAFT`, linked to a spec `.md`; BENCH plans to offer it "with the north-star sitting after the walk", and FOUNDRY noted it as premature. So 0 rulings you can actually make |
| 2d | "older (N)" fold | asks older than 3 days | noisy | it folded the only row, so the section read "to rule 1 / older (1)" |
| 3 | **to provide** | needs=owner and the text matches `_PROVIDE_RE` (address, password, host...) | useful, rare | absent at 17:30 |
| 4 | **to look at** | (a) `pulse.py hand` records that have `--read-by`; (b) `biome_ffar` sheets that have a valid `.prereview.json`; (c) ledger looks that link to an artifact (never `.md`, never a commit, never a live walk) | **useful, the thing you value**, but starved | "0 · nothing waiting" while 25 items sat held back and the art-eval shadow sheets were invisible |
| 4b | "Biome sheets: N" group | sheets with the same group label | useful | - |
| 5 | answered, agent to follow up (N) | your card or words landed after the ask, but `needs` is still owner | noisy | 1 row (`ART_EVAL_PIPELINE_BUILD_OPUS_GRADES_FIRST`): an agent's debt, not yours |
| 6 | telemetry / WSL warn rows ◆ | telemetryd amber alerts; telemetry stale >5 min; WSL restarted, with a list of the windows that ended with it | noisy, except the WSL line | 1416 warn openings, median 21 s; tel:vitals alone opened 932 times |
| 7 | recovered (N) | a red with recovery evidence (`track_incidents`) or a job that failed and then passed | noisy | `build:RimMandrake_FlowWorks failed (winbuild exit 23) · recovered: passed 07:43`, which is ordinary agent iteration |
| 8 | failed, not blocking (N) | `failures.jsonl` streak without blocks/lost; artpipe `failed/` count | noisy | `artpipe · 1020 jobs in failed/ · not blocking` |
| 9 | held back, not pre-read (N) | hands with no `read_by`; sheets with no prereview record | **misleading** | 25 rows: 13 hands from as early as 10-15, 12 sheets from 10-17 to 10-22. This is the agents' backlog; you cannot act on any of it |
| 10 | acknowledged (N) | acked alarms | noisy | 17 acks, all made by agents or the CLI |
| 11 | Sparklines: tps×, exc/s, mem GB, disk GB | telemetry `sparks`, last 2 h | noisy | `tps× –  exc/s –` (the game was on the world screen); mem 23, disk 1950. Grafana already shows these |

### 1c. Collapsed strip (`build_strip`, `build_chips`, `renderStrip`)

| Display | Rule | Verdict | Evidence |
|---|---|---|---|
| `✖ monitor down` / `◌ stale` / `◌ blind: x` | widget lost SSE / snapshot >20 s old / a collector failing | useful when true (you cannot trust anything else) | none at 17:30 |
| red pills `✖ <cause> · hh:mm` | each unacked red | misleading | `✖ colony loss latched on unnamed row: Gam… · 17:25`, truncated before the noun that matters |
| amber `◐ SEAT question` | a seat's card is up | useful | - |
| `◑ SEAT finished · idle` | amber_soft | misleading (see 2b) | - |
| `◆ warn` pills | telemetry/WSL warn | noisy | - |
| `↺ N recovered` | recovered non-job reds | noisy | - |
| `◇ N to rule`, `✎ N to provide`, `▣ N to look at` | counts of 2c/3/4 | **useful**, and these counts are the point | `◇ 1 to rule` (premature) |
| `✓ 74` done tally → opens the digest | ledger close/implemented/verify-pass since the last digest | misleading | 74 = 33 implemented + 32 *verified criterion* + 9 closed; 64 BENCH, 7 FOUNDRY, 3 OWNER-seat. It counts events, not finished things |
| chips: `bench`, `foundry` (state + agent count) | sessions + subagents; always present (missing/unknown when absent) | useful | `foundry run 2`, `bench run 2` |
| chips: `rimworld` (UP/down/unprobed · bridge holder), `artpipe` | probe/BRIDGE; artpipe counts | rimworld useful at desk; artpipe noisy | `artpipe · 6 active · 24 queued · 17411 done · 1020 failed` |
| chip `mem` | red if an unacked kernel/memwatch OOM | noisy | duplicates the red pill |
| dim chip `phone · emerg · hestia` | idle non-seat windows | noisy | - |

### 1d. Every red source, and what you could actually DO about it

| Red source (code) | 15-day count | Typical life | What you could do |
|---|---|---|---|
| telemetry `mem_low` (Windows free RAM) | 47 | minutes | Nothing overnight. At the desk: close a program. Agents cause and relieve it; they should handle it |
| telemetry `vitals:colony_dead` / `colonist_hostile` | 39 / 3 | seconds to minutes | **Nothing.** These are BENCH's throwaway test colonies dying as tests do. The word "colony" reads like your campaign. Red only if it is your own play session |
| session `lost:` (window process died, session file left behind) | 21 | until replaced | Reopen a **seat** with `claude --resume`. That is a real action, but only for BENCH/FOUNDRY, and only if no agent restarts it. For other windows: nothing |
| kernel OOM `oom:seat:*` (seat window or tool cgroup) | 9 | auto-recovers in ~10 min | Usually nothing: the agent retries. It is yours only if the seat stayed dead (that becomes `lost`) |
| kernel OOM `oom:svc:rm-pulse` | rare | systemd restarts it | Nothing. If it stays down, the widget's own `monitor down` already says so |
| failures `lost` (a scheduled digest never written) | 0 live | - | Nothing you do yourself; a seat reruns it. You need it only so you know the morning read is missing |
| failures `blocks` >15 min (a required build/job stuck) | 0 live | - | Tell a seat to look, which an agent should do anyway |
| widget `monitor down` / `stale` | - | - | **Real:** restart WSL or the `rm-pulse` service. It is the one red that is both yours and true |

Conclusion: of eight red sources, **one** (monitor down) is reliably something you act on, **one** (a seat
that died and stayed dead) is sometimes yours, and six are agent or machine events that resolve themselves.
The current rule makes a row red when *something bad happened*. The rule should be: red when *you must act
and the work waits until you do*.

### 1e. Outside the widget

| Channel | Rule | Verdict |
|---|---|---|
| Windows toasts | every red without `toasted_elsewhere`, every seat amber | noisy (same reds) |
| Digest `.md`, 06:00 and 17:30 (`rm-pulse-digest.timer`) | sections What broke / Needs your verdict or a fact / To look at / Done | the right idea; its content repeats the widget's noise (17:30: "What broke: 3", all three not yours; "Done: 74" as 74 id lines) |
| Phone push | `PHONE_PUSH_ENABLED = False` (pulse.py:71), *"NOT decided by the owner"*; the 10-22 card said no push | none exists. Whatever you see on your phone today does not come from RimPulse |
| Health timer (10 min), update timer (2 min) | daemon self-checks | invisible to you; fine |

---

## 2. INTERACTIONS: what you need from FOUNDRY and BENCH, by moment

The seats: **FOUNDRY** runs the queue on its own and never asks; it files `needs owner`. **BENCH** sits
with you and owns all FlowWorks + GSS; it asks cards when you are present. Agents decide nearly everything
(delegation_policy.md). What is still yours (§2): north-star bars and L4 criteria, irreversible acts on others'
work, replacing art you kept, overturning a standing ruling, outward or paid acts, presence-bound acts
(flyer flight, `./bridge`, broadcast).

### M1. Mid-night glance at the phone (5 seconds, half-asleep)

| Need | Question in your words | Answer today? |
|---|---|---|
| Alive | "Is it still running?" | partly (seat chips), Windows only |
| Making progress | "Is it doing anything, or did the belt stop?" | no: idle shows as "waiting for you", stuck is dim |
| Must I get up | "Is anything burning that only I can stop?" (runaway spend, disk filling, WSL wedged) | no: reds are mostly test maps |
| Can I unblock it now | "Is a seat stuck on a card I could answer from bed?" | partly, while the card's window is open |
| Permission to sleep | "Nothing needs you before morning." | never said explicitly |

### M2. Wake-up morning read (5-15 minutes, phone or desk)

| Need | Decision it supports |
|---|---|
| **What finished, in words**, grouped by mod or goal ("FlowWorks: pit rescue fixed, ladders lean right") | what to play or test today |
| **What is waiting on your word**: real rulings, each as a card with options | answer now vs. at a sitting |
| **What is for you to open**: pre-judged sheets, images, pages, each with size and time ("Fauna shadow sheet, 21 rows, ~5 min") | when to sit and in what order |
| **What agents decided for you**: delegated calls, and any *replaced your kept art* | overturn or let stand |
| **What broke and is still broken, and is yours** | act, or accept the seat's plan |
| **What changed in the game**: deploys, mods added or removed, ModsConfig delta, "next load will show X" | whether to load, what to expect |
| **Spend and limits**: plan usage window used, GPT/image spend, near-limit | throttle, or let it run tonight |
| **What happens next**: the queue for today, what waits on what | redirect priorities |
| **What can be undone**: reverts available (art ledger, delegated calls) | undo cheaply |
| **What must be restarted**: dead seats, WSL restarted, a service down | restart |

### M3. Mid-day check-in (at the desk, maybe playing)

| Need | Decision |
|---|---|
| Who holds the bridge, and is the running game theirs or yours | can I play now |
| What each seat is on right now (item, in words) | interrupt or not |
| Cards up right now | answer |
| What is ready for a sitting (rulings + looks, total time) | schedule the sitting |
| Am I near a limit | slow down |

### M4. Return after days away

| Need | Decision |
|---|---|
| The arc: which goals moved (V1 rows, epics), which stalled and why | re-prioritise |
| Rulings, ranked by what they block, aged | which three to answer first |
| Delegated calls rolled up by class | audit the classes, not the instances |
| Standing problems that persisted for days (artpipe 1020 failed, a seat dead) | escalate or fix |
| Spend across the absence | budget |
| A "start here" order | where to begin |

### What you do back (the verbs)

Answer a card · open an artifact and rule on its rows · give a fact · overturn a delegated call · revert a
replaced kept picture · restart a seat, WSL or a service · hand the bridge / take the game · pause or stop the
run · re-prioritise the queue · approve spend or an outward act. A display entry earns its place only if it
leads to one of these verbs, or confirms that none is needed.

---

## 3. EVALUATION: what SHOULD be reported, ranked

| Rank | Report | Decision it supports | Source exists? |
|---|---|---|---|
| 1 | **Waiting on your word**: count, oldest, *what it blocks*, each a card with options | answer now / at the sitting | ledger needs=owner + live cards; the options are usually missing (prose `reason`) |
| 2 | **For you to open**: pre-judged artifacts, with row count and estimated minutes | when to sit | hands + prereview; scanner blind outside `biome_ffar` |
| 3 | **Run health in one sentence**: "2 seats working, belt full" / "FOUNDRY idle since 02:14, queue not empty" / "WSL restarted 03:10, seats not reopened" | sleep / get up / restart | sessions + ledger `next` |
| 4 | **Outcomes in words**, grouped by goal, with "playable now" | what to play or test | ledger titles + deploy log; needs a writer |
| 5 | **Decided for you**: delegated calls, kept-art replacements, with overturn/revert links | audit | `infrastructure/state/delegated/`, art ledger; **digest never written** |
| 6 | **Still broken and yours**: only items whose fix is one of your verbs | act | incidents, filtered by action |
| 7 | **Game and mod-list delta** since you last loaded; bridge holder | load / play | deploy logs, ModsConfig parse, BRIDGE |
| 8 | **Spend and limits** | throttle | **not measured anywhere today** (needs a source) |
| 9 | **Next**: today's queue head per seat | redirect | `rimflow next` / queue projections |
| 10 | **Undo handles** | undo | art ledger reverts, delegated records |

**Remove from your view** (they move to an agent-facing page, or only to the digest's appendix):
- every telemetry red and warn about test maps, and mem_low; Grafana keeps them (1416 warns + 89 reds in 15 days, none yours)
- `recovered`, `failed, not blocking`, the artpipe totals (`17411 done · 1020 failed`): agent iteration
- `held back, not pre-read (25)`: agent backlog; the agents owe pre-reads or withdrawals, and an agent sweep should get them
- `answered, agent to follow up`: agent debt; show it only if it ages past a day
- `✓ 74` as an event count, and done rows as item ids: replace with outcomes (rank 4)
- sparklines, source lights (show them only when blind), the `mem` chip, the dim idle-window chip, `memory pen proven`
- the red shown twice (row + pill); the "older (1)" fold when there is a single row
- "finished, idle, waiting for you" as a request: it becomes health line 3 ("belt stopped")

---

## 4. THREE DISTINCT REDESIGNS

The mocks are illustrative: their rows, percentages and dollar figures are invented to show the layout, not measured.

They differ in **what the surface is made of**: A is a composed *document*, B is a list of *actions*,
C is a picture of the *run over time*.

### A. "The Morning Paper": a pre-read brief, plus a heartbeat

A seat composes one brief at fixed times (05:30, 12:00, or when you ask) from the ledger, delegated
verdicts, art ledger, deploy log and git log. A second agent reads it before it is listed (nothing reaches
you unread). The widget and phone show the brief's front page and a one-line heartbeat. Between briefs only
the heartbeat changes.

```
+-- RimPulse ------------------------------- 06:00 brief, read by FOUNDRY-judge ----+
| ● running · bench 2 agents · foundry 2 agents · nothing needs you before 09:00  |
|---------------------------------------------------------------------------------|
| NEEDS YOUR WORD (2)                                          ~4 min             |
|  1 FlowWorks bars: accept the five rebuilt bars?   [Yes] [Show me] [Not yet]   |
|  2 Rot names: 14 picked, 3 contested               [open card]                 |
| OPEN THESE (2)                                               ~12 min            |
|  ▣ Fauna shadow sheet: 21 rows, 8 kept / 13 redrawn, 2 replaced YOUR kept art   |
|  ▣ Bridge redraws: old vs new, 6 images                                         |
| OVERNIGHT, IN WORDS                                                             |
|  FlowWorks: pit rescue works again; ladders lean the right way; water stubs ok  |
|  Fauna: Contagion round 1 judged, nothing installed yet                         |
|  Game: FlowWorks deployed 07:43; next load adds 0 mods, changes 1               |
| DECIDED FOR YOU (295, 6 classes)  ·  overturn ↗   UNDO: 2 kept-art swaps ↗      |
| SPEND  plan window 62% · GPT images $4.10          NEXT  BENCH: hose reel ...   |
+---------------------------------------------------------------------------------+
```

- **Data:** ledger (needs=owner, close/implemented with titles), `infrastructure/state/delegated/`, art ledger,
  deploy logs, ModsConfig parse, sessions (heartbeat), a new spend source.
- **Red is earned only** in the heartbeat, and only as one of: *"run stopped: no seat working, queue not empty,
  for 30 min"* (restart), *"monitor down"* (restart WSL/service), *"a card blocks a seat"* (answer). The brief
  itself has no red.
- **Failure modes:** the brief is stale when its writer dies (show its age in large type; a missed brief is
  the heartbeat's red). Agent prose can overclaim "works again" (the pre-read judge checks each sentence
  against a ledger verify event). Real-time items wait for the next brief, so live cards still come through
  the heartbeat.
- **Build cost:** medium, about 3 items. Composer + judge step (deterministic sections, with LLM only for the
  "in words" lines), the delegated digest (owed anyway), a spend source. The widget shrinks: heartbeat line +
  brief view.

### B. "The Decision Inbox": only things you can act on, each with its button

The surface is a queue of actions. An entry exists only if one of your verbs applies, and it carries that
verb as a button: answer (card options shown inline), open, overturn, revert, restart, take the game.
Everything else is one line: "all running, nothing for you". Inbox zero is the goal and the reward.

```
+-- RimPulse inbox ------------------------------------------- 3 for you · 0 urgent -+
| RULE   FlowWorks bars: accept the five rebuilt bars?      blocks 4 items  2 d    |
|        ( Yes )  ( Yes, but redo bar 3 )  ( No, explain )  ( later )             |
| OPEN   Fauna shadow sheet · 21 rows · ~5 min              [open ↗]   since 05:10  |
| UNDO?  Pipeline replaced 2 pictures you kept              [review] [revert both]  |
|---------------------------------------------------------------------------------|
| ✓ all running · bench 2 · foundry 2 · game: BENCH's test map (not yours)          |
| history ▸ (what happened overnight lives in the digest)                         |
+---------------------------------------------------------------------------------+
```

- **Data:** ledger needs=owner with a **structured card payload** (question, 2-4 options, trade-offs) on the
  `needs` event; prereviewed hands/sheets from every sheet directory, not only `biome_ffar`; art-ledger
  kept-art swaps; sessions for restart entries.
- **Red is earned** when an entry blocks work and has waited past a threshold you set (for example 12 h), or is
  a restart that no agent can do. Red means "this inbox item is now costing progress."
- **Failure modes:** a button that answers a card writes owner authority (`--by-card`) from a web page, so
  the widget becomes a writer of your rulings. It must be your hand only (auth, no agent can POST). Most
  current `needs owner` events are prose with no options, so agents must re-ask in card form or the inbox stays
  empty. It contradicts the 10-22 card ("no inbox"). Overnight outcomes leave the surface entirely.
- **Build cost:** high, about 5 items. A card schema on `needs`, a rimflow verb to answer by card from the API,
  local auth for the widget's POST, a sheet scanner across all sheet roots, and an agent migration of open asks.

### C. "The Night Watch": the run as a timeline since you left

The surface is a timeline from your last prompt to now. Each seat is a swimlane (working / idle / stuck /
dead), with milestones on it (deploys, items closed per goal, game loads, cards asked), a spend bar and one
status sentence. At night it answers "is it alive and moving". In the morning the timeline *is* the report:
tap a segment to see what happened in it.

```
+-- RimPulse · since you left 23:40 (6h 20m) -------------------------------------+
| Running fine. Nothing needs you. Next sitting: 2 rulings, 2 sheets (~16 min).   |
|        00     01     02     03     04     05     06                             |
| BENCH  ██████████████████▒▒▒▒████████████████████  ◆deploy 01:12 ◆deploy 04:50 |
| FOUND  ████████████░░░░░░░░░░░██████████████████   idle 01:50-03:40 (queue had 3)|
| GAME   ▓▓ test map ▓▓▓▓▓▓▓▓ ×colony died 02:31 (test) ▓▓▓▓▓▓▓▓                   |
| SPEND  ▁▂▃▃▄▅▅▆▆▇  plan window 62% · resets 09:00                                |
| DONE   FlowWorks 9 · Fauna 4 · Pulse 3      ASKED  2 cards (03:12, 05:40)        |
+---------------------------------------------------------------------------------+
```

- **Data:** the session history pulse already keeps (`pulse.jsonl`, 2 MB), the alarm open/close events in
  `metrics.jsonl`, ledger timestamps grouped by goal, deploy logs, telemetry, a spend source.
- **Red is earned** by *projection*, not by events: "the run stopped and the queue is not empty" (restart),
  "at this rate the plan limit runs out at 03:00, before the queue empties" (throttle or accept), "disk fills
  before morning" (free space). Each red names its verb and its deadline.
- **Failure modes:** a timeline is dense on a phone (the top sentence must carry it alone). Without a spend
  source the projections are guesses (show "unmeasured", never a number). It explains the run well, but you
  still need a separate list of what to rule and open (the sentence only counts them). Test-map events must be
  labelled as tests in the GAME lane.
- **Build cost:** medium, about 3 items. Lane builder from existing history, goal grouping (ledger `row` or
  `caused_by`), a spend source, a projection rule. The widget's body becomes the chart; the strip becomes the
  sentence.

### Side by side

| | A Morning Paper | B Decision Inbox | C Night Watch |
|---|---|---|---|
| Surface is | a pre-read document | a list of actions | a timeline |
| Best moment | M2 wake-up, M4 return | M3 mid-day, M2 | M1 mid-night, M4 |
| Red means | run stopped / monitor down / card blocks | your item is costing progress | a projected failure before morning |
| Contradicts 10-22 card | narrows the widget | yes ("no inbox") | narrows the widget |
| Biggest risk | prose overclaim, staleness | widget writes your rulings | dense on phone, no rule list |
| Build | ~3 items, medium | ~5 items, high | ~3 items, medium |

---

## 5. RECOMMENDATION

**A, with C's top sentence as its heartbeat**, delivered in three steps:

1. **Now, inside the 10-22 card (defects only).** Remove the §3 "remove" list from your view. Make red mean
   "your verb, and work waits on it" (§1d: monitor down, seat dead and not replaced, a card blocking a seat).
   Point the sheet scanner at every sheet root. Turn "finished, idle" into a health line. Retire `✓ 74`.
   Cheap, mostly deletions, and it removes the red errors you object to.
2. **The brief** (A): composer + pre-read judge + the delegated digest (already owed, now filed as
   `DELEGATED_DIGEST_FIX_NEVER_WRITTEN`), at your chosen wake time.
3. **Later, if you want it:** B's answer-buttons only for cards that carry a structured option list, after the
   widget can prove a POST came from your hand.

Why not B first: it needs every agent to re-ask in card form and makes the widget write your rulings. Why
not C alone: it shows the night well but does not tell you what to rule or open.

### Open questions only you can answer (each becomes a question card)

**Q1. Reopen the 10-22 "keep widget, fix defects only" card?**
- *Defects only*: do step 1 above and nothing else. Cheapest; the surface keeps today's shape.
- *Morning Paper (A)*: the widget becomes heartbeat + brief. It narrows the widget, which the card forbade.
- *Decision Inbox (B)*: actions with buttons. Reverses "no inbox"; the largest build.
- *Night Watch (C)*: timeline since you left. Narrows the widget; best for the mid-night glance.

**Q2. Overnight, should anything reach you before you wake?**
- *Never*: silent until morning; the morning read covers everything. Risk: a stopped run wastes the night.
- *Only if the whole run stopped* (no seat working, queue not empty, 30 min). A rare, real wake-up.
- *Also when a seat's card blocks work.* More pings, but you can unblock from bed.
(Any push to the phone reverses the 10-22 "no phone push"; nothing pushes today.)

**Q3. Where do you do the wake-up read?**
- *Phone* (needs a phone-reachable page; how your phone reaches the widget today is not known to us).
- *Windows widget at the desk*: works today; nothing new to reach.
- *Ask BENCH in chat* ("brief me"): BENCH reads the brief to you; nothing new to build for the phone.
- *A digest file* you open: exists today (06:00 / 17:30), but it repeats the noise.

**Q4. Test-map and machine alarms (colony dead, colonist hostile, Windows low memory):**
- *Remove from RimPulse*; Grafana keeps them. You will not see them at all.
- *Show only when the running game is your own play session*, not a BENCH or FOUNDRY test.
- *Keep, but amber and folded.* Visible on request, never red.

**Q5. "Done overnight": how should it read?**
- *Outcomes in words, by goal*, written by an agent and checked by another against the ledger. Readable; costs a
  judge pass.
- *Counts per goal* ("FlowWorks 9 · Fauna 4"): cheap and exact, but tells you little.
- *Item list as now* (74 ids): exact, unreadable.

**Q6. Spend and limits: which should it show?**
- *Claude plan usage* (window used, reset time): decides whether tonight's belt can stay full.
- *GPT / image spend in dollars*: the art pipeline is the paid part.
- *Both.*
- *Neither*: you check them yourself.
(No source for either exists in pulse today. Whichever you pick needs a measured source first, never an estimate.)
