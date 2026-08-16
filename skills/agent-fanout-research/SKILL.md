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
