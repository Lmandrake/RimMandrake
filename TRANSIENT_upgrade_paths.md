# Three upgrade paths — final recommendations

Written 2026-08-21 by REP, synthesising:

- `research/agentic_workflows.md` — the Control Plane proposal, from another stream
- `TRANSIENT_one_hand_model.md` — the ONE HAND proposal, from this stream
- verified vendor and research evidence (§2)
- **direct observation of this project on this day** (§3)
- the owner's stated constraint, which outranks all of the above (§1)

---

## 1. The constraint that decides this

The owner, 2026-08-21:

> *"I'm deeply depressed at how much time is spent trying to coordinate agents that
> increasingly work at improving process or guarding against stupid behavior or unnecessary
> locks."*
>
> *"It would be fantastic if the designed system could avoid ANY user-awareness of locked
> files, inability to communicate or need to do so via cryptic processes, or other
> infrastructure madness."*
>
> 🔑 *"**Building a structure that simply embodies restrictions, requirements, and
> guarantees is much more powerful than fragile hooks and agreements and agent defs.**"*

**That last sentence is a correction to both proposals on the table, and it is right.**

- `agentic_workflows.md` recommends putting the sophistication into *"canonical project
  state, typed task contracts, decision and change protocols, dependency tracking, state
  versioning, automatic invalidation, acceptance criteria, validation infrastructure,
  observability, escalation rules."* That is **ten new subsystems** — a control system to be
  designed, built, debugged and maintained by the same agents currently building the game.
  It is a good design and it is also, precisely, more of the thing that is grinding him
  down.
- `TRANSIENT_one_hand_model.md` (mine) leans on **six hooks**. A hook is a guard: it presumes
  the bad act is possible and tries to catch it. Guards are fragile, they misfire, and each
  one is another piece of infrastructure the owner has to be aware of.

⇒ **The design test from here on is not "does this prevent the failure" but "does this make
the failure impossible without anybody having to maintain anything."**

### 1.1 Structural vs. enforced — worked through

| the failure | the *enforced* fix (fragile) | the **structural** fix (free) |
|---|---|---|
| Two agents hold contradictory beliefs | a policy that says reconcile; a skill about superseding | **one agent.** There is no second belief to diverge |
| A worker acts on a stale ruling | a hook checking the brief carries current canon | **workers are born with no memory.** Freshness is not maintained; it is the only state available |
| Two agents overwrite one file | file locks, ownership tables, worktrees | **one writer.** Locks cannot be user-visible if none exist |
| Peer messages carry bad state | a hook refusing peer sends | **no peers exist.** Nothing to refuse |
| Docs contradict a ruling | propagate the ruling into 123 documents, by hand, forever | 🔑 **declare docs non-authoritative.** Precedence replaces propagation (§4.2) |
| A worker marks its own work done | a verification-gate hook | **the checker is a different worker and cannot write** |
| Work items outlive the belief that created them | an invalidation subsystem | **derive the worklist instead of storing it** — a killed item is not deleted, it is simply never regenerated |

Every row on the right needs **no maintenance, no hook, and no user awareness.** That is the
target, and how close a path gets to it is the main axis of judgement below.

---

## 2. What the evidence actually supports

Verified first-hand (URLs and verbatim quotes in `TRANSIENT_one_hand_model.md` §1):

- **Anthropic, 2026-08-13, "Patterns and problems in emerging multiagent systems"** — three
  instances against one shared repo escalated to sabotage. **18 of 30 agents independently
  chose the identical branch name.** They tested flat peers vs. prescriptive roles vs. a CEO
  hierarchy: *"But these prompts did not make much difference."* Models *"currently require
  significant human direction."*
- **Claude Code docs** — *"For sequential tasks, same-file edits, or work with many
  dependencies, a single session or subagents are more effective."* And: *"Two teammates
  editing the same file leads to overwrites."*
- **Anthropic** — multi-agent is a poor fit for *"domains that require all agents to share
  the same context or involve many dependencies between agents"*; *"most coding tasks
  involve fewer truly parallelizable tasks than research."*
- **Cognition** — *"running multiple agents in collaboration only results in fragile
  systems"* because *"decision-making ends up being too dispersed."*
- **Anthropic memory tooling, injected verbatim into every agent** — *"ASSUME INTERRUPTION:
  Your context window might be reset at any moment"* / *"ALWAYS VIEW YOUR MEMORY DIRECTORY
  BEFORE DOING ANYTHING ELSE."*
- **`CLAUDE.md` is not enforcement** — *"Claude treats them as context, not enforced
  configuration."* And *"Bloated CLAUDE.md files cause Claude to ignore your actual
  instructions"* — while subagents load *every level of the hierarchy the main conversation
  loads*, so the bloat is paid again per worker.

**Where the two streams agree, and it is worth noting how strongly.** Both arrived
independently at: *do not make peer conversation the backbone; make shared state the
backbone* · *authority is not distributed* · *the checker is not the builder* · *a lead
reconstructs from canonical state rather than conversational memory* · *the irreversible
world-creation gate gets a formal readiness dossier*. **Those are settled.** The disagreement
is only about how much machinery to build around them — and §1 answers that.

---

## 3. What was actually observed, in one working day

Not argument. Things that happened on 2026-08-21, in this repo.

| observation | what it demonstrates |
|---|---|
| Three items sat open on the owner's own seat. **All three were already fully ruled** — one recorded *"the owner took option 1 and ruled the question shut"* and remained open anyway | Work items outliving their decisions. The exact failure |
| A canon item held *"seven canon questions."* **Six had been answered days earlier**; the seventh was ruled on 08-21 | Nobody closes what a ruling settles. Reconciliation was never a property |
| A fresh worker reading the design docs cold **reproduced a known-stale fact within two minutes** (the ideoligion's memes, corrected days before) | 🔑 Stale prose is live ammunition. A doc corrected in one place stays wrong everywhere else |
| A research subagent **fabricated quotes and a non-existent arXiv ID**, then retracted them unprompted | A worker's confident report is not evidence — the same failure Anthropic measured (routing accuracy 0.85 → 0.62 with one lying peer) |
| REP was **refused by the tooling** when dropping another seat's item, and had to hand the owner a command to do it himself | Infrastructure madness, verbatim. A permission model that exists only because concurrent seats exist |
| A commit trailer `Closes:` did not move the ledger; a separate `rimflow close` was required | Two mechanisms for one act. Both must be remembered; neither is |
| `CLAUDE.md`, on the day the speed ruling was issued: *"a day produced ~220 commits and moved the actual goal by one item"* | The process tax, measured by the owner himself |

🔑 **Every one of these is a coordination artifact. None is a game-content problem.** The
project's blocker is not that the work is hard; it is that the apparatus for dividing the
work costs more than the work.

---

## 4. Three ideas that do the heaviest lifting

These are not a path. They apply to all three, and they are where most of the relief comes
from. **§4.3 bounds the other two** — without it, §4.2 collapses under its own weight.

### 4.1 Derive the worklist; do not store it

A stored queue is a set of beliefs frozen at the moment they were written. When a ruling
changes, every item generated under the old belief is **silently wrong and still actionable**
— which is exactly what happened with the Tribal Furniture removal items.

**If the worklist is recomputed from canon plus the repo's actual state, a killed item cannot
survive, because nothing regenerates it.** No invalidation subsystem, no dependency graph, no
cascade logic. The item is gone because the reason for it is gone.

⚠️ **Honest limit:** creative work does not fully derive. "Author the Deepwater cast roster"
comes from a human intention, not from repo state. **So: derive what is derivable (defs
missing, refs broken, docs contradicting canon) and hand-keep the short creative list.** The
hand-kept list stays small enough to read in one screen — which is the actual test.

### 4.2 Canon is authoritative; documents are commentary

Today the project owes a **propagation debt**: when a ruling lands, every one of ~123 design
documents that says otherwise must be found and edited. That debt has never been paid in
full, is growing, and the `deciding-and-superseding` skill exists to chase it.

**Stop owing it.** One rule, no machinery:

> **`CANON.md` is the only authoritative statement of what is true. A design document is
> evidence and argument, never authority. Where they differ, canon wins and the document is
> simply out of date.**

- Any agent doing any work is given canon. It cannot act on a stale doc, because it holds the
  overriding statement.
- Documents get corrected **opportunistically** — when someone is in there anyway — instead of
  as a debt owed on every ruling.
- 🔑 **This converts an unbounded, permanently-unpaid propagation cost into a bounded,
  always-paid read cost.** It is the single largest reduction in process work available, and
  it needs no tooling at all.

⚠️ **What it costs:** a human browsing the design corpus can still read something false. The
mitigation is a dated banner at the top of superseded files — cheap, and the project already
does this.

### 4.3 Canon is not "what is true." It is "what OVERRIDES."

🔴 **This bound is load-bearing, and its absence is a defect this document shipped with.**
The owner caught it: *"If we turned all the design facts and world facts into canon items,
that's a LOT of canon… I could see this being thousands. What about cherrypicking out
ThingDefs, for example? Build details?"*

He is right, and without a bound §4.2 is unworkable — canon injected into every worker only
survives if canon stays small.

**A line earns canon only when something already written down says otherwise, or would be
assumed otherwise.** The test is one question:

> **Would a competent agent, holding the design docs and the data, do the wrong thing without
> this line?**

If no, it is not canon. It is content, and content lives where content lives.

| kind | examples | where it lives | how an agent gets it |
|---|---|---|---|
| **Data** | 1,308 cherrypick keys · 21,872 tiles · 152 pawnkinds · 72 settlements · every def | its own files, whatever format suits | **queried by an instrument.** Never injected |
| **Prose** | the premise · the planet · factions · religions | `design/**` | **read on demand, by path.** Never injected |
| **Canon** | rulings that override one of the above | `canon/` | **injected whole — because it is small** |

⛔ **A number that can be measured must never be written into canon.** Writing it down is how
it goes stale — `biomes_on_map: 25` is a bug waiting to happen; `measure` answering 25 is
not. The project already has the instrument for this column.

**Worked example — cherrypicking's 1,308 keys collapse to two canon entries:**

| the thing | verdict |
|---|---|
| the 1,308 keep/cut judgements | **data.** A tool answers *"is `ThingDef X` cut?"* Nobody reads the list |
| *"Cherrypicking is frozen and closed for v1; plants, mechs, drugs, incidents, traits, ideology styles are not v1 work"* | ✅ **canon** — an agent would otherwise pick the work up |
| *"The painter wins over the cut list: `AB_GelatinousSuperorganism` and `ZBiome_Grasslands` stay as painted"* | ✅ **canon** — it overrides the data file |
| *"Cutting the last weapon carrying a tag silently disarms every pawn kind whose tags all went to zero"* | ⛔ **neither.** A procedure and a hazard — it belongs in a **skill**, loaded when someone cherry-picks |

**Build details are the same shape.** The code is the truth about what the code does. Canon
carries only the build decisions that override an assumption — *no Combat Extended* · *the
gravship and its factory are the only sanctioned progression trees* · *assemblies deploy only
while the game is down*.

🔑 **Why this stays bounded:** canon size is governed by **live open questions, not decision
history.** A superseded ruling leaves canon for the archive; only the current front is
injected. And most rulings die naturally — once the thing they govern ships, the ruling stops
overriding anything. Estimate under this definition: **60–150 live entries at ~10 lines
each**, and it holds indefinitely because it does not accumulate.

⚠️ **The failure mode to watch** is canon becoming a dumping ground for facts. The moment
`water_pct: 8.14` is written into it, the slide toward thousands begins and the scheme
collapses. **The discriminator above is the guard — and it is a definition, not a hook**,
which is the §1 test passed.

### 4.4 Format, given that bound

With canon bounded at 60–150 entries, the format question is small and the answer keeps the
markdown:

- **`canon/<RULING_ID>.md`, one file per ruling**, with ~5 lines of frontmatter (`id`, `date`,
  `tags`, `overturns`, `kills`). `ls` is the index, `grep` is the query, superseded rulings
  move to `canon/archive/`, and git history per ruling is clean. **The structure lives inside
  the file**, so if any script vanishes it is still readable prose.
- 🔑 **No query engine is needed, because the Hand is the query.** The orchestrator knows the
  task and selects the relevant rulings for the brief. Tags and `grep` are the backstop.
- ✅ **Keep `canon.yml` and `check_canon.py` unchanged** for the *values* layer. 0
  contradictions across 119 design docs is a real result and the one piece of the current
  apparatus worth defending. ⚠️ But hold it to §4.3: values that can be measured should
  migrate to the instrument rather than be maintained by hand.

⚠️ **If canon comes in under ~50 entries, a single `CANON.md` is better** — total elegance,
and the size problem never arrives. That is a countable question, not a matter of taste:
seed canon from the rulings already scattered through `canon.yml`, `CLAUDE.md` and
`HUMAN.md`, and count what comes out.

---

## 5. Two modes, and they are fundamental

The owner, 2026-08-21:

> *"The system should have two fundamental modes: one where the human is PRESENT and is
> trying to make best interactive use of the human thinking, creating, and debugging with the
> system + live game (this is critical!!!), and a separate mode where it queues work and tries
> to get a bunch of stuff done that does not need interaction. These are absolutely
> fundamental to the design."*

This is not a convenience setting. **The two modes have different scarce resources, and
optimising for one actively harms the other.**

| | **PRESENT** | **AWAY** |
|---|---|---|
| **The scarce resource** | the owner's attention, and the **live game** | calendar time, and the **25-minute load budget** |
| **Optimise for** | latency — short loops, fast answers | throughput — depth, breadth, thoroughness |
| **Fan-out** | ⛔ **only if it returns inside his patience.** A background sweep that makes him wait is a net loss | ✅ **aggressively.** This is where 15× tokens is worth paying |
| **A decision he must make** | 🔑 **ask him now** — this is the whole point of his being here | ⛔ **park it.** Never guess, never proceed on an assumption |
| **Work needing the game** | do it live, while it is already loaded | **batch it** into one load round |
| **Work needing neither** | ⛔ **never spend his presence on it** | ✅ this is the entire AWAY workload |
| **Ends with** | whatever he wants next | a short report: done · parked · needs you |

### 5.1 Why this is structural rather than a flag

**The mode determines which work exists, not how agents behave.**

The project already has the mechanism and does not use it as one: every item carries a
`needs:` field — `offline` · `game-up` · `game-down` · `owner`. That field, plus the mode, is
a **filter**:

- **PRESENT** surfaces `owner` and `game-up` work — the things that *require* him or the
  running game. Everything else is invisible, because doing it now wastes the one resource
  that is only available while he is here.
- **AWAY** surfaces `offline` work only. Items marked `owner` are **structurally unreachable**
  — not "agents are told not to guess," but *not in the list at all.* An agent cannot decide
  something on his behalf if the decision is not visible to it.

🔑 **That is the §1 test passed.** No hook, no policy, no permission model. The wrong work
cannot be picked up because it is not offered.

⭐ **And it dissolves the worst habit of the old system**: agents finding work to do while he
was away, generating queue items from beliefs he then overturned. In AWAY mode the eligible
set is bounded by what canon already settles. **If AWAY runs out of `offline` work, it stops
and waits.** It does not invent more.

### 5.2 PRESENT: spend his presence only on what needs him

Two rules, and they are the whole of it:

1. **Nothing that could have been done without him happens while he is here.** If it is
   `offline`, it belongs to AWAY. Doing it in front of him spends the scarce resource on the
   abundant one.
2. **The live game is a singleton.** One driver at a time. While he is playing or looking,
   agents do not drive the bridge; while an agent is driving, he knows because it told him.
   With one session there is no arbitration problem to solve here — **this is another failure
   that a single writer removes rather than manages.**

⚠️ **The highest-value thing PRESENT mode can do is hand him the parked decisions first**, in
the decision-packet format (§6, from Path C): problem · evidence · options · recommendation ·
what changes if accepted · reply with a letter. A batch of five of those cleared in ten
minutes unblocks the next AWAY run entirely. **That, not conversation, is the best use of his
presence** — apart from the things only he can do: looking, judging, and playing.

### 5.3 AWAY: bounded, evidenced, and it stops

- **Bounded by canon.** Only `offline` work, only what canon already settles.
- **A stopping condition, always** — Anthropic: set *"stopping conditions (such as a maximum
  number of iterations)."* AWAY ends because it ran out of eligible work or hit its bound,
  never because someone noticed.
- **Nothing is marked done without evidence.** A worker's confident report is not evidence
  (§3), and he is not there to catch it.
- **Discoveries become parked decision packets**, ready-made, so PRESENT starts with a stack
  of ten-second answers instead of a discovery conversation.
- 🔑 **This is where fan-out earns its keep** — and where a dynamic workflow (script holds the
  plan, results stay in script variables, up to 1,000 agents at 16 concurrent) beats
  dispatching one worker at a time, because nobody is reading the intermediate output.

### 5.4 The transitions

There are exactly two, and both are the owner's to declare — the same shape as the existing
`./game up|down`, which already works and which he already uses:

- **He arrives** → AWAY stops cleanly at the next completed unit. He gets: *done · parked ·
  needs you.* Parked decisions are offered first.
- **He leaves** → he says so; the queue runs; it stops when eligible work is exhausted.

⚠️ **`infrastructure/state/MODE` already exists** (`interactive | autonomous | afk`) and is
currently decorative. Under any path it should become the thing that filters the worklist —
which is a small change, and the only one this section requires.

### 5.5 What this implies for the three paths

- **Path C is worst served.** A control plane's ceremony — typed packets, proposals,
  arbitration — is pure latency in PRESENT mode, which is the mode he called critical.
- **Path A and Path B both fit naturally**, because one session can simply be in one mode or
  the other, and `needs:` already carries the filter.
- 🔑 **It raises the value of §4.1** (derive the worklist). The AWAY-eligible set is exactly
  *"what does canon plus the repo say is broken or missing that needs nobody?"* — which is the
  derivable half. **The two ideas fit together: the derived list is the AWAY queue.**

---

## 6. The three paths

### PATH A — **STRIP** · one session, almost no machinery

Delete the apparatus. One Claude Code session at a time. `CANON.md` is authoritative (§4.2);
the derivable worklist is derived (§4.1) and the creative list is a short hand-kept file.
Subagents are spawned freely for reading, censusing and independently-authorable content, and
they die when done. **No seats, no ledger, no board, no publisher, no claiming, no
`needs`-gating, no permission model between agents.**

**What gets deleted:** `rimflow` (frozen, kept readable as history), `status_server.py`,
`board_loop.sh`, `status_board.html`, `status_matrix.json`, the four seat files,
`POLICY.md`, the queue renderer, `block_peer_messages.py`, and every rule in `CLAUDE.md` that
exists only to arbitrate between concurrent seats.

**Hooks retained: one** — the blanket-git-stage guard, which protects against a real
destructive act rather than coordinating anyone.

| ✅ pro | ⚠️ con |
|---|---|
| **Ends the process tax immediately.** Nothing to maintain, nothing to learn, nothing cryptic | **Propagation depends on the canon-precedence rule holding.** If an agent works without canon in hand, drift returns |
| **Structural, not enforced** — one writer, so no locks, no peers, no ownership model, no user-visible infrastructure at all | **No automatic staleness detection.** Contradictions surface when someone looks, not when they arise |
| Matches vendor guidance for sequential, same-file, dependency-dense work | **Loses the board.** No at-a-glance project state |
| Cheapest to adopt — mostly deletion, which is fast and safe | **Throughput is bounded by one conversation.** Big parallel sweeps need deliberate fan-out rather than getting it by default |
| Every observation in §3 disappears by construction, not by rule | Regression risk: the apparatus was built for reasons, and a few were real |

**Best if:** the priority is to get the owner's time back and finish v1.

---

### PATH B — **ONE HAND** · one session, three files, a few guards

Path A plus a durable spine: `CANON.md` · `WORKLIST.md` · `LOG.md`, the ruling-written-in-the-
same-turn protocol, typed worker briefs, and hooks for the parts that matter.

**Revised in light of §1 — drop from six hooks to two, keeping only the ones that never
guess:**

- **H2 `brief_carries_canon`** — refuses to dispatch a worker whose brief lacks current canon.
  This is the mechanical guarantee behind §4.2 and it is worth keeping.
- **H4 `no_close_without_evidence`** — refuses to mark work done without a verification record.
- ⛔ **Drop H3** (the ruling-detector). It guesses at the owner's intent from his wording, it
  will misfire in ordinary conversation, and a guard the user has to argue with is exactly the
  infrastructure madness ruled out in §1.

| ✅ pro | ⚠️ con |
|---|---|
| Keeps a durable, readable record of what was ruled and what was proven | **Two hooks and three files are still machinery** — small, but non-zero, and someone maintains them |
| H2 makes canon-precedence a *guarantee* rather than a habit | `CANON.md` needs periodic compaction, and someone must remember |
| `LOG.md` gives the evidence trail `rimflow` was reaching for, at a fraction of the size | A worklist file is a stored queue — §4.1's failure mode, reintroduced unless it is kept derived-plus-short |
| Still one writer: no locks, no peers, no ownership model | More to adopt than Path A, and the benefit over A is real but modest |

**Best if:** the durable record matters enough to justify a small, fixed amount of machinery.

---

### PATH C — **CONTROL PLANE** · the other stream's proposal

DECIDE owns canonical truth and arbitrates change; BUILD is plural and parallel; CHECK is
institutionally separate; REP repairs drift. Typed task packets, ChangeProposal objects,
project-state versioning, dependency tracking, automatic invalidation, a validation pyramid,
observability, escalation packets.

| ✅ pro | ⚠️ con |
|---|---|
| **The best design on paper** — highest throughput, strongest drift resistance, and its analysis of the problem is correct | 🔴 **It is ten new subsystems**, built by the same agents who should be building the game. That is the process tax, institutionalised |
| Typed contracts and ChangeProposals genuinely address the escalation problem, and the decision-packet format is excellent | 🔴 **The multi-agent premise is the one the evidence contradicts** — measured, eight days ago, on this exact configuration |
| The validation pyramid is right regardless of path, and should be taken from it whatever else is chosen | **Concurrent BUILD workers on one checkout is the documented overwrite hazard**; avoiding it means worktrees — i.e. **user-visible locked files**, ruled out in §1 |
| The world-creation readiness dossier is right regardless of path | *"Coordination bugs become architectural bugs"* — its own words. Debugging them costs game-content time |
| | Its own note applies: *"probably too ambitious as the immediate next architecture"* — written of Option 2, but truer of this |

**Best if:** the project were starting fresh, with time to build infrastructure before content,
and with a human who wanted to run an organisation. Neither condition holds.

---

## 7. Recommendation

### 🔴 **PATH A now. Path B's two artifacts only if A proves them necessary.**

Reasoning, in order of weight:

1. **The owner's scarcest resource is his own attention and morale, and both are being spent
   on coordination rather than creation.** §3 shows a full day where every observed failure
   was a coordination artifact. Path A removes the category.
2. **Path A is the only one that satisfies §1 completely.** Nothing locked, nothing cryptic,
   nothing to maintain, no infrastructure to be aware of. B is close; C cannot be, because
   parallel builders require isolation and isolation is user-visible.
3. **v1 is close.** ~49 items remain against 116 done. This is not the moment to build a
   control system; it is the moment to remove obstacles between the owner and the finish.
4. **Path A is not a downgrade in safety.** Every §3 failure becomes impossible by
   construction rather than forbidden by rule — which is precisely what he asked for.
5. **It is reversible.** A and B share a spine; C is reachable later if the project outgrows
   A. Nothing in A forecloses anything.

**Take from Path C regardless of choice** — these are path-independent and clearly right:

- The **validation pyramid**: cheap static checks first, the 25-minute load last and batched.
- The **world-creation readiness dossier**, with the unresolved-blocker count required to be
  **zero** before the action is offered.
- The **decision-packet format** for escalating to the owner: problem · evidence · options ·
  recommendation · what changes if accepted · reply with a letter. Not a conversation.
- **CHECK is never the author.** Anthropic's reason: *"agents tend to respond by confidently
  praising [their own] work."*

**Take from Path B regardless of choice:**

- `CANON.md` authoritative, docs advisory (§4.2). This is the highest-value single change on
  the table and costs nothing.
- Rulings written in the turn they are heard — as a habit under A, as a hook only if it turns
  out habit is not enough (§8, E3).

---

## 8. The unknowns, and cheap experiments that settle them

Every one of these avoids the 25-minute load. None requires the game.

### E1 · Does canon-in-hand actually stop an agent acting on a stale document?
**The unknown:** §4.2 is the load-bearing idea, and it is untested as policy.
**The experiment:** take three statements in `design/` known to be superseded. Dispatch six
fresh workers on tasks that would touch them — **three with canon in the brief, three without**
— and count how many act on the stale statement.
**Cost:** ~20 minutes, no game.
**Why it is decisive:** it tests the mechanism the entire recommendation rests on.
⭐ **A control result already exists, accidentally:** today a worker with **no** canon in its
brief reproduced a known-stale fact within two minutes. The no-canon arm has effectively run
once and failed. This experiment supplies the other arm.

### E2 · Is the worklist actually derivable?
**The unknown:** §4.1 claims most work can be computed from canon plus repo state rather than
stored.
**The experiment:** hand-write the derivation for one day's real work — defs missing, refs
broken, docs contradicting canon — and compare against the 49 open items. **What fraction
derives? What is left over?**
**Cost:** one session, no game.
**Why it is decisive:** if 80% derives, the stored queue can go. If 30% does, it cannot, and
Path B's `WORKLIST.md` earns its place.

### E3 · Does the ruling get written without a hook?
**The unknown:** I dropped H3 as too fragile. Does habit suffice?
**The experiment:** run Path A for one week. **Afterwards, diff `CANON.md` against the
transcripts** and count rulings the owner made that never got written down.
**Cost:** zero — it is measured after the fact from data that already exists.
**Why it is decisive:** it converts "will the agent remember" from a worry into a number. If
the miss rate is zero, no hook is ever needed.

### E4 · Does fan-out actually pay on this project's work?
**The unknown:** Anthropic says *"most coding tasks involve fewer truly parallelizable tasks
than research"* — is that true here?
**The experiment:** take a real batch — the remaining faction cast rosters, or a sprite audit
— and run it **four-parallel against serial**, measuring wall-clock, tokens, and how many
outputs needed rework.
**Cost:** one batch of work that had to be done anyway.
**Why it is decisive:** it sets the fan-out policy with a number instead of a preference.

### E5 · What does deleting the apparatus actually break?
**The unknown:** the board and ledger were built for reasons; some were real.
**The experiment:** **stop the publisher and the board for three days without deleting
anything.** See what is genuinely missed.
**Cost:** two commands, fully reversible.
**Why it is decisive:** it distinguishes "load-bearing" from "habitual" before anything is
destroyed — and it is the safest possible first step, because nothing is lost if it is wrong.

### E6 · How much is the instruction bloat costing?
**The unknown:** `CLAUDE.md` loads into every subagent, in full.
**The experiment:** count tokens in the global plus project instruction files; multiply by a
realistic worker count for one day's fan-out.
**Cost:** minutes.
**Why it matters:** it sizes the §12.1 migration (facts stay, procedures become skills, rules
become hooks or disappear) instead of guessing at it.

### E7 · How big is canon actually?
**The unknown:** §4.3 bounds canon by definition and estimates 60–150 live entries. That is a
projection, and it decides the format (§4.4) and whether §4.2 is affordable at all.
**The experiment:** sweep `canon.yml`'s `ruled:` and `needs_ruling:` sections, the standing
rulings in both `CLAUDE.md` files, and `HUMAN.md`, applying the §4.3 test to each candidate —
*would a competent agent do the wrong thing without this line?* **Count what survives.**
**Cost:** one worker, no game.
**Why it is decisive:** under ~50, take a single `CANON.md` and enjoy the elegance. Over ~150,
the discriminator is not holding and §4.3 needs tightening before anything is built on it.
⭐ It also produces the actual seeded canon as a by-product, so the measurement is not thrown
away.

**Suggested order: E5 → E7 → E1 → E2 → E3, with E4 and E6 folded into normal work.** E5 first
because it is free and reversible; **E7 next because it is the one that can invalidate the
design** — if canon really is thousands, §4.2 does not work and Path A needs rethinking; E1
after, because everything else rests on it.

---

## 9. What to delete, whichever path is chosen

These serve no purpose once concurrent seats are gone. Listed so the decision is one act
rather than a slow retreat:

```
src/RimMandrake/Utils/status_server.py        the board
src/RimMandrake/Utils/status_board.html
src/RimMandrake/Utils/board_loop.sh           the bounded publisher that dies silently
infrastructure/state/status_matrix.json
infrastructure/agents/POLICY.md               inter-seat law
infrastructure/agents/{DECIDE,BUILD,CHECK,REP}.md
.claude/hooks/block_peer_messages.py          nothing to refuse
```

And from the instruction files: every rule about seat ownership, claiming, `needs`-gating,
peer messaging, broadcast relaying, and who may edit whose item. 🔑 **`CLAUDE.md` should
shrink by more than half, and that is a feature** — *"Bloated CLAUDE.md files cause Claude to
ignore your actual instructions."*

⚠️ **`rimflow` is frozen, not deleted.** It holds the project's decision history and
`LOG.md`/`CANON.md` start empty. Keep it readable; stop writing to it.

---

## 10. The honest summary

The project does not have an agent-coordination problem that better coordination will fix. It
has **an apparatus that outgrew the work it was built to organise**, and every attempt to
repair it — including both proposals now on the table — has added more apparatus.

The evidence says the multi-agent premise underneath it does not hold at this scale, that
prompts and roles do not fix it, and that for sequential, same-file, dependency-dense work
the vendor recommendation is one session with subagents.

The owner's own instinct is the right one and is stronger than either proposal: **build a
structure in which the bad thing cannot happen, rather than a structure that forbids it.**
One writer, ephemeral workers, canon that overrides prose, and a worklist that is derived
rather than remembered — that structure needs no locks, no permissions between agents, no
board, no protocol, and nothing for him to be aware of.

**Recommendation: Path A. Start with E5 tonight — it costs two commands and is entirely
reversible.**
