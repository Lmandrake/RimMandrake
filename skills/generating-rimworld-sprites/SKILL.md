---
name: generating-rimworld-sprites
description: Produces RimWorld-ready sprite art that matches an existing reference asset — correct canvas, real alpha, silhouette inside the original footprint, and a style that reads as shipping in the same game. Use when creating or altering RimWorld textures, pawn or building art, damaged or variant states of an existing thing, or any PNG destined for a mod's Textures folder. Wraps generating-images and editing-images with the game's hard constraints and an offline validator that rejects art before it costs a game load.
---

# RimWorld sprite art

A RimWorld texture is not a picture, it is an asset with a contract: exact
canvas, real alpha, and a silhouette that occupies the tiles the def says it
occupies. Art that violates any of those looks broken in game and costs a
**~23–30 minute** cold load to discover.

So the rule that governs everything here: **no sprite reaches the Mods folder
until the validator passes offline.** The load is for learning things that
cannot be computed. Canvas size and alpha can be computed.

Builds on `generating-images` (engine, chroma key) and `editing-images`
(invariants, drift detection). Read
`../generating-images/references/codex-contract.md` for the verified CLI facts.

## 🔴 HOW BIG SHOULD THE TEXTURE BE? 128 px PER CELL OF OCCUPANCY

**Owner's ruling, 2026-08-23:** *"2048x2048 be used for a 16x16 creature… 128 pixels per
cell occupancy for modern, high quality art."*

    texture edge (px)  =  drawSize (cells)  x  128        then round UP to a power of two

🔑 **`drawSize` is measured in CELLS and is completely independent of pixel resolution.**
Raising a texture from 256 to 1024 changes nothing about the creature's footprint, its
collision, or any def — it occupies exactly the same ground and simply stops being blocky.
⇒ **Resolution is never a reason to touch `drawSize`, and `drawSize` is never a reason to
leave a texture small.**

| drawSize | 128 px/cell wants | ship |
|---|---|---|
| 1.0 | 128 | 128 or 256 |
| 2.0 | 256 | 256 |
| 3.7 | 473 | **512** |
| 4.3 | 557 | **512** or 1024 |
| 8.0 | 1024 | **1024** |
| 16.0 | 2048 | **2048** |

⚠️ **Mod convention is FAR below this and is not the standard to copy.** Measured over
Alpha Animals' 350 loose creature textures: **321 are 256x256** and only **four** reach
512 — including creatures we draw at 3.69 cells, i.e. **69 px per cell**. That is the
blockiness a player sees on a big animal, and it is the donor mod's budget decision, not a
constraint.

### There is no engine ceiling, and the constant that looks like one is dead

- `StaticTextureAtlas.MaxTextureSizeForTiles = 512` **is never read anywhere in the 1.6
  codebase** — measured, its declaration is the only match. ⛔ Do not treat 512 as a cap.
- The real bound is `MaxPixelsPerAtlas = (SystemInfo.maxTextureSize / 2)^2`
  (`StaticTextureAtlas.cs:31`), GPU-dependent and typically 8192 or 16384 on anything
  modern, and `GlobalTextureAtlasManager.BakeStaticAtlases` simply **flushes a batch and
  starts a new atlas** when the budget is reached.
- ⇒ A large texture costs **atlas budget and a draw call**, never correctness. For a
  handful of headliner creatures that is not a real cost; for 300 animals it would be.

⭐ **Past ~128 px/cell you are paying VRAM for pixels no zoom will ever show.** Going above
the table is a deliberate choice for a headliner, not a default.

## ⚠️ The size trap — read this before generating anything

`gpt-image-2` requires **both edges to be multiples of 16** and **total pixels
between 655,360 and 8,294,400**.

Typical RimWorld sprites fail both ends:

| asset | pixels | legal to generate? |
|---|---|---|
| a `512x640` facing | 327,680 | ❌ **below the minimum** |
| a `1416x1416` sheet | 2,005,056 | ❌ 1416 is not a multiple of 16 |
| `1024x1024` | 1,048,576 | ✅ |
| `2048x2048` | 4,194,304 | ✅ |

**Never generate at the target size.** Generate at a legal size with the right
*aspect*, then downscale with `pnglib.resize_rgba`, which premultiplies alpha
and so avoids the dark halo that plain averaging produces on a cutout.

## First ask whether this is a COLOUR job — those need no pixels at all

Separate the ask into **colour** (free, and scale-proof, because it is the mean)
and **silhouette** (dents, tears, holes — the only part that needs drawing).

The default `Cutout` shader multiplies `graphicData/color` over the whole sprite,
so a mask is **not** required to tint a building. Measured over the live `DefDump`:
of **945** buildable defs in ship-relevant categories, 501 are plain `Cutout` and
only 36 carry a `CutoutComplex`-family shader — yet **944 of 945 accept a colour
with no new art**. Ludeon relies on it: `AncientFortifiedWall` `(127,135,127)` and
`OrbitalAncientFortifiedWall` `(132,140,140)` are two defs over one atlas, neither
masked. The opt-out proves the default — exactly two shipped buildings set
`<ignoreThingDrawColor>true</ignoreThingDrawColor>` (`GrayDoor`,
`AncientBlastDoor`), and a `<color>` patch on those two silently does nothing.

⚠️ **`<color>` MULTIPLIES, so it can only ever darken.** Solve it rather than
guessing: `color = 255 * target / source_mean`; if that clips past 255 the source
is too dark to reach the target and no value exists. `GravshipStructuralBeam_Atlas`
means `(54,53,54)`, so a mid-brown is unreachable, while a wash with max channel
255 — e.g. `(255,150,96)` — bleeds the cold grey out at the same luminance.
**Aging is free; brightening is not.**

Ask "does the def declare a mask?" only when you need **two independently
paintable regions**. And read the shader and `texPath` from the **live def dump,
not the shipped XML** — Vanilla Gravship Expanded retextures the vanilla gravship
set, so a plan written off Odyssey's XML targets art the game is not drawing.

## Workflow

Copy this checklist and work down it:

```
- [ ] 1. Measure the reference (canvas, alpha, coverage, palette)
- [ ] 2. Generate or edit on a chroma key at a LEGAL size
- [ ] 3. Cut the key to alpha
- [ ] 4. Conform to the reference canvas
- [ ] 5. Validate against the reference
- [ ] 6. Look at it composited, at true display size
```

### 1. Measure the reference

```bash
python skills/generating-rimworld-sprites/scripts/validate_sprite.py \
  --reference path/to/original_south.png --describe
```

Never assume the canvas. RimWorld sprites routinely **transpose between
facings** — the smelter is `512x640` north/south and `640x512` east/west. A
validator that checks one canvas for all four facings will pass broken art.

### 2. Generate or edit

Match the reference's *aspect*, not its size. For a `512x640` reference
(4:5), generate `1024x1280` — both multiples of 16, 1,310,720 px, in range.

Always pass `--chroma-key`; RimWorld textures need alpha and there is no other
route to it on this install.

### 3–4. Cut and conform

```bash
python skills/generating-images/scripts/chroma_key.py \
  --input raw.png --out cut.png

python skills/generating-rimworld-sprites/scripts/conform_sprite.py \
  --reference original_south.png --input cut.png --out final_south.png
```

`conform_sprite.py` trims, scales and **registers the subject against the
reference by mask overlap** rather than by bounding-box centre — damaged art is
missing chunks, so its bounding box centre is not where the machine sits.

### 5. Validate

```bash
python skills/generating-rimworld-sprites/scripts/validate_sprite.py \
  --reference original_south.png --candidate final_south.png
```

Findings are graded: **REJECT** blocks, **WARN** asks a human to look, and
`--strict` promotes warnings to blocks.

| Family | Catches |
|---|---|
| Canvas | size differs from the reference |
| **Linear span** | subject width or height off by >6%, either direction |
| **Subject aspect** | art squashed rather than redrawn |
| **Origin** | subject sits somewhere else on the canvas |
| Footprint | silhouette overruns the reference's box |
| Coverage | area collapsed, or ballooned (warn) |
| Alpha channel | missing entirely |
| Corners | key not fully removed |
| **Faint fringe** | pixels at alpha 1–31: invisible, but they corrupt every measurement |
| **Mid-alpha mass** | a fat alpha histogram middle — art renders washed out |
| **Key spill** (warn) | the rim is measurably more key-coloured than the body |
| **Canvas contact** (warn) | subject touches an edge the reference does not — clipping |
| **Fragments** (warn) | solid pixels detached from the main mass |
| Identity | pixel-identical to the reference — nothing changed |

⚠️ **Span is checked separately from coverage, and that separation is the
point.** A wreck legitimately *loses area* — material is removed — so the area
tolerance has to stay loose. But it must still *span* its footprint. Checking
only area is what let a sprite ship 20% undersized while every check passed.

### The validator is itself tested

```bash
python skills/generating-rimworld-sprites/scripts/selftest.py \
  --reference path/to/any_real_sprite.png
```

Nine cases: a control that must pass, and eight synthesised defects that must
each be rejected *for the stated reason*. Run it after changing any threshold.

It has already earned its place twice. It found the fringe threshold set at
0.5% when the real defect measured 0.12% — above the bug it was written to
catch, so it would never have fired. And it found the identity check hashing
*file bytes*, so re-encoding the same pixels defeated it; it now hashes pixels.

**Thresholds are calibrated against measurements, not taste.** Each constant in
`validate_sprite.py` carries the observation that set it. If you change one,
re-run the self-test and update the note.

### 6. Look at it

```bash
python skills/generating-images/scripts/preview_alpha.py \
  --input final_south.png --out _check.png --max-dim 128
```

**At true display size**, not at generation size. The project's own pilot
learned this the hard way: art that read beautifully at 1024px read as brown
mud at sprite size, because the damage was mid-tone surface detail rather than
silhouette.

To judge several candidates at once, or to judge one against the reference:

```bash
python skills/generating-rimworld-sprites/scripts/contact_sheet.py \
  --reference original_south.png --out sheet.png a.png b.png c.png
```

Two rows — large for craft, true sprite size for whether it reads at all — all
over a checkerboard so transparency is visible rather than read as black.
**The validator says shippable; only this says good.**

🔴 **"Good" is judged by Fable-tier review, not the owner (owner's ruling,
2026-09-01).** Art presence in game — magenta, invisible Graphic_Multi, wrong
texPath — is proven by MACHINE against a screenshot or atlas; art quality and
style coherence are graded by Fable evaluation. The owner sees art only inside
a staged review environment, and only for the calls that genuinely need him
(`infrastructure/VALIDATION_LADDER.md`).

## Art direction that survives downscaling

Earned on this project's pilot; both rules are now non-negotiable.

1. **Silhouette, not surface.** Damage must be **subtractive** — chunks torn
   out of the outline. Surface corrosion disappears into noise at sprite size.
   Lit indicators and hard cable shapes survive; mid-tone rust does not.
2. **Nothing projects past the outline.** A hose reaching outside the footprint
   overlaps whatever the player built next door, *and* costs the machine its
   own size, because conforming scales the whole drawing back into the original
   canvas. Measured cost on the first attempt: **14% of body size**.

3. **A soft curve collapses into a hard wall.** A muzzle drawn correctly on a
   1934 px master, with 22 px of clear margin inside a 512 canvas, rendered at
   ~104 px as a vertical face with a square top corner — which at the front of a
   head reads as *cut off*. Nothing was missing and every offline check passed.
   Redraw the feature as a continuous taper **so that it survives the
   downsample**: the master gets blunter and more exaggerated so the sprite gets
   better. Then confirm the bbox is unchanged — it staying at (8,168,490,293)
   across the fix is what proves nothing else moved.

Phrase all three positively in the prompt — "every fitting terminates flush against
the hull", never "no cables sticking out". See
`../generating-images/references/prompting.md`.

## Matching the reference's style

Attach the reference with `--image` and edit from it rather than generating
fresh. A generated-from-scratch sprite will not match a shipped mod's palette
and line quality, and mismatch is more obvious in game than missing detail.

State the invariants every iteration: *"the silhouette, canvas, camera angle
and palette stay exactly as they are; change only the surface"*.

## Multi-facing assets

RimWorld `Graphic_Multi` things ship four facings that must agree — a hole in
one flank appears in every view that can see that flank.

**Prove one facing before attempting four.** Four-view consistency fails for
reasons unrelated to whether the pipeline works, and one facing is enough to
learn whether the art direction survives downscaling.

### ⚠️ Generate facings individually, not as a 2×2 sheet

The sheet is the obvious way to get consistency — one machine drawn four ways,
in one pass. **Measured 2026-08-12, it is the wrong trade**, and the reason is
resolution rather than art.

A generation returns roughly a fixed pixel budget regardless of what is in it.
Put four facings in one image and each gets a quarter of it:

| approach | pixels per facing | oversampling vs a 512×640 sprite |
|---|---|---|
| 2×2 sheet (1254×1254) | ~393,000 | **1.2×** |
| individual (1120×1405) | ~1,574,000 | **4.8×** |

**4× fewer pixels per facing, leaving almost no downsampling headroom.** The
crispness of a finished sprite comes from generating well above target and
area-averaging down; at 1.2× there is nothing to average.

What the sheet *did* do well, so this is a trade rather than a failure: it held
the 2×2 layout, kept each cell's own viewing direction, and produced four
panels more stylistically alike than four independent runs. It still did not
deliver verifiable damage correspondence between views.

**Recommendation: generate each facing individually, anchored to a chosen
sibling** — pass the reference as image 1 and the approved facing as image 2,
and ask for a match on palette, material and damage language. That buys most of
the consistency at full resolution.

⚠️ **Codex `edit` hangs on roughly one call in four, with no error of its own.**
Cap `--timeout` at **120 s** (a good call returns in ~80) and wrap every facing in a
retry loop. 🔑 **The full measurement, the budgeting table and the harness bug that
made it look worse than it is live in `../generating-images/SKILL.md` >
"Cost and timing"** — they are engine facts, not sprite facts, so they are kept in
one place rather than two.

⚠️ **Two-image anchoring is not reliable here** — it hung three times running, which
looked like the cause and was not. ✅ **Anchor with WORDS instead:** edit each facing
from ITS OWN reference and carry the approved sibling's treatment in the prompt —
*"segmented chitin plating with clean segment breaks, speckled shell, wet translucent
flesh with a bioluminescent glow inside it, deep red and rose palette, hard black
outline"*. Write that sentence down the moment the first facing is approved. Measured
2026-08-24: it held three facings together on two different creatures.

## Multi-facing assets

RimWorld `Graphic_Multi` things ship four facings that must agree — a hole in
one flank appears in every view that can see that flank.

**Prove one facing before attempting four.** Four-view consistency fails for
reasons unrelated to whether the pipeline works, and one facing is enough to
learn whether the art direction survives downscaling.

### ⚠️ Generate facings individually, not as a 2×2 sheet

The sheet is the obvious way to get consistency — one machine drawn four ways,
in one pass. **Measured 2026-08-12, it is the wrong trade**, and the reason is
resolution rather than art.

A generation returns roughly a fixed pixel budget regardless of what is in it.
Put four facings in one image and each gets a quarter of it:

| approach | pixels per facing | oversampling vs a 512×640 sprite |
|---|---|---|
| 2×2 sheet (1254×1254) | ~393,000 | **1.2×** |
| individual (1120×1405) | ~1,574,000 | **4.8×** |

**4× fewer pixels per facing, leaving almost no downsampling headroom.** The
crispness of a finished sprite comes from generating well above target and
area-averaging down; at 1.2× there is nothing to average.

What the sheet *did* do well, so this is a trade rather than a failure: it held
the 2×2 layout, kept each cell's own viewing direction, and produced four
panels more stylistically alike than four independent runs. It still did not
deliver verifiable damage correspondence between views.

**Recommendation: generate each facing individually, anchored to a chosen
sibling** — pass the reference as image 1 and the approved facing as image 2,
and ask for a match on palette, material and damage language. That buys most of
the consistency at full resolution.

🔴 **CODEX `edit` FAILS INTERMITTENTLY HERE, AND A FAILURE COSTS THE WHOLE
TIMEOUT.** Measured 2026-08-23 over seven calls in one sitting: **four succeeded in
79-81 s** and **three produced no output at all** and were killed by their own
timeout, with codex's stderr suggesting re-authentication.

⚠️ **CORRECTION, and it is the point of this entry.** The first three failures were
all two-image calls and this file briefly said the SECOND IMAGE was the cause. Then
a **single**-image call failed the same way. ⇒ **It is not the second image**, it is
not the documented variadic-`-i` bug either (`codex_image.py:241` already appends the
`--` terminator, which was read before blaming it) — it is **intermittent**, and the
sample that looked conclusive was four calls deep and confounded.

**How to work with it:**
- ⏱️ **Cap the timeout at 120 s, never 780.** A failure burns the entire budget before
  it reports, so a batch of four hung calls at 780 s is **52 minutes for nothing**. A
  good call returns in ~80 s; anything past 120 s is not coming.
- 🔁 **Retry rather than diagnose.** Three of seven failed and the same prompt
  succeeded on a later attempt. Wrap each facing in a retry loop instead of
  reasoning about why one died.
- ⛔ **Do not draw a conclusion about the CAUSE from a handful of calls in one
  sitting.** This entry exists because that is exactly what happened.

🔴 **AND SOME OF THOSE "HANGS" WERE THE RETRY HARNESS KILLING ITSELF.** A cleanup
line of the shape

    pgrep -f codex_image.py | xargs -r kill -9      # ⛔ NEVER

matches the **parent shell too**, because a script created by a heredoc carries its
own text — including that string — in the parent's command line. So the retry loop
SIGKILLed the job it was retrying, and the batch died with an unexplained exit 1 or
144 partway through. ✅ **`timeout` already reaps the child; no cleanup line is
needed.** If you must kill strays, match on something that cannot appear in the
parent's own argv.

✅ **Anchoring still works without the second image:** edit each facing from ITS OWN
reference and carry the approved sibling's treatment in the PROMPT as words —
*"segmented chitin plating with clean segment breaks, speckled shell, wet translucent
flesh with a bioluminescent glow inside it, deep red and rose palette, hard black
outline"*. Write that description down the moment the first facing is approved; it is
the anchor, and it survives whichever call shape you end up using.

## Multi-facing assets

RimWorld `Graphic_Multi` things ship four facings that must agree — a hole in
one flank appears in every view that can see that flank.

**Prove one facing before attempting four.** Four-view consistency fails for
reasons unrelated to whether the pipeline works, and one facing is enough to
learn whether the art direction survives downscaling.

### ⚠️ Generate facings individually, not as a 2×2 sheet

The sheet is the obvious way to get consistency — one machine drawn four ways,
in one pass. **Measured 2026-08-12, it is the wrong trade**, and the reason is
resolution rather than art.

A generation returns roughly a fixed pixel budget regardless of what is in it.
Put four facings in one image and each gets a quarter of it:

| approach | pixels per facing | oversampling vs a 512×640 sprite |
|---|---|---|
| 2×2 sheet (1254×1254) | ~393,000 | **1.2×** |
| individual (1120×1405) | ~1,574,000 | **4.8×** |

**4× fewer pixels per facing, leaving almost no downsampling headroom.** The
crispness of a finished sprite comes from generating well above target and
area-averaging down; at 1.2× there is nothing to average.

What the sheet *did* do well, so this is a trade rather than a failure: it held
the 2×2 layout, kept each cell's own viewing direction, and produced four
panels more stylistically alike than four independent runs. It still did not
deliver verifiable damage correspondence between views.

**Recommendation: generate each facing individually, anchored to a chosen
sibling** — pass the reference as image 1 and the approved facing as image 2,
and ask for a match on palette, material and damage language. That buys most of
the consistency at full resolution.

🔴 **BUT TWO-IMAGE EDITS HANG ON THIS INSTALL — measured 2026-08-23.** Four
consecutive `edit` calls carrying two `--image` arguments produced **no output at
all** and were killed by their own 780 s timeout, with codex's stderr suggesting
re-authentication. The very next **single**-image edit succeeded in **79 s**, and
so had two before it, so it is neither auth nor rate limiting — it is the second
image. ⛔ **It is NOT the documented variadic-`-i` bug**: `codex_image.py:241`
already appends the `--` terminator for any non-empty image list, and that was
read and confirmed before blaming it.

✅ **The working fallback, and it is nearly as good:** edit each facing from ITS
OWN reference only, and put the approved sibling's treatment into the PROMPT as
words — *"segmented chitin plating with clean segment breaks, speckled shell,
wet translucent flesh with a bioluminescent glow inside it, deep red and rose
palette, hard black outline"*. Write that description down when the first facing
is approved; it is the anchor, and it costs one 80-second call per facing.

⚠️ Budget for it: a hung two-image call costs the FULL timeout before it fails,
so a batch of four is 52 wasted minutes. If you try the two-image form again,
give it a **120 s** timeout, not 780.

## Before it ships

Deploying is a separate claim from writing. The game reads the Steam Mods
folder, never this repo — run `python src/RimMandrake/Utils/deploy_custom_mods.py` for a plan,
read it, then `--apply`. Per `infrastructure/agents/POLICY.md`, only deploy your own files.

## Validation plan — what you owe whoever holds the game

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

### Worked example

```
PROVE    spawn JawaWreckedSmelter on clear ground, rotate to south, default zoom
EXPECT   a torn notch out of the upper-left housing, open ground visible through it · the notch reads as ~15% of sprite width at 104 px; outline still fills one 1x1 tile
LIES     bare-path fallback — a failed _south deploy draws WreckedSmelter.png and looks fine
```

## Reference

- `scripts/validate_sprite.py` — the graded reference-vs-candidate gate; `--describe` to
  measure a single file.
- `scripts/selftest.py` — nine cases proving the validator catches what it claims.
- `scripts/contact_sheet.py` — candidates beside the reference, two sizes.
- `scripts/conform_sprite.py` — trim, scale, register onto the reference canvas.
- `../generating-images/` — engine, chroma key, alpha preview, prompting.
- `../editing-images/` — invariants and drift detection.

## Dependencies

None beyond the standard library.
