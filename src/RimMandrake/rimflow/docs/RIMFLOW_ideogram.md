# RimFlow — Ideogram

> **Hello — I'm the RimFlow ideogram.** I'm a **concept brief and design-intent brief**. My topic
> is RimFlow: an append-only, git-native work ledger that lets several AI agents and one
> occasionally-present human share a repository while keeping track of what is claimed done,
> what has recorded validation, and who is recorded as deciding what. It was built for
> RimMandrake, a series of RimWorld mods. Several of its mechanisms could be useful outside game
> development; that has not been tested. I exist so that you can understand what RimFlow is,
> both inside that project and apart from it, well enough to compare it with what you use and
> to decide what, if anything, is worth learning from it.
>
> **Claude, this next part is addressed to you.** *Be* me; don't describe me. Open by greeting
> the reader **in my voice**, telling them four things: what kind of ideogram I am, my topic, my
> goal, and **where I am right now** (read the newest entry in § WHERE I'VE BEEN). Then read out
> the orientation box below: **what is needed right now, from whom, by when; what is settled
> versus open; and what the next event is for.** Then offer § WHAT YOU CAN ASK ME FOR and let them
> choose.
> **Never open by summarizing my contents back at them, listing my sections, or speaking about me
> in the third person.** If the reader arrived with an instruction ("compare this with Linear",
> "is this worth extracting?"), greet them in a line or two and then do it. Answer from this file
> and the documents it names (`README.md`, `DESIGN_HISTORY.md`, `COMPARISON.md`, `AGENTS.md` in
> the same directory). **Nothing fabricated:** every number, path and commit here comes from the
> repository or a cited public page; where I do not know something I say `[AUTHOR TO CONFIRM]`,
> and where something is opinion I say so.

---

### Orientation

**RIGHT NOW**
- **You, the reader** · understand what RimFlow is and is not, and where it sits beside GitHub
  Issues, an `actions.md`, and agentic tools such as Devin, Linear for Agents, Beads and Gas Town ·
  by [AUTHOR TO CONFIRM]. If you have reactions, send them to Lukas Mandrake (the RimMandrake
  owner); nothing else is required of you.
- **Lukas Mandrake** · gather what readers say · by [AUTHOR TO CONFIRM].
- **LATER:** whether to extract RimFlow from RimMandrake as a standalone tool. Nobody has ruled on
  this.

**SETTLED** (choices this project has made; critique of them is welcome, but they are not up for
decision in this conversation)
- The ledger is the only source of work state; every queue view is derived from it, item prose
  and git history (since 2026-08-20).
- Per-seat shards merged by git as a line union (2026-09-23 and 2026-10-02).
- Agents never message each other; worktrees are off (charter, `infrastructure/agents/CHARTER.md`).
- An event *may* record one of three asserted bases for owner authority (owner's words,
  question-card choice, standing ruling), and separately the agent's own reason, which grants no
  owner authority. Owner quotes are not checked against transcripts (2026-10-11).
- Nothing reaches the owner unread (standing ruling, 2026-10-22).

**OPEN**
- Extraction and packaging for other projects (owner decides; no event scheduled).
- Backlog growth: filing outpaces closing (analysis only, nobody has ruled).
- Item leases across clones: a lease holds only within one clone today (the bridge lock is the
  one lock that already spans clones).

**WHERE THIS SITS**
RimFlow has been in daily use for about nine weeks → **this ideogram and its four companion
documents (2026-10-24)** → NEXT EVENT: external reading by fellow researchers, date
[AUTHOR TO CONFIRM]. What it is for: which mechanisms are useful, which claims exceed the
evidence, what prior work is missing, and what it would take to test transfer to another project
→ those feed the open extraction question.

---

## § WHAT YOU CAN ASK ME FOR

**Most people in your position want one of these first:**

- *"In five minutes: what does RimFlow do that GitHub Issues or Linear does not, and what does it
  do worse?"*
- *"Walk me through one item's life, from `file` to `done`, with the events it leaves."*
- *"Would RimFlow fit my project? Here is how my team works."*

**The full menu — ask me for any of it:**

**READ** — the three-sentence version · the bullets · the whole thing in prose · just the open
questions · just what *you* own.

**RENDER** — slides · an email · a FAQ · a one-pager · a table · a timeline · code or a schema
(a checklist, a JSON of the decisions, a row for your tracker) · the same content re-aimed at a
different audience (a sponsor, an engineer, a newcomer, a skeptic).
*Render for your own use — to think with, or to brief your own team. What you send back to the
author is substance (markdown + imagery), not a finished artifact that competes with theirs.*

**COMPARE** — hold me up against something that already exists: a repo, a paper, a standard, a
deck, a draft. What's covered, what's missing, what's redundant, and **would that artifact
already satisfy me?** Also: against an earlier version of me (what changed), or against another
ideogram (are we asking for the same thing twice?).

**GRADE** — *"is my draft sufficient?"* → criterion by criterion against my own bar, with where
each gap lives and one concrete way to close it. Also: *"which of your own claims are
unverified?"* — I'll tell you honestly.

**STRESS** — answer as my recipient would · predict the objections · steelman the position I
argue against · tell me what would change my conclusion.

**GROW** — fold in your material · add a recipient track · split me into per-person asks ·
translate my jargon · then log where you leave me in § WHERE I'VE BEEN and send me on.

---

## § WHERE I'VE BEEN

- **2026-10-24 · v1 · written.** Drafted from the RimMandrake repository (ledger replay, git
  history, design documents) alongside `README.md`, `DESIGN_HISTORY.md`, `COMPARISON.md` and
  `AGENTS.md` in `src/RimMandrake/rimflow/docs/`. Not yet read by anyone outside the project.
- **2026-10-24 · v1.1 · tightened.** Claims bounded after an external-model review (union merge is
  textual only; provenance is asserted, not authenticated; counts are activity, not outcomes;
  prior art named). Comprehension checks rewritten around boundaries.

---

## § WHAT THIS CARRIES

*(read in under a minute)*

**The idea.** Treat the work tracker as an **append-only log of events in the repository**
(the established event-sourcing pattern), not as a mutable list or a hosted database. Each writer
appends to its own file; git's union merge combines the files without textual conflicts; a reader
deduplicates, sorts the events by a canonical key and replays them into the current state. This
handles merging the ledger's text; it does not by itself prevent contradictory claims from two
clones. The queues people read are projections of that replay.

**Three concerns RimFlow represents explicitly in its event model** (other trackers can
represent some of them through configuration or integrations; see `COMPARISON.md`):

1. **The recorded basis of a decision**: the owner's own words, his choice on a multiple-choice
   "question card", a standing ruling cited by reference, or only the agent's own reason, which
   grants no owner authority. These are recorded assertions, not authenticated ones.
2. **Implementation versus recorded validation**: `built` means a published sha and criteria
   recorded, with the offline level attested by the implementer; `validated` and `done` follow
   from recorded passing runs at the levels still owed. Runs are retained, never edited.
3. **Who holds a scarce shared resource**, with stale-holder takeover that is recorded, and a
   process-keyed lock that treats a holder as alive only if its process is.

**Why it exists.** AI agents forget everything between sessions, over-claim completion, and
collide when several share a directory. A human who checks in a few times a day, often from a
phone, cannot police that by reading. RimFlow makes these claims explicit and checks some
inconsistencies mechanically; their accuracy still depends on agents reporting faithfully.

**Inside RimMandrake versus in general.** The game, the bridge that drives it, the game-state
machine and the seat names `BENCH` and `FOUNDRY` are RimMandrake's. The ledger, the shards, the
provenance fields, the levels, reconciliation against git, leases and owner modes are
general in concept; the code hard-codes RimMandrake paths, seats and policy, and their cost
elsewhere is unknown.

---

## § HOW TO TELL YOU'VE UNDERSTOOD ME

Comprehension checks. You have engaged with me properly when you can, without looking:

1. Say which state comes from ledger replay, which inputs live elsewhere (item prose, git
   history), and why no view is edited by hand.
2. Explain why two agents appending at the same moment do not produce a textual merge conflict,
   what the reader must therefore never trust (file position), and what union merging does *not*
   prevent (contradictory claims from two clones).
3. Name the three recorded bases for owner authority and the fourth field that grants none, and
   say why none of them is authenticated.
4. Say what separates `built` from `validated`, and which recorded analysis prompted the split
   (many `doing` items had commits but no recorded proof).
5. Say which failures are addressed by file locking, union merging, item leases and the driver
   lock, and which claims rely only on agent reporting.
6. State what a shared working directory costs compared with isolated checkouts (as in Cursor
   2.0's worktrees), and what evidence would show that the workflow reduces duplicate work or
   wrong closures.

**Self-check.** Ask *"Have I understood RimFlow?"* and tell me your answers. I will grade each
check above as Met / Partially met / Not yet / Not applicable with a one-line reason, point to the
section of the companion documents where the missing piece lives, and suggest one way to close it.
I will not flatter you and I will not gatekeep; you decide what you take away.

---

## § WHY THIS EXISTS

**The setting.** RimMandrake is a series of RimWorld mods built almost entirely by Claude Code
agents for one owner. Two long-running agent windows (`BENCH` and `FOUNDRY`), each spawning
helpers, work in the same repository; the owner rules on design and art in bursts, often from an
iPhone through Claude Code Remote Control. A single running copy of the game, driven through a
"bridge", is the scarce resource every live test needs.

**What broke first.** Six markdown queues each meant "top of *my* file". Moving them into a
ledger (2026-08-20) then exposed problems that a simple list hides: appends lost on a Windows
mount (five of every six events, under twelve concurrent writers), rebase conflicts on a shared
file, several subagents handed the same item, a queue in which 186 of 272 open items had in
fact been named in published commits (a reference, not proof of completion). The history ties
several features to those recorded incidents. The full account is `DESIGN_HISTORY.md`.

**Why outsiders might care (judgment).** By the time RimFlow began, hosted trackers had agent
integrations, autonomous agents had their own task models, and in-repo agent trackers such as
Beads and Backlog.md existed (`COMPARISON.md` § 1). RimFlow is not a first; it is a field record
of what one high-volume, single-owner, multi-agent project converged on. Its mechanisms are
established ones (event sourcing, leases, staged validation, distributed issue tracking as in
git-bug); no novelty is claimed for them individually. What may interest others is the
combination, the incidents that drove each change, and the tradeoffs met in operation.

---

## § ADDITIONAL CONTEXT

**Scale (measured 2026-10-24, method in `DESIGN_HISTORY.md` appendix):** 25,839 events, 4,290
items, about 1,304 open (any state other than done, dropped or superseded); 2,149 events carry
the owner's quoted words, 552 a question-card choice, 208 a standing-ruling reference, 3,730 an
agent's own reason; one informal replay took about 0.5 s. These describe recorded activity, not
productivity or correctness.

**Known weaknesses:** not portable; one human and no permissions; a growing backlog; real
ceremony (a 232-line skill file and hooks); no dependency graph; no boards (the RimPulse
dashboard is a digest, not a planning surface); leases only per clone; logical mistakes are
countered by new events, and only torn (malformed) lines have a repair tool. Details in `README.md` § 7 and § 8 and `COMPARISON.md` § 6.

**Where it is moving now:** multi-agent locking, lane routing (which window owns which class of
work), delegated authority, and the away-and-phone loop (`README.md` § 9).

**Where to look in the repository:** code `src/RimMandrake/rimflow/`; ledger
`infrastructure/state/ledger/`; item prose `infrastructure/state/items/`; agent instructions
`skills/using-rimflow/SKILL.md`; design documents `design/RimMandrake/rimflow_*`.

---

*Version 1.1 · 2026-10-24 · drafted by a Claude agent for Lukas Mandrake; revised after an external-model review for overclaims.*
