# Building a minimal load to corner a bug

_The **trigger** is in `SKILL.md` §2 — three failed hypotheses deep, stop
bisecting downward. This is the **procedure**, once you have decided to run it._

## Why minimise rather than keep bisecting

Removing one suspect at a time from a 500-mod stack costs a full load per guess,
and only ever tests the guess you already had. Cutting to the ~20 mods that can
possibly be involved costs **one** load, loads in a couple of minutes instead of
half an hour, and answers a strictly better question: *does the feature work at
all in isolation?*

Either answer is progress:

- **It works** — you now have a known-good baseline to bisect *upward* from, in
  halves, which converges in log₂ loads rather than linearly.
- **It does not** — the fault is in the feature's own mods rather than in the
  stack, which is a far smaller search and needs no more big loads at all.

## Derive the minimal set — do not guess it

Guessing reproduces the same blind spot that cost you the first three loads.

1. **From a live def dump**, list the defs the feature actually depends on and
   read off their owning `packageId`.
2. **Walk the transitive `modDependencies` closure** from each `About.xml`.
3. **Check what your own patch mod references from outside that set.** Anything
   behind a `PatchOperationConditional` or `PatchOperationFindMod` guard will
   silently no-op and can be left out. An unconditional `Defs/` reference will
   **dangle** and must be satisfied.
4. **Back up the full `ModsConfig.xml` first**, under a name that says how many
   mods it had — the count is what makes the backup identifiable later.

⚠️ Name the backup by content, not by date alone, and **never pin a doc or a
script to that filename**. A pinned baseline filename is the classic stale
instruction: the file stays correct forever while ceasing to be current. Take
the newest with `ls -t … | head -1` instead.

## Two traps inside the reduced set itself

- **Your mod manager may re-add dependencies you excluded.** Re-read the
  *resolved* list rather than assuming you got the set you asked for.
- **It will almost certainly re-sort the order.** Put your own patch mods back
  at the tail and **assert** the orderings in code rather than eyeballing them.
  See `SKILL.md` §5b, and write `loadAfter` rules so the manager stops undoing
  you.

## When to reach for it

**After the second failed hypothesis, not the fourth.** A speech-bubble mod drew
nothing across a 567-mod stack; four theories were tested and disproved over a
**day**, and cutting to 25 mods took minutes and worked immediately. Minimising
costs roughly one load, so it becomes the cheapest option at the point where you
notice you are *generating* hypotheses rather than *testing* a theory.
