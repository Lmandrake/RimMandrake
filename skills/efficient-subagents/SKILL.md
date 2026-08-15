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
- **Cheap model for cheap work.** `model: haiku` for greps, censuses, existence
  checks.

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
