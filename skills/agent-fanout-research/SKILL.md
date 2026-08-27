---
name: agent-fanout-research
description: Answer a broad question by launching several agents at once on different evidence domains, then compose returns that contradict each other. Covers choosing the domain split (local source, binary/data, web, installed inventory), why the disk thread beats the web thread on any claim about this machine, per-agent output budgets and CONFIRMED-vs-UNCERTAIN marking, forbidding file writes, and correcting the synthesis in the record when a later return overturns an earlier one. Use when a question is too broad for one thread, when you are about to investigate four things serially, or when web research and local facts might disagree.
---

# Fan-out research

Related: `efficient-subagents` decides **whether** to spawn one and how to bound its
token cost. This skill assumes you have decided yes, and is about the **shape of the
fan** and what to do when the returns disagree.

---

## 1. When a fan-out is the right instrument

Fan out when the question decomposes into **domains that use different evidence**, not
into subtasks of one investigation.

The worked example, 2026-08-15 — *"how do we build one world and keep it?"* — split four
ways:

| agent | domain | evidence it alone could reach |
|---|---|---|
| 1 | **local DLL / source audit** | `ilprobe` on the engine, what the code actually does |
| 2 | **savegame binary structure** | the `.rws` on disk, its arrays and encodings |
| 3 | **web research** | published mods, forum answers, what other people did |
| 4 | **installed-mod inventory** | what is on THIS disk and what is active |

The synthesis was better than any single thread and took **one wall-clock pass**. Run
serially it would have been four, and thread 3 would have poisoned the answer before
thread 4 could correct it (see §2).

⛔ **Do not fan out** when the second question depends on the first's answer — that is a
pipeline, and running it in parallel just produces one wasted agent. Do not fan out a
single search across four synonyms either; one agent handles synonyms fine.

## 2. 🔴 THE BIGGEST LESSON: the local source beat the web every time

**Web agent's finding:** a mod called *WorldEdit* exists, it is abandoned, world editing
is not really available.

**Inventory agent's finding, from disk:** **WorldEdit 2.0 is INSTALLED and ACTIVE** — a
different, current mod, a full planet editor.

The web answer was not stale so much as **about a different object**. It was correct
about the general published landscape and wrong about this machine, and it arrived first
and sounded authoritative.

⇒ 🔑 **A published answer about the general case is not an answer about THIS install.**

* **Always pair a web thread with a disk thread** when the question has any "what do we
  have" component.
* **On any fact about the local machine, the disk thread WINS by default.** Not "is
  weighed against" — wins. The web thread's job is vocabulary, approaches and names to
  go looking for; the disk thread's job is what is true here.
* ⚠️ **The web thread will sound more confident**, because a published article is
  written in finished prose and a directory listing is not. Discount for it deliberately.

## 3. Scoping so the answers COMPOSE

* **One domain per agent, stated as a domain, not as a task list.** "Everything about
  the savegame binary format" composes with the others; "check these six things" returns
  six unrelated fragments and you do the synthesis anyway.
* 🔴 **Give an explicit output budget in words** — *"return under 400 words"* — or they
  flood the parent and you have paid for a subagent and received a transcript. The
  budget is the single highest-leverage line in the prompt.
* 🔴 **Set `model` per agent — it is the second.** A fan-out is where the cost lands:
  four agents at the parent's tier is four times the wrong price. `sonnet` for a
  domain the agent must interpret, `haiku` for one it only has to enumerate.
  `infrastructure/agents/Agent_Policy.md`.
* **Demand structure that survives merging:** a finding per line, each marked
  **CONFIRMED** or **UNCERTAIN**, each with its evidence (a path, a defName, a URL).
  Unmarked confidence is the thing that makes contradictions unresolvable later.
* **Require SOURCE URLs on web work.** Without them you cannot check publication date,
  and you cannot tell an official page from a five-year-old comment.
* **"Do not write files"** unless that agent owns a deliverable. Four agents each writing
  a notes file leaves you with four files to read and no synthesis. The return message
  *is* the artifact.
* **Say what the parent already knows** so nobody re-derives it, and name the sibling
  domains in one line each so nobody duplicates a sibling's sweep.

## 4. 🔴 Composing contradictory returns

Contradiction is the normal, valuable case — it is why you ran four and not one.

1. **Classify the disagreement before resolving it.** Different *object* (WorldEdit vs
   WorldEdit 2.0), different *time* (published 2021 vs disk today), or genuine conflict
   about the same thing. The first two are not conflicts and dissolve on naming.
2. **Apply the precedence rule:** measured on this machine > read from this machine's
   source > published general claim. Say which one you applied.
3. 🔴 **When a later return overturns an earlier synthesis, correct it IN THE RECORD,
   not just in chat.** The commit
   `3a9541b Correct the record: WorldEdit 2.0 is active and is a full planet editor`
   exists because the wrong version had already been written down. **A correction that
   lives only in a conversation has not happened** — the next reader finds the doc.
4. **Keep the overturned claim visible with its correction**, so nobody re-derives it
   from the same web page next month.

## 5. Operational notes that cost time

* ⚠️ **A stale or duplicate completion notification is normal and means nothing.** You
  will be told an agent finished that you already read, or told twice. Do not re-spawn on
  it, and never write the notification yourself — if the return has not arrived, say it
  is still running.
* **Do not run a search yourself once you have delegated it.** Duplicated work is the
  most common way a fan-out ends up slower than a serial pass.
* **Launch all of them in ONE message.** Sequential `Agent` calls serialise the wall
  clock, which is the entire thing you were buying.
* **Expect one thread to return nothing useful.** The four-way split had a clear weakest
  member; that is a healthy fan, not a mistake. A fan where all four return gold means
  the question was narrower than you thought and one agent would have done.
* **Synthesise yourself.** Do not hand four returns to a fifth agent to merge — the
  contradiction handling in §4 needs the parent's own knowledge of what the question was
  for.

## 6. Cheap external models as the worker pool

Fan-out workers do not have to be full-price agents. Measured 2026-08-26 against
NVIDIA's free endpoint: read-only census and retrieval work is exactly what the cheap
models are good at — 5/5 on a five-part chained repo task, needle retrieval at 616k
prompt tokens, correct tool-call arguments, no quota wall. **Everything that failed
them was WRITING**, which a fan-out worker never does. Ranking, liveness and the
harnesses: `research/FANOUT_WORKER_EVALUATION.md`.

Three rules carry over, and they matter more with a cheap worker than a strong one:

* 🔴 **Never state a fact in the prompt that the worker is supposed to find.** Every
  model tested accepted a false premise embedded in the ask and computed cheerfully
  from it, ignoring the text in front of it. ⚠️ **This is the fan-out-specific
  failure and it does not average out:** a wrong assumption in the SHARED prompt makes
  every worker wrong *the same way*, and correlated error comes back looking exactly
  like consensus. The parent's framing is the single point of failure.
* ✅ **Put an explicit abstention clause in every worker prompt.** *"If the text does
  not contain the answer, reply exactly: NOT IN THE PROVIDED TEXT."* Measured, same
  battery, same items: fabrications fell from 3-of-7 to 0-or-1-of-7. It is the
  cheapest safety available. ⛔ But do not then grade the run on that instrument — an
  escape hatch makes every model look near-perfect and hides which ones fabricate.
* 🔑 **Fan out for CANDIDATES, never CONCLUSIONS.** A worker that invents a plausible
  entity, with plausible detail, for a name that does not exist is the failure that
  poisons a synthesis, because the parent cannot tell it from a finding. Two of the
  models tested did exactly that. Anything that lands in a doc as a number gets
  confirmed by the parent.

⚠️ **The catalog decays.** 102 invocable models one day, 83 the next, with four probed
models delisted in between. Re-check liveness before pinning any model name into
tooling; never take one from a doc.

## 7. Sizing a cheap worker's job — the ceiling is OUTPUT, not input

Measured 2026-08-26 on `nemotron-3.5-lightning-30b-a3b`, after the owner reframed the
question from *"does it fail at something big"* to *"how big a job can it take"*. Three
synthetic axes were swept and **none of them bound**:

| axis | result |
|---|---|
| one needle in a growing haystack | clean to **120 000 chars** |
| independent questions in one call | clean to **8** |
| items that must ALL be examined (a count) | clean to **32** |

Near the top of every axis it scored 19–20 of 20. ⛔ **Do not read a "ceiling" off a
sweep that is not monotonic** — a larger size passing after a smaller one failed means
you measured noise. Guard for it; `nemotron_ceiling.py` refuses to report one.

🔴 **What actually binds is COMPLETION tokens spent reasoning.** The same model, given
one real 400-line repo XML file — a trivial **7 833 input tokens** — answered **0 of 3**,
every attempt stopping at exactly the 8 192-token completion cap with its answer never
reached. It narrates its way through every candidate element and runs out of budget
mid-thought. Strip the file's comments (63% of it was commentary) and the same question
on the same file answers **2 of 3**.

⇒ **Size a cheap worker's job by how much it will NARRATE, not by how much you send.**
- **Strip prose, comments and near-miss text before handing a file to a cheap worker.**
  It is the single highest-leverage thing you can do, and it is free.
- A task that requires *classifying every element* costs far more output than one that
  requires *finding one thing*. Same file, same length, completely different job.
- Raise `max_tokens` generously, then check `completion_tokens` on every return. ⚠️ A
  reply that stopped exactly at the cap is a TRUNCATION, not an answer — and it arrives
  looking like a thoughtful analysis with no conclusion.

⚠️ **Cite-check every line number, even when the verdict is right.** Two runs of the
identical prompt, identical input, `temperature: 0`, returned `121, 131, 144` and
`121, 129, 142`. The first is correct; the second is wrong twice, by two lines. The
worker's VERDICT was right both times. **Its EVIDENCE was not**, and evidence is the
part you were going to paste into a doc.

