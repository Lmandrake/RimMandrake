# Validation plan — what you owe whoever holds the game

Moved verbatim from `../SKILL.md`; the parent skill keeps a pointer.

The validator proves the file is shippable. Only the game proves the art is
*drawn*, and a cold load costs **~23–30 minutes** — so a sprite is not finished
until it ships with the plan for looking at it. Write the plan in the same
commit as the PNG; the alternative is that the person holding the game invents
one, and theirs will not carry your prediction.

**1. The observable — what a player SEES when it works.**
🔴 **A positive observation, never "no error".** Name the thing on screen.

**2. The route — the exact call, click path or spawn that produces it.**
The defName, the tool call with its arguments, the menu path. ⚠️ **If the route
needs a tool that does not exist yet, say so and file it as blocked on the
tool.**

**3. The prediction — written BEFORE the look.**
A number or a specific string. Without it you will rationalise whatever you see.

**4. The threshold — what CLOSES it, and what is explicitly out of scope.**
⭐ **A good threshold is usually one observation, not a battery.**

**5. Batch or solo.**
Most checks ride together. Solo is for anything that would destroy attribution.

**6. What a FALSE PASS looks like.**
The way this particular check lies. Every check has one, and it is the field
people skip.

```
PROVE    <exact call / defName / click path>
EXPECT   <number or string, written before the look>
LIES     <how this check produces a false pass>
```

Three lines. If it does not fit, the item is really two items.

### How sprite checks lie

Five earned ones — full cases as per the trap file:

- **The validator grades the WHOLE sprite, so a distortion confined to one region
  is invisible to it.** Compositing a beast into a vehicle's animal band at
  **+34.6% width stretch** returned `PASS` — canvas, span, origin and subject
  aspect are all measured against the reference *as a whole*, and the cart either
  side of the band held every one of them inside tolerance. At sprite size the
  animal read as a green sliver rather than a beast. ⇒ When you are replacing
  **part** of a sprite, the validator cannot see your part. Measure the distortion
  of the region itself — fit the source to the *band's* aspect before scaling, not
  the canvas's — and then look at it. Measured 2026-08-21; `selftest.py` still
  passes 9/9, so this is a scope limit and not a defect.

- **The bare-path fallback drew instead of your file.**
  `Graphic_Multi.Init` calls `ContentFinder.Get(req.path)` — the path *without*
  any `_north`/`_east` suffix — before it errors. A suffix-less PNG at the base
  path silently satisfies a directional request, so a mis-deployed `_south`
  renders as a pass. Name the facing you looked at.
- **Correct at source, broken at render.** Canvas right, alpha real,
  bbox inside the footprint, and the muzzle still read as "cut off" because a
  soft curve collapsed into a hard vertical wall at ~104 px. Predict what the
  shape does at **display** size, not at generation size.
- **A missing direction is not a defect.** `visibleFacing` lets a def
  ship three facings deliberately — a back attachment has no south. Read the
  def's own declaration before calling a facing broken, or you will file a
  commission the engine would never have drawn.
- **The review image is not the rendered image.**
  A raw PNG on a contact sheet is not what the game draws: `<color>` tints it,
  and a `HairDef`/apparel override is only drawn when that style is **selected**
  — a pawnkind spawn rolls its own style, so the look passes or fails at random.
  Pair the spawn with the selection.
- **The reference-vs-candidate REJECT check is the wrong check for a
  `Graphic_Random` sibling variant** — multiple interchangeable art files for
  one graphic slot (e.g. a plant's leafless-state alternates). Those are
  MEANT to differ from a reference in span/aspect/origin, so this check
  REJECTs correct art; even shipped, working game art fails it 6-for-6 when
  run this way. Use the reference-INDEPENDENT checks (canvas, real alpha,
  clean corners, fringe %, duplicate pixel-hash) for this art class instead.
- **A "must NOT flag" regression pin can pass VACUOUSLY if the pinned file is
  later deleted or renamed** — it never re-asserts the file is present, only
  that IF checked, it's clean. Prove any such pin is actually live by
  pointing it at a nonexistent filename first and confirming THAT fails,
  before trusting that it passes on the real file.

### Worked example

```
PROVE    spawn JawaWreckedSmelter on clear ground, rotate to south, default zoom
EXPECT   a torn notch out of the upper-left housing, open ground visible through it · the notch reads as ~15% of sprite width at 104 px; outline still fills one 1x1 tile
LIES     bare-path fallback — a failed _south deploy draws WreckedSmelter.png and looks fine
```
