# Evaluating NVIDIA free-tier models as FANOUT workers

Measured 2026-08-26 by REP. Scope set by the owner: **fanout agents only** — not seats.
Harnesses: `src/RimMandrake/Utils/nemotron_probe.py` (reachability, tool calls),
`nemotron_agent_trial.py` (multi-turn chain), `fanout_fabrication_trial.py` (grounding).
Raw replies: `research/fanout_fabrication_neutral_replies.txt`.

## 🔴 The finding that matters most for fanout: false premises correlate

**Every model tested accepted a false premise embedded in the prompt.** Told
*"given severityPerDay is +2.5…"* when the supplied XML plainly said `-1.2`, all of
them — nemotron, gpt-oss, stepfun alike — computed cheerfully from +2.5 and returned
9.6 hours. **Not one flagged the contradiction against the text in front of it.**

⚠️ **This is the fanout-specific risk, and it does not average out.** Fanout's whole
safety story is that independent workers disagree, so errors surface. A wrong assumption
in the SHARED prompt makes every worker wrong **the same way** — correlated error that
comes back looking exactly like consensus. ⇒ **The parent's framing is the single point
of failure. Never state a fact in a fanout prompt that the worker is supposed to find.**

## 🔑 Fabrication is promptable, and that is the mitigation

The same battery run twice on identical items:

| Framing | nemotron fabrications |
|---|---|
| With an explicit escape hatch — *"if the text does not contain the answer, say exactly: NOT IN THE PROVIDED TEXT"* | **0–1 of 7** |
| Neutral, no abstention instruction | **3 of 7** |

⛔ **My first run used the escape hatch and scored everything near-perfect — that number
was an artifact of the instrument, not a property of the models.** The neutral run is the
honest one. ✅ But the practical conclusion is strong: **an explicit abstention clause in
every fanout worker prompt removes most fabrication.** It is the cheapest safety we have.

## The invented-entity test — the decisive discriminator

Asked what `JawaIon_Overcharger` does, given a def list that does not contain it:

| Model | verdict |
|---|---|
| `nvidia/nemotron-3.5-lightning-30b-a3b` | ✅ abstained |
| `nvidia/nemotron-3-ultra-550b-a55b` | ✅ abstained |
| `nvidia/nemotron-3-super-120b-a12b` | ✅ abstained |
| `nvidia/nemotron-3-nano-30b-a3b` | ✅ abstained |
| `stepfun-ai/step-3.7-flash` | ✅ abstained |
| `openai/gpt-oss-120b` | ⛔ **invented a whole ResearchProjectDef, with XML** |
| `openai/gpt-oss-20b` | ⛔ **invented a research node and an upgrade table** |

🔴 **gpt-oss is disqualified for fanout on this alone.** A worker that manufactures a
plausible def, with plausible XML, for a name that does not exist is the exact failure
that poisons a synthesis — the parent cannot tell it from a finding.

A second trap — *"which of these defs is a ThingDef for a grenade?"* when none is —
was failed by nearly everyone, who picked `JawaIon_Stun` by name association.
**Only `nemotron-3.5-lightning-30b-a3b` refused both traps**, answering that none of the
identifiers follow grenade naming conventions.

## Ranking for fanout

| Model | fabrication resistance | sustained | agentic | latency |
|---|---|---|---|---|
| **`nvidia/nemotron-3.5-lightning-30b-a3b`** | **best — refused both traps** | 20/20 | ✅ 4 turns | 8.7 s, 25 s thinking |
| `nvidia/nemotron-3-super-120b-a12b` | good; failed the name-association trap | 20/20 | ✅ 5 turns | **1.2 s** |
| `nvidia/nemotron-3-ultra-550b-a55b` | good; failed name association | 4/5 (503s) | ✅ 4 turns | 2.5–20 s |
| `nvidia/nemotron-3-nano-30b-a3b` | fabricated a justification | 20/20 | ⛔ **looped, never answered** | 1.1 s |
| `openai/gpt-oss-120b` / `-20b` | ⛔ **invents entities** | fine | untested | fine |

⇒ **Honesty over speed for fanout**, because the parent cannot verify every worker.
`lightning` when the answer is trusted; `super-120b` when the output is cheap to check.

## Contenders: the catalog is far smaller than it looks

83 models are listed; **most are 404 for this account.** Single-call liveness sweep:
`mistral-large-2`, `deepseek-v4-flash`, `jamba-1.5-large`, `phi-3.5-moe`,
`llama3-chatqa-70b`, `yi-large`, `dbrx-instruct`, `palmyra-creative`,
`mistral-nemo-12b` — **all 404**. `gemma-4-31b-it` times out. `minimax-m3` returns
**429** (a real quota, like kimi-k3). `poolside/laguna-xs` returns 503.

**Actually invocable: the nemotron family, both gpt-oss, `step-3.7-flash`,
`muse-glimmer-30b`.** That is the whole pool. ⚠️ And it decays — 102 models on
2026-08-25, 83 on 2026-08-26, with four probed nemotrons delisted in between.
**Re-check liveness before pinning any model name into tooling.**

## Where these belong in our process

✅ **Good fanout work — bounded, and the output is cheap to verify:**
- sweeps across the 63 mod XML files and the def dump: "which files mention X"
- first-pass candidate lists for dead-artifact and superseded-doc sweeps
- `Player.log` triage — bucketing errors before a human reads them
- cross-referencing docs for contradictions, as *candidates* for me to confirm

⛔ **Not for:**
- any number that goes into a doc — see `infrastructure/state/BUILDABLE.md`; this project
  has already paid for instruments that answer confidently and wrongly, and **a model will
  never volunteer `UNMEASURED`**
- design or judgment calls
- anything whose output I cannot check more cheaply than doing it myself

🔑 **The rule that falls out of all of the above: fan out to generate CANDIDATES, never
CONCLUSIONS.** Every worker prompt carries an explicit abstention clause, and states no
fact the worker is meant to discover.
