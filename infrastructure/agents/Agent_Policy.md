# Agent_Policy — which model does which work

**Binds BENCH and FOUNDRY.** Read with `CHARTER.md`. This is the ONLY file that
says which model does what *for this repo's seats*; every other doc in RimMandrake
points here. The routing axis is measured, not argued.

🔴 **FOR WHAT THE FLEET CAN ACTUALLY REACH, ASK `~/dev/DispatchOpenCode/bin/delegate`.**
A census on 2026-10-01 found six files across `~/dev` restating a model ladder in prose,
three of them naming a model the gateway does not serve. `bin/delegate where` reports
reachability and `bin/delegate route <kind>` picks a destination from published figures;
a `PreToolUse` hook on `Agent|Task` now refuses an unservable model at the spawn instead
of letting it 400 afterwards. **What stays here is the SEAT policy** — which of this
repo's jobs is design and which is grind — because that is a judgement about RimMandrake
and not a fact about the gateway. Anything in this file that is a claim about model
*availability* is subordinate to `bin/delegate`, which measures it.

## 🔴 The seat models — fleet ladder updated by the owner, 2026-10-20

> `opus` for design work and complex code generation; `sonnet` for well-defined coding, prose a
> human will read and act on, and cross-context judgment; `haiku` (Haiku 5.5) for mechanical bulk
> work with a checkable outcome: OS-level searches, greps, globs, inventories, file sweeps,
> extraction, classification, dedup pre-screens. **No Fable.** Pass `model` on every spawn.
> Haiku 5.5 is served on both JPL GenAI accounts as of 2026-10-20. `haiku` is an alias resolved
> through `ANTHROPIC_DEFAULT_HAIKU_MODEL`: read the environment (or `~/dev/GenAiSwitch/bin/genai-switch
> status`, `~/dev/DispatchOpenCode/bin/delegate where`) before trusting a rung; name no account.
> Ladder source of truth: `~/dev/Lodestar/claude/global/45-subagents.md`.
> (Superseded 2026-10-20: the 2026-10-01 to 2026-10-07 notes that Haiku was struck or remapped to Sonnet.)

`fable` is the name that genuinely 400s (the harness expands it to a literal id).

BENCH runs on Opus 5.5 and orchestrates. It does not do design in-window and does not grind:
it holds the owner's attention, backgrounds design to an **Opus** subagent, and keeps the
conclusion. FOUNDRY runs on Sonnet 5.5 and escalates to Opus per item when the work is complex
code generation or has no checkable outcome.

## The one question

Tier does **not** follow how hard the task looks. It follows:

> ## 🔑 If this goes wrong, WHO CATCHES IT?

Our register of failures is not bad code — it is **plausible answers nobody
disbelieved**: seven instruments returning confident wrong counts in one session;
~40 bridge calls reporting success and changing nothing; an `<li>` discarding a
whole def and costing 26 biomes. Cheap models are safe exactly where failure is
loud, and dangerous exactly where it is silent.

| Who catches a wrong answer | Use |
|---|---|
| It is an **OS-level search** (grep, glob, file inventory) whose result is re-checked | **haiku** |
| A **compiler, selftest, validator or hook**, before anyone reads it | **sonnet** |
| **Another agent**, who will re-derive it before acting | **sonnet** |
| **Nobody** — it becomes a recorded fact other work cites | **opus** |
| **Only taste** — art, the world, prose he reads | **opus** judge agent (not the maker), then his curated review — `design/RimMandrake/delegation_policy.md`; the naive pre-review of anything shown to him is this row (`standing_rulings.md` §Nothing reaches the owner unread) |

⛔ If you cannot name the catcher, you are on row 3. "It'll be obvious" is not a catcher.

## The ladder

| | Alias | For |
|---|---|---|
| **Opus 5.5** (+fast mode) | `opus` | **Design** — design judgment, decision drafting, synthesis across contradictory evidence, rosters, specs, skill curation — always as a backgrounded subagent from BENCH. **Complex code generation** — Harmony/C#, new systems, multi-file forensics, bridge writes, the frozen world. **BENCH's window**, the orchestrator |
| **Sonnet 5.5** | `sonnet` | **Well-defined coding with a checkable outcome** — patches, defs, deploys, quicktests, fixes a selftest or validator proves. Log triage, interpretive sweeps, first drafts. **OS-level searches** — greps, globs, censuses, existence checks, inventories (folded in 2026-10-01; see below). FOUNDRY's default |

Fable is not on the ladder (owner, 2026-09-29). Pass `opus`, `sonnet` or `haiku`; read the environment
(`ANTHROPIC_DEFAULT_*_MODEL`) before trusting any alias.

Escalate the **model**, never the ceremony: a hard problem gets a smarter model on
the same short leash. Put `model: opus` on an item you already know is hard;
otherwise FOUNDRY starts at Sonnet and self-escalates after one failed attempt, or
whenever the call itself is row 3 of the table above — triage and verification
judgment with nobody else to catch it (a stale-drop ruling, grading a subagent's
findings) — noting it in the closing commit. External free workers (nemotron):
candidate narrowing only, never conclusions, never writing —
`research/FANOUT_WORKER_EVALUATION.md`.

## Subagents — this is where the saving is

🔴 **Every `Agent` call takes `model`. Pass it, every time**
(`block_agent_without_model.py` refuses otherwise).

| Job | Model |
|---|---|
| OS-level search: grep, glob, inventory, "does X exist", fixed-shape census; extraction/classification with a checkable result | **haiku** |
| Well-defined coding a compiler, selftest or validator will check | **sonnet** |
| Sweep where the agent must interpret or classify | **sonnet** |
| Fan-out whose returns will contradict; adversarial refutation | **sonnet** |
| **Design** — a spec, a roster, a taxonomy, anything the owner reads as design | **opus**, backgrounded |
| **Complex code generation** — a new system, Harmony/C#, cross-file changes with no test to catch them | **opus** |
| Anything acted on **without re-deriving it** | **opus** — and ask why it is a subagent |

A subagent's return is EVIDENCE, never a finding — it carries CONFIRMED/UNCERTAIN
and the window decides what is true. Never spawn a duplicate for "reliability".

## Four places a cheaper tier is forbidden outright

1. **Deciding whether an instrument told the truth** (`BUILDABLE.md` exists because they lie).
2. **Live bridge writes** — the world is frozen and hand-authored, no regenerate behind it.
3. **The world, and art** — *"iterate by LOOKING"*; realism is not scoreable.
4. **Text the owner reads as a conclusion** — above all a number.
   ↳ 🔴 **One carve-out, owner ruling 2026-09-16: north-star `must read` verdicts.**
   Verbatim: *"Let a model YES green a line."* A model judging a mod's letter or
   flavour prose against a `must read` line MAY return a pass, and that pass greens
   the line — it is not routed to him. The tier floor still applies (opus), and
   `cannot read` lines stay absolute. Rationale and the residual risk are in
   `design/RimMandrake/north_star_validation_spec.md` §10.4: the rule it replaced
   would have made any text-first mod permanently ungreenable unattended, and an
   off-register letter is a bounded, recoverable failure. **This carve-out is
   read-verdict-only** — a number, a count, or a finding he will act on still lands
   on row 3 and still comes to him.

## The escalation clause every cheap-worker prompt carries

> Escalate instead of guessing if: the criteria do not decide the case · the change
> reaches files outside the ones named · a measurement disagrees with the item · a
> tool returns success and you cannot see the effect · you would have to invent a
> defName, field or namespace.

Escalating is a success; record it. Stamp the model on closes (`model=sonnet-5.5` in
the `note`) so the ledger can answer accepted-work rate per model.
