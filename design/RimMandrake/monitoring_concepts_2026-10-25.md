# RimMandrake monitoring concepts (2026-10-25)

Status: SKELETON — being filled section by section.

Owner ask (verbatim): "consider the magnificent Lodestar Companion for things we might want to monitor on this system too. Then do several suggestions for an improved monitoring system, given Rimflow runs this system rather than Lodestar. Ticket monitoring, understanding which mods are being worked on, let's see many concepts on what we might actually benefit from tracking not just for fun but to inspire different choices and logic."

## 0. Data census (what exists today, measured)
PENDING

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
PENDING

## C. Architectures
PENDING

## D. Recommended first slice, with measured prototype numbers
PENDING

## Progress (helper memory; removed at the end)
- A done. Ledger census: 15768 shard events (+10890 frozen events.jsonl), keys/ops in scratchpad census.txt
- use model.replay(observe=) for item timelines; next: metrics script (lead/cycle, WIP age, owner wait, leases, mod heat, verify, rework)
