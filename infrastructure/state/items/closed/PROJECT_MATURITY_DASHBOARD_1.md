## 🔴 THE CONSTRAINT THAT OUTRANKS EVERY DESIGN CHOICE BELOW

**Owner, 2026-09-07, verbatim:**
> *"we CANNOT revert to spending ALL of our time chasing down every little
> confirmation rather than developing (this happened in the early project). So the
> 'proof' should be the lightest proof possible (did it load without errors and do
> anything? Then it's implemented but not fully checked out). We must keep moving.
> Full validation comes only at the last step and with the decision to do so...
> I need verification you understand here and don't build a horrible hook-laden
> chain that grinds us to a halt and burns all my tokens 'verifying' things at
> every check-in."*

⛔ **NO HOOKS. NONE.** No `PreToolUse` gate, no commit gate, no per-ticket
verification, nothing that intercepts ordinary work. **The dashboard READS state;
it never blocks it.**
🔑 **Verification rides a load we are already paying for, or it waits for a
campaign the owner chooses to spend. It is never its own errand.**
⚠️ **If a future agent "improves" this by adding a hook or a mandatory check, that
is a REGRESSION against an explicit owner ruling — revert it.**

---

## why this exists

Owner, 2026-09-07: *"We have been fairly undisciplined in terms of adding new
content, new mods, changing deployment schedules... so much so we rarely see a
ticket close confirmed live and good. And that's ok when we're world building.
That era is finally wrapping up."*

**The goal: the first honest answer to "how close are we to delivery", by item
count — and, when something breaks, a visible regression in the number.**

⭐ Tickets are the small unit. **This is project tracking of the MAJOR efforts**,
at capability level. The clean/dirty code sheet becomes **one small readout on
this dashboard**, not its parent.

## ruled 2026-09-07

### 1. TWO SPINES, ONE DASHBOARD
They answer different questions and must not be forced onto one axis.

- **SYSTEMS** — mods and capabilities: pits, ocean biomes, trenches, water types,
  droids, cuisine, reset tenders, the Rust Cathedral kit, … Tracked on the
  maturity grid below.
- **CONTENT** — the world inventory **already written in
  `infrastructure/state/GOAL_SHEET.md`** (10 sections: planet, factions,
  religion, pawns, items, creatures, the start, events, presentation, the last
  mile). ⚠️ **Do NOT invent a parallel inventory — GOAL_SHEET is it.** What it
  lacks is only that its boxes are binary and hand-ticked, so it can never
  express "how close".

One page, both spines, one headline number with its weighting stated on the page.

### 2. TWO AXES PER SYSTEM, NOT ONE LADDER

| | |
|---|---|
| **FUNCTION** | `planned → designed → implemented → runnable → checked-out` |
| **CONTENT** | `none → placeholder → authored → final` |

A system is **done** only at top-right. This keeps the coming art/normalization
wave visible as movement on its own axis without touching function, and stops a
working-but-unarted system reading the same as an arted-but-broken one.

### 3. RIMFLOW OWNS THE DATA; RENDER AN ARTIFACT

- A capability registry written **only through rimflow** (never hand-edited),
  with history from `events.jsonl` — which is what makes **regression** visible.
- Rendered to a published dashboard, the way `codebase_health` already renders
  (`Transient/codebase_health_artifact.html` is the working model).
- ⛔ **GitHub Projects was considered and NOT chosen** as the primary: it cannot
  compute a rung from a live game test, its historical charts are weak (regression
  is the thing it does worst), and making it authoritative would need two-way sync
  against a ledger that deliberately never reads back. The existing one-way issue
  mirror stays as it is. *(A later one-way push of the ladder as a GH custom field
  remains possible; not now.)*

### 4. EVIDENCE — LIGHTEST POSSIBLE, AND FRONT-LOADED NOWHERE

| rung | what it costs |
|---|---|
| `planned`, `designed`, `implemented` | **self-declared. Zero friction, no evidence, no ceremony.** |
| `runnable` | **the lightest proof there is** — it loaded without errors and did something. Falls out of `harvest_log.py` on a load we were already paying for. **No new load, no new work.** |
| `checked-out` | the expensive rung. **Entered ONLY by the owner's decision, in deliberate batches** — see `MINIMAL_LIST_MOD_RETROSPECTIVE_1`. Never demanded at check-in. |

⭐ **INCIDENTAL EVIDENCE COUNTS — owner, 2026-09-07:** *"every time we see some
content work in a game, that counts too, even if it wasn't intended for one item
or another's verification."* **Any observation may promote a rung, whether or not
anyone set out to test that thing.** A screenshot, a log line, a play session, a
pass done for another item — all bankable. 🔑 **This inverts the economics: we
HARVEST evidence we already got, rather than SPENDING time to produce it.**
*(Worked example: the 2026-09-07 worldmap session incidentally proved the three
seas exist, the rivers laid, a colony generated and a pawn spawned — none of it a
verification errand.)*

⭐ **AND CHEAP INSTRUMENTS ARE WELCOME — same ruling:** *"we shouldn't shy away
from building verification instruments that run cheaply and easily to keep honest
with ourselves."* The ban is on **ceremony**, not on measurement. An instrument
that runs in seconds and answers honestly REDUCES cost — `harvest_log.py` already
does this on every load for free. Build those freely; just never make one a
prerequisite for stating a number.

✅ Where an instrument already exists and is free, use it. Where it does not,
a dated sighting is enough. **Never build an instrument as a prerequisite for
saying a number.**

## design notes for the build

- Registry schema stays **generic** (system, axis, rung, evidence-ref, date) —
  the owner may reuse this at work, so nothing RimWorld-specific in the schema or
  the renderer.
- Headline: item counts per rung on both axes, plus % — and **show raw counts
  beside every %**, because a percentage over ~40 capabilities moves misleadingly.
- Regression view: rung-over-time from `events.jsonl`, so a drop is visible.
- The clean/dirty sheet is **one tile** on the page.

## open, and deliberately not blocking
Weighting for the headline number (equal-weight per capability by default, stated
on the page). The owner can retune once he sees real numbers.
