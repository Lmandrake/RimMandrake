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

⭐ **ZOOM-ONLY ART SCALES TO ITS ZOOM — owner, 2026-10-18:** *"That resolution limit should
always change if something can only be seen at certain zoom levels. Scale things
rationally."* 128 px/cell is for art seen at close zoom. Art drawn ONLY when zoomed out
(e.g. a tree canopy that fades in past a zoom threshold) is sized to the px/cell it is
actually shown at — canopies ship at **32 px/cell** (ruled by card the same day). State the
zoom band and achieved px/cell in the asset's `PLAN.md`.

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

Findings are graded: **REJECT** blocks, **WARN** asks for a look — yours or a naive judge's, before any human
(owner, 2026-10-22: nothing reaches him unread) — and
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

Twelve cases: a control that must pass, eight synthesised defects that must
each be rejected *for the stated reason*, and three synthetic upright cylinders
for the `--upright-cylinder` camera check (0.56 passes, 0.22 and 0.90 warn). Run it after changing any threshold.

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
- **A test that pins art to draw constants must measure the exact files the draw code loads, per look, and run in `run_selftests`.** A hose-connector row kept measuring pieces the draw code had stopped using and lived in a file not named `selftest*.py`, so when all four Coupling_Bare.png were replaced every coupling landed 0.25-0.38 fitting-size short of its nozzle and nothing turned red (the C# route suites check END POINTS, never where a drawn piece's opaque face lands). When porting a mod, list which offline rows ran before and make them run after. Likewise generate any hand-measured art coordinate in C# (nozzle u, port offset) from the installed PNG + the def's `drawSize` and keep a `--check` selftest (`selftest_hose_ports.py`), or a reinstall/drawSize change silently strands it.
- **Selftest inputs derived from LIVE data decay.** A frozen 'known-bad' calibration input that is a live sprite stops being bad the moment someone fixes the sprite (Anooba_m/FireWasp rescaled by owner words): freeze pre-fix bytes as fixtures, never loosen the threshold. `random.sample(glob(live_dir), N)` with a fixed seed is NOT deterministic either (glob order is unsorted and every new file reshuffles the pick; `_artsrc` also holds renders of FAILED jobs and white icons): freeze the sample by shas in the art store. Art-ledger selftests that append through `artledger.append()` must pin `L.seat` and pop `RIMFLOW_SEAT`/`AGENT_SEAT` (they outrank `ART_SEAT`, so the fixture event lands in another shard and reads as 'event lost'); see `pin_seat` in `selftest_art_ledger_fixes.py`.
- **A refusal row keyed on a bare keyword or `rc != 0` is vacuous.** `selftest_rule_canvas.py`'s rows still PASSED with the per-axis and integer-multiple checks deleted, because the wrongly accepted INFO line contained 'canvas' and a later geometry REJECT gave rc 1. Key each refusal row on the REJECT text itself (`canvas is 256x256`) or the guard's own exit code and message, compare the whole record, and prove it by mutating or deleting the guard it protects on a scratch copy.

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

🔴 **"Good" is judged by Opus-tier review, not the owner (owner's ruling,
2026-09-01).** Art presence in game — magenta, invisible Graphic_Multi, wrong
texPath — is proven by MACHINE against a screenshot or atlas; art quality and
style coherence are graded by Opus evaluation. The owner sees art only inside
a staged review environment, and only for the calls that genuinely need him
(`infrastructure/VALIDATION_LADDER.md`) — and only after an agent or naive judge has looked at every picture and
dropped the broken ones (`standing_rulings.md` §Nothing reaches the owner unread, 2026-10-22).

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
- **Generate creature sprites at 256 px, not 512.** 512-sourced and 256-sourced art are pixel-identical once downscaled to play sizes (RMSE 5-7 at every zoom), while 512 costs about 4x the atlas VRAM (183 renders: ~241 MB vs ~64 MB), a real out-of-memory axis on a large mod list. Default 256; `fill_queue.py` warns past it without an `oversize_reason`.
- **Gate legibility with `art_zoom_sim.py`.** Downscale the candidate to on-screen tiers beside a same-tier vanilla control (vanilla small creatures ship at 128 px) and LOOK. Vanilla reads at 24-32 px through a thick dark keyline, a few bold shapes and body value clearly apart from the ground; fine detail and thin or absent outlines turn to mud.
- **Head art fit: centre and size on the SKULL MASS** (top of head to the detected chin/skull bottom), never the alpha bounding box. Ears, horns, crests, stalks and other appendages are ignored when finding crown/chin (owner: the blue Ortolan head sat too high because its ears were used as the chin).
- **Generated sprites that must meet a neighbour at the cell edge (ropes, cables, rails) are painted with a ~5% canvas margin** (a styled anchor's rope ends at 243/256), so a seam shows in game. Measure the painted end from alpha and draw the remainder in code; never assume art reaches the edge.
- **`Graphic_Linked` atlas tiles: compose and mock against the SHOWN cell.** A tile is 176 px but the game shows only its inner 132 px (UV inset 1/32), so couplings hidden in the padding, an elbow kink and detached caps all look fine if you draw or mock the whole tile. One period repeats every cell, so any broad feature in a strip (a repair band, a blotch, a mirrored palindrome period) reads as per-cell dashes: cut a seamless non-mirrored period and damp broad along-pipe colour.
- **Shrinking a creature render to the canvas rule:** use a premultiplied BOX downscale for integer reductions too, not only repads (generator renders carry ~3-11% sub-31 alpha dust; a premultiplied 4x LANCZOS raised it 10% -> 17.6%, BOX kept the source level with no halo), and measure size with the alpha>=32 bbox (the raw `getbbox` said 'fills the canvas' while the solid body was 525 px tall). A GPT shrink to 256 cannot be emitted directly (gpt-image minimum is ~655k px): first a Codex edit at 1024 asking for a redraw 'for 256 display' with thin parts thickened to >= 8 px, a dark outline ~4 px and the palette named and locked to the original (without the lock colour drifted 13.7, with it ~7), then a premultiplied BOX reduction to 256 (PIL `RGBa` resize BOX); `conform_sprite.py` against the original fixes the 9-11% subject-size drift GPT adds. Expect `validate_sprite` to WARN area +16-35%: that is the intended thickening. Pure-BOX shrinks of chunky creatures are fine; the redraw matters for thin limbs, tails and whips. `art.py install --why` REFUSES to displace an owner-KEPT picture even for a resize of his own pick, so ask for the shrink in the same card as the pick.
- **A hi-res redraw of a liked low-res set drifts in SCALE per facing, not shape.** If the w and h ratios against the reference agree within ~2% (e.g. x1.066/x1.051 or x0.936/x0.944 while the other facings sit ~1.01) it is generator scale noise: no regen or new reference is owed. `conform_sprite.py` onto the reference upscaled 2x NEAREST (geometry only) restores the footprint with the drawing untouched, and `validate_sprite --drawsize` then passes. If the ratios disagree the shape changed: judge/regen.
- **Quarter turns of NON-square sprites: PIL `Image.rotate(90*k, expand=False)` keeps the w x h canvas**, cropping the turned piece to its old width and putting any paste offset computed from the unturned height (h-w)/2 px off (end caps shipped clipped and floating 7-10 px clear on 3 of 4 pipe looks). Use `expand=True` or `np.rot90`. Second half: before pixel-fixing a shipped texture run `art.py status` on it; an owner-KEPT picture refuses a mechanical install at pre-push (delegation_policy 3), so build the fix as a script with `--out` candidates plus an `--install` that needs his ruling, not a direct PNG write.

## Matching the reference's style

Attach the reference with `--image` and edit from it rather than generating
fresh. A generated-from-scratch sprite will not match a shipped mod's palette
and line quality, and mismatch is more obvious in game than missing detail.

State the invariants every iteration: *"the silhouette, canvas, camera angle
and palette stay exactly as they are; change only the surface"*.
- **Codex derivations draw a darker, crisper outline than painterly accepted art**, which the judge flags F_INCONSISTENT/SIBLING_MISMATCH. Add an explicit clause: 'copy the contour of images 1 and 2: thin, soft, feathered edge in a dark shade of the local body colour, NOT a black or navy ink line' (fixed Vhorrin and CanopySwinger, not Dovvik).
- **Thickening a painted sprite by dilation closes rung gaps into a slab** (THICK 6 px at 384 failed). Get width from a wider perspective quad plus ~2 px growth and a 3 px keyline, all at 4x supersample before one downsample. `validate_sprite.py` against a flat reference REJECTs any upright redraw on size/aspect/origin by design (the point is a different silhouette); `placeholder_detect.py file` still reports real.

## 🔴 Buildings are drawn from ONE camera — owner, 2026-10-14

*"They should be from the same perspective used to look at machines and the wall."* Measured from 27 shipped
buildings: **orthographic, ~35° above horizontal; a round thing's top rim is an ellipse 0.56 tall for its width
(0.48–0.64), its top face lit and fully visible**, light overhead-front, extra height extending NORTH
(`drawOffset.z = (drawSize.y − size.z)/2`). A side elevation — a domed head with no top face, a hatch drawn as a
circle facing the camera — is the defect. Anchor the camera with a grey geometry guide as image 1 of an edit, and
check with `validate_sprite.py --upright-cylinder`. Numbers and method: `references/building_camera_perspective.md`.

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
- 🔴 **A redo whose note rejects the ANATOMY carries no reference image.** An enact
  redo for "make it alien / fails the Terran check" attached the rejected render as
  `canon_reference`; the generator redrew the rejected creature and the canon check
  failed it twice (ulvassk, 2026-10-10). Build that prompt from the def's
  description instead.
- ⚠️ **An owner-kind canon check grades EVERY sentence of `owner_note`.** A workflow
  clause ("generate AFTER the source is settled") is graded as a visual requirement
  and can fail a render forever — mark it with the job's `canon_na` +
  `canon_na_reason`, don't retry. The converse: a note holding only provenance
  ("decision taken by question card …") passes 0/0 VACUOUSLY and grades nothing
  (`rotimmature_greylady_v1`). Put the visual ask in `owner_note` when filing.
- ⛔ **A pose change from a live reference is a generator limit, not a prompt
  problem.** A dead-catch job drawn from a living reference copied the reference
  pose in three rounds — appended HARD REQUIREMENT tails and a front-loaded pose
  sentence alike scored 0/1. Derive from a passing dead master instead (2026-10-11).
- **Search before queuing.** `python3 src/RimMandrake/Utils/artpipe/artpipe_state.py find <term>`
  searches the artpipe state dir (`done/`, `_artsrc/`, `registry.jsonl`; `D:\ClaudeWork\rimmandrake\artpipe`, outside
  git since 2026-10-02) — that, and any `.decisions.json` review sheet, can already hold
  finished, ruled-on art for the subject — the daemon runs continuously and
  its output regularly sits unused. Grep `registry.jsonl` for `source:
  "<ITEM_ID>"` before filing: one wave's "81 owed renders" was actually 77
  already in flight and 24 finished renders waiting on review, not 81 to
  generate (BENCH 2026-09-21). Full rule: `CLAUDE.md > Check for existing
  regenerated art before queuing more`.
- **`fill_queue.py` input shape.** Feed it a LIST of rows, one row per creature, each with `canvas_w`/`canvas_h`; it expands each row across its `facings` list itself, so per-facing input rows file NxN jobs with doubled suffixes (`_south_east`). A single JSON object or other wrong shape is not an error: it prints "0 filed, 0 errors". Run the dry run first and compare its job count to rows x facings.
- **Grep `pending/` AND `done/` (and `active/`) for the subject in every spelling before filing or copying jobs.** A same-subject job under another naming convention (`rutwelcomeblanket` vs `scald_welcomeblanket`) files a duplicate; copying pushed job files into the live `pending/` double-queues any the daemon already moved to `active/` or `done/`.
- **Camera or facing-set words kill an artpipe job and the queue then LOOKS done.** `top-down` is a banned camera word, and `three facings`/`all facings` in a per-facing prompt are refused by the daemon's facing guard (`common.load_job`): `bad_job_file`, nothing rendered, every derived facing then `master_failed` (15 jobs once sat for days looking like a Codex outage). `fill_queue` accepts them at filing, and a faced job is refused at filing only for `viewed from directly above / top-down`; keep that phrase on single-facing rows only. Say the surface (side view, seen from behind), never the camera. Run `common.load_job` on job files before queuing (filename must equal job id), check `worker_status` (`bad_job_file` vs `worker_error`), and remember 'queue empty' is not 'renders exist': count `_artsrc` PNGs per subject.
- **`fill_queue`'s eligibility gate (`regen_eligibility`) judges the texPath a def DRAWS NOW.** An `install_to`/`target_texpath` no def of ours draws yet is `REFUSED_UNCONFIRMED` ('orphan'), and a def borrowing one of OUR renders as interim art is `REFUSED_REGEN`. For interim art borrow a vanilla texture and omit `install_to`, so the gate sees DONOR/VANILLA (queue against the borrowed vanilla path, verdict DONOR). New slots (female/variant/young art) are declared in a committed table the gate reads (`design/RimMandrake/extra_art_commission/commission.csv`, `_scan_commission_slots`), not by wiring a def to a missing texture (magenta) or a placeholder (the allowlist only shrinks). Also: `validate_patch.py` reports a ParentName 'resolves to no def' when the abstract parent sits in a Defs file you did not pass; pass the mod's whole Defs dir (with `--defs` Data, Mods AND the workshop root, ~260 s) or the result is UNMEASURABLE; and `gpt_consult` fails with WSL `UtilAcceptVsock accept4 110` when codex.exe interop is down.
- **`fill_queue` loses or mislabels reference/target fields.** It silently DROPS `canon_reference` on a row filed with `no_subject`/`--no-subject` (that branch returns before canon refs are read): patch `canon_reference` into the pending job JSON before the daemon claims it, or the model draws blind (reskin-by-reference of no-def art, e.g. per-look pump art). It also back-fills `target_texpath` with the target def's MAIN texture, so a job for a leafless/polluted twin carries the main path: anything judging coverage keys on `install_to` first and treats `target_texpath` as a fallback only.
- **Artpipe state dir has two env names.** `state_dir.py` reads `ARTPIPE_STATE_DIR` but `bulk_accept_renders.py` (imported by `donor_regen_jobs.py`) still reads `ARTPIPE_STATE`. A process that sets only one gets the right queue for some tools and the default for others; set both (as `idle_fill.py` and its unit do), or route `bulk_accept_renders` through `state_dir`.
- **A 'done' artpipe job is not usable art until its PNG is opened.** Renders live under more than one `_artsrc` root (`D:\Luke\dev\Rimworld\infrastructure\artpipe\_artsrc` for older jobs, `D:\ClaudeWork\rimmandrake\artpipe\_artsrc` for newer; `stdout_tail` may name a third, gone, `D:\Luke\dev\_artpipe`): take each job's path from the manifest's `worker_stdout_tail` OK line, and probe a known-present job first, or an audit reports 'NO_OUTPUT 94' for outputs that exist. When the manifest names a gone tree the raw output is usually recoverable: `meter_after.rollout` names the worker (wN) and session id, and `C:\Users\Mandrake\.codex_workers\artpipe\<wN>\generated_images\<session-id>\exec-*.png` holds the raw full-res render (1254 px, real alpha); the canvas-sized copy is lost, so an install re-fits the raw.
- **Before carrying forward any 'still owed' art claim from a ledger note, run `git log -S` on the texPath (or the defName's texture folder).** A note saying art is 'not installed' can be wrong from the day it is written (five subjects had been installed three days before the notes said none were). The same goes for a defect filed from a capture: compare the capture's file time with later commits to the same code, because the fix may predate the report.
- **An item's description of an EXISTING def can be wrong about both its body and its art.** Read the BodyDef and LOOK at every installed texPath before designing around it (one item called a limbless SnakeBody serpent a quadruped, and said the body set was tan donor art when only the swimming set was).

## Before it ships

Deploying is a separate claim from writing. The game reads the Steam Mods
folder, never this repo — run `python src/RimMandrake/Utils/deploy_custom_mods.py` for a plan,
read it, then `--apply`. Per `infrastructure/agents/POLICY.md`, only deploy your own files.

🔴 **Art shipped at a donor's own texPath can be silently regressed by a
later-loading mod shipping art at the same texPath** — no error, no log entry,
the custom art just quietly reverts (FOUNDRY 2026-09-12, `RSW_Anooba`/`RSW_Dragonsnake`).
So our creature art lives at a path of our own (`Textures/RimStarWars/SWBestiary/<Name>/`,
`Textures/RimUtinni/UtinniPatches/<Name>/`) and the donor def is pointed at it by a
`Patches/ArtFold/<Name>_ArtFold.xml` patch; the standalone `*ArtOverride` mods are
gone (ART_OVERRIDE_FOLD_ALL_1, manifest + checker `src/RimMandrake/Utils/art_fold_check.py`).
Before shipping art for a species, check that manifest for where its art already lives.
- **Installing art: `art.py install` needs a MECHANICAL reason, and never copy the PNG into `Textures/` by hand.** `--why` alone records reason `agent-why`, which the pre-push art guard (`art_guard`, ART_VERSION_WRANGLING_1) REFUSES for texture PNGs. Use `--reason artpipe-collect --why 'delegated: art <verdict>'` for artpipe renders, `--reason script:<committed repo path of the writer>` for script-made or ported art (e.g. a committed writer calling `artledger.install_bytes(dest, bytes, reason='script:<its path>')`, then commit script + `infrastructure/state/art/events/<SEAT>.jsonl`), or an owner field (`--owner-said`/`--ruling`). An install over bytes already in `Textures/` answers `already-live` (or `already-live-ruled`, a keep ruling only) and writes NO live event, so the push is refused as unledgered: leave the old bytes in place and install by sha (`art.py install <mod> <rel> <sha> --ruling <keep id>`), or to repair an installed one delete the PNG from the worktree and re-run with the right `--reason` (re-install old then new sha if already committed; the latest event at head wins). `art.py install` keys events by the mod string given, so pass `src/RimStarWars/SWBestiary`, not `SWBestiary`. `put`/`install --file` refuse files outside the clone: store a render with `artledger.store_put_file(Path)` then `art.py install <mod path> <rel under Textures/> <sha> --owner-said`; a purged sha cannot install until `art.py unpurge` with his newer words. `--by-card` writes THREE ledger lines per PNG (ruling, install, live), and a texture add/move or deletion of old art needs a live event for its bytes.
- **Commit installed art and its ledger together.** `art install` writes new PNGs that a pathspec commit of only the edited defs leaves untracked (defs on main then point at missing textures); and committing the art-ledger shard before the PNGs it records are staged makes the push fail on ART_VERSION_WRANGLING_1 (the guard also refuses PNGs without the ruling lines). In a shared clone select your ledger lines by the installed PNGs' sha256, not by path text. Tool-side corollaries: `./publish` ledger/art guard runs at pre-push, so run `art_guard.py range A..HEAD` before pushing.
- **To take art OUT of the game without rejecting it** (a v2 deferral, a cut feature that may return) use `artledger.retire(path, owner_said=...)`: it archives the bytes in the art store, deletes the PNG and writes a live `sha=None` event that `art_guard` accepts; `art.py purge` is reject-forever and refuses live pictures. Restore later with `art.py install <mod> <rel> <sha>`. A Windows case-twin texture pair (`PaleTree_B`/`_b`) blocks a compose: retire one via `artledger.retire`.
- **A texture ported to a new mod/def can carry the PRE-redraw art** and silently undo an accepted redraw: check a port's PNG hashes against the art ledger's latest live install of that file name. Anything derived from a body's silhouette (a Pack overlay) goes stale when the body is redrawn: re-derive it (`pack_overlay_fit.py --apply --refit`; `selftest_swbestiary_pack_overlays.py` catches it by re-rendering). `donor_standins.apply` with a HAND-BUILT plan writes to `Textures/<dest_tex minus last segment>/<name>`, so for a `Graphic_Random` (folder) texPath the source names must carry the folder (`PoisonShrub/ShrubLowA.png`) or the files land one level up and the texPath resolves to nothing.
- **Installing new art for `RM_LiquidTank` (any look) or a reel turns `FlowWorks/selftest_hose_ports.py` red** unless the picture draws an end hose-port fitting at BOTH canvas edges (<= 4 px) on the `TankPortGeometry.PortDz` row of that look: the hose couples to drawn flanges. Run `selftest_hose_ports.py` (and grep the tests for the texture's filename) before any tank or reel install, and after a reel install plus `reel_intake_geometry.py` also the C# joint rule (`HoseJointChecks`), which runs only inside `src/RimMandrake/Utils/selftest_flowworks_stock.py`, not in `FlowWorks/selftest_hose_*.py`: an off-centre north nozzle put a feed in air.

## Validation plan

→ full validation plan (PROVE/EXPECT/LIES, how sprite checks lie, worked example): `references/validation-plan.md`.

## Who owns this

Art generation answers to The Artist (`src/RimMandrake/rimflow/roles/artist.md`); what the owner has shown he likes is in
`design/RimMandrake/art_style_memory.md`. This skill stays the how-to until the role proves out.

## Reference

- `scripts/validate_sprite.py` — the graded reference-vs-candidate gate; `--describe` to
  measure a single file.
- `scripts/selftest.py` — twelve cases proving the validator catches what it claims.
- `references/building_camera_perspective.md` — the measured building camera (angle, ellipse ratio, light, overhang).
- `scripts/contact_sheet.py` — candidates beside the reference, two sizes.
- `scripts/conform_sprite.py` — trim, scale, register onto the reference canvas.
- `../rimworld-sprite-facings/` — what north/south/east/west mean, multi-facing generation,
  cross-facing audits, Spastic appendages, flying flip-book frames.
- `references/validation-plan.md` — the PROVE/EXPECT/LIES plan owed with every sprite, how sprite checks lie.
- `../generating-images/` — engine, chroma key, alpha preview, prompting.
- `../editing-images/` — invariants and drift detection.

## Dependencies

None beyond the standard library.

## Prove the game lacks the art before generating any
- **Show the magenta boxes first (owner: ironclad).** Do not infer "the art is missing" from files we have not made: the game often needs only two views and derives the rest by symmetry, and a magenta-heads case was fixed by path and namespace, not regeneration. A magenta square is a failed texture lookup and a failed lookup logs: `grep -c "Failed to find any textures at" <Player.log>`. Magenta has a blind spot on a `Graphic_Multi` thing: `Graphic_Multi.Init` falls back `_north` to `_south` rotated 180, `_east` and `_west` flipped, and reaches `BadMat` only when all four suffixes AND the bare path miss, so a partially shipped directional set never goes magenta. `ContentFinder<T>.Get` also resolves per file path walking the mod list backwards, so a partial reskin at another mod's path silently mixes both mods' art on one object. Ask the engine what it will draw before commissioning anything.

## Running the artpipe daemon
- **The daemon loads its code once, at start.** A merged change to `artpiped.py` or anything under `artpipe/` (constant, manifest field, `canon_reference`) does nothing until the daemon restarts (queue idle, SIGTERM): one 'unfixable' failure across 9 jobs was two real fixes sitting in source while the old process ran, and a daemon that ran stale code for a day rendered every redo without canon guidance. Before trusting any 'still broken after the fix', compare the process start time (`ps` lstart) with the commit/last edit, and run `pgrep -af artpipe`: two daemons fight over the w0/w1/w2 codex slots and produce 'no rollout file found' failures that look like a Codex bug. It runs from the BENCH clone's tree, so the change must also have reached that clone.
- **The daemon stays wedged after a Codex quota reset.** Its idle meter refresh only re-reads the newest rollout in a leased worker home, and no rollout is written while it refuses jobs. Run one trivial `codex exec` per leased home (w0/w1/w2, via `codex_image.child_env`) to write a fresh 0% reading, and it resumes within ~30 s (it once sat idle 10 h after a 99% stop).
- **Select a Codex meter window by its declared `*_window_minutes`, never by field position.** The provider once dropped the 5 h bucket and moved weekly into `primary_*`, so a positional `secondary=weekly / primary=5h` mapping silently disconnected the weekly backstop.
- **An auth-plumbing ceiling looks exactly like a rate limit from the queue.** The 'max 3 concurrent' was three stale worker-home `auth.json` files losing a refresh-token race while the account meter sat at 12% and refused nothing even at N=32. Scratch homes (`codex_home_facing_regen`, `_w3`, `ramp2`) hold stale auth too (401 'refresh token already used'): check a home's `last_refresh` before a batch, use the shared home serially if it works, and do not copy `auth.json` into a scratch home another process refreshes.
- **Degradation can arrive as jobs getting FASTER.** The median wall clock FELL as concurrency rose (107.9 s@8, 80.5 s@12, 65.2 s@32) because the agent was skipping its resize step. A latency improvement under load is a defect signal, not a win.
- **The slowdown ratchet baseline is 140 s.** Real 512 px renders take 80-210 s; a 62 s baseline made the one-way ratchet cut concurrency from 5 to 1 within minutes.
