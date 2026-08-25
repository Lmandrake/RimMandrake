# Kimi K2.6 as an Auxiliary AI Workforce for RimWorld Development

> ⚠️ **ANSWERED 2026-08-24 by `research/Multimodel_architecture_analysis.md`.** That assessment
> measured this project against these questions and corrects three assumptions here: the harness
> risk (§Risk 6) is largely dissolved — Claude Code talks to a non-Anthropic model through a
> gateway with two env vars and none of our hooks, skills or tooling moving; the 1M-vs-256K
> context argument does not bite, because our real artifacts (332 MB–782 MB) fit in neither and
> our session preamble is only ~6.5% of a 256K window; and the work-packet prerequisite it treats
> as the hard part **is already met** (29 of 36 open items carry `## verify` + `## criteria`).
> It also finds Sonnet 5 — full 1M context, no endpoint risk — to be the option this note does
> not consider. Read the answer before acting on the questions.

**Planning note — 2026-08-24**

## Purpose

This document is input to a project-agent planning cycle. Its purpose is **not** to prescribe where Kimi K2.6 must be used, but to identify a potentially important new resource and ask the project to determine where it creates the most leverage.

The central opportunity is simple:

> **Kimi K2.6 is currently available through NVIDIA Build as a free developer API endpoint, so work sent to it does not consume our Claude Max / Opus weekly allocation.**

That does **not** mean Kimi is unlimited, equivalent to Opus 5, or guaranteed to remain free. It means we may now have a strong, separate inference pool that can absorb useful development work while preserving scarce Opus capacity for the work where Opus provides the greatest marginal value.

The planning cycle should explicitly evaluate Kimi K2.6 as:

- a surrogate for **DECIDE**;
- a surrogate for **BUILD**;
- a surrogate for **CHECK**;
- a surrogate for **REP**;
- a temporary overflow implementation of any of those roles;
- or an **altogether different class of worker** that complements rather than imitates the existing four-agent architecture.

Do not assume that mapping Kimi one-for-one onto an existing agent is the best use of it.

---

## What Kimi K2.6 Is

**Kimi K2.6** is an open multimodal Mixture-of-Experts model developed by Moonshot AI and currently served by NVIDIA through the NVIDIA Build/NIM API catalog.

NVIDIA describes it as a **1-trillion-parameter model with 32 billion active parameters per token**, intended for long-horizon coding, agentic tool use, complex multi-step work, and image/video understanding.

Relevant capabilities include:

- strong software-engineering and coding performance;
- native function/tool calling;
- agentic multi-step workflows;
- text, image, and video input;
- open-agent-framework compatibility;
- a context window of roughly **256K tokens** (NVIDIA's catalog UI reports approximately **262K**);
- availability as a **free NVIDIA-hosted developer endpoint** at the time of this writing.

The model card reports **80.2% SWE-bench Verified**, **58.6% SWE-bench Pro**, **76.7% SWE-bench Multilingual**, and **66.7% Terminal-Bench 2.0** under the reported evaluation configurations. These numbers establish that this is a serious coding model, but they should **not** be treated as proof that it is equivalent to Opus 5 in our repository, harness, task distribution, or long-running agent behavior.

---

## The Important Economic Difference

Our normal development environment relies heavily on **Claude Opus 5**, generally using its **1M-token context** through Claude Code.

That environment is extremely capable but constrained by Claude subscription usage limits. Sustained multi-agent development, repeated verification, long sessions, and tool-heavy loops can consume the available weekly allocation.

Kimi changes the resource equation because NVIDIA inference is a **separate provider**:

- Kimi calls do **not** consume Claude Max usage.
- Kimi work can continue when conserving or exhausting Opus allocation.
- Kimi can potentially absorb high-volume work that is wasteful to perform with the most scarce model.
- Multiple Kimi-backed workers could increase total project throughput without multiplying Claude subscription consumption.

The right mental model is therefore not necessarily:

> "Kimi is cheaper Opus."

A more useful model may be:

> **"We have acquired another pool of reasonably powerful cognitive labor whose scarcity characteristics are different from Opus."**

That difference may justify changing the topology of the agent system rather than merely swapping a model underneath an existing role.

---

## Important: Free Does Not Mean Unlimited

The NVIDIA endpoint should be treated as **free but semi-rate-limited and non-guaranteed**.

NVIDIA states that Developer Program members receive free NIM API access for prototyping, research, development, testing, and experimentation. NVIDIA's API Trial Terms also state that API use is subject to NVIDIA-defined limits, may involve limited credits or access duration, and is not intended as a guaranteed production service.

Recent NVIDIA developer-forum discussions commonly report a free-tier ceiling around **40 requests per minute**, but NVIDIA staff explicitly state that actual limits can depend on the **model, use case, and overall service traffic**. Therefore, 40 RPM should be treated as an observed current operating characteristic, **not as a contractual entitlement**.

For our purposes, this is still potentially generous. A single software-development agent rarely needs 40 full LLM turns per minute. The constraint becomes more relevant if we create large parallel swarms in which many agents simultaneously perform short tool/reasoning loops.

The planning system should therefore distinguish between:

- **weekly-capacity scarcity** — a major issue with our Claude usage;
- **short-term request-rate scarcity** — the more likely Kimi constraint;
- **endpoint continuity** — NVIDIA may change limits, credits, models, or free availability.

A Kimi integration should fail gracefully and should never make the project dependent on the continued existence of a free endpoint.

---

# Kimi K2.6 vs. Our Normal Opus 5 Environment

| Characteristic | Claude Opus 5 | Kimi K2.6 via NVIDIA Build |
|---|---|---|
| Normal role today | Primary high-end development intelligence | Potential auxiliary workforce |
| Context window | **1M tokens** | **~256K / 262K tokens** |
| Max-context relationship | Baseline | Roughly one quarter of Opus |
| Coding ability | Frontier/high-end baseline for this project | Strong enough to merit serious evaluation |
| Long-horizon agent work | Major strength | Explicit design target |
| Tool calling | Yes | Yes |
| Vision | Yes | Yes |
| Video input | Provider/harness dependent | Model supports it |
| Claude Code integration | Native | Requires another harness/API integration |
| Consumes Claude weekly allocation | **Yes** | **No** |
| NVIDIA hosted price today | N/A | **Free developer endpoint** |
| Limiting resource | Subscription/API usage allocation | Rate limits, trial limits, availability |
| Service predictability | Relatively high | Lower; free endpoint can change |
| Appropriate for canonical judgment | Proven current default | Must be evaluated |
| Appropriate for cheap parallel labor | Expensive in scarce capacity | **Potentially excellent** |

## The 1M vs. 256K Context Difference Is Architecturally Important

Kimi should **not** be treated as a drop-in replacement for an Opus session whose effectiveness depends on loading enormous portions of project history, source, world design, queues, decisions, and validation state at once.

Opus 5's 1M-token context is roughly four times Kimi's currently published context capacity.

That suggests two classes of work:

### Work that naturally favors Opus

- project-wide architectural reasoning;
- decisions involving many interacting world/design constraints;
- interpreting a large fraction of the repository simultaneously;
- maintaining canonical continuity across many evolving decisions;
- tasks where subtle global context is more important than raw implementation labor;
- tasks for which failure or conceptual drift has large downstream cost.

### Work that may naturally favor Kimi

- bounded implementation work;
- isolated subsystem analysis;
- code generation and refactoring with a curated file set;
- test construction;
- log investigation;
- XML/Def inspection;
- mechanical repository audits;
- alternative implementations;
- independent code review;
- parallel hypothesis generation;
- documentation transformation;
- repetitive validation;
- tasks that can be expressed as a well-defined **work packet** substantially below 256K tokens.

A successful Kimi strategy may therefore depend heavily on improving our ability to construct **small, explicit, self-contained work packets**.

That architectural discipline is valuable even independently of Kimi.

---

# Question for the Planning Cycle

Do **not** begin with:

> "Which Claude agent should we replace with Kimi?"

Begin with:

> **"Which kinds of cognition in this project actually require Opus 5, and which kinds merely require a competent agent with the right context, tools, acceptance criteria, and verification?"**

Then determine where Kimi belongs.

---

# Option 1 — Kimi as a DECIDE Surrogate

## Potential value

DECIDE performs vision keeping, dreaming, design, continuity management, scope selection, and decisions about what enters or leaves a build.

Kimi could potentially:

- research alternatives before DECIDE sees them;
- generate design branches;
- examine precedent across the repository;
- identify contradictions;
- critique proposed mechanics;
- estimate consequences of alternatives;
- perform structured pre-analysis;
- independently challenge DECIDE's conclusions.

## Concern

DECIDE is probably the role with the **highest cost of subtle conceptual failure**.

It benefits disproportionately from:

- broad context;
- nuanced judgment;
- continuity;
- willingness to reject superficially attractive solutions;
- understanding of the project's evolving intent.

Kimi's smaller context window may also be especially relevant here.

## Hypothesis

**Kimi should initially be tested as a shadow/analyst for DECIDE rather than immediately replacing DECIDE's canonical authority.**

A valuable pattern may be:

**Kimi explores broadly → DECIDE/Opus adjudicates narrowly.**

This could dramatically reduce the amount of expensive Opus reasoning spent exploring dead ends.

---

# Option 2 — Kimi as a BUILD Surrogate

## Potential value

This is probably the most obvious direct-substitution opportunity.

BUILD work frequently has:

- explicit requirements;
- identifiable files;
- testable acceptance criteria;
- compiler/runtime feedback;
- local rather than project-global context;
- repeated edit/test/debug loops.

Candidate Kimi BUILD work includes:

- implementing defined RimWorld features;
- C# coding;
- Harmony patches;
- XML/Def work;
- refactoring;
- compilation-error repair;
- writing or extending tests;
- constructing diagnostic tooling;
- investigating errors;
- dependency tracing;
- repetitive code cleanup;
- documentation updates tied to implementation;
- implementing several alternative solutions for later selection.

## Major advantage

BUILD can often be checked mechanically.

If the task has good acceptance criteria, we can tolerate a weaker model more readily because failure is detectable.

## Hypothesis

**BUILD is the highest-priority role for direct Kimi substitution trials.**

A possible routing rule:

> If the task is well-specified, bounded, reversible, and mechanically verifiable, try Kimi before spending Opus.

Escalate to Opus when Kimi:

- repeatedly fails;
- discovers a genuine architectural ambiguity;
- needs substantially more global context;
- produces behavior that passes narrow tests but conflicts with project intent.

---

# Option 3 — Kimi as a CHECK Surrogate

## Potential value

CHECK worries, measures, tests, validates, aligns, gates, protects, and records.

Kimi may be particularly valuable here **because it is not Claude**.

Using the same model family to create and validate a solution risks correlated blind spots. A different capable model can provide genuinely independent scrutiny.

Candidate Kimi CHECK work:

- code review;
- requirements-to-implementation tracing;
- static inspection;
- test generation;
- failure-mode enumeration;
- adversarial review;
- checking XML references;
- searching for regressions;
- comparing intended behavior with implementation;
- reviewing screenshots or visual outputs;
- analyzing RimWorld logs;
- checking save compatibility assumptions;
- independently reproducing BUILD's reasoning.

## Hypothesis

**Independent Kimi verification may be more valuable than using Kimi as a simple cheaper clone of BUILD.**

A strong writer/verifier pattern could be:

**Opus BUILD → Kimi CHECK**

or:

**Kimi BUILD → Opus CHECK for high-risk changes**

or, when capacity allows:

**Kimi BUILD → separate Kimi CHECK instance → Opus only adjudicates disagreements or unresolved failures**

The planning cycle should examine whether model diversity can become an explicit V&V asset.

---

# Option 4 — Kimi as a REP Surrogate

## Potential value

REP coordinates, monitors, represents, translates, tracks, plans, and communicates with the human.

Much REP work may not require the strongest available model if the project state is already structured.

Candidate Kimi REP work:

- summarizing queue state;
- assembling status;
- identifying blocked tasks;
- collecting results from workers;
- producing human-readable digests;
- updating structured project records;
- tracking dependencies;
- detecting stale work;
- preparing candidate questions for the human;
- converting technical agent output into concise project state.

## Concern

REP is the human interface and may need unusually good judgment about:

- what actually merits interruption;
- what the user needs to know;
- contradictory agent claims;
- prioritization;
- interpreting evolving intent.

A mediocre REP that generates noise could cost more human attention than it saves.

## Hypothesis

Kimi may be excellent for **REP's information-processing workload**, while Opus or the existing REP policy retains authority over high-value human interaction.

Consider splitting REP into:

- **REP-INTERNAL** — cheap state aggregation and monitoring;
- **REP-HUMAN** — high-quality judgment and communication.

Kimi could perform most of the former.

---

# Option 5 — Do Not Make Kimi One of the Four Agents at All

This may ultimately be the highest-leverage design.

The existing agents are **roles**. Kimi is a **resource**.

Those concepts need not map one-to-one.

Consider creating a separate Kimi-backed labor pool that any canonical agent can invoke.

Possible conceptual models follow.

---

## A. Kimi Worker Pool

DECIDE, BUILD, CHECK, and REP remain canonical roles.

Each can fan bounded work out to disposable Kimi workers:

```text
                 ┌─ KIMI WORKER
DECIDE ──────────┼─ KIMI WORKER
                 └─ KIMI WORKER

                 ┌─ KIMI WORKER
BUILD ───────────┼─ KIMI WORKER
                 └─ KIMI WORKER

                 ┌─ KIMI REVIEWER
CHECK ───────────┼─ KIMI REVIEWER
                 └─ KIMI REVIEWER
```

The Kimi workers do not own project state and do not become authorities.

They receive a work packet, produce an artifact/result, and terminate.

This minimizes propagation of stale assumptions.

---

## B. Kimi SCOUT

Create a specialized exploratory role whose job is to search possibilities **before an expensive canonical agent thinks deeply about them**.

Examples:

- investigate three possible mod APIs;
- locate every implementation touching a mechanic;
- compare five approaches;
- inspect relevant upstream source;
- identify likely failure mechanisms;
- gather evidence;
- produce a concise decision packet.

Then Opus spends its scarce cognition on **selection and judgment**, not discovery.

---

## C. Kimi PROBE / Hypothesis Farm

When a problem is uncertain, ask several independent Kimi instances to solve it from different assumptions.

For example:

```text
Bug / design problem
   ├── Kimi A: diagnose from architecture
   ├── Kimi B: diagnose from logs
   ├── Kimi C: attempt minimal reproduction
   ├── Kimi D: search for interaction failures
   └── Kimi E: propose an alternate implementation
                  ↓
             Opus adjudicates
```

The relevant economic insight is that **several free independent attempts may be cheaper in scarce resources than one very long Opus investigation**.

This should be tested rather than assumed.

---

## D. Kimi ADVERSARY

Instead of asking another agent to "check the work," create an explicitly adversarial worker.

Its job is to prove the proposed implementation or decision wrong.

Inputs:

- intended requirement;
- BUILD result;
- test evidence;
- relevant code.

Outputs:

- counterexamples;
- hidden assumptions;
- missing cases;
- suspicious passes;
- regression risks;
- evidence required before acceptance.

This could be especially useful for CHECK.

---

## E. Kimi QUEUE SCAVENGER

Allow Kimi workers to consume suitable low-risk backlog items whenever they are available.

Eligible work might include:

- cleanup;
- documentation alignment;
- inventory;
- static checks;
- data extraction;
- test expansion;
- deprecated-reference removal;
- low-risk refactors;
- asset metadata checks;
- backlog investigation.

This turns spare NVIDIA capacity into project progress without occupying the primary Opus development thread.

---

## F. Kimi CONTEXT PREPROCESSOR

The 256K context limitation can itself motivate a useful function.

A Kimi worker could take a repository region and construct a concise, structured context artifact:

- subsystem map;
- API inventory;
- dependency graph;
- relevant decisions;
- known tests;
- known failures;
- unresolved questions.

That artifact can then be given to either Kimi or Opus.

This reduces repeated repo-discovery work and may reduce Opus token consumption even when Opus ultimately performs the important reasoning.

---

## G. Kimi N-WAY IMPLEMENTER

For difficult but bounded features, ask multiple Kimi workers to produce different implementations rather than forcing a single expensive agent to discover the best design sequentially.

Example:

```text
Specification
   ├── Implementation A — minimum patch
   ├── Implementation B — clean architecture
   ├── Implementation C — performance-first
   └── Implementation D — compatibility-first
                         ↓
                  CHECK / DECIDE
```

This exploits inference abundance to buy **optionality**.

---

## H. Kimi Capacity Circuit Breaker

Kimi could be integrated as an automatic overflow provider.

Routing might consider:

1. task risk;
2. context requirement;
3. mechanical verifiability;
4. current Claude capacity;
5. current NVIDIA rate pressure;
6. previous success of each model on that task class.

A task should not be routed to Opus merely because Opus is available.

Likewise, it should not be routed to Kimi merely because Kimi is free.

The router should eventually learn:

> **Use the least scarce model that reliably meets the task's assurance requirement.**

---

# Suggested Initial Routing Hypothesis

A reasonable **starting hypothesis to test**, not a final architecture, is:

| Work | First choice |
|---|---|
| Canonical project vision | **DECIDE / Opus** |
| Major architecture | **DECIDE / Opus** |
| Ambiguous cross-system design | **Opus** |
| Broad exploratory research | **Kimi** |
| Design-option generation | **Kimi → Opus adjudication** |
| Well-specified coding | **Kimi BUILD** |
| Repetitive implementation | **Kimi BUILD** |
| Compiler/test repair loops | **Kimi BUILD** |
| Difficult cross-cutting implementation | **Opus BUILD** |
| Static review | **Kimi CHECK** |
| Independent verification | **Kimi CHECK** |
| High-consequence acceptance decision | **CHECK/DECIDE with Opus as needed** |
| Repository inventory | **Kimi** |
| Context packet generation | **Kimi** |
| Status aggregation | **Kimi-assisted REP** |
| Important human-facing synthesis | **REP with strongest appropriate model** |
| Parallel alternatives | **Multiple Kimi workers** |
| Claude-limit exhaustion | **Kimi fallback wherever acceptance criteria allow** |

---

# Work-Packet Design

Kimi's smaller context window makes **work-packet quality** especially important.

A strong packet should include only what the worker needs:

```yaml
task_id:
goal:
why_it_matters:
authority:
  may_change:
  may_not_change:
inputs:
relevant_files:
relevant_decisions:
known_constraints:
acceptance_criteria:
verification_commands:
required_outputs:
escalate_if:
```

The packet should make explicit:

- what is authoritative;
- what is merely background;
- which files may be edited;
- what behavior must remain unchanged;
- what constitutes success;
- how success can be independently checked;
- what ambiguity must be escalated rather than guessed.

This reduces dependence on model identity.

---

# Critical Risks to Evaluate

## 1. Context truncation and hidden dependencies

A 256K worker can miss relationships that an Opus 1M session sees.

Mitigation:

- package context intentionally;
- require dependency discovery;
- escalate when the worker discovers scope larger than its packet;
- keep canonical architecture outside disposable workers.

## 2. False economy

Free inference is worthless if bad outputs consume substantial human or Opus time correcting them.

Measure **total cost of accepted work**, not API price.

A Kimi task is successful only if:

> Kimi execution + validation + correction costs less scarce effort than doing the task with Opus initially.

## 3. Correlated Kimi verification

Two Kimi instances are not fully independent merely because they are separate runs.

For important assurance work, model diversity can still matter.

## 4. Rate-limit bursts

Parallel agents can hit provider limits even if average usage is low.

Use:

- a centralized request queue;
- concurrency limits;
- exponential backoff;
- retry handling;
- provider health telemetry.

## 5. Endpoint instability

The free model or its limits can change.

The system should treat `Kimi` as a provider capability, not embed it deeply into project semantics.

## 6. Harness quality

Kimi is an API model, not Claude Code.

Its practical usefulness depends heavily on the agent harness that provides:

- filesystem access;
- terminal commands;
- diff/edit mechanics;
- tool schemas;
- context assembly;
- persistence;
- retries;
- permissions;
- validation;
- handoff into RimFlow/project state.

A poor harness can make a strong model appear weak.

## 7. Trial-service terms

NVIDIA's hosted free endpoint is for development/testing/prototyping rather than guaranteed production use.

Using Kimi **to develop the RimWorld project** fits the intended experimentation/development use case; building a shipped production dependency that requires NVIDIA's free trial endpoint should not be assumed acceptable or durable.

---

# What We Should Measure

Do not decide this from public benchmark scores.

Run our own evaluation against real project work.

For each candidate task, record:

- task class;
- model;
- context supplied;
- wall-clock completion;
- number of model turns;
- number of tool calls;
- number of retries;
- test result;
- CHECK result;
- defects found later;
- amount of Opus intervention;
- amount of human intervention;
- whether the result was accepted unchanged;
- whether conceptual drift occurred.

Especially measure:

### Accepted-work rate

**How often can Kimi complete a real work packet that CHECK accepts without Opus repair?**

### Escalation rate

**How often does Kimi correctly recognize that it lacks enough context or authority?**

### Correction tax

**When Kimi fails, how much expensive effort does recovery consume?**

### Parallelism benefit

**Do several Kimi attempts produce better/faster outcomes than one Opus attempt?**

### Context sensitivity

**At what task size or repository breadth does Kimi's 256K window become a practical disadvantage?**

### Role fitness

**Which of DECIDE, BUILD, CHECK, REP, or new auxiliary roles yield the greatest accepted output per unit of scarce Opus attention?**

---

# Recommended Bake-Off

Select a small set of **real pending project tasks**, not synthetic tests.

Include at least:

1. one bounded BUILD task;
2. one difficult BUILD/debug task;
3. one CHECK/review task;
4. one DECIDE/design-analysis task;
5. one REP/state-synthesis task;
6. one broad repository investigation;
7. one task solved by several parallel Kimi workers.

For each, compare Kimi K2.6 with our normal Opus 5 workflow.

Do not ask only:

> "Which response looks smarter?"

Ask:

> **"Which workflow produces accepted project state with the least human attention and the least scarce Opus consumption?"**

That is the relevant system metric.

---

# Planning Questions for DECIDE / BUILD / CHECK / REP

The planning cycle should explicitly answer the following.

### DECIDE

- Which DECIDE activities truly require 1M holistic context?
- Can Kimi perform exploration and option generation before DECIDE adjudication?
- Could Kimi act as an independent challenger to DECIDE?
- What DECIDE outputs are too consequential to delegate?

### BUILD

- What fraction of BUILD's queue is bounded enough for Kimi?
- Can task packets be generated automatically?
- Which acceptance tests allow us to safely use a less-trusted implementer?
- Should Kimi become BUILD's default child-worker provider?
- Can multiple Kimi workers implement different pieces concurrently without merge chaos?

### CHECK

- Where does model diversity improve assurance?
- Can Kimi independently validate Opus-produced work?
- Can Kimi run adversarial checks rather than merely repeat BUILD's reasoning?
- Which checks can be made mechanical enough that model quality matters less?

### REP

- How much REP work is state processing versus judgment?
- Can Kimi continuously assemble the internal project picture while REP retains human-facing authority?
- Can Kimi detect queue drift, blocked work, stale assumptions, or mismatched sprint assignments?
- Would a cheap internal REP materially reduce the amount of Opus context spent on project administration?

### Architecture

- Should Kimi be assigned to an existing station at all?
- Should it instead be an on-demand worker pool?
- Should every canonical agent be allowed to spawn Kimi workers?
- Should RimFlow route tasks by risk/context/verifiability rather than by fixed model?
- Could Kimi enable a writer/verifier architecture that was previously too expensive?
- Could Kimi enable N-way solution generation followed by Opus adjudication?
- Could Kimi perform low-priority vN work whenever primary agents are occupied?
- How should provider health, rate limits, failures, and model identity appear in telemetry?
- How do we prevent disposable workers from becoming accidental sources of canonical truth?

---

# Provisional Recommendation

**Do not replace Opus 5 globally.**

Instead, treat Kimi K2.6 as a new source of **abundant-but-not-authoritative cognitive capacity** until project-specific evaluation demonstrates otherwise.

The most promising initial applications are:

1. **Kimi-backed BUILD workers** for bounded and testable implementation;
2. **Kimi-backed CHECK workers** for independent/adversarial validation;
3. **Kimi scouts** that gather and compress evidence before Opus reasoning;
4. **parallel Kimi hypothesis/implementation workers** whose outputs are adjudicated by a canonical agent;
5. **Kimi internal-project workers** for inventory, queue maintenance, documentation alignment, and context preparation.

DECIDE should be the most conservative role to replace because project-level conceptual drift has high downstream cost and because DECIDE benefits heavily from Opus 5's 1M context and stronger judgment.

The broader opportunity is not merely to save Claude credits.

It is to move from:

> **four expensive agents doing nearly everything themselves**

toward:

> **four accountable project roles commanding a larger pool of inexpensive, disposable, specialized workers.**

If that architecture works, Opus usage becomes concentrated where it buys something genuinely scarce: **judgment, integration, ambiguity resolution, architecture, and high-consequence decisions**.

Kimi capacity is then spent on everything that can be parallelized, bounded, tested, challenged, summarized, searched, or retried.

That is the concept the planning cycle should evaluate.

---

# Current Sources

Accessed 2026-08-24.

1. **NVIDIA Build — Kimi K2.6**  
   https://build.nvidia.com/moonshotai/kimi-k2.6

2. **NVIDIA Kimi K2.6 Model Card**  
   https://build.nvidia.com/moonshotai/kimi-k2.6/modelcard

3. **NVIDIA NIM — Run NIM Anywhere / Developer Program access**  
   https://docs.api.nvidia.com/nim/docs/run-anywhere

4. **NVIDIA API Trial Terms of Service**  
   https://assets.ngc.nvidia.com/products/api-catalog/legal/NVIDIA%20API%20Trial%20Terms%20of%20Service.pdf

5. **NVIDIA Developer Forum discussion of free-tier rate limiting**  
   https://forums.developer.nvidia.com/t/request-for-nvidia-nim-api-rate-limit-increase-40-200-rpm/369472

6. **Anthropic — Claude model overview**  
   https://platform.claude.com/docs/en/about-claude/models/overview

7. **Anthropic — Claude Opus 5 guidance**  
   https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5

---

## One-Sentence Planning Directive

> **Evaluate Kimi K2.6 not simply as a cheaper replacement for Opus 5, but as a separate, free, rate-limited pool of capable agentic labor that may substitute for portions of DECIDE, BUILD, CHECK, or REP—or enable an entirely new worker-pool architecture that preserves scarce Opus 5 1M-context capacity for the decisions where it matters most.**
