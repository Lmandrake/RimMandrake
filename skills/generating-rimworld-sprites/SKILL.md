---
name: generating-rimworld-sprites
description: Produces RimWorld-ready sprite art that matches an existing reference asset — correct canvas, real alpha, silhouette inside the original footprint, and a style that reads as shipping in the same game. Use when creating or altering RimWorld textures, pawn or building art, damaged or variant states of an existing thing, or any PNG destined for a mod's Textures folder. Wraps generating-images and editing-images with the game's hard constraints and an offline validator that rejects art before it costs a game load.
---

# RimWorld sprite art

A RimWorld texture is not a picture, it is an asset with a contract. The contract has three parts:

- an exact canvas;
- real alpha;
- a silhouette that occupies the tiles that the def says it occupies.

Art that breaks one part looks broken in game. You discover the fault only after a cold load. On the full mod list, plan
for **15 to 30 minutes** (the `rimworld-load-round` skill holds the dated measurements).

So one rule governs everything here: **no sprite reaches the Mods folder until the validator passes offline.** Spend a
load only to learn things that a program cannot compute. A program can compute canvas size and alpha.

This skill builds on two skills that live in MandrakeWorkflows (`D:\Luke\dev\MandrakeWorkflows\skills\...`):

- `generating-images` (engine, transparency): `~/dev/MandrakeWorkflows/skills/generating-images/SKILL.md`;
- `editing-images` (invariants, drift detection): `~/dev/MandrakeWorkflows/skills/editing-images/SKILL.md`.

`src/RimMandrake/Utils/image_skills.py` resolves both paths. `$RM_IMAGE_SKILLS_ROOT` overrides where it looks. For the
verified CLI facts, read `~/dev/MandrakeWorkflows/skills/generating-images/references/codex-contract.md`.

## 🔴 HOW BIG SHOULD THE TEXTURE BE? 128 px PER CELL OF OCCUPANCY

**Owner's ruling, 2026-08-23:** *"2048x2048 be used for a 16x16 creature… 128 pixels per
cell occupancy for modern, high quality art."*

    texture edge (px)  =  drawSize (cells)  x  128        then round UP to a power of two, floor 256, ceiling 1024

The code for this rule is `common.canvas_for_cells` in `src/RimMandrake/Utils/artpipe/`. The art judge's
`policy.canvas_rule` gives the same numbers. The floor of 256 is the owner's prefer-higher tiebreak
(`ART_PAINTERLY_RESTORATION_1`, 2026-09-14). The same ruling allows high resolution "as long as the user will actually
see the resolution".

- `fill_queue.py` only WARNS when a row's canvas is larger than the rule. The tool files the job anyway. State the reason in
  the row's `oversize_reason`.
- A row with no `drawsize` field and no measured def reads as 1.0 cell, so the rule gives 256. Put the real `drawsize`
  on the row.

**THE CEILING IS THE GENERATOR, NOT THE RULE — owner, 2026-09-02: "Accept, amend the contract."** The target is
128 px/cell. You cannot reach the target once `drawSize × 128` exceeds what the image model actually renders.

- The model returns about **1.5 megapixels natively**. So a canvas beyond ~1024–1280 px is an upscale. The file is
  bigger and carries interpolated pixels, not more detail. The code stops at 1024 (`CANVAS_CEILING_PX`).
- The measured case is the sea-beast colossi (`drawSize` 12–20). The 128 px/cell target puts them at 2048. The colossi shipped
  at **1024, i.e. 85–96 px/cell**. That size is CORRECT, not a shortfall.
- **For any creature whose 128 px/cell target lands above 1024 px, do two things:**
  - **Ship the largest canvas that the generator fills with real detail: 1024.**
  - **STATE the achieved px/cell in that creature's `PLAN.md`.**
- Do not round up to a power of two that you cannot fill. A reviewer who sees 85 px/cell on a leviathan sees the
  ceiling, not sloppy work.
- This exception covers the LARGE end only. Below the ceiling, 128 px/cell still binds. Nothing here licenses a
  1.0-cell animal under the 256 floor.

**ZOOM-ONLY ART SCALES TO ITS ZOOM — owner, 2026-10-18:** *"That resolution limit should
always change if something can only be seen at certain zoom levels. Scale things
rationally."*

- The 128 px/cell target is for art that the player sees at close zoom.
- The game draws some art ONLY when the player zooms out. An example is a tree canopy that fades in past a zoom
  threshold. Size such art to the px/cell at which the game actually shows it. Canopies ship at **32 px/cell** (ruled by
  card the same day).
- State the zoom band and the achieved px/cell in the asset's `PLAN.md`.

**`drawSize` is measured in CELLS and is completely independent of pixel resolution.**

- A texture change from 256 to 1024 changes nothing about the creature's footprint, its collision or any def. The
  creature occupies exactly the same ground. The creature only stops being blocky.
- **Resolution is never a reason to touch `drawSize`. `drawSize` is never a reason to leave a texture small.**

| drawSize | 128 px/cell wants | ship |
|---|---|---|
| 1.0 | 128 | **256** (the floor) |
| 2.0 | 256 | 256 |
| 3.7 | 474 | **512** |
| 4.3 | 550 | **1024** |
| 8.0 | 1024 | **1024** |
| 16.0 | 2048 | **1024** (the ceiling: 64 px/cell, state it) |

**Mod convention is FAR below this and is not the standard to copy.** Measured over Alpha Animals' 350 loose creature
textures: **321 are 256x256**, and only **four** reach 512. The 256x256 set includes creatures that we draw at
3.69 cells, i.e. **69 px per cell**. A player sees that blockiness on a big animal. The size is the donor mod's budget
decision, not a constraint.

### There is no engine ceiling, and the constant that looks like one is dead

- `StaticTextureAtlas.MaxTextureSizeForTiles = 512` **is never read anywhere in the 1.6 codebase**. Measured: its
  declaration is the only match. ⛔ Do not treat 512 as a cap.
- The real bound is `MaxPixelsPerAtlas = (SystemInfo.maxTextureSize / 2)^2` (`StaticTextureAtlas.cs:31`). The bound
  depends on the GPU. Typically the bound is 8192 or 16384 on anything modern.
- At that budget, `GlobalTextureAtlasManager.BakeStaticAtlases` simply **flushes a batch and starts a new atlas**.
- So a large texture costs **atlas budget and a draw call**, never correctness. For a handful of headliner creatures,
  that is not a real cost. For 300 animals it is a real cost.

**Which zoom shows more than 128 px/cell depends on the camera mod.**

- At a 1826-px render, the closest zoom shows 83 px/cell in vanilla (root 11) and 114 px/cell with SimpleCameraSetting
  (`ray1203.simplecamerasetting`, root 8). Those two are measured live. At both, the offline simulation puts the
  difference between 128 and 512 px/cell stored art at or under the noticeable level (2.0/255, the edge, at 114).
- Camera+ (`brrainz.cameraplus`) at its defaults lets the camera go to root 2, which is 456 px/cell. That figure comes
  from the Camera+ source (`Settings.cs`, `zoomedInPercent` 1); nobody has measured it live. At 456 px/cell, the
  offline simulation (`src/RimMandrake/Utils/art_maxzoom_probe.py sim`) shows 128 px/cell stored art visibly blurred
  (12/255 against 512), and 256 slightly soft (5/255).
- Do not cut a canvas below the table on the claim that nobody can see the difference: a Camera+ player can. To go above
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

**Never generate at the target size.** Generate at a legal size with the right *aspect*. Then downscale with
`pnglib.resize_rgba`. That function premultiplies alpha. So the function avoids the dark halo that plain averages make on a cutout.

**For a repad/recenter-in-place fix on EXISTING game art, prefer BOX (area-averaging) over LANCZOS.**

- A sprite can carry sub-visible alpha dust: near-zero but nonzero alpha that reaches past the visible silhouette.
- A LANCZOS resample rings, and so it amplifies the dust. Measured on one facing: 1055→3452px of such pixels. The fix
  traded a boundary-clip finding for a worse `transparency_real` finding.
- Of LANCZOS/BICUBIC/BILINEAR/BOX, only BOX left the file no worse than before (`ZEER_EAST_TOP_CLIP_1`, 2026-09-19).

## First ask whether this is a COLOUR job — those need no pixels at all

Separate the ask into two parts:

- **colour**: free, and scale-proof, because it is the mean;
- **silhouette**: dents, tears, holes. Only this part needs new art.

The default `Cutout` shader multiplies `graphicData/color` over the whole sprite. So you do **not** need a mask to tint
a building.

- Measured over the live `DefDump`: **945** buildable defs are in ship-relevant categories. Of these, 501 are plain
  `Cutout`, and only 36 carry a `CutoutComplex`-family shader. Yet **944 of 945 accept a colour with no new art**.
- Ludeon relies on this. `AncientFortifiedWall` `(127,135,127)` and `OrbitalAncientFortifiedWall` `(132,140,140)` are
  two defs over one atlas. Neither def has a mask.
- The opt-out proves the default. Exactly two shipped buildings set
  `<ignoreThingDrawColor>true</ignoreThingDrawColor>`: `GrayDoor` and `AncientBlastDoor`. A `<color>` patch on those two
  silently does nothing.

**`<color>` MULTIPLIES, so it can only ever darken.** Solve for the value. Do not guess:
`color = 255 * target / source_mean`.

- If the value clips past 255, the source is too dark to reach the target. Then no value exists.
- `GravshipStructuralBeam_Atlas` has the mean `(54,53,54)`. So a mid-brown is unreachable. But on
  that same source, a wash with max channel 255, e.g. `(255,150,96)`, bleeds the cold grey out at the same luminance.
- **Aging is free; brightening is not.**

Ask "does the def declare a mask?" only when you need **two independently paintable regions**.

Read the shader and `texPath` from the **live def dump, not the shipped XML**. Vanilla Gravship Expanded retextures the
vanilla gravship set. So a plan from Odyssey's XML targets art that the game does not draw.

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

Never assume the canvas. RimWorld sprites routinely **transpose between facings**. The smelter is `512x640` north/south
and `640x512` east/west. A validator that checks one canvas for all four facings passes broken art.

### 2. Generate or edit

Match the reference's *aspect*, not its size. For a `512x640` reference (4:5), generate `1024x1280`. Both edges are
multiples of 16. The total is 1,310,720 px, in range.

**Ask for a transparent background directly in the prompt.** The `generate`/`edit` commands have no `--chroma-key` flag
any more (removed 2026-09-06). The built-in tool emits real alpha when you ask for it. See
`~/dev/MandrakeWorkflows/skills/generating-images/SKILL.md`. `chroma_key.py` is now only a standalone post-process
script. Use it in the rare case that already has a flat key to cut.

### 3. Conform

```bash
python skills/generating-rimworld-sprites/scripts/conform_sprite.py \
  --reference original_south.png --input raw.png --out final_south.png
```

`conform_sprite.py` trims the subject, scales it, and **registers the subject against the reference by mask overlap**.
The script does not use the bounding-box centre. Damaged art has lost chunks, so its bounding-box centre is not where the
machine sits.

### 4. Validate

```bash
python skills/generating-rimworld-sprites/scripts/validate_sprite.py \
  --reference original_south.png --candidate final_south.png
```

The validator grades each finding:

- **REJECT** blocks.
- **WARN** asks for a look. You or a naive judge looks, before any human (owner, 2026-10-22: nothing reaches him
  unread).
- `--strict` promotes warnings to blocks.

| Family | Catches |
|---|---|
| Canvas | size differs from the reference (`--drawsize`: see below) |
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

**For a redraw at another resolution, pass `--drawsize <the def's drawSize>`.** The validator then judges the candidate at
scale and does not refuse it for canvas size. The validator does so only for a candidate that is square on
the rule canvas (`canvas_for_cells`). The candidate must also be an exact integer multiple or divisor of the reference
on both axes. Any other canvas difference is still a REJECT.

**Span is checked separately from coverage, and that separation is the point.** A wreck legitimately *loses area*,
because its damage removed material. So the area tolerance has to stay loose. But a wreck must still *span* its
footprint. An area-only check once let a sprite ship 20% undersized while every check passed.

🔴 **This reference-vs-candidate REJECT is the WRONG check for a `Graphic_Random` sibling variant.** Such variants are
multiple interchangeable art files for one graphic slot, e.g. a plant's leafless-state alternates.

- The variants are *meant* to differ from a reference in span/aspect/origin. So this validator REJECTs correct art.
- Even our own shipped, working art fails it 6-for-6 (`EmberGrassA/B/C`, the donor `Sovereign_Tuskens/Wraps.png`).
- For this art class, use the reference-INDEPENDENT checks: canvas, real alpha, clean corners, fringe %, duplicate
  pixel-hash. Never use the reference-vs-candidate family (`EMBERGRASS_LEAFLESS_ALTS_1`,
  `DESERT_WRAPS_ART_COMMISSION_1`, 2026-09-19).

### The validator is itself tested

```bash
python skills/generating-rimworld-sprites/scripts/selftest.py \
  --reference src/RimMandrake/CrackedLands/Textures/Things/Item/RM_ZennaqFilament.png
```

Use a crisp, hard-edged reference. A soft sprite has few solid pixels, so the semi-transparent case fails on it and
proves nothing. Check a different reference first: `python3 src/RimMandrake/Utils/selftest_sprite_reference_crisp.py
--reference <png>`.

The selftest has twelve cases:

- a control that must pass;
- eight synthesised defects; the validator must reject each one *for the stated reason*;
- three synthetic upright cylinders for the `--upright-cylinder` camera check (0.56 passes, 0.22 and 0.90 warn).

Run the selftest after you change any threshold.

The selftest has already earned its place twice:

- It found the fringe threshold at 0.5%, when the real defect measured 0.12%. The threshold was above the bug that it
  was there to catch. So the check was never able to fire.
- It found that the identity check hashed *file bytes*. A re-encode of the same pixels defeated that check. The check
  now hashes pixels.

**Thresholds are calibrated against measurements, not taste.** Each constant in `validate_sprite.py` carries the
observation that set it. If you change a constant, run the selftest again and update the note.

**A "must NOT flag" pin, added to prove a fix stuck, can pass VACUOUSLY if the pinned file is later deleted or
renamed.** The pin never asserts again that the file is present. The pin asserts only that the file is clean IF
something checks it. So prove that the pin is live before you trust a pass on the real file. First point the pin at a
nonexistent filename, and confirm that the pin FAILS (`ZEER_EAST_TOP_CLIP_1`, 2026-09-19).

More traps for this section: [references/traps.md](references/traps.md) § The validator is itself tested.

### 5. Look at it

```bash
python ~/dev/MandrakeWorkflows/skills/generating-images/scripts/preview_alpha.py \
  --input final_south.png --out _check.png --max-dim 128
```

Look **at true display size**, not at generation size. The project's own pilot learned this the hard way. Art that read
beautifully at 1024px read as brown mud at sprite size. The cause: the damage was mid-tone surface detail, not
silhouette.

To judge several candidates at once, or to judge one against the reference:

```bash
python skills/generating-rimworld-sprites/scripts/contact_sheet.py \
  --reference original_south.png --out sheet.png a.png b.png c.png
```

The sheet has two rows. The large row shows craft. The row at true sprite size shows whether the art reads at all. Both
rows sit over a checkerboard, so transparency is visible and does not read as black. **The validator says shippable;
only this says good.**

🔴 **"Good" is judged by Opus-tier review, not the owner (owner's ruling, 2026-09-01).**

- A MACHINE proves art presence in game, against a screenshot or atlas. Presence faults are magenta, an invisible
  Graphic_Multi and a wrong texPath.
- Opus evaluation grades art quality and style coherence.
- The owner sees art only inside a staged review environment, and only for the calls that genuinely need him
  (`infrastructure/VALIDATION_LADDER.md`).
- First, an agent or naive judge looks at every picture and drops the broken ones. Only then does he see the rest
  (`standing_rulings.md` §Nothing reaches the owner unread, 2026-10-22).

## Art direction that survives downscaling

Three rules. The project's pilot earned rules 1 and 2. All three are non-negotiable.

1. **Silhouette, not surface.** Damage must be **subtractive**: chunks torn out of the outline. Surface corrosion
   disappears into noise at sprite size. Lit indicators and hard cable shapes survive. Mid-tone rust does not.
2. **Nothing projects past the outline.** A hose that reaches outside the footprint overlaps whatever the player built
   next door. The hose *also* costs the machine its own size. The cause: the conform step scales the whole drawing
   back into the original canvas. Measured cost on the first attempt: **14% of body size**.
3. **A soft curve collapses into a hard wall.**
   - A muzzle was correct on a 1934 px master, with 22 px of clear margin inside a 512 canvas. At ~104 px the muzzle
     rendered as a vertical face with a square top corner. At the front of a head, such a face reads as *cut off*.
     Nothing was missing, and every offline check passed.
   - Redraw the feature as a continuous taper **so that it survives the downsample**. The master gets blunter and more
     exaggerated so that the sprite gets better.
   - Then confirm that the bbox is unchanged. In that fix the bbox stayed at (8,168,490,293). That proves that nothing
     else moved.

Phrase all three positively in the prompt: "every fitting terminates flush against the hull", never "no cables sticking
out". See `~/dev/MandrakeWorkflows/skills/generating-images/references/prompting.md`.

- **Size a creature from its `drawSize`** (§HOW BIG SHOULD THE TEXTURE BE), never from a fixed edge. The 2026-09-13
  finding that 512 shows no more than 256 was measured at vanilla zoom only. The owner is not convinced that it holds at
  the zoom levels of the current mod stack, so sizes err generous.
- **Look at legibility with `art_zoom_sim.py`.** Downscale the candidate to on-screen tiers beside a same-tier vanilla
  control (vanilla small creatures ship at 128 px), and LOOK. At 32 px/cell two features carry a sprite: a few bold
  shapes, and a body value clearly apart from the ground. Fine surface detail turns to mud. Judge legibility by eye.
  Never refuse a sprite on a legibility number (`design/RimMandrake/art_judge_brief.md`, section B. Style).
- 🔴 **No outlines (owner card, 2026-10-04; `art_judge_brief.md`, rule No outlines).** Value and colour contrast carry the silhouette.
  A sprite without an outline is correct. A heavy drawn keyline is STYLE_OFF. `fill_queue.py` strips the retired
  black-outline clause from a row, and refuses a row that still says "black outline" or "keyline". That rule of the
  brief lists the exceptions by creature.

More traps for this section: [references/traps.md](references/traps.md) § Art direction that survives downscaling.

## Matching the reference's style

Attach the reference with `--image` and edit from it. Do not generate fresh. A sprite generated from scratch does not
match a shipped mod's palette and line quality. In game, a mismatch is more obvious than missing detail.

State the invariants in every iteration: *"the silhouette, canvas, camera angle
and palette stay exactly as they are; change only the surface"*.

More traps for this section: [references/traps.md](references/traps.md) § Matching the reference's style.

## 🔴 Buildings are drawn from ONE camera — owner, 2026-10-14

*"They should be from the same perspective used to look at machines and the wall."*

Measured from 27 shipped buildings:

- The camera is **orthographic, ~35° above horizontal**.
- **A round thing's top rim is an ellipse 0.56 tall for its width (0.48–0.64). Its top face is lit and fully visible.**
- The light is overhead-front.
- Extra height extends NORTH (`drawOffset.z = (drawSize.y − size.z)/2`).

A side elevation is the defect. Examples are a domed head with no top face, and a hatch drawn as a circle that faces the
camera.

Anchor the camera with a grey geometry guide as image 1 of an edit. Check with `validate_sprite.py --upright-cylinder`.
Numbers and method: `references/building_camera_perspective.md`.

## Facings, mirroring, appendages and flight

For facings, mirroring, Spastic appendages and flight frames, read the `rimworld-sprite-facings` skill.

## Before filing a job through the artpipe queue

- 🔴 **`reference=` on an artpipe job triggers reskin-validate.** That check tests pixel-fidelity against the OLD sprite.
  - A deliberate RESTYLE always fails it. 21 Pyrelands jobs REJECTed this way, on canvas/subject-size mismatch vs the
    donor.
  - For a restyle, file **reference-less**: prompt + library images for inspiration only (BENCH 2026-09-13). Reskin-validate
    then does not run. Other checks can still fail the render, for example a wrong
    canvas, a flat placeholder shape, or a picture that the owner banned.
  - No legibility gate runs. The gate is off by default since 2026-09-14 (`ART_PAINTERLY_RESTORATION_1`). The daemon then
    records `skipped`, which is not a pass. So LOOK at the render (§5. Look at it).
- **A brief can cite reference art that does not exist.** "Match `X`'s art" is checked only when the job's `reference`
  field holds `X`'s path. Nothing checks prose in `style_notes`.
  - A def with a name and a `drawSize` does not always have a texture.
  - Before you write "match the existing X", resolve the cited def's `texPath`. Then confirm a real PNG (2026-09-23).
- 🔴 **A redo whose note rejects the ANATOMY carries no reference image.** Build that prompt from the def's description
  instead.
  - The evidence: an enact redo for "make it alien / fails the Terran check" attached the rejected render as
    `canon_reference`. The generator redrew the rejected creature. The canon check flagged it twice (ulvassk, 2026-10-10).
- **The canon check is an ADVISOR, never a gate** (owner, 2026-10-15, by card; `canon_check.py`). The check attaches its
  verdict to the picture. The check never fails a job, never blocks one and never files a retry. FAIL predicted 0 of 64
  owner rejections. So never redraw on its score alone.
  - A job with a canon entry (`design/RimStarWars/canon_references/<slug>/description.md`) is graded on the `## Must show`
    lines of the entry. The owner note is then context only.
  - A job with no canon entry but with an owner note is graded on each sentence of the note. The note is the `owner_note`
    field. When the field is empty, the note is the tail of the prompt. The tail starts at the first sentence that names
    the owner, a rejection or a ruling.
  - The check grades a workflow clause ("generate AFTER the source is settled") as a visual requirement, and flags it.
    Mark such a clause with the job's `canon_na` + `canon_na_reason`. Do not retry the render.
  - A note with only provenance ("decision taken by question card …") has only n/a lines. The verdict is then
    UNGRADED (0/0), which is not a PASS (`rotimmature_greylady_v1`). Put the visual ask in `owner_note` when you file.
- ⛔ **A pose change from a live reference is a generator limit, not a prompt problem.** A dead-catch job used a living
  reference. The render copied the reference pose in three rounds. Appended HARD REQUIREMENT tails and a front-loaded
  pose sentence alike scored 0/1. Derive from a dead master that passed instead (2026-10-11).
- **Search before queuing.** Run `python3 src/RimMandrake/Utils/artpipe/artpipe_state.py find <term>`.
  - The command searches the artpipe state dir: `done/`, `_artsrc/` and `registry.jsonl` in
    `D:\ClaudeWork\rimmandrake\artpipe` (outside git since 2026-10-02).
  - That dir, and any `.decisions.json` review sheet, can already hold finished, ruled-on art for the subject. The daemon
    runs continuously, and its output regularly sits unused.
  - Before you file, grep `registry.jsonl` for `source: "<ITEM_ID>"`. One wave's "81 owed renders" were
    not owed: they were already in flight, or finished and waiting on review (BENCH 2026-09-21).
  - Rule: `CLAUDE.md > Check for existing regenerated art before queuing more`. Full text:
    `design/RimMandrake/standing_rulings.md` §Check for existing regenerated art before queuing more.

More traps for this section: [references/traps.md](references/traps.md) § Before filing a job through the artpipe queue.

## Before it ships

A claim that you deployed a file is separate from a claim that you wrote it. The game reads the Steam Mods folder, never
this repo. Run `python src/RimMandrake/Utils/deploy_custom_mods.py` for a plan. Read the plan. Then run it with
`--apply`. Never deploy over the uncommitted files of another window
(`infrastructure/agents/CHARTER.md`).

🔴 **Art shipped at a donor's own texPath can be silently regressed by a later-loading mod shipping art at the same
texPath.** There is no error and no log entry. The custom art just quietly reverts (FOUNDRY 2026-09-12,
`RSW_Anooba`/`RSW_Dragonsnake`).

- So our creature art lives at a path of our own: `Textures/RimStarWars/SWBestiary/<Name>/` or
  `Textures/RimUtinni/UtinniPatches/<Name>/`.
- A `Patches/ArtFold/<Name>_ArtFold.xml` patch points the donor def at that path.
- The standalone `*ArtOverride` mods are gone (ART_OVERRIDE_FOLD_ALL_1, manifest + checker
  `src/RimMandrake/Utils/art_fold_check.py`).
- Before you ship art for a species, read that manifest. It says where the species' art already lives.

More traps for this section: [references/traps.md](references/traps.md) § Before it ships.

## Validation plan

Full validation plan (PROVE/EXPECT/LIES, how sprite checks lie, worked example): `references/validation-plan.md`.

## What he has shown that he likes

What the owner has shown that he likes is in `design/RimMandrake/art_style_memory.md`. That file is a reference, not a constraint.

## Reference

- `scripts/validate_sprite.py` — the graded reference-vs-candidate gate; `--describe` to
  measure a single file.
- `scripts/selftest.py` — twelve cases proving the validator catches what it claims.
- `references/building_camera_perspective.md` — the measured building camera (angle, ellipse ratio, light, overhang).
- `scripts/contact_sheet.py` — candidates beside the reference, two sizes.
- `scripts/conform_sprite.py` — trim, scale, register onto the reference canvas.
- `references/history.md` — evidence that left this file.
- `../rimworld-sprite-facings/` — what north/south/east/west mean, multi-facing generation,
  cross-facing audits, Spastic appendages, flying flip-book frames.
- `references/validation-plan.md` — the PROVE/EXPECT/LIES plan owed with every sprite, how sprite checks lie.
- `~/dev/MandrakeWorkflows/skills/generating-images/` — engine, chroma key, alpha preview, prompting.
- `~/dev/MandrakeWorkflows/skills/editing-images/` — invariants and drift detection.

## Dependencies

None beyond the standard library.

## Prove the game lacks the art before generating any

More traps for this section: [references/traps.md](references/traps.md) § Prove the game lacks the art before generating any.

## Running the artpipe daemon

More traps for this section: [references/traps.md](references/traps.md) § Running the artpipe daemon.
