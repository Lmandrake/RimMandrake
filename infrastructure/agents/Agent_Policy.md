# Agent_Policy — which model does which work

**Binds DECIDE, BUILD, CHECK, REP.** Read with `POLICY.md` and your own seat file.
Filed 2026-08-24, after `research/Multimodel_architecture_analysis.md` measured that **every
census, sweep and existence check in this project's history ran on Opus** — because the one line
that said otherwise sat at `skills/efficient-subagents/SKILL.md:52` and was never executed.

---

## The one question

Tier does **not** follow how hard the task looks. It follows:

> ## 🔑 If this goes wrong, WHO CATCHES IT?

That is the axis because it is the axis this project already turns on. Our register of failures is
not bad code — it is **plausible answers nobody disbelieved**: seven instruments returning
confident wrong counts in one session; ~40 bridge calls reporting success and changing nothing;
`PatchOperationConditional` returning true on no match; an `<li>` discarding a whole def and
costing 26 biomes; `strings -a -el` finding 16 of 115 names and calling it an answer.

**Cheap models are safe exactly where failure is loud, and dangerous exactly where it is silent.**

| Who catches a wrong answer | Use |
|---|---|
| A **compiler, selftest, validator or hook**, automatically, before anyone reads it | **haiku** |
| **Another agent**, who will re-derive it before acting | **sonnet** |
| **Nobody** — it becomes a recorded fact other work cites | **opus** |
| **Only the owner's eye** — art, the world, prose he reads | **opus**, and it goes to him |

⛔ **If you cannot name the catcher, you are on row 3.** `validate_patch.py` is a catcher. A
selftest is a catcher. "It'll be obvious" is not.

---

## The three tiers

| | Context | in / out $/MTok | Ratio | For |
|---|---|---|---|---|
| **Opus 5** | 1M | 5 / 25 | 1× | Judgment, propagation, adjudication, the owner |
| **Sonnet 5** | **1M** | 2 / 10 | **2.5× cheaper** | Bounded work with acceptance criteria; long sessions |
| **Haiku 4.5** | **200K** | 1 / 5 | **5× cheaper** | Disposable workers: greps, censuses, existence checks |

Prices are API list, cached 2026-06-24 from the `claude-api` skill. ⚠️ **We are on Max, so dollars
are a RATIO, not our currency** — subscription weighting per model is UNMEASURED. Never quote a
saving in dollars.

- ⭐ **Sonnet 5 has the full 1M window.** Context is therefore *never* the reason to prefer Opus
  over Sonnet. Name the judgment instead, or use Sonnet.
- ⚠️ **Haiku is a subagent tier, not a seat tier.** Our eager preamble alone is ~16.6k tokens.
  Never run a seat window on it.
- **Fable 5 is not in this policy.** If a problem defeats Opus that is a conversation with the
  owner, not a routing decision.

---

## Defaults by seat

Set per window with `/model`. Reversible in a keystroke, changes no file. Switching mid-session is
expected: drop to Sonnet for a mechanical stretch, come back to Opus to decide what it meant.

| Seat | Default |
|---|---|
| **DECIDE** | **Opus.** Rulings, and the propagation that makes one real |
| **CHECK** | 🔴 **Opus, never downgraded.** Deciding whether a measurement can be believed |
| **BUILD** | **Sonnet** where `## verify` + `## criteria` exist; **Opus** for bridge writes and the frozen world |
| **REP** | **Sonnet** for board, queue, aggregation; **Opus** to compose for the owner or carry him a number |

---

## Defaults by subagent — this is where the saving is

🔴 **Every `Agent` call takes `model`. Pass it, every time.** `haiku` · `sonnet` · `opus` · `fable`.
Enforced by `.claude/hooks/block_agent_without_model.py`, which gates only the generic built-ins —
`fork` ignores the parameter and a named agent type carries its own.

| Job | Model |
|---|---|
| Grep, glob, inventory, "does X exist", line counts | **haiku** |
| Census with a fixed output shape; reading a doc set and reporting what it says | **haiku** |
| Sweep where the agent must interpret and classify what it finds | **sonnet** |
| Fan-out whose returns will contradict each other; adversarial "try to refute this" | **sonnet** |
| Anything you will act on **without re-deriving it** | **opus** — and ask why it is a subagent |

⛔ **A subagent's return is EVIDENCE, never a finding.** It carries CONFIRMED / UNCERTAIN marks
because the seat decides what is true. That rule is what makes cheap workers safe.

⛔ **Never spawn a second worker to make a result "more reliable by replication."** Two haiku runs
are not two opinions.

---

## Five places a cheaper tier is forbidden outright

1. **Deciding whether an instrument told the truth.** `BUILDABLE.md` exists because they lie.
2. **Live bridge writes.** ~40 calls report success and change nothing; the world is frozen and
   hand-authored, with no regenerate behind it.
3. **Closing an item.** A `close` is durable truth with a citation graph.
4. **The world, and art.** *"Iterate by LOOKING."* Realism and honour are not scoreable.
5. **Text the owner reads as a conclusion** — above all a number.

---

## When a cheap worker must hand back

Cheap models do not fail by refusing. They fail by producing something confident. **Put the trigger
in the prompt:**

> Escalate instead of guessing if: the criteria do not decide the case · the change reaches files
> outside the ones named · a measurement disagrees with the item · a tool returns success and you
> cannot see the effect · you would have to invent a defName, field or namespace.

**Escalating is a success.** Record it; it is not a failed run.

---

## Record the model, or this can never be checked

🔑 **The ledger is already the instrument.** It records who claimed an item, who closed it, how long
it took (median **2.89 h**) and whether verification returned pass / partial / fail (**81 / 66 / 12**
to date). Stamp the model and it answers **accepted-work rate per model** with no new tooling.

Until a field exists, put `model=sonnet-5` in the `note` on `close`. One token, no schema change.

⚠️ **The tier profiles are CONFIRMED; the routing is judgment, and it is wrong somewhere.** Revise
this file from the ledger, not from argument.

---

## See also

`skills/efficient-subagents/SKILL.md` — scoping a worker once you have chosen its model ·
`skills/agent-fanout-research/SKILL.md` — output budgets and CONFIRMED/UNCERTAIN marking ·
`POLICY.md` § Model choice · `research/Multimodel_architecture_analysis.md` — the measurements, and
the non-Anthropic options (Kimi via gateway, FLUX.1 Kontext) that are **out of scope here**.
