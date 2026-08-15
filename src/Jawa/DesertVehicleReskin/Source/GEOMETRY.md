# GEOMETRY.md — the measured build sheet for the Alpha Vehicles reskin

_CREATE, 2026-08-13. Measured, not estimated. Every number here came from reading
the shipped PNGs and masks; nothing is inferred from a name or a screenshot._

**Why this file exists.** The reskin is 5 vehicles × 3 facings = **15 textures
plus 15 masks**. Re-measuring per facing is the expensive part and it is
completely front-loadable, so it was done once, in parallel, and written down.
Read this before touching any facing.

Source (read-only, never composited — the mod is not ours to redistribute):
`/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3028675048/Textures/Things/Vehicles/Land/Tier0/`

---

## 0. Scope — it is FIVE vehicles, and the test is a def tag, not the art

Confirmed against all 12 vehicles. Exactly five carry `<li>AV_TractionAnimal</li>`:
**Chariot · WarChariot · CoveredCarriage · OxCart · DogSled.** Nothing outside
the five has an animal; all five do.

⛔ **Do NOT identify them by "the mask has a black region".** That test is false
and would over-scope by five. Seven of twelve have a black region, and five of
those have no animal at all — the **Balloon's** 70,839 black px (the largest in
the mod) are its envelope and rigging; Hwacha's are the rocket bundle;
OutriggerCanoe's are hull and sail; Palanquin's the canopy; RowBoat's the oars.
Only Rickshaw and Wheelbarrow are genuinely all-red.

## 1. The mask is NOT a segmentation map — dilate by 8 px

Full write-up as per the trap file. The
short version, because it governs every facing below:

**The black region is the animal's interior FILL.** Its 4–6 px pure-black keyline
is tagged RED (vehicle), so the mask is an inward-eroded copy of the animal,
inset on **every** edge — leading, trailing and lateral.

| | Chariot | OxCart | CoveredCarriage | WarChariot |
|---|---|---|---|---|
| raw inset (N/S/E) | 6 / 6 / 6 | 5 / 4 / 5 | 4 / 4 / 4 | **6** / 5 / 5 |
| depth to *majority* black | — | — | 6 / 7 / 6 | **8 / 8 / 7** |

⇒ **Dilate the black region outward by 8 px** and it covers every facing measured.

⚠️ **Filter connected components ≥600 px first.** CoveredCarriage tags its wheel
rims black — 4 blobs north, 6 south, 3 east, 62–364 px each. A blanket erase
deletes wheel detail. WarChariot has almost none (0/2/1).

⚠️ **Colour cannot substitute for the mask on WarChariot.** Its horses are
near-grey `(65,65,61)` against a `(127–213)` grey chariot. CoveredCarriage is the
easy case — grey body `(187–227)`, saturated brown horses `(173,99,58)`.

## 2. The isolated hitch — where the cheap route exists, and where it does not

The cheap erase is "clear everything on the animal's side of the hitch", because
the rigging gets redrawn anyway. It needs a band containing the shaft **and
nothing else**. That band does not always exist.

| vehicle | facing | isolated hitch | notes |
|---|---|---|---|
| DogSled | south | y 254–266, x 256–267 | used by `build_eopie_sled_south.py` |
| DogSled | north | y 248–257, x ~238–249 | hitch runs *below* the animals |
| CoveredCarriage | south | **rows 321–342**, x 246–265 (w 20) | clean |
| CoveredCarriage | east | **cols 307–336**, y 225–250 | clean |
| WarChariot | south | **rows 270–287**, x 245–267 (w 23) | clean |
| WarChariot | east | **cols 238–297** | two thin runs |
| OxCart | north | **y 224–235** (12 rows) | plus a yoke crossing the oxen at y 107–118 |
| OxCart | south | **y 270–278** (9 rows) | yoke at y 305–317 |
| OxCart | east | **x 249–276** (28 cols) | yoke is a vertical band at x 360–374 |
| Chariot | south | **rows 237–282** | clean |
| Chariot | east | **cols 196–247** | two shaft bars merging at x 245–247 |
| 🔴 Chariot | **north** | **NONE** | pole painted *over* the animal's back, x 250–261, y 165–270 |
| 🔴 CoveredCarriage | **north** | **NONE** | wagon canvas fills the centre from y 101 and abuts the horses at y 198 |
| 🔴 WarChariot | **north** | **NONE** | chariot front abuts animal black directly at y 276/277 |

**On the three 🔴 facings the stencil route is the only route** — dilate the mask
and erase by it, component-filtered.

## 3. Per-vehicle animal geometry

All canvases are **512×512**. All masks are fully opaque over the whole canvas,
so "animal" must always be computed as `art_opaque AND mask_black`, never from
the mask alone.

### DogSled — the one that is DONE (south)

| facing | animal bbox | layout | art leads at |
|---|---|---|---|
| south | x 202–311, y 269–467 (11,957 px) | 2 cols × 2 rows, 4 dogs | y 267 |
| north | x 202–309, y 38–245 (13,335 px) | 2 cols, x 202–241 / 271–309 | y 34 |
| east | x 261–488, y 200–291 (11,207 px) | 2 groups, x 261–369 / 379–488 | — |

North shows the dogs **from behind** — ears at the far end, curled tails nearest.
It is a different drawing from south, not a flip.

### OxCart — 2 oxen, north/south are near-exact mirrors

| facing | animal bbox | layout | inter-animal gap |
|---|---|---|---|
| north | x 154–357, y 32–220 (21,028 px) | 2 cols: 154–244 / 267–357 | **x 245–266, 22 px, full length, 0 black** |
| south | x 155–356, y 282–430 (17,973 px) | 2 cols: 155–243 / 268–356 | x 244–267, 24 px, full length |
| 🔴 east | x 282–505, y 158–337 (21,949 px) | **stacked, silhouettes MERGE** | only y 250–255 (6 px) and only for x 302–398 |

North/south ox halves are exact mirrors (10,514 / 10,514 px). **East is the odd
one**: the two oxen are stacked front-to-back, merge over x 400–474, and give a
single x-run and y-run — there is no full-length corridor.

### CoveredCarriage — 2 horses, grey body, brown horses

| facing | animal bbox (blobs ≥600) | layout | gap |
|---|---|---|---|
| north | x 175–336, y 36–198 (10,045 px) | 2 cols: 175–256 / 267–336 | x 257–266 (w 10), filled with wagon below y 101 |
| south | x 176–335, y 268–484 (14,478 px) | merged by the central rein; split at x 261 | body zone x 234–277, w 31–43 |
| east | x 280–506, y 155–324 (15,685 px) | stacked; split at y 242 | **trunk gap y 240–246, only 5–7 px** |

### WarChariot — 2 horses, near-grey, plus a turret overlay

| facing | animal bbox | layout | gap |
|---|---|---|---|
| north | x 151–361, y 44–276 (26,427 px) | bridged by a central rein blob x 215–294; split at x 255 | body zone x 230–281, w 42–52 |
| south | x 165–347, y 200–457 (21,225 px) | split at x 256; real bodies begin y 305 | x 237–275, w 31–39 |
| east | x 212–494, y 148–336 (21,080 px) | stacked; split at y 244 | **trunk gap y 241–248, w 2–7** |

**The turret does not overlap the animals at rest** on any facing —
`AV_ArcherTurret.png` is 128×128, no mask, `Cutout` (never tinted), drawn as a
separate layer. ⚠️ But it is **Rotatable**, radius ~59.8 px, and on **north** the
swept disc reaches into the animal region by ~23 px over x 196–316. A rotated bow
will be drawn over whatever sits at y 253–276.

### Chariot — 1 horse

| facing | animal bbox (body proper) | note |
|---|---|---|
| north | x 209–302, y 32–267 | 🔴 **asymmetric — 944 mismatched px.** Do NOT mirror-copy it |
| south | x 210–301, y 287–468 | symmetric to within **2 px** |
| east | x 254–486, y 191–342 | rein tagged black runs 77 cols past the animal, to x 171 |

⚠️ **All three Chariot black bboxes overstate the animal**, because a thin 4–17 px
rein is tagged black and trails far across the cart. Filter rows by black count
≥18 px to isolate the body.

## 4. Things that will bite at load time, not at author time

- **Driver draw-offsets are hard-coded per vehicle** (`drawOffsetEast` etc.). Move
  the cart body on the canvas and the driver sprite floats. **Keep every row
  outside the animal band pixel-identical** — that is why the sled build copies
  them verbatim rather than re-rendering.
- **West is auto-mirrored from east** on all five (`Vehicles.Graphic_Vehicle`).
  Do not author `_west`. Asymmetric markings will swap sides when facing west.
- **`DogSled` is tinted GREY** — `color (71,71,71)`, `colorTwo (100,100,100)`,
  `colorThree (50,50,50)`. Anything left RED in its mask renders grey regardless
  of what colour it was painted. The other four are brown triples.
- **The animal has zero def-side graphic presence** — no overlay, no second
  `texPath`. Repainting costs **no def edits**.
- ⚠️ **But the labels stay.** The defs carry animal-named damage components
  (`FrontLeftDog`, `LeftOx`, `RightHorse`), flesh types (`AV_WoodenAndDogVehicle`)
  and hurt sounds (`Pawn/Animal/Dog/Dog_Injured`). The health tab will say "Front
  Left Dog" over a picture of an eopie. Label-and-sound only, cheap, and it costs
  no texture iteration — but "art problem, not a def problem" is *almost* right,
  not right.
- **1.5 and 1.6 have identical art contracts.** Verified by diff; the only
  differences are gameplay/API renames.
