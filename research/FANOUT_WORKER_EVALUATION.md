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

## 🔴 How BIG a job? Measured 2026-08-26, after the owner reframed the question

*"Perhaps we should be attempting to determine the max job size these lesser agents can
handle, rather than watching them fail at something big."* — owner. He is right, and the
answer is not the axis anyone would pick. Harness:
`src/RimMandrake/Utils/nemotron_ceiling.py` (`--axis haystack|questions|enumerate`).

**Three synthetic axes swept on `nemotron-3.5-lightning-30b-a3b`. None of them bound:**

| axis | largest size tested | score |
|---|---|---|
| one needle in a growing haystack | 120 000 chars | 3/3 |
| independent questions in one call | 8 | 3/3 |
| items that must ALL be examined (a count) | 32 | 4/4 |

19–20 of 20 at the top of every axis, and the isolated failures were **non-monotonic** —
a larger size passing after a smaller one failed. ⛔ That is noise, not a ceiling, and the
harness now refuses to report a number from a non-monotonic sweep.

### What actually binds: completion tokens spent reasoning

One real 400-line repo file — `GalacticEmpire.xml`, a trivial **7 833 input tokens** —
defeated it completely:

    WITH comments      ptok=7833  ctok=8192  ->  0 of 3 reached an answer
    comments STRIPPED  ptok=2963  ctok~7800  ->  2 of 3 answered correctly

**Every failure stopped at exactly the 8 192 completion cap.** The model narrates its way
through every candidate element and runs out of budget mid-thought; **63% of that file is
commentary**, and the commentary is what it spends the budget on. Raw evidence:
`research/nemotron_distractor_density_2026-08-26.txt`.

⇒ 🔑 **Size a cheap worker's job by how much it will NARRATE, not by how much you send.**
Stripping comments before dispatch is free and is the highest-leverage change available.
A task that classifies EVERY element costs far more output than one that finds ONE thing,
at identical input length. ⚠️ **A reply that stopped exactly at the cap is a truncation,
not an answer** — and it arrives looking like a careful analysis that simply has no
conclusion. Check `completion_tokens` on every return.

### And cite-check the evidence even when the verdict is right
Two runs, identical prompt, identical input, `temperature: 0`: `121, 131, 144` and
`121, 129, 142`. Ground truth is the first. The VERDICT was right both times; the
**line numbers were not** — and the line numbers are the part that gets pasted into a doc.

### Two instrument defects this sweep produced, both already fixed
Recorded because both are the house failure mode — an instrument answering confidently:
* An answer shape written as `<1> | <2>` was **echoed back literally** instead of filled
  in, scoring a correct model as a failure. Never hand a model angle-bracket placeholders.
* A size for which **no jobs could be built** printed as `0/0`, indistinguishable from
  "tested and scored zero". It now prints `UNMEASURED` and says why.

## ✅ The loop closed: the same sweep, with the sizing rule applied

The 60-file sweep that scored **0 hits** before the sizing rule was re-run with comments
stripped and the completion cap raised. Dispatcher:
`src/RimMandrake/Utils/nemotron_fanout.py`. Raw:
`research/nemotron_fanout_sweep_2026-08-26.json`.

Question: *does this file contain a `PatchOperationReplace` whose xpath targets
`pawnGroupMakers`?* Ground truth by grep: **3 of 60**.

| | before | after |
|---|---|---|
| true positives | 0 | **2 of 3** |
| false positives | 0 | **0** |
| false negatives | 3 | 1 (`HomesteadDefenseLeague.xml`, 1 Replace, abstained) |
| truncated / malformed | 12 | **0** |
| correct abstentions | 48 | **57 of 57** |

⇒ **57 of 57 true negatives and zero fabrications across 60 real files.** That is the
property fan-out actually needs — it will not invent work for you — bought at the cost of
a recall miss. 🔑 **Use it to NARROW a corpus, never to prove absence.** 12.7 min wall on
8 workers, free.

### Two more instrument defects, both mine, both caught by ground truth
* ⛔ **A negative VERDICT was scored as a HIT.** The model answered *"VERDICT: No Replace
  targets pawnGroupMakers"* — a correct NO, filled into the answer shape instead of using
  the abstention token — and the classifier called it a find. That was the sweep's only
  "fabrication", and it was the instrument's. `classify()` now returns `NEGATIVE`.
* ⚠️ **Stripping comments destroys line-number provenance.** Every `EVIDENCE` line number
  is relative to the *stripped* body and will not match the file on disk. Re-locate by the
  quoted text, never by the number. The dispatcher now says so on every run.

🔑 **The pattern across every instrument built today:** each one was calibrated against an
answer already known, and each one was wrong the first time in a way that produced a
clean, plausible number. Not one was caught by reading its output.

