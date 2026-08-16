---
name: frozen-artifacts
description: Protect a file that holds a human's decisions from the generator that would silently regenerate over it — and, more often, decide NOT to. Covers the three tests a file must pass before it deserves a freeze, writing the frozen flag and its meaning into the artifact itself, making only the overwriting generator refuse while the reading one stays free, putting the unfreeze instructions in the refusal message, and the whole-file auto-writer that deletes top-level keys it does not recognise. Use when a curation export, spec, roster, prefill or hand-built artifact is finished and something else can rewrite it, or when someone proposes locking a file.
---

# Frozen artifacts

## 0. 🔴 Read this before you freeze anything

Owner, 2026-08-16, on being shown the first freeze:

> *"don't get too excited, this could be annoying if you keep freezing things
> unnecessarily, should remain easy to unfreeze."*

**Freezing is a cost paid by every future person who touches the file.** It is a
refusal, a flag to clear, and a step to remember. A repo full of frozen files is a repo
where nothing can be regenerated and everybody has learned to pass the override flag by
reflex — at which point the guard protects nothing and only slows people down.

⇒ **The default is DO NOT FREEZE.** This skill is mostly about the three tests, and only
then about the mechanism.

---

## 1. The three tests. All three, or do not freeze.

| # | test | if false |
|---|---|---|
| **a** | **A human spent real effort on decisions in this file** — judgement calls a machine cannot reproduce | it is derived; regenerate it freely |
| **b** | **A generator exists that would overwrite them** without being asked to | a commit already protects you; git restores it |
| **c** | **The overwrite would be hard to notice** — no error, no visible break, plausible-looking output | you will catch it; a comment is enough |

**Worked negative examples, so the bar is clear:**

* A def dump, a contact sheet, a `--stat` report ⇒ **fails (a)**. Regenerating it is the
  point of having it.
* A hand-written design doc nothing generates ⇒ **fails (b)**. Nothing is coming for it.
  A commit is the whole protection it needs.
* A `ModsConfig.xml`-shaped file whose corruption produces an immediate, loud failure ⇒
  **fails (c)**. Being wrong announces itself.

✅ **Passes all three:**
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review\worldmap_elements.prefill.json` —
the owner's 449-row keep/cut curation (296 whitelisted, 52 rejected, 2 deliberately
undecided, 332 notes), against `worldmap_prefill.py`, which would rewrite the whole file
with an agent's original *guesses* and produce a file that looks exactly as valid.

⚠️ **When two of three are true, say so and let the human decide.** Do not freeze on your
own initiative to be helpful — the owner's caution above is precisely about that reflex.

## 2. The flag lives INSIDE the artifact, and it says what it MEANS

Four keys, not one. A bare `"frozen": true` tells the next reader nothing about whether
it still applies.

```json
"frozen": true,
"frozenOn": "2026-08-16",
"frozenBy": "owner",
"frozenMeaning": "FROZEN by the owner 2026-08-16. These are the shipping curation
  decisions for world-map elements. Do NOT regenerate the pre-fill over this file -
  worldmap_prefill.py would overwrite the owner's calls with CHECK's guesses. Posture
  is WHITELIST: the 2 rows left undecided are STRIPPED, deliberately."
```

* **Name the generator that must not run.** "Do not regenerate" is useless; a filename
  is actionable.
* **`frozenBy` distinguishes an owner ruling from an agent's caution** — the two carry
  very different weight when someone is deciding whether to override.
* In a format with no room for extra keys, the flag goes in a sidecar named after the
  file, and the refusal reads the sidecar. Never only in a doc — docs are not on the path
  anyone walks.

## 3. Freeze the WRITER, not the artifact, and only the writer that overwrites

Two scripts touch that file. Exactly one is dangerous.

| script | what it does | frozen? |
|---|---|---|
| `worldmap_prefill.py` | **writes** the pre-fill — would replace the owner's calls | 🔴 **refuses** |
| `worldmap_review.py` | **reads** it and rebuilds the HTML sheet | ✅ untouched |

🔑 **Regenerating the VIEW must stay free.** If freezing the data also freezes the sheet
that displays it, the human loses the ability to look at his own decisions, and the
freeze becomes the annoyance the owner warned about. Trace every consumer and lock only
those that write.

The guard sits at the top of the script, before it can do anything:

```python
if "--i-know-this-overwrites-the-owners-decisions" not in sys.argv:
    print("REFUSING: %s is FROZEN (owner, 2026-08-16)." % path)
    print("Re-run with --i-know-this-overwrites-the-owners-decisions to replace his calls.")
    sys.exit(1)
```

* **A comment saying "do not run this" is not a guard.** It is read after the damage.
* **Name the override flag after the consequence**, not after the mechanism. Nobody types
  `--i-know-this-overwrites-the-owners-decisions` by accident, and nobody types it
  without having read what it says. `--force` fails both tests.

## 4. 🔑 Unfreezing is ONE obvious step, and the instructions live in the refusal

**The refusal message is the best place in the world to put the unfreeze instructions,
because it is where the person is standing at the moment they need them.** Not in a
README, not in this skill, not in a commit message.

Unfreezing is two things and no more:

1. Run the generator with the override flag — which the refusal just printed.
2. Set `"frozen": false` (or drop the four keys) in the artifact.

⚠️ **Never make unfreezing require finding a doc, remembering a convention, or asking
another seat.** If it does, the freeze will one day be defeated by someone hand-editing
the guard out of the script, and then it is gone permanently and silently.

## 5. Say what freezing COSTS, at the moment of freezing

A freeze converts "not yet decided" into "decided, negatively", and the human may not
have noticed he was doing that.

Under **whitelist posture**, rows left undecided are *stripped*. At freeze time the two
were named out loud: **`VEE_Cactus_Barrel` and `VEE_Cactus_Beavertail`**, both occurring
0 times in the current world. The owner froze with them open, so the cut is deliberate —
but it is deliberate *because it was named*.

⇒ Before writing the flag, produce the sentence: **"freezing now means X, and here are
the specific rows that changes."** Then freeze.

## 6. 🔴 The trap: a whole-file auto-writer DELETES keys it does not know about

Measured, and it nearly erased the freeze on the day it was written.

The review sheet auto-saves by **rewriting the entire JSON from its in-memory model**.
The file had meanwhile gained `frozen` / `frozenOn` / `frozenBy` / `frozenMeaning` from a
different commit — keys the page had never heard of. **The first keystroke in the sheet
would have silently removed all four**, leaving a file that still validated, still
loaded, and was no longer frozen.

⇒ **Read the existing file, carry unknown top-level keys through verbatim, re-emit them.**
Your writer is not the only author of its own file.

✅ **Prove it byte-for-byte:** simulate the write and diff it against disk. The first
auto-write must produce a **zero-line `git diff`**. Anything else means the format
drifted, every future diff is noise, and a deletion is hiding in it.

⚠️ The generalisation is bigger than freezing: **any component that serialises a whole
document from a partial model is a deletion engine.** The freeze marker is just the case
where you notice.

## 7. Candidates in this repo

| artifact | state |
|---|---|
| `design\Jawa\worldbuilding\review\worldmap_elements.prefill.json` | ✅ **frozen 2026-08-16**, owner. `worldmap_prefill.py` refuses. |
| `src\Jawa\ideoligion\The Salvation.rid` | **candidate** — hand-authored ideoligion, and anything that re-emits it from a spec would overwrite real authoring. Not frozen; apply §1 before doing it. |
| the shipped world savegame | **candidate, strongest case** — 🔴 per `CLAUDE.md` the world is built **by hand, once, and frozen**; players receive it and nothing regenerates behind it. A file with no regenerate path behind it is exactly what a freeze is for. |

⚠️ Note that all three of these are project-scale decisions. That is the correct rate.
**One freeze a month is healthy; three in an afternoon means the tests in §1 are not
being applied.**
