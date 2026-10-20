# Painted-head envelope — measurements, rules and the Tabula Rasa findings (2026-10-20)

Steps 1 and 2 of `design/RimStarWars/head_parts_painted_vs_attached_2026-10-20.md`, owner-approved 2026-10-20
(*"I agree to all your proposed head efforts."*). Offline only; no shipped PNG was changed.
Status key: MEASURED / READ (decompiled or def source) / PROPOSED (an agent's number, the owner may move it) / UNMEASURED.

## How the game maps a head texture to the screen (READ)
- `HeadTypeDef.GetGraphic` builds a `Graphic_Multi` with draw size `Vector2.one`; the head node draws it on
  `HumanlikeMeshPoolUtility.GetHumanlikeHeadSetForPawn` = a **1.5 x 1.5** world-unit mesh (x Biotech life-stage
  `headSizeFactor`). The texture is stretched over that mesh whatever its pixel size, so **a head's drawn size is
  its alpha bbox as a fraction of its canvas**. Vanilla is 128 px, ours 512 px; fractions compare directly.
  This answers the earlier UNMEASURED "canvas-to-world scale": the full canvas is 1.5 cells, and the canvas edge is
  a hard limit (nothing draws beyond it).
- Head position: `PawnRenderer.BaseHeadOffsetAt` = `BodyTypeDef.headOffset` (Male (0.04, 0.34), Female/Hulk
  (0.10, 0.34), Thin/Fat (0.09, 0.34)) x sqrt(bodySizeFactor). **No per-head-type offset or scale exists on
  `HeadTypeDef`**; its only geometry fields are `hairMeshSize`, `beardMeshSize`, `beardOffset`,
  `beardOffsetXEast`, `eyeOffsetEastWest` (AverageBase hair/beard (1.5,1.5); NarrowBase hair (1.3,1.5)).
- **Headgear uses the same head mesh** (`PawnRenderNode_Apparel.MeshSetFor`, `useHeadMesh`), so a hat covers the
  vanilla head extent in the same canvas frame; whatever we paint outside it shows around the hat.
  `DrawData.scale` exists on render nodes but varies only by child stage and `bodyTypeScales`, not head type.

## Tabula Rasa (READ, ilspycmd decompile of workshop 1660622094 `1.6/Assemblies/TabulaRasa.dll`)
- `DefModExt_HeadTypeStuff` has exactly two fields: `useSkinShader` (default true) and `shaderType`
  (`ShaderTypeDef`). **No offset, scale or size field.** Its Harmony postfix on `HeadTypeDef.GetGraphic` only swaps
  the shader (our Mimbanese `CutoutComplex` use). Note: its cache loop never returns on a hit, so it adds a new
  graphic to the list on every call (harmless but grows; not ours to fix).
- `DefModExt_ApparelAlts` (on an apparel def) would load per-head-type alternate worn textures
  (`<WornGraphicPath>_<headTypeDef>[_<style>]`, or `path`), which is the cheap form of "species helmets". **But the
  static `curHeadTypeDef` it keys on is never assigned anywhere in this DLL** (grep of the full decompile), so in
  this build the feature looks inert unless another assembly sets it. UNMEASURED live; one state read would settle it.
- So helmet option 3 ("per-head-type scale/offset") does not exist in Tabula Rasa or vanilla.

## Vanilla head extents (MEASURED, 42 Core head textures from `RimWorldWin64_Data/resources.assets`, alpha>20)
Extracted with UnityPy to `D:\ClaudeWork\scratch\head_envelope\vanilla\`. All canvases 128 x 128.
Median of the 8 Average/HeavyJaw types (Male+Female x Normal/Pointy/Wide + HeavyJaw), in 512-px equivalents:

| facing | width | height | top | chin | centre x | width range | height range |
|---|---|---|---|---|---|---|---|
| south | 184 (0.359) | 200 (0.391) | 158 | 358 | 256 | 0.359–0.375 | 0.391–0.398 |
| east  | 200 (0.391) | 200 (0.391) | 156 | 356 | 256 | 0.359–0.398 | 0.383–0.391 |
| north | 184 (0.359) | 200 (0.391) | 158 | 358 | 256 | 0.359–0.375 | 0.391–0.398 |

Narrow types (6): width 156 (0.305) every facing, height 206–210, chin 366.
Two corrections to the old tool's constants: the vanilla chin is **356–358**, not 365 (365 came from borrowed donor
heads), and the vanilla **east is centred at 256**, not 270. Our four species all sit at chin 365 and east x≈270,
inherited from those constants.

## Our painted heads (MEASURED; `src/RimStarWars/StarWarsRaces/Textures/RimMandrakeSW/Heads/*`, 512 px)
Ratios to the vanilla Average median (full table: `Transient/head_envelope_report_2026-10-20.md`):

| species | south w/h | east w/h | north w/h | main defects |
|---|---|---|---|---|
| Lasat | 1.40 / 1.20 | 1.12 / 1.34 | 1.37 / 1.07 | front 40% too wide; side 34% too tall (crest 0.30 above crown) |
| Mimbanese | 0.95 / 1.20 | 1.19 / 1.19 | 0.73 / 0.86 | side profile 1.36x its own front; north far smaller than south (0.72 height) |
| Nelvaanian | 0.97 / 1.20 | 1.14 / 1.32 | 0.87 / 1.30 | side and back too tall (horns 0.27–0.28 above crown); side 1.28x front |
| Ortolan | 1.11 / 1.20 | 0.82 / 1.36 | 1.14 / 1.20 | side hangs 0.20 of a head below the chin (trunk), so bottom-aligning shifted it up |

Every species is 1.20x vanilla height on the south: that is the old `--target-h 240` default (240/200).

## The envelope (PROPOSED limits, MEASURED base) — data in `src/RimMandrake/Utils/art/head_envelope.json`
Per facing, against the vanilla Average median of THAT facing:
- width 0.75–**1.25x**, height 0.85–**1.25x** (the 25% is the ear/crest/stalk allowance; a hat covers 1.0x);
- above the vanilla crown at most **0.25** of a vanilla head height; below the vanilla chin at most **0.06**
  (and the chin no more than 0.06 above it) — the neck seat is fixed by `headOffset`, so the chin must sit there;
- centre x within **0.03** of canvas (15 px);
- at least **0.02** of canvas clear of every edge;
- facings agree: east and north height within **±10%** of south; north width within **±15%** of south; east width at
  most **1.20x** south (vanilla is 1.09x).
- `species_overrides` in the JSON lets the owner grant one species more (the Rakata eye-stalks will need width
  ~2x on south/north); none granted yet. A snout/trunk species needs a `below_chin_max` override or a repaint.

## What the tool does now (`src/RimMandrake/Utils/art/fit_head_canvas.py`)
- `measure PNG...` bbox fractions; `vanilla DIR --write` re-measures the extracted Core heads into the JSON;
- `check HEAD_DIR... [--report MD]` judges each species dir per facing (masks `*_southm.png` skipped, a blank or
  missing facing is UNMEASURED, never a pass), exit 1 on any violation;
- `fit` scales all facings by ONE factor (south height = vanilla x `--height-ratio`, default 1.10), clamped so every
  facing fits the width/height maxima, centres on the vanilla centre and seats the chin on the vanilla chin;
  `--anchor crown` keeps east/north on the south's crown line for a facing that hangs a trunk below the chin. It then
  prints the envelope check of its output. One uniform scale cannot fix facing disagreement (Lasat/Nelvaanian east
  height, Mimbanese north): those need a repaint or a per-facing decision. The legacy argv form still works.
- Selftest: `src/RimMandrake/Utils/art/selftest_fit_head_canvas.py` (synthetic cases plus a sanity probe that the
  shipped Mimbanese side profile is flagged).

## Open (not done here)
Steps 3–4 of the parent design (strip duplicate attachment genes; the joint hat test). The live state read of
`curHeadTypeDef` above. Re-fitting the shipped heads waits on the owner choosing between rescale and repaint per
species.
