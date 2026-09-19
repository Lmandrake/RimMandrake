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

⭐ **THE CEILING IS THE GENERATOR, NOT THE RULE — owner, 2026-09-02: "Accept, amend the
contract."** 128 px/cell is the target, and it stops being achievable once
`drawSize × 128` exceeds what the image model actually renders. The model returns about
**1.5 megapixels natively**, so a canvas beyond ~1024–1280 px is upscaling: a bigger file
carrying interpolated pixels, not more detail. Measured on the sea-beast colossi
(`drawSize` 12–20, which 128 px/cell would put at 2048): they shipped at **1024, i.e.
85–96 px/cell**, and that is CORRECT, not a shortfall.

⇒ **For any creature whose 128 px/cell target lands above ~1280 px, ship the largest
canvas the generator fills with real detail and STATE the achieved px/cell in that
creature's `PLAN.md`.** Do not round up to a power of two you cannot fill. A reviewer
seeing 85 px/cell on a leviathan is looking at the ceiling, not at sloppy work.
⚠️ This is an exception for the LARGE end only. Nothing here licenses shipping a 1.0-cell
animal at 64 px — below the ceiling, 128 px/cell still binds.

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

## 🔴 WHAT NORTH AND SOUTH MEAN — owner ruling, 2026-09-15

> *"North facing is 'looking away from the player camera' (their butt). South
> facing is 'looking at the player camera' (standard eyes-forward). We should NOT
> have 'top down view rotated north or south.' That's not Rimworld perspectives.
> Some of our animals currently show this."*

| facing | what the viewer sees |
|---|---|
| **south** | the creature's **front** — eyes-forward, face and belly toward camera |
| **north** | the creature's **rear** — its back, its behind; **no face, no eyes** |
| **east / west** | a side **profile** |

⛔ **A top-down view rotated 180° is NOT a north/south pair.** It is the same view
turned around, and it is the specific defect the owner named. North and south must
show *different surfaces of the animal* — back versus face — not one surface at
two rotations.

### Why this section exists — measured 2026-09-15

Nothing in this skill previously said what north and south *mean*, and the cost
showed up in one review sitting of 28 Pyrelands rows. Of 19 creature rows only
about three had no defect against them, and the owner's own rejection notes were
dominated by this one fact: *"North is HUGE compared to east, and South isn't
south"* (Anooba) · *"Norht isn't north, south isn't very south either"* (Orray) ·
*"south isn't south, north isn't north"* (Iriaz).

🔴 **The donor art obeys the convention and our regenerated art breaks it.** Three
creatures exist as both donor art and our override; mirror-symmetry measured on
the visible silhouette:

| creature | donor (SWBestiary) | our override |
|---|---|---|
| Dalgo | 0.96 / 0.97 | **0.31 / 0.18** |
| Iriaz | 0.99 / 0.99 | **0.49 / 0.47** |
| Nuna | 1.00 / 1.00 | 1.00 / 0.99 |

Across 190 donor three-facing sets the convention is consistent (norths cluster
0.96–1.00), with occasional shipped errors — Nuna's donor north shows a beak,
which is inverted. ⛔ **Vanilla base-game art has NOT been checked**: there is no
RimWorld install on the Laptop and no `resources.assets`, so whether vanilla
itself is internally consistent is still owed from the Windows box.

### Generate to satisfy this, not to be judged against it

- **Say the surface, never the compass.** A prompt that says "north" invites a
  top-down rotation. Say *"rear view, seen from behind, no face or eyes visible"*
  and *"front view, eyes toward the viewer"*.
- 🔑 **Derive facings from ONE master rather than prompting three.**
  `ARTPIPE_FACING_COHERENCE_1` already rules this — *"N faces away, S faces toward,
  facings derived from one master"* — and prompting three independently is
  precisely why height, palette and facing all disagree: each is a separate roll of
  the dice with no shared reference. It also takes 3 renders per creature to 1.
- **Yield, measured**: 94 generations produced 65 sprites (1.45 attempts each);
  25 of 65 targets needed more than one attempt, some three. Getting the facing
  right in the prompt is the cheapest credit you will ever save.

### What can be checked without a model, and what cannot

Mirror symmetry about the vertical axis separates a profile-as-north from a real
rear view: Orray's north scores **0.53** against a donor cluster of 0.96–1.00,
and it agrees with the owner's eye on Orray, Iriaz and Anooba-south.

⚠️ **Symmetry cannot catch a FACE in the north** — a frontal face is symmetric.
Anooba's north scores 0.84 while showing teeth to camera. That one needs something
that looks at the image.

### No facing may BE another facing — and what that test does and does not find

**✅ The identity case is the single highest-yield check in this skill.** Hash every
facing and every variant; a match means a file was copied, not drawn. Measured
2026-09-15, it found seven real pairs in one biome's roster: Anooba's male sprite
is byte-identical to the female in **all three** facings, Nuna's male north and
south are the female's, and GizkaW differs from Gizka on east alone. One of those
*caused* an owner complaint he could only phrase as *"north and south aren't the
right color"* — the colour was wrong because the file was the wrong animal's.

⛔ **The rotation/flip extension was measured and abandoned.** The idea was to
catch a facing manufactured from another by testing all eight dihedral transforms
(90/180/270, each with and without a flip), exempting east↔west since west
legitimately *is* a flipped east. Across 84 within-set pairs, comparing at native
scale over the union silhouette so shared transparency could not inflate the
score, **nothing reached 0.90** — the whole corpus sits between 0.57 and 0.86.
No defect here is a literal rotation of another facing.

Three measurement traps burned on the way to that answer, all of which make the
metric look like it works when it does not:

| what I did | why it lied |
|---|---|
| cropped each sprite to its own bbox and stretched both to 64×64 | destroys scale, so a wide profile and a narrow rear view look alike — Porg, a **correct** pair, scored 0.86 |
| compared whole canvases at native scale | mostly-transparent 512×512 art matches on *emptiness*; every pair scored 0.83–0.98 |
| `point(lambda v: 1 if …)` then `.convert("1")` | `convert("1")` thresholds at 128, so 1 → 0 and every IoU came out **0.00** on all 40 sets |

🔑 The wrong views we actually have were drawn from the wrong angle, not
manufactured — so **mirror symmetry catches them and exact-transform matching
does not**. Keep the hash; do not add a fuzzy transform threshold without a corpus
that separates.

The full ruleset, both tiers, lives in
`design/RimMandrake/art_review_facts_spec.md`.

### Measuring a sprite's extent — use the VISIBLE silhouette

🔴 **Never take an alpha bounding box at `alpha > 0`.** Renders in this project
carry a sub-visible export halo (alpha 1–16, under 6% opacity) on **13 of 19**
rows sampled, which inflates the box far past the painted body:
`FurnaceBeast_east` has 3,901 such pixels reaching y=480 while the body stops at
y=400 — a 460px box around a 286px animal.

Measuring at `alpha > 0` on downscaled thumbnails produced two false "clean"
verdicts that were reported to the owner before being caught: FurnaceBeast at
1.03× (really **1.64×**) and BarbSlinger at 1.15× (really **1.61×**). ✅ Threshold
at **`alpha > 16` on the original**, never the thumbnail.

That halo is itself a pipeline defect worth fixing at the export step rather than
by re-rendering 13 sprites.

### Two more traps from the same sitting

- ⛔ **A delivered file is not proof a render happened.** Anooba's male sprite is
  byte-identical to the female in all three facings; Nuna's male north and south
  are the female's; GizkaW differs from Gizka on east alone. Duplicates masquerade
  as finished work, and one of them *caused* an owner complaint he could only
  phrase as *"north and south aren't the right color"*. **sha256 every facing and
  variant** before calling a set complete.
- ⛔ **Provenance is not appearance.** Pre-filling an art review with "this came
  through the current pipeline, so keep it" mispredicted **6 of the owner's first
  9 verdicts**. He rejected Bolotaur and Iriaz as *"cartoonish"* despite both
  passing through the painterly wave. What the pipeline touched says nothing about
  what the sprite looks like.

⚠️ **This file needs a curation pass**: "Multi-facing assets" appears three times
(from line 284, 336 and 414), the copies diverging after ~37 identical lines.

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

## 🔴 Flying creatures need a DIFFERENT asset shape — not a wing layer

**A flier's animation is a whole-body directional flip-book, never a separate
wing texture jiggled by a render-tree node.** Owner ruling 2026-09-19, filed
after `FIREHAWK_FLIGHT_BEHAVIOR_1` shipped a custom `BodyDef` wing part +
`PawnRenderNodeProperties_Spastic` node and it looked broken live: standing
still with no visible flap going sideways, and one wing missing (the other
misaligned) going north. That is not a tuning miss — a Spastic node idle-jiggles
ONE static texture; it was never built to express a per-facing "wings up" vs
"wings down" pose, and nothing keeps a single wing texture registered across
four facings. Full account and the CLAUDE.md correction: search this repo's
CLAUDE.md for "If it flies in the fiction".

**The real mechanism is `PawnKindDef.flyingAnimationFramePathPrefix`** — MEASURED
against the installed game by extracting `Chicken_Flying_*` from
`resources.assets` (UnityPy) and diffing frame 1 against frame 5:

```xml
<flyingAnimationFramePathPrefix>Things/Pawn/Animal/Chicken/Chicken_Flying_</flyingAnimationFramePathPrefix>
<flyingAnimationFrameCount>8</flyingAnimationFrameCount>
<flyingAnimationTicksPerFrame>2</flyingAnimationTicksPerFrame>
<flyingAnimationDrawSize>2.4</flyingAnimationDrawSize>
<flyingAnimationDrawSizeIsMultiplier>true</flyingAnimationDrawSizeIsMultiplier>
<flyingAnimationInheritColors>true</flyingAnimationInheritColors>
```

**What to generate, per commissioned flier:** `frameCount` full-body poses (8 is
vanilla's number for Chicken/Duck/Goose/Sparrow; Locust ships 5), each one
covering the WHOLE animal wings-and-all in a different point of the wingbeat
cycle — frame 1 tucked/streamlined, a mid-cycle frame fully spread, same idea
as a walk cycle but for flight — **times three directions**, named
`<prefix><N>_<direction>` for N = 1..frameCount and direction in
`north`/`east`/`south` (no separate west — mirrors east, same convention as
every other RimWorld facing set). That is `frameCount × 3` individual images,
not `frameCount` images reused across facings and not a 2×2-style sheet (the
per-facing generation guidance above applies here too, doubled by frame count).
Gendered species (vanilla Quail, Peafowl) add a second full set under
`flyingAnimationFramePathPrefixFemale`.

**Before generating anything**, read the reference doc a fresh implementation
pass should start from: `~/Desktop/RIMWORLD_1_6_NATIVE_ANIMAL_FLIGHT_IMPLEMENTATION.md`
(owner, 2026-09-19) if present, or re-derive the same facts from the installed
game the way this section did — Sparrow (Odyssey) is the cleanest from-scratch
template, Chicken/Duck/Goose (Core) are the retrofit references for turning an
existing grounded animal into a flier. `flyingAnimationDrawSizeIsMultiplier`
scales the flying sprite relative to the grounded one — most vanilla fliers
read bigger mid-flight, and that is timing/scale tuning, not art.

**Validation plan for a flier specifically** (on top of the standard one below):
verify the cycle actually alternates pose (not a static image, per the
worked-example lie above), verify all three facings resolve (a missing
`_north_3` silently drops to the bare-path fallback — see "How sprite checks
lie"), and verify the grounded graphic returns cleanly on landing. A screenshot
of the animal standing still proves nothing about whether it flies; step ticks
until it actually takes off and look then.

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
