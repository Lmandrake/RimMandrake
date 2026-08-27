---
name: efficient-subagents
description: Decide whether to spawn a subagent, and how to scope, feed and bound it so it returns 1-2k tokens instead of flooding the parent. Use before any Agent/Task call, when fanning out searches or censuses, or when a seat's context is filling with tool output.
---

# Efficient subagents

A subagent buys **one thing**: its tool output never enters your context. You pay a
fresh system prompt, a full re-read of whatever it needs, and a summary you cannot
grep. Spawn only when the thing you are avoiding is bigger than that.

## Spawn / don't

**Spawn when** the work will produce output you will not reference again — a sweep
over many files, a census, a log triage, a "which of these 40 defs mentions X".
Rule of thumb: >3 tool calls of throwaway output, or output you cannot predict the
size of.

**Do not spawn when:**
- One tool call answers it. `grep -rn 'defName' path/` is not a delegation.
- You know the file and the line. Read it.
- The answer must be exact text you will edit. A summary of a file you are about
  to patch is worse than the file.
- The subagent would need more setup prose than the task is worth. Use a `fork`
  (inherits your context) or do it yourself.

## Hard rules

1. **Never fan out duplicates for reliability.** Three agents on the same question
   is not a quorum, it is 3x cost and a tie you cannot break. If a result is
   doubtful, verify the *specific* claim with one tool call.
2. **Never spawn for something the parent does in one tool call.**
3. **>20 files to read means the ask is wrong.** Re-scope: narrow the glob, name
   the directories, or split by question — not by file count.
4. **One wide read-only sweep beats three overlapping ones.** Overlap is paid
   twice and reconciled by you.
5. **Never let a subagent write to shared state** (git, `NEXT_RELOAD.md`, queue
   files, deploys). It cannot see the other seats. It returns findings; the parent
   writes.

## Scoping the ask

One question. Bounded inputs. An explicit stop condition.

- **One question** — if the prompt has an "and also", it is two subagents or one
  narrower one.
- **Bounded inputs** — pass paths, defNames, line numbers, the values you already
  know. Never "read the repo and figure it out"; that is the parent's context
  problem being handed downstream at full price.
- **Stop condition** — "stop after the first match", "check these 6 files only",
  "if X is absent, return NOT FOUND and stop". Without one it keeps looking.
- 🔴 **Always pass `model`.** Omitting it inherits the parent — which is how every
  grep in this project's history ran on Opus. `haiku` for greps, censuses and
  existence checks; `sonnet` when the agent must interpret what it finds; `opus`
  only if you will act on the return without re-deriving it, which means asking why
  it is a subagent. Full ladder: `infrastructure/agents/Agent_Policy.md`.

## What must come back

State the shape in the prompt. Target **1-2k tokens**. Demand:

```
Return ONLY:
- VERDICT: <one line>
- EVIDENCE: up to 5 rows of `absolute/path:line` + <=15-word quote
- UNKNOWN: what you could not determine
No file dumps, no narration, no summary of your process.
```

Composability comes from **stable keys, not prose**: absolute paths, defNames,
line numbers. A parent can merge three agents' rows if every row is
`path:line -> value`. It cannot merge three paragraphs without re-reading.
If a result is big, have the agent write it to a file and return the path plus
the verdict.

## Trusting what comes back

🔴 **Grade the ANSWER. Never the exit code, the status field, or the fact that
something arrived.** A weak or cheap delegate does not fail loudly — it fails
*fluently*. Measured 2026-08-26 across three cheap models on identical tasks:

- One ran ten turns of real tool calls, lost the prompt, and replied *"I need to see
  the actual questions you'd like answered."* — clean exit, valid JSON, zero of five
  parts answered.
- One completed a task that was **already done**, rewrote tuned constants it had no
  reason to touch, and reported *"2 entries rewritten"* — a sentence indistinguishable
  from success.

⇒ Before you delegate, write down the ground truth you will check the return against.
An exact-format answer line you grade field by field beats any amount of prose. If you
cannot state what a correct return looks like, the ask is not scoped yet.

### The checklist passes what the diff catches

🔴 **A criteria checklist can only find losses in the dimensions it names.** In the
run above, a 14-check structural grader — built from the task's own criteria and
stop signs, and *calibrated to score the known-good answer 14/14 first* — passed the
regression **14/14**. Structure intact, semantics destroyed. Only `git diff` found it.

- **If a delegate wrote anything, read the diff.** Not the summary, not the checklist.
- Tuned constants, balance numbers, weights and prose are exactly what a structural
  check cannot see — and exactly what a confident delegate flattens.
- Calibrate any grader on a known-correct input **before** it judges anything. A grader
  that fails the right answer is not measuring what you think.

### Two failure modes to design the prompt against

1. 🔑 **"Is this already done?" must be answered before you delegate, not by the
   delegate.** Hand over a stale ticket and a weak worker re-does finished work —
   and re-doing is how it gets damaged. Check the target's current state yourself;
   it is one grep, and it is the parent's job.
2. 🔑 **An example's CONSTANTS are not part of its shape.** "Copy the pattern that
   file already ships" is read by a weak model as "copy that file's numbers". If you
   point at an exemplar, say explicitly which parts are the pattern and which are
   that instance's own values.

**Cheap external models are viable for read-only fan-out and not for authorship** —
everything that failed above was *writing*. The measured pool, its ranking, and the
abstention clause that removes most fabrication are in
`research/FANOUT_WORKER_EVALUATION.md`.

## Limits that actually exist

- **20 concurrent** subagents per session, then `Concurrent subagent limit
  reached` (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`). No cap on total per session.
- **Depth 3** by default — subagents may spawn subagents up to three layers below
  the main conversation; at the limit the `Agent` tool is withheld
  (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, `1` disables nesting).
- Only the **top-level** subagent's summary returns to you; nested output is
  invisible.
- A subagent cannot ask you a question mid-flight. Ambiguity comes back as a
  wrong answer.
- Practical budget here: **4-6 in flight**, not 20. Each costs ~600 MB of seat
  heap.

## Examples

**Before** (unbounded, no shape, will read hundreds of files):
> Look into our mod patches and see if anything conflicts.

**After:**
> In `/mnt/d/Luke/dev/Rimworld/src/RimMandrake/Jawa_Patches/Patches/` only, list
> every `<xpath>` that targets `ThingDef[defName="Gun_Autopistol"]`. Return rows
> of `file:line -> xpath`. Max 12 rows. If none, return NONE. Do not read
> anything outside that directory.

---

**Before** (a job for one grep):
> Spawn an agent to find where `RimBridgeServer` is registered.

**After:** run `grep -rn 'RimBridgeServer' src/ --include=*.cs` yourself.

---

**Before** (duplicate fan-out, banned):
> Three agents each confirm whether `ModsConfig.xml` lists Vanilla Expanded.

**After:** one agent, or one `grep -c` — and if the answer matters, the parent
reads the one line.
