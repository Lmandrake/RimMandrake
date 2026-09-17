# FLOWWORKS art candidates — 2026-09-16

The ART lane of `FLOWWORKS_BUILD_PROGRAM_1`. **Candidates only.** Nothing is deployed and
nothing is wired into any mod's `Textures/`. Owner rules Thursday-ish.

**Look at this first:** `CONTACT_SHEET.png` — every candidate at craft size and at in-game size.

Spec followed: `design/RimMandrake/fluid_canals_mod_definition.md` on `origin/main`, §7 (what the
player must SEE), §13 (partial fill nearly free, vanilla ramp reuse), §21.3 (a dry cell needs one
inner-shadow edge treatment; four depths × dry is the finite art set).

## Canvas conventions — MEASURED, not assumed

Extracted from `RimWorldWin64_Data/resources.assets` (Core) with UnityPy this session:

| asset class | vanilla files measured | canvas |
|---|---|---|
| terrain surface | `Sand` `Gravel` `Soil` `SoilRich` `Mud` `RoughStone` | **1024×1024**, RGB, opaque |
| water depth "Ramp" | `WaterShallowRamp` `WaterChestDeepRamp` `WaterDeepRamp` | **64×64**, RGBA, near-flat colour blocks |
| UI designator | `Mine` `Cancel` `Haul` `PlanOn` `Deconstruct` `Harvest` `RemoveFloor` `Claim` `Flick` `Open` `Uninstall` | **128×128**, RGBA |

In-repo corroboration: `src/RimUtinni/RotSporeKit/Textures/RotSporeKit/Terrains/*` are all 1024×1024.

🔑 **Vanilla's depth read is literally "darker = deeper", and it is subtle.** The three water Ramps
measure `(85,94,96)` → `(74,85,90)` → `(66,75,85)`. A dry pit has no water to carry the cue, so this
set pushes the ladder much harder and adds the lip shadow §21.3 calls for.

Palette anchors used: vanilla `Sand` mean `(126,110,91)`, luma 112.7 · the campaign desert reads
about `(107,86,57)` at full bright (`Palettes/flooring_rusted.md`) · `Palettes/sandscoured.md` for
the dry-ground vocabulary.

## 1 — Dry excavation bed, four depths × two variants

`terrain/RUT_CanalBed_{A,B}_{shallow,mid,deep,superdeep}.png` — 1024×1024 RGB, seamless.

- **Variant A — loose excavated sand / spoil.** Scrape marks, spill ridges, gravel working up.
- **Variant B — cut hardpan / exposed strata.** Cracked caliche, banded rock, chisel facets.

Depth ladder, measured on the shipped files (luma; vanilla `Sand` = 112.7 for comparison):

| | shallow | mid | deep | superdeep |
|---|---|---|---|---|
| A | 95.3 | 60.8 | 34.4 | **14.6** |
| B | 95.3 | 62.4 | 39.9 | **18.5** |

One gain per variant (A ×0.667, B ×0.655) set so *shallow* lands at 0.85 × Sand — the raw
generations came back **brighter than the surrounding desert**, which inverts the "dug = darker"
read. The gain is uniform across the four depths, so the generated relationships are untouched.

**Seamlessness** is enforced (cosine cross-blend against a half-rolled copy, so every border comes
from what was interior). Measured `wrap-seam step ÷ interior step`: **1.04–1.53** across the eight
tiles (1.00 = the seam is indistinguishable from ordinary interior noise; there is no hard line).

### The inner-shadow edge treatment (§21.3)

- `terrain/RUT_CanalBed_*_Ramp.png` — 64×64 flat blocks at 0.82 × the bed's own mean, one per
  bed, matching the vanilla Ramp convention exactly.
- `terrain/RUT_CanalLipShadow_{depth}.png` — 128×128 RGBA, pure black gradient, **authored
  procedurally, not generated** (a shadow is a gradient, not a drawing). Peak alpha 76 / 122 / 168 /
  219 and falloff 0.16 / 0.24 / 0.34 / 0.46 of a cell as depth increases. Rotate per lip edge.

⚠️ **Honest weakness:** at *shallow* the bed is only ~15% darker than surrounding sand, so the lip
shadow is carrying most of the read. If the owner wants shallow to be obvious on its own, the gain
for shallow needs to come down independently (which breaks the single-gain-per-variant discipline —
a deliberate call, not an oversight).

## 2 — Ladder

`buildings/RUT_Ladder_{A,B}.png` — 256×256 RGBA (1-cell building; 128 px/cell target).
A: scrap-metal rails, lashed hardwood rungs, hooked lugs at the lip. B: pegged desert timber with a
stone counterweight. Top-down, rails vertical, rungs crossing — reads as a thin ladder stripe in one
cell at 32 px.

## 3 — Designator icons

`designators/RUT_Designator_{DigCanal,DigDeeper,FillIn}_{A,B}.png` — 128×128 RGBA, the measured
vanilla canvas. Vanilla style copied deliberately: thick even black outline, few flat saturated
fills, slight three-quarter object, **cyan arrow for the directional action** (vanilla uses exactly
that on `Haul` and `RemoveFloor`). B variants are the bolder, flatter, fewer-shapes read.

## 4 — Sluice gate (programme 2 preview)

`buildings/RUT_SluiceGate_{A,B}_{closed,open}.png` — 256×256 RGBA.
A: stone-and-scrap abutments with a strapped timber gate. B: riveted scrap-plate pylons with a
rusted hull-plate slab. In both pairs the **open** state shows a clear dark channel mouth between
the abutments and the gate stacked against the upper one — the closed/open difference is a
silhouette difference, not a surface one, so it survives the downscale.

## Validation done offline

- `validate_sprite.py --describe` on all 12 RGBA sprites → `validator_describe.txt`.
  **Every one: real alpha, fringe 0.00%, all four corners clear.**
- sha256 over all 32 candidate PNGs: **0 duplicates** (the identity trap — a delivered file is not
  proof a render happened).
- Measurements per file in `manifest.json`.

## Validation plan — what is owed the person holding the game

```
PROVE  set one map cell to the canal-bed terrain at each of the four depths, side by side
       on open Sand, default zoom, and screenshot
EXPECT the four cells read as a monotone dark ladder: shallow barely darker than the sand,
       superdeep effectively black; mean cell luma falls below 95 / 61 / 37 / 17
LIES   RimWorld's terrain shader samples by world position, so how many CELLS one 1024 tile
       spans is set shader-side and could NOT be measured offline. The contact sheet assumes
       3 cells. If the real span is 1, the grain is 3x too coarse and every tile will read as
       boulders — and the depth ladder will still pass, because the depth cue is value, not
       grain. Judge grain and value separately.
```

```
PROVE  build the sluice gate on a dug cell, toggle it, screenshot both states at default zoom
EXPECT the gap between the abutments is filled edge to edge when closed and is an open dark
       mouth when open — readable at 32 px without zooming in
LIES   the bare-path fallback. A Graphic_Single with one state deployed draws for both, and
       "it looks right" is then a statement about one file. Name which state you looked at.
```

## Not produced here, and why

The **strained/depleted source** (§13 item 2), the **burning liquid surface** (item 3) and
**irrigated ground** (item 4) were not in this commission. Filled-channel art needs no authoring at
all — §13 rules it is vanilla's own depth terrains plus adoption of Alpha Biomes' `AB_Tar` family.
