# Agent_Policy — which model does which work

**Binds BENCH and FOUNDRY.** Read with `CHARTER.md`. Revised 2026-08-27 for the
two-window topology and the full current Anthropic line; the routing axis is
unchanged and still measured, not argued.

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
| A **compiler, selftest, validator or hook**, before anyone reads it | **haiku** |
| **Another agent**, who will re-derive it before acting | **sonnet** |
| **Nobody** — it becomes a recorded fact other work cites | **opus** |
| **Only the owner's eye** — art, the world, prose he reads | **opus**, and it goes to him |

⛔ If you cannot name the catcher, you are on row 3. "It'll be obvious" is not a catcher.

## The ladder

| | Context | For |
|---|---|---|
| **Fable 5** | 1M | BENCH: design judgment with the owner, decision drafting, synthesis across contradictory evidence, the skill-curation session |
| **Opus 5** (+fast mode) | 1M | Per-item escalation: Harmony/C#, bridge writes, the frozen world, multi-file forensics. Fast mode for interactive latency, same model |
| **Sonnet 5** | 1M | FOUNDRY's default: patches, defs, deploys, quicktests, log triage, interpretive sweeps, first drafts |
| **Haiku 4.5** | 200K | Disposable subagents: greps, censuses, existence checks, inventories. Never a window |

Escalate the **model**, never the ceremony: a hard problem gets a smarter model on
the same short leash. Put `model: opus` on an item you already know is hard;
otherwise FOUNDRY starts at Sonnet and self-escalates after one failed attempt,
noting it in the closing commit. External free workers (nemotron): candidate
narrowing only, never conclusions, never writing — `research/FANOUT_WORKER_EVALUATION.md`.

## Subagents — this is where the saving is

🔴 **Every `Agent` call takes `model`. Pass it, every time**
(`block_agent_without_model.py` refuses otherwise).

| Job | Model |
|---|---|
| Grep, glob, inventory, "does X exist", fixed-shape census | **haiku** |
| Sweep where the agent must interpret or classify | **sonnet** |
| Fan-out whose returns will contradict; adversarial refutation | **sonnet** |
| Anything acted on **without re-deriving it** | **opus** — and ask why it is a subagent |

A subagent's return is EVIDENCE, never a finding — it carries CONFIRMED/UNCERTAIN
and the window decides what is true. Never spawn a duplicate for "reliability".

## Four places a cheaper tier is forbidden outright

1. **Deciding whether an instrument told the truth** (`BUILDABLE.md` exists because they lie).
2. **Live bridge writes** — the world is frozen and hand-authored, no regenerate behind it.
3. **The world, and art** — *"iterate by LOOKING"*; realism is not scoreable.
4. **Text the owner reads as a conclusion** — above all a number.

## The escalation clause every cheap-worker prompt carries

> Escalate instead of guessing if: the criteria do not decide the case · the change
> reaches files outside the ones named · a measurement disagrees with the item · a
> tool returns success and you cannot see the effect · you would have to invent a
> defName, field or namespace.

Escalating is a success; record it. Stamp the model on closes (`model=sonnet-5` in
the `note`) so the ledger can answer accepted-work rate per model.
