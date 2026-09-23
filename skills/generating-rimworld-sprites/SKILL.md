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

Builds on `generating-images` (engine, transparency) and `editing-images`
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

⚠️ **For a repad/recenter-in-place fix on EXISTING game art, prefer BOX
(area-averaging) over LANCZOS.** LANCZOS resampling on a sprite carrying
sub-visible alpha dust (near-zero but nonzero alpha reaching past the visible
silhouette) amplifies it via ringing — measured 1055→3452px of such pixels on
one facing, trading a boundary-clip finding for a worse `transparency_real`
finding. Of LANCZOS/BICUBIC/BILINEAR/BOX, only BOX left the file no worse than
it found it (`ZEER_EAST_TOP_CLIP_1`, 2026-09-19).

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
- [ ] 2. Generate or edit at a LEGAL size, asking for a transparent background in the prompt
- [ ] 3. Conform to the reference canvas
- [ ] 4. Validate against the reference
- [ ] 5. Look at it composited, at true display size
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

**Ask for a transparent background directly in the prompt.** There is no
`--chroma-key` flag on `generate`/`edit` any more (removed 2026-09-06) — the
built-in tool emits real alpha when asked for it. See
`../generating-images/SKILL.md`. `chroma_key.py` is now only a standalone
post-process script for the rare case that already has a flat key to cut.

### 3. Conform

```bash
python skills/generating-rimworld-sprites/scripts/conform_sprite.py \
  --reference original_south.png --input raw.png --out final_south.png
```

`conform_sprite.py` trims, scales and **registers the subject against the
reference by mask overlap** rather than by bounding-box centre — damaged art is
missing chunks, so its bounding box centre is not where the machine sits.

### 4. Validate

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

🔴 **This reference-vs-candidate REJECT is the WRONG check for a `Graphic_Random`
sibling variant** — multiple interchangeable art files for one graphic slot
(e.g. a plant's leafless-state alternates). Those are *meant* to differ from a
reference in span/aspect/origin, so this validator REJECTs correct art: even
our own shipped, working art (`EmberGrassA/B/C`, the donor
`Sovereign_Tuskens/Wraps.png`) fails it 6-for-6. Use the reference-INDEPENDENT
checks instead for this art class — canvas, real alpha, clean corners, fringe
%, duplicate pixel-hash — never the reference-vs-candidate family
(`EMBERGRASS_LEAFLESS_ALTS_1`, `DESERT_WRAPS_ART_COMMISSION_1`, 2026-09-19).

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

⚠️ **A "must NOT flag" pin, added to prove a fix stuck, can pass VACUOUSLY if the
pinned file is later deleted or renamed** — it never re-asserts the file is
present, only that IF checked, it's clean. Prove any such pin is live by
pointing it at a nonexistent filename first and confirming that FAILS, before
trusting it passes on the real file (`ZEER_EAST_TOP_CLIP_1`, 2026-09-19).

### 5. Look at it

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

## Facings, mirroring, appendages and flight

→ facings, mirroring, Spastic appendages, flight frames: the `rimworld-sprite-facings` skill.

## Before filing a job through the artpipe queue

- 🔴 **`reference=` on an artpipe job triggers reskin-validate** (pixel-fidelity
  against the OLD sprite). A deliberate RESTYLE will always fail it — 21
  Pyrelands jobs REJECTed on canvas/subject-size mismatch vs the donor this
  way. For a restyle, file **reference-less** (prompt + library images for
  inspiration only), gated by the legibility gate, not reskin-validate
  (BENCH 2026-09-13).
- ⚠️ **A brief can cite reference art that does not exist.** "Match `X`'s art"
  is only checked when `X`'s path is passed as the job's `reference` field —
  prose in `style_notes` is unchecked. A def having a name and a `drawSize`
  does not mean it has a texture; resolve the cited def's `texPath` and
  confirm a real PNG before writing "match the existing X" (2026-09-23).
- **Search before queuing.** `infrastructure/artpipe/done/`, `_artsrc/`,
  `registry.jsonl` and any `.decisions.json` review sheet can already hold
  finished, ruled-on art for the subject — the daemon runs continuously and
  its output regularly sits unused. Grep `registry.jsonl` for `source:
  "<ITEM_ID>"` before filing: one wave's "81 owed renders" was actually 77
  already in flight and 24 finished renders waiting on review, not 81 to
  generate (BENCH 2026-09-21). Full rule: `CLAUDE.md > Check for existing
  regenerated art before queuing more`.

## Before it ships

Deploying is a separate claim from writing. The game reads the Steam Mods
folder, never this repo — run `python src/RimMandrake/Utils/deploy_custom_mods.py` for a plan,
read it, then `--apply`. Per `infrastructure/agents/POLICY.md`, only deploy your own files.

🔴 **A species with its own `<Name>ArtOverride` mod can be silently regressed by
a later-loading donor mod shipping art at the same texPath** — no error, no
log entry, the custom art just quietly reverts. Before extracting or shipping
art for a species, check whether `src/RimStarWars/<Name>ArtOverride/About/About.xml`
exists and read exactly which facings it claims (the exempted set varies per
species); never ship a competing copy at a path an override mod already owns
(FOUNDRY 2026-09-12, `RSW_Anooba`/`RSW_Dragonsnake`).

## Validation plan

→ full validation plan (PROVE/EXPECT/LIES, how sprite checks lie, worked example): `references/validation-plan.md`.

## Reference

- `scripts/validate_sprite.py` — the graded reference-vs-candidate gate; `--describe` to
  measure a single file.
- `scripts/selftest.py` — nine cases proving the validator catches what it claims.
- `scripts/contact_sheet.py` — candidates beside the reference, two sizes.
- `scripts/conform_sprite.py` — trim, scale, register onto the reference canvas.
- `../rimworld-sprite-facings/` — what north/south/east/west mean, multi-facing generation,
  cross-facing audits, Spastic appendages, flying flip-book frames.
- `references/validation-plan.md` — the PROVE/EXPECT/LIES plan owed with every sprite, how sprite checks lie.
- `../generating-images/` — engine, chroma key, alpha preview, prompting.
- `../editing-images/` — invariants and drift detection.

## Dependencies

None beyond the standard library.
