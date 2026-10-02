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

## 🔴 The seat models — owner, 2026-09-29 (replaces the 2026-09-02 Fable ladder);
## Haiku struck 2026-10-01 — no Haiku model on the gateway (but see the correction below:
## the ALIAS resolves to Sonnet 5 and works; `fable` is the name that actually 400s)

> The owner asked for **Opus 5.5 for design work and complex code generation, Sonnet 5.5 for
> well-defined coding tasks with checkable outcomes, and the most recent Haiku only for
> OS-level searches.** Fable is dropped from the ladder entirely (decision taken by question
> card, 2026-09-29).

**Haiku is gone as a MODEL, and the ruling below is unchanged — but the mechanism stated
here was wrong and is corrected.** The sanctioned gateway at `$ANTHROPIC_BASE_URL` serves 40
model ids — only `us-gov.anthropic.claude-{opus-4-8,opus-5,sonnet-4-5-20250929-v1:0,sonnet-5}`,
three Amazon Nova ids, and a Titan embedder — and carries no Haiku id at all; the entire
`us.anthropic.*` prefix is dead (HTTP 400). Verify with `~/dev/DispatchOpenCode/bin/delegate
where`, which asks the gateway and reports "could not ask" separately from "serves nothing".

🔴 **CORRECTED 2026-10-01: `model: haiku` does NOT 400. It resolves to Sonnet 5 and works.**
This paragraph previously said a haiku spawn "launches and only *then* 400s", which was true
before the same day's fix and false after it. `ANTHROPIC_DEFAULT_HAIKU_MODEL` is
`us-gov.anthropic.claude-sonnet-5`, so the alias is remapped and a haiku subagent returns
normally — measured by spawning one. **An ALIAS IS NOT A MODEL ID**: the thing to check is
what the alias resolves to, not whether the gateway lists the alias's name. The id that
genuinely dies is **`fable`**, which the harness expands to `claude-fable-5-1` and which no
environment key can retarget.

**The ruling stands and is now simply clearer.** `haiku` and `sonnet` currently resolve to the
*same model*, so the haiku rung is cosmetic rather than cheap — and an escalation ladder that
retries haiku→sonnet re-runs the same weights. OS-level searches (grep, glob, inventories,
existence checks) fold into **Sonnet** below, for the original reason: there is no cheaper
Anthropic rung on this gateway to drop them to. Pass `sonnet`, not `haiku`, so the policy says
what it means.

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
| It is an **OS-level search** (grep, glob, file inventory) whose result is re-checked | **sonnet** — no cheaper rung exists on this gateway (Haiku struck 2026-10-01) |
| A **compiler, selftest, validator or hook**, before anyone reads it | **sonnet** |
| **Another agent**, who will re-derive it before acting | **sonnet** |
| **Nobody** — it becomes a recorded fact other work cites | **opus** |
| **Only the owner's eye** — art, the world, prose he reads | **opus**, and it goes to him |

⛔ If you cannot name the catcher, you are on row 3. "It'll be obvious" is not a catcher.

## The ladder

| | Alias | For |
|---|---|---|
| **Opus 5.5** (+fast mode) | `opus` | **Design** — design judgment, decision drafting, synthesis across contradictory evidence, rosters, specs, skill curation — always as a backgrounded subagent from BENCH. **Complex code generation** — Harmony/C#, new systems, multi-file forensics, bridge writes, the frozen world. **BENCH's window**, the orchestrator |
| **Sonnet 5.5** | `sonnet` | **Well-defined coding with a checkable outcome** — patches, defs, deploys, quicktests, fixes a selftest or validator proves. Log triage, interpretive sweeps, first drafts. **OS-level searches** — greps, globs, censuses, existence checks, inventories (folded in 2026-10-01; see below). FOUNDRY's default |

Fable is not on the ladder (owner, 2026-09-29). **Haiku is not on the ladder either, struck
2026-10-01: the sanctioned gateway serves no Haiku id, so `model: haiku` 400s rather than
resolving to any version.** Only `opus` and `sonnet` resolve to live models on this gateway;
verify with the `/v1/models` call above before trusting any alias to resolve.

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
| OS-level search: grep, glob, inventory, "does X exist", fixed-shape census | **sonnet** (folded in 2026-10-01 — the gateway has no Haiku) |
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
