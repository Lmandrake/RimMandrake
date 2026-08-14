# The validation plan — the house format

**Copy this section into any skill that produces something a game has to render,
run or resolve.** It is reproduced verbatim rather than linked because skills
package as independent zips: a cross-skill pointer does not ship.

A validation plan is what you owe whoever holds the game when you hand them
something to check. It exists because **a game load costs 23–30 minutes**, and an
unplanned look burns one and settles nothing.

---

## The six fields

**1. The observable — what a player SEES when it works.**
🔴 **A positive observation, never "no error".** "The log is clean" is not an
observable; it is the absence of one, and absences are the cheapest thing in the
world to produce by accident. Name the thing on screen: a quest card in the tab,
slag on open ground, a pawn facing north with a frill.

**2. The route — the exact call, click path or spawn that produces it.**
Not "spawn the pawn and look". The defName, the tool call with its arguments, the
menu path. ⚠️ **If the route needs a tool that does not exist yet, say so and file
it as blocked on the tool** — do not queue it for a load it cannot survive.

**3. The prediction — written BEFORE the look.**
A number or a specific string. This is the field that turns a look into evidence:
a prediction on record converts "hmm, that seems low" into a finding. Without it
you will rationalise whatever you see.

**4. The threshold — what CLOSES it, and what is explicitly out of scope.**
State the bar and state the minutia you are choosing not to chase. An item with
no threshold is never closed; it is inspected forever. ⭐ **A good threshold is
usually one observation, not a battery.** If you cannot say what would close it,
you do not yet understand what you built.

**5. Batch or solo.**
Most checks ride together. **A new assembly goes solo** — it is the change most
likely to destroy attribution, because if the load comes up wrong nobody can tell
whether it was the DLL or the three def changes beside it.

**6. What a FALSE PASS looks like.**
The way this particular check lies. Every check has one, and it is the field
people skip. Worked examples that cost real cycles:
- **An absent input read as an empty one.** A tool returning `null` for a field it
  never models reads as "the thing is not there". Ask *can the instrument see this
  at all* before believing a negative.
- **A shared signal read as yours.** A filth count attributed to our scatterer
  when four vanilla sources lay the same filth. Ask *what else produces this*.
- **Art that is only drawn when SELECTED.** Spawning the pawnkind does not test a
  `HairDef` or apparel override — the pawn draws whatever style it rolled. Pair
  the spawn with the selection, and name the facing: usually one rotation is
  broken, so a shot from the wrong side passes for the wrong reason.
- **The consumer is stale.** The artifact is right and the game never read it. Ask
  *what did the consumer last load, and when* before concluding the artifact is
  wrong.

---

## The shape to hand over

```
ITEM     <what is being validated>
SEE      <the positive observation>
ROUTE    <exact call / defName / click path>
PREDICT  <number or string, before the look>
CLOSE    <the bar> — NOT chasing: <the minutia deliberately skipped>
RIDE     batch | solo (<why, if solo>)
LIES     <how this check produces a false pass>
```

Seven lines. If it does not fit, the item is really two items.

---

## When to produce one

**Whenever you finish something you cannot verify yourself.** That is the trigger,
not a request. Authoring a def, a texture, a layout or an assembly ends with a
validation plan in the same commit — because the alternative is that the person
holding the game invents one, and theirs will not carry your prediction.

⚠️ **"Deployed" and "verified" are different words.** A validation plan is what
sits between them. Writing the file is not deploying it; deploying it is not
seeing it work.
