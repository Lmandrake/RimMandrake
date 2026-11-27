# MACHINES - which machines get pictures, and how each picture is made

_The machine list is `TREATED` (the 18 factory machines) and `SMALL` (the power
cell, the emanator and the component icon) in `Source/grab_source_art.py`.
This file and those two tables must agree. `python3 Source/grab_source_art.py
--list` prints the tables._

---

## The tiers and their pictures

| Tier | Its picture |
|---|---|
| Wrecked | Its own picture, edited from the donor's. The machine is dead and broken open, and nothing on it is lit. The damage takes material away: plates and corners are missing and the dark inside shows through. Everything stays inside the donor's outline. |
| Kludged | Its own picture, edited from this machine's fitted Wrecked picture, so every hole is the same hole. Patch plates of a different metal close the holes, hand-spliced cabling runs across the body, and one bodge is strapped on inside the outline. It is plainly working: lamps are lit, and the conveyor belts and the intake are clear. |
| Refurbished | No picture of its own. It draws the donor's own picture. |

The component (`RM_WM_AncientComponent`) is an item, so it gets one icon instead
of the two tiers.

The smelter's approved Wrecked and Kludged pictures are the style anchor for
every other machine: `Textures/WreckedMachines/Factories/AutomatedSmelter/{Wrecked,Kludged}/AutomatedSmelter_<facing>.png`.
The same folder also holds `Repaired/`, which the Defs still name. It is not
made by this lane and nothing here writes to it.

---

## The register

Columns: the line key, the donor defName, the short name (the folder and file
stem), the donor's drawSize, the donor's canvas, how many facing files the
donor ships, the facings the game fills from another file, and other PNGs in the
donor's texture folder. Read from the donor's own ThingDef and files.

| Key | Donor defName | Short | drawSize | Canvas | Files | Filled | Other PNGs |
|---|---|---|---|---|---|---|---|
| smelter | `VFEFactory_AutomatedSmelter` | AutomatedSmelter | (4,5) | 512x640/640x512 | 4 | - | - |
| autoloom | `VFEFactory_Autoloom` | Autoloom | (4,6) | 512x768/768x512 | 4 | - | - |
| alloyforge | `VFEFactory_AutomatedAlloyForge` | AutomatedAlloyForge | (6,6) | 768x768 | 4 | - | - |
| drill | `VFEFactory_AutomatedDrillPlatform` | AutomatedDrillPlatform | (4,4) | 512x512 | 4 | - | - |
| autofarmer | `VFEFactory_Autofarmer` | Autofarmer | (7, 3) | 384x896/896x384 | 3 | west=mirror of east | AutofarmerBase_east.png, AutofarmerBase_north.png, AutofarmerBase_south.png |
| biofuelrefinery | `VFEFactory_AutomatedBiofuelRefinery` | AutomatedBiofuelRefinery | (4,5) | 512x640/640x512 | 4 | - | - |
| masonrysaw | `VFEFactory_AutomatedMasonrySaw` | AutomatedMasonrySaw | (4,4) | 512x512 | 4 | - | - |
| mincer | `VFEFactory_AutomatedMincer` | AutomatedMincer | (4,4) | 512x512 | 4 | - | - |
| conveyoroven | `VFEFactory_ConveyorOven` | ConveyorOven | (4,6) | 512x768/768x512 | 4 | - | - |
| assembler | `VFEFactory_AutomatedAssembler` | AutomatedAssembler | (6,6) | 768x768 | 4 | - | - |
| neutroamine | `VFEFactory_NeutroamineSynthesizer` | NeutroamineSynthesizer | (6,4) | 512x768/768x512 | 4 | - | - |
| ammopress | `VFEFactory_AutomatedAmmunitionPress` | AutomatedAmmunitionPress | (4,5) | 512x640/640x512 | 4 | - | - |
| distillery | `VFEFactory_AutomatedDistillery` | AutomatedDistillery | (4,4) | 512x512 | 4 | - | - |
| granulator | `VFEFactory_MedicineGranulator` | MedicineGranulator | (6,4) | 512x768/768x512 | 4 | - | - |
| machiningbay | `VFEFactory_AutomatedMachiningBay` | AutomatedMachiningBay | (6,6) | 768x768 | 4 | - | - |
| crematorium | `VFEFactory_AutomatedCrematorium` | ConveyorCrematorium | (4,4) | 512x512 | 4 | - | - |
| fishfarm | `VFEFactory_AutomatedFishfarm` | AutomatedFishfarm | (4,4) | 512x512 | 4 | - | - |
| cannery | `VFEFactory_AutomatedCannery` | AutomatedCannery | (4,6) | 512x768/768x512 | 4 | - | - |
| powercell | `RM_WM_PowerCellBase` | VanometricPowerCell | (2,3) | 128x256/256x128 | 2 | south=same as north; west=mirror of east | - |
| emanator | `RM_WM_EmanatorBase` | PsychicEmanator | (2,2) | 128x128 | 1 | - | - |
| component | `RM_WM_AncientComponent` | AncientComponent | None | 64x64 | 1 | - | - |

What the "filled" column means: when a Graphic_Multi has no file for a facing,
the game draws west as the mirrored east, east as the mirrored west, south as
the north and north as the south. Those facings get no picture and no brief;
`HOLES.txt` in each tier folder lists them.

| Machine | Wrecked | Kludged |
|---|---|---|
| AutomatedSmelter | 4/4 approved | 4/4 approved |
| Autoloom | pilot, see below | pilot, see below |
| every other row | not started | not started |

Owed but not started: a Wrecked and a Kludged picture of the vanometric power
cell and of the psychic emanator, and the component icon. Their briefs are
written by the same grabber.

Open questions for the owner:
- The Autofarmer's texture folder also holds `AutofarmerBase_*` files. They
  are a second layer drawn under the machine. Whether the wreck needs its own
  base layer is not decided.
- `RM_WM_AncientComponent` names `graphicClass` Graphic_StackCount with texPath
  `Things/Item/Resource/ComponentSpacer`, but the vanilla dump holds one file,
  `ComponentSpacer.png`. The grabber treats it as one icon.

---

## How a picture is made

One image-model call per facing. A 2x2 sheet of four facings was tried on the
smelter and rejected on measurement: each facing got about 393,000 px, 1.2x
oversampling against a 512x640 sprite, where one facing per call gets about
1,574,000 px, 4.8x. Crisp sprites come from generating well above the target
and area-averaging down.

Run every command from `src/RimMandrake/WreckedMachines/`. `--root DIR` (or the
environment variable `WM_ART_ROOT`) points every tool at a work folder outside
the repo; without it they use `art_source/`.

1. `python3 Source/grab_source_art.py <defName> [--root DIR]` writes
   `<root>/<short>/`:
   - `restored/`: the donor files (git-ignored; not ours to redistribute);
   - `MANIFEST.json`: the donor's measurements, which every check reads;
   - `CONTACT_SHEET.png`: the donor facings on one sheet;
   - `wrecked/HOLES.txt`, `kludged/HOLES.txt`: the facings still owed;
   - `briefs/<TIER>_<facing>.md` and `.txt`: one brief per facing and tier,
     written by `Source/briefs.py`. The `.txt` is the prompt exactly as sent.
     The `.md` lists the images to attach, in order, and the three commands.
2. For each Wrecked facing, run the three commands in its brief:
   - the image call: `codex_image.py edit` with image 1 = the donor facing and
     image 2 = the smelter's approved Wrecked facing;
   - `python3 Source/fit_sprite.py <short> --tier wrecked --facing <f> --apply`;
   - `python3 Source/check_sprite.py <short> --tier wrecked`.
   Then look at the fitted picture.
3. For each Kludged facing, the same three commands, with image 1 = this
   machine's FITTED Wrecked facing and image 2 = the smelter's approved Kludged
   facing.
4. A judge who did not make the pictures looks at them at true size.
5. Install only after the judge passes, with `src/RimMandrake/Utils/art/art.py
   install` to `Textures/WreckedMachines/Factories/<Short>/{Wrecked,Kludged}/<Short>_<facing>.png`.
   The XML then names that texPath. Nothing in this lane writes to `Textures/`.

The image is generated with its long edge at 1408 px, at the donor facing's
proportions, both edges a multiple of 16, because gpt-image-2 needs edges in
multiples of 16 and a total of 655,360 to 8,294,400 px. `fit_sprite.py`
brings it down to the donor's canvas; nothing is ever sized up.

### What fit_sprite.py does

Its docstring lists the steps. In short: if the picture came back opaque, it
keys the background out from the canvas edge, seals what leaked in, drops
specks, matches the silhouette to the donor's, registers scale and offset by
mask overlap, composes onto the donor's exact canvas, and gives back the
donor's dark rim inside the donor's outline. `--apply` moves the raw picture to
`<tier>/_raw/` and writes the fitted one in its place.

It scales with one factor, except in one case. Sometimes the image model draws
the whole machine in the wrong proportions. For example, the Kludged refinery
south had its tanks always 7% too wide, and the Kludged oven south was 10% too
tall. One factor then fits the long side and leaves the body short on the other
side (fill 91 to 94%). In that case the fitter scales x and y by different
factors, so that the width and the height both match the donor's. It does this
only when two things are true:
- the silhouette's aspect is 5% to 12% off the donor's;
- the two-factor fit raises the mask overlap by at least 0.03 IoU.

A part that is torn off shortens the box but gains almost no overlap (the
refinery east, +0.018), so it keeps one factor. Over 12%, round tanks would
deform visibly: the fitter uses one factor and says so. The output gives both
factors and the skew that it corrected. The limits come from 135 raw pictures
measured on 2026-11-27 (see the constants in the file). `--no-stretch`
reproduces a fit made before the stretch, byte for byte.

### What check_sprite.py checks

A FAIL blocks; a warn asks for a look.

| Check | Result |
|---|---|
| file present and readable | FAIL |
| canvas equals the donor's | FAIL |
| some pixels transparent | FAIL |
| at least 5% of the canvas drawn | FAIL |
| silhouette centre within 2% of the donor's | FAIL |
| at most 0.25% of the drawn pixels outside the donor's outline grown by 2 px | FAIL |
| not byte-identical to the donor | FAIL |
| the general sprite checks (`src/RimMandrake/Utils/check_sprite.py`) | FAIL or warn |
| drawn area grew | warn |

The outline limit comes from a measurement: on the 12 approved smelter
pictures the worst share outside the outline is 0.08% (Kludged west). The limit
is three times that. Each run ends with one line: the files read, the worst
centre drift against its limit, and the worst outside-outline share against
its limit.

Tested on machines other than the smelter (2026-11-27), with planted pictures
in a scratch root: a crematorium facing with a hole cut in it passes; the same
facing with a bar drawn past its edge fails on drift and on the outline; an
emanator and the component icon pass. The emanator first failed: keying a
black background had also taken the donor's dark rim (13% of its pixels), and
the fit came out 10% too large. The fitter now registers against the donor
keyed the same way and gives the rim back afterwards.

---

## What the smelter taught (2026-08-12)

- The owner dropped cross-facing damage correspondence on 2026-08-12. Holes
  need not be the same physical holes from facing to facing. Do not re-raise
  it as a defect.
- Damage must take material away. A wreck drawn as mid-tone surface rust
  reads as brown mud at true size.
- Nothing may stick out past the outline. The fitter scales the whole drawing
  into the donor's footprint, so a projecting cable shrinks the machine; the
  first wrecked attempt lost 14% of its body that way.
- The owner's two corrections to the Kludged smelter: the conveyor belts stay
  clear, because they show where material flows; and the machine is sealed up
  and running, with no open breach full of fire.
- Asking for "about 1400 pixels on its long edge" stops the model echoing the
  input size.
- Thin smoke is semi-transparent, so the fringe check warns about it inside
  the silhouette and fails it only beyond the silhouette.
- The checks test the contract (canvas, alpha, placement, outline), never the
  brief. Every picture has needed a human look after a pass.

---

## Donor mods

| Mod | packageId | Machines |
|---|---|---|
| Vanilla Furniture Expanded - Factory | `VanillaExpanded.VFEFactory` | the 18 in `TREATED` |
| RimWorld (core) | `Ludeon.RimWorld` | the power cell, the emanator, the component icon, read from the vanilla texture dump (`WM_VANILLA_DUMP`) |

The grabber finds a Workshop mod by its packageId, never by its folder number,
and reads texPath, graphicClass and drawSize from the donor's own ThingDef. It
refuses when a table's short name no longer matches the donor's texPath, or
when one of our defs no longer names the texPath the table expects.

When a donor mod updates its art, our pictures can stop matching it. Re-run the
grabber after any donor update; a changed measurement in `MANIFEST.json` means
the pictures need redrawing.
