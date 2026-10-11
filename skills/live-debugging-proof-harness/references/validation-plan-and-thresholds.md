# The validation plan and the closing bar

These sections say what a live check owes before it
runs and what closes it. For handing a check to someone else, see
`skills/rimworld-modding/references/validation-plan.md`. For deciding whether a
check needs a map at all, see `rimworld-debug-testing` §6.

## 🔴 The validation plan

A plan says what a result will be worth before you spend the run on it.

🔴 **A live run must be proven needed.** The default is source. If you cannot say in one
line what source cannot tell you, verify it there and close the item. Live is for what the
engine does that you cannot compute, and what an eye must judge.

A live check owes three lines: the call, the expected reading, and how a pass could be
false. 🔑 Whoever proves it **closes** it — no hand-back — then greps
`infrastructure/state/items/` for what else it settled.
The rule and the false passes: `skills/rimworld-modding/references/validation-plan.md`.

The six fields, one line each, so you know whether you need to open it:

| field | what it holds |
|---|---|
| **observable** | what a player SEES when it works — a positive sighting, never "no error" (`rimworld-debug-testing` §4) |
| **route** | the exact call, defName or click path that produces it — blocked on a missing tool is a finding, not a queue item |
| **prediction** | a number or string written BEFORE the look; without it you rationalise whatever you see |
| **threshold** | what CLOSES it, and the minutia deliberately skipped (below) |
| **batch or solo** | most checks ride together; **a new assembly goes solo** or attribution dies |
| **false pass** | how *this* check lies — the field everyone skips |

```
PROVE    <exact call / defName / click path>
EXPECT   <number or string, written before the look>
LIES     <how this check produces a false pass>
```

Three lines. If it does not fit, the item is really two items.

⚙️ **Write it before you run `rimworld-debug-testing` §6 (bridge, quicktest or load), not after.** Half the items that look like
they need a cold load turn out, once the observable and route are written down, to
be closable on a quicktest — and the plan is what makes that visible.

## 🔴 Threshold discipline — an item with no closing bar is inspected forever

**The scarce resources here are game loads and the owner's attention, not
thoroughness.** A check with no stated bar does not fail; it recurs — looked at
again next load, and the load after, because nobody can point at the sentence that
closed it.

Every item states **both halves**:

- **the bar** — the single thing that, once seen, ends the item. *"One screenshot
  of the pawn facing north with the strap drawn."*
- **the minutia NOT being chased** — named on purpose, so the next reader knows it
  was a decision rather than an oversight. *"NOT chasing: the two-pixel seam at the
  belt buckle, or the other three rotations."*

⭐ **A good threshold is usually ONE observation, not a battery.** Four rotations,
three light levels and a stress test is not rigour — it is an item that will not
fit in a load and will be half-done twice. Pick the one view most likely to be
wrong (usually north, usually the rotation nobody drew) and close on it.

**If you cannot say what would close it, you do not yet understand what you
built** — and that, not the load, is the thing to go and fix.

⚠️ **A threshold met is announced.** Say "closed by `<screenshot path>`" and stop
looking. Re-inspecting something already closed costs exactly what inspecting it
the first time cost, and buys nothing anybody asked for.
