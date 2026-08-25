# Agent_Policy — which model does which work

> ⏳ **PROPOSED 2026-08-24, NOT YET BINDING — awaiting the owner.** Nothing points at this file
> yet and no seat is bound by it. If you found it by accident, it is a draft. The wiring plan
> (POLICY.md § Subagents, the four seat files, `efficient-subagents`, `agent-fanout-research`,
> `CLAUDE.md`) is what is under review; delete this banner when he says go.

**Binds DECIDE, BUILD, CHECK, REP.** Read alongside `POLICY.md` and your own seat file.
Filed 2026-08-24 after `research/Multimodel_architecture_analysis.md` measured that **every
census, sweep and existence check in this project's history ran on Opus** — because the one line
in `skills/efficient-subagents/SKILL.md` that says otherwise has never been executed.

---

## The one question

Model tier does **not** follow how hard the task looks. It follows one question:

> ## 🔑 If this goes wrong, WHO CATCHES IT?

That is the axis because it is the axis this whole project already turns on. Our register of
failures is not a register of bad code — it is a register of **plausible answers nobody
disbelieved**: seven instruments returning confident wrong counts in one session; ~40 bridge calls
reporting success and changing nothing; `PatchOperationConditional` returning true on no match; an
`<li>` discarding a whole def and costing 26 biomes; `strings -a -el` finding 16 of 115 names and
calling it an answer.

**Cheap models are safe exactly where failure is loud, and dangerous exactly where it is silent.**

### The ladder — walk it top to bottom, stop at the first match

| | Who catches a wrong answer | Use |
|---|---|---|
| **1** | A **compiler, selftest, validator or hook** catches it, automatically, before anyone reads it | **Haiku 4.5** |
| **2** | **Another agent** will read it as evidence and re-derive it before acting | **Sonnet 5** |
| **3** | **Nobody** catches it — it becomes a recorded fact other work will cite | **Opus 5** |
| **4** | **Only the owner's eye** catches it — art, the world, prose he reads | **Opus 5**, and it goes to him |

⛔ **If you cannot name the catcher, you are at rung 3.** "It will probably be obvious" is not a
catcher. `validate_patch.py` is a catcher. A selftest is a catcher. A hope is not.

---

## The three tiers

Prices are Anthropic API list, cached 2026-06-24 from the bundled `claude-api` skill. ⚠️ **We are
on Max, so dollars are a RATIO, not our currency** — how Claude Code weights subscription
consumption per model is **UNMEASURED**. Use the ratio to reason about relative cost; do not quote
a saving in dollars.

| | Context | in / out $/MTok | Ratio | This is for |
|---|---|---|---|---|
| **Opus 5** | 1M | 5 / 25 | 1× | Judgment, propagation, adjudication, the owner |
| **Sonnet 5** | **1M** | 2 / 10 | **2.5× cheaper** | Bounded work with acceptance criteria; long sessions |
| **Haiku 4.5** | **200K** | 1 / 5 | **5× cheaper** | Disposable workers: greps, censuses, existence checks |

### ⭐ Sonnet 5 has the FULL 1M window

**Context is therefore never the reason to prefer Opus over Sonnet.** The reason is judgment, and
you must be able to say which judgment. "It might need more context" is not an argument for Opus
over Sonnet — it is an argument that was already answered.

### ⚠️ Haiku is a SUBAGENT tier, not a SEAT tier

200K is comfortable for a bounded worker and easy to overrun in a working session — our eager
preamble alone is ~16.6k tokens before POLICY.md. **Never run a seat window on Haiku.**

### Fable 5 is not in this policy

It exists and it is more capable than Opus on the hardest reasoning. It is also priced above
Opus-tier and has a different API surface. **Nothing here routes to it.** If a problem genuinely
defeats Opus, that is a conversation with the owner, not a routing decision.

---

## Defaults by seat

| Seat | Default | Why |
|---|---|---|
| **DECIDE** | **Opus 5** | Rulings, and the propagation that makes a ruling real. Knowing which of 411 items and ~119 docs now contradict a decision is the one job where breadth genuinely is the capability |
| **CHECK** | **Opus 5** | 🔴 **Never downgrade.** CHECK's actual work is deciding whether a measurement can be believed, against a register of instruments known to lie. A wrong pass here writes a durable false fact |
| **BUILD** | **Sonnet 5** for items carrying `## verify` + `## criteria`; **Opus 5** for live bridge writes and anything touching the frozen world | Failure is loud where the criteria exist and silent where they do not |
| **REP** | **Sonnet 5** for state aggregation, board work, queue triage; **Opus 5** when composing for the owner or carrying a number to him | A wrong number travels furthest through this seat |

**Seat model is set per window with `/model`, is reversible in one keystroke, and changes no
file.** Switching mid-session is legitimate and expected: drop to Sonnet for a mechanical stretch,
come back to Opus to decide what it meant.

---

## Defaults by subagent — this is where the saving actually is

🔴 **Every `Agent` call takes a `model` parameter. Pass it. Every time.** Allowed values:
`haiku` · `sonnet` · `opus` · `fable`. Omitting it inherits the parent, which is how we arrived
at a project where every grep ran on Opus.

| Subagent job | Model |
|---|---|
| Grep, glob, file inventory, "does X exist", line counts | **haiku** |
| Census with a fixed output shape — count these, list those, tabulate | **haiku** |
| Reading a doc set and reporting what it says | **haiku** |
| Sweep where the agent must *interpret* what it finds and classify it | **sonnet** |
| Fan-out research where returns will contradict each other | **sonnet** |
| Adversarial review — "try to refute this finding" | **sonnet** |
| Anything whose return you will act on **without re-deriving it** | **opus** — and ask why it is a subagent at all |

⛔ **A subagent's return is EVIDENCE, never a finding.** It carries `CONFIRMED` / `UNCERTAIN`
marks because the seat, not the worker, decides what is true. That rule is what makes cheap
subagents safe, and it is already in `skills/efficient-subagents/SKILL.md` — this policy only
adds which model.

⛔ **Never spawn a second worker to make a result "more reliable by replication."** Unchanged from
`POLICY.md`. Two Haiku runs are not two opinions.

---

## Routing by work class

Mapped onto the `kind` field the ledger already carries.

| `kind` | Typical routing | The catcher |
|---|---|---|
| `task` — bounded implementation | **Sonnet** | criteria + selftest + `validate_patch.py` |
| `fix` / `defect` / `bug` | **Sonnet**, unless the mechanism is unknown | reproduction |
| `build` — tooling, scripts, companion `[Tool]` methods | **Sonnet** | compiler + selftest |
| `check` — verification | 🔴 **Opus** | **nobody** — this IS the catcher |
| `decision` / `ruling` | 🔴 **Opus** | nobody; it becomes canon |
| `question` | **Opus** — it ends up in front of the owner | the owner |
| `finding` | **Sonnet** to gather, **Opus** to believe | the seat that acts on it |

### Five places a cheaper tier is forbidden outright

1. **Deciding whether an instrument told the truth.** `BUILDABLE.md` exists because they lie.
2. **Live bridge writes.** ~40 calls report success and change nothing; the target is a frozen,
   hand-authored world with no regenerate behind it.
3. **Anything that closes an item.** A `close` is durable project truth with a citation graph.
4. **The world, and art.** *"Iterate by LOOKING"* — realism and honour are not scoreable.
5. **Text the owner will read as a conclusion.** Especially a number.

---

## When a cheap worker must hand back

Give every downgraded worker its escalation condition **in the prompt**, explicitly. Cheap models
do not fail by refusing; they fail by producing something confident. Name the trigger:

> Escalate instead of guessing if: the acceptance criteria do not decide the case · the change
> reaches files outside the ones named · a measurement disagrees with what the item says · a tool
> returns success and you cannot see the effect · you would have to invent a defName, field or
> namespace.

The last one is doctrine already: **never guess a defName, field or namespace.** It is also the
single likeliest way a cheaper model quietly breaks a def.

**Escalating is a success.** A worker that stops and says "the criteria do not cover this" has
done its job. Record it; do not treat it as a failed run.

---

## Record the model, or none of this can ever be checked

🔑 **The ledger is already the measurement instrument.** It records, per item, who claimed it, who
closed it, how long it took (median **2.89 h**) and whether verification returned pass / partial /
fail (**81 / 66 / 12** to date). Stamp the model on the work and it answers **accepted-work rate
per model** with no new tooling — which is exactly the metric that decides whether this policy is
right.

Until a field exists, put it in the `note` on `close`:
```
model=sonnet-5
```
One token. Nothing else changes.

⚠️ **This policy is judgment, not measurement.** The tier profiles and prices are CONFIRMED; the
routing table is a considered opinion about our work, and it is wrong somewhere. The ledger is how
we find out where. Revise this file from the ledger, not from argument.

---

## Anti-patterns

| ⛔ Don't | Why |
|---|---|
| Downgrade because the task *looks* easy | The axis is who catches the error, not perceived difficulty |
| Upgrade because the task *feels* important | Importance without a silent-failure mode is still Sonnet work |
| Use Opus "to be safe" on a grep | That is the habit this file exists to end |
| Use Haiku for a seat window | 200K; our preamble is ~16.6k before POLICY.md |
| Prefer Opus over Sonnet "for the context" | Sonnet 5 is 1M. Name the judgment instead |
| Let a cheap worker's output become a finding | It is evidence. The seat decides |
| Spawn three cheap workers instead of one good one | Replication is not verification |
| Change the model mid-item without saying so | The ledger stamp is how we learn anything |

---

## See also

- `research/Multimodel_architecture_analysis.md` — the measurements this rests on, and the
  non-Anthropic options (Kimi via a LiteLLM gateway, FLUX.1 Kontext for art) that are **out of
  scope for this file**. This policy covers Anthropic tiers only.
- `skills/efficient-subagents/SKILL.md` — how to scope, feed and bound a subagent once you have
  chosen its model.
- `skills/agent-fanout-research/SKILL.md` — output budgets and CONFIRMED/UNCERTAIN marking.
- `POLICY.md` § Subagents — the two hard rules that predate this file and still bind.
