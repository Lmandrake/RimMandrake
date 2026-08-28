# Models and tokens

You burn a week's Max allocation in ~4 days. The levers below are ranked by expected
savings; the model ladder maps the full current Anthropic line onto this project's
actual actions.

## §1 Token levers, ranked

1. **The doctrine tax (biggest, recurring, input-side).** 30–50k tokens of
   constitution+skills+memory per wake, × 4 windows, × every reboot (F1). The charter
   cuts the constitution to ~1k tokens; the topology cuts windows from 4 to 2; skill
   curation (WORKING_PATTERNS §3) halves the skill load over time. Combined this is a
   several-fold reduction in fixed input cost per working day — the single largest
   lever available.
2. **Model tiering (recurring, both sides).** Everything currently runs at the top of
   the ladder. Moving FACTORY to Sonnet and fan-out to Haiku cuts the *price of the
   same tokens* by 3–10× on the majority of daily work (§2).
3. **Verification ceremony (output + tool calls).** The reversibility table deletes
   claim/start/verify/spec on T1/T2 work — which the ledger says is most work
   (361 closes vs 197 verifies, and verifies concentrate on things that never needed
   them, F3).
4. **Stale-item burns.** The stale-drop default converts each ~10-minute
   already-done verification into one grep (F6).
5. **The shrink treadmill.** Retiring doc budgets ends the recurring "re-fit prose
   under the limit" sessions (F4).
6. **Report length.** "Done, `<hash>`" as the T1 report form. The SPEED ruling
   already says this; with 200 fewer competing rules it will actually bind.

Worth stating: your prompt-caching already softens repeated context within a session;
the levers above attack what caching cannot — cold wakes, four parallel cache lines,
and paid *output* (ceremony prose, reports, re-verification narration).

## §2 The model ladder for this project

Current line: **Haiku 4.5 · Sonnet 5 · Opus 5 (+fast mode) · Fable 5** (this model;
Mythos-class tier above Opus). External free tier: NVIDIA nemotron (§4).

| model | use it for (this project's actions) | do not use it for |
|---|---|---|
| **Haiku 4.5** | Fan-out greps, censuses, existence checks, file inventories, log bucketing, contact-sheet assembly, `path:line` sweeps, roster/index regeneration checks — anything whose answer is enumerable and the parent will verify | Anything requiring judgment about what it found; anything it writes that lands unreviewed |
| **Sonnet 5** | **FACTORY's default.** XML patch authoring, def edits, texture pipeline driving, deploys, quicktest rounds, Player.log triage, subagent sweeps that must *interpret* (staleness probes, audit passes), first drafts of docs and art briefs | Rulings, redesigns, multi-constraint C# debugging where the first hypothesis being wrong costs a load |
| **Opus 5** | Per-item escalation from FACTORY: Harmony/C# work, bridge-tool design, multi-file refactors, T3 item execution, gnarly load-order forensics. **Fast mode** when you're waiting on it interactively — same model, lower latency, ideal for BENCH-style back-and-forth on hard problems | Routine queue work (that's paying Opus prices for Sonnet tasks — the current default, and lever #2) |
| **Fable 5** | **PAIR.** Design judgment with you, decision drafting, campaign/creative direction, synthesis across contradictory evidence, the periodic skill-curation session (deciding what to *delete* is the hardest editorial task in the shop), and any redesign-of-the-process work | Being four resident windows. One Fable window at your side is the right spend; Fable running greps is the wrong one |

**Escalation rule of thumb:** escalate the *model*, never the *ceremony*. A hard
problem gets a smarter model on the same short leash — not more spec sections. Put
the tier in the item line (`model: opus`) when filing anything you already know is
hard; otherwise FACTORY starts at Sonnet and escalates itself after one failed
attempt, noting the escalation in the closing commit.

**Subagents:** the existing rule (always set `model`) is right and stays. Default
Haiku for enumeration, Sonnet for interpretation — `efficient-subagents` already says
this; under the new topology it finally becomes the common case instead of the
exception, because FACTORY at Sonnet spawning Haiku is the normal shape of a sweep.

## §3 Nemotron / free-compute verdict

Your instinct ("statistics of its usage appear nearly useless for our purposes") is
half right, and your own evaluation (`research/FANOUT_WORKER_EVALUATION.md`) found
the half that works:

- **Keep it for exactly one job: candidate narrowing over corpora you'd otherwise
  grep with a model.** Measured shape: 57/57 true negatives, zero fabrications with
  the abstention clause, but it *missed a real hit* — so it narrows, it never proves
  absence, and no number it returns lands in a doc unconfirmed. Player.log bucketing,
  "which of these 60 XML files mention X," first-pass superseded-doc candidates.
- **Drop the "highly templated code" idea.** Everything that failed in your own
  evaluation was *writing* — it rewrote tuned constants it had no reason to touch and
  reported success. Templated code is still writing; the review cost of checking its
  output exceeds Haiku's price for doing it right. Haiku 4.5 is the correct floor for
  generation.
- **Cap further harness investment.** `nemotron_fanout.py` works; the ceiling
  scripts answered their question. The catalog decays daily and the workforce saves
  single-digit dollars per week against Haiku — do not spend Fable-hours improving
  it. Park it; use it when a sweep is embarrassingly parallel and zero-stakes.
