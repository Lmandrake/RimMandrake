# Handing over something you cannot check yourself

## First: does it need the game at all?

**The default is source.** Answer in one line: *what can source not tell me here?*
If you cannot answer it, verify it yourself now and close the item.

| question | answered by |
|---|---|
| does the artifact say the right thing | the def, the patch, the C#, the capture |
| is the deployed copy the repo copy | `md5sum` |
| does a number match a spec | `measure`, the def dump, an offline script |
| does the ENGINE do what you cannot compute | **live** |
| does it LOOK right to a human eye | **live** |

⛔ Never ask for a live run to be thorough, to be safe, or because the artifact matters.
✅ The owner may delete any live check. Record in one line what became unverified; do not argue.

## What a live check owes

Three lines: **the call**, **the expected reading** as a number or string, and **how a pass
could be false**. The last is the only part the reader cannot reconstruct.

🔴 Name a positive observation, never "no error". An absence is the cheapest thing to produce
by accident.

## Whoever proves it, closes it

No hand-back to the author. Then:

```
grep -rl "<defName or tool or ID>" infrastructure/state/items/
```

and close whatever else it settled, naming the proof that did it.

## The four ways a check lies

- **The conditional never ran.** A `PatchOperationConditional` in a mod loading *before* the
  mod it patches matches nothing, no-ops, and prints no log line — "clean log" and "patch
  applied" are indistinguishable. Assert the load index (§5b).
- **The consumer is stale.** RimWorld reads defs once, at startup. "Deployed" and "live" are
  different claims (§6); the file mtime against the process start time is the evidence.
- **The instrument cannot see it.** A reader that returns null for a field it never captured
  reads identically to a field that is empty. Check the instrument's coverage first.
- **The sample was too small.** 2 of 10 bounds a rate loosely. Say what the run established
  — that it happens — rather than how often.
