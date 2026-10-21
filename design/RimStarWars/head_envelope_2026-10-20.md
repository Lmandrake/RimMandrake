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
Since the owner's skull-mass ruling (below) every rule reads one of two extents per facing, against the vanilla Average
median of THAT facing measured by the same detector:
- the **SKULL** (bulk head mass, appendages removed): height 0.85–**1.25x** the vanilla skull; chin within **0.06** of a
  vanilla head height of the vanilla chin (either way) — the neck seat is fixed by `headOffset`, so the chin must sit
  there; centroid within **0.03** of canvas of the vanilla centre; facings agree: east and north skull height within
  **±10%** of south, north skull width within **±15%** of south, east skull width at most **1.20x** south;
- the **BBOX** (alpha>20, appendages included) carries the appendage allowance: width 0.75–**1.25x**, at most **0.25**
  above the vanilla crown and **0.25** below the vanilla chin (`appendage_below_chin_max`), and at least **0.02** of
  canvas clear of every edge (the canvas edge is a hard limit: nothing draws beyond it).
- `species_overrides` (PROPOSED by FOUNDRY 2026-10-20 under the ruling's "ears free"; the owner may move any number):
  Lasat bbox width 1.65 and 0.40 above the crown (its ears); Ortolan bbox width 1.55, 0.80 below the chin (its ears),
  skull chin 0.25 below the vanilla chin and facing height ±30% (its back view carries a nape below the dome that the
  trunk hides on the front, so the north skull reads ~1.24x; the north is seated on the south's CROWN instead).
- `known_violations`: a real defect left visible, owned by an item. `check` prints it as KNOWN, and FAILS once it no
  longer occurs (stale), so the entry cannot outlive the defect. None today (the Ortolan side view was repainted, below).

## What the tool does now (`src/RimMandrake/Utils/art/fit_head_canvas.py`)
- `skull_mass()`: alpha mask; largest inscribed radius R by erosion depth; morphological OPENING with radius 0.55 R
  (removes everything thinner: ears, horns, crests, eye-stalks, trunks, hair strands); largest central connected mass
  (the core); then a row-width walk off the core's top and bottom — a run that ENDS within the opening radius is the
  chin point or dome edge the opening rounded off and is given back, a run still going is a trunk/horn/stalk and is
  not (the crown walk reaches half as far: a dome is blunt, a muzzle can be long). Crown/chin = top/bottom of that
  mass, cx = its centroid. Vanilla heads (no appendages) read the same as their bbox to within 2 px.
- `measure PNG...` bbox and skull; `vanilla DIR --write` re-measures the extracted Core heads (bbox and skull);
  `check HEAD_DIR... [--report MD]` (masks `*_southm.png` skipped, blank or missing facing UNMEASURED, exit 1 on a new
  or stale violation); `overlay HEAD_DIR... --out PNG` tints the skull mass green with the skull box yellow, the bbox
  cyan and the vanilla head box red, to LOOK at what the detector picked; `lineup HEAD_DIR... --vanilla-dir D --out PNG`
  shows the species beside a vanilla head at true scale with the vanilla head box red in every cell.
- `fit` scales all facings by ONE factor (south SKULL height = vanilla skull x `--height-ratio`, default 1.0), clamped
  so every facing fits the skull height, bbox width and canvas-margin limits; it puts the skull centroid on the vanilla
  centre and the skull chin on the vanilla chin (one translation-only re-seat after re-measuring the output), so ears,
  horns and trunks hang free. `--anchor crown` puts east/north on the south's skull crown, `--anchor north-crown` only
  the north. One uniform scale cannot fix facing disagreement, so `--facing-scale FACING=X` (uniform) and
  `--squeeze-x FACING=X` (horizontal, refused below 0.93) remain. Legacy argv still works.
- Selftest `src/RimMandrake/Utils/art/selftest_fit_head_canvas.py`: synthetic heads with ears hanging below the chin
  (plus a trunk), horns above the crown and wide eye-stalks — the old bbox reading misses each skull, the skull reading
  finds crown/chin/centre within 6 px; fit seats the skull chin, not the ear tips; sanity probes that the pre-fit
  Mimbanese side and the bbox-seated 6d77ea123 Ortolan are flagged; the shipped heads pass (bar the known one).

## Fit applied to the shipped heads (2026-10-20, FOUNDRY, skull-mass seated)
All twelve PNGs refitted from the ORIGINAL pre-fit art (git `e9d81b61f`, no compounded resize) and installed through
`art install` on the owner's ruling. Masks (`*_{south,east,north}m.png`) are uniform black and geometry-free, so
unchanged. Skull ratios to vanilla (MEASURED by `check`); crown/chin offsets in vanilla head heights (+ = crown higher /
chin lower than vanilla):

| species | flags | south skull h, crown, chin | east | north |
|---|---|---|---|---|
| Lasat | `--facing-scale north=1.10` | 1.00, +0.00, +0.00 | 1.02, +0.02, 0.00 | 0.91, -0.09, 0.00 |
| Mimbanese | `--facing-scale east=0.935 --squeeze-x east=0.93 --facing-scale north=1.40` | 1.00, 0.00, 0.00 | 0.93, -0.07, 0.00 | 0.99, -0.01, 0.00 |
| Nelvaanian | `--facing-scale east=0.89 --squeeze-x east=0.93` | 0.99, -0.01, 0.00 | 0.90, -0.10, 0.00 | 0.90, -0.10, 0.00 |
| Ortolan | `--anchor north-crown --facing-scale north=0.98` (east = repainted ear) | 1.00, 0.00, 0.00 | 0.94, -0.06, 0.00 | 1.24 (nape), 0.00, +0.25 |

Before (the bbox-seated 6d77ea123, same detector) the Ortolan skull was 0.70x vanilla on the south with its chin 0.43 of
a vanilla head ABOVE the vanilla chin (0.60 on the side, 0.25 on the back): the ear tips had been seated as the chin.
**Ortolan side view (repainted 2026-10-20, owner by card: "Ortolan side-view ear ~25% longer than the front ear … Repaint
that ear shorter?" -> "Repaint the ear"):** the east ear was shortened with `editing-images` from the pre-fit `e9d81b61f`
art (skull, eye, trunk, palette kept) so its tip ends level with the trunk tip, as on the front; refitted with the same
one-scale fit as south/north, no east facing-scale. The side skull is now 0.94x vanilla (was 0.74x) and the
`known_violations` entry is deleted; `check` passes all four species without it.

UNMEASURED: how they read in game (`HEADS_VERIFY_SHRUNK_TO_FIT_THE_HATS`).

## Open (not done here)
Step 4 of the parent design (the joint hat test). The live state read of `curHeadTypeDef` above.

## Owner ruling 2026-10-20 (centre on the skull mass)

Owner: "Please record that when looking at head art you must center the head regardless of additional appendages such as horns, ears, or anything else. The bulk of the head must be searched for detectable chins (or bottom of skull mass) vs top of head ignoring these extensions." The chin-seated bounding-box fit (6d77ea123) used ear tips as the bottom on the Ortolan. Done the same day: the tool, envelope and fit above now register on the skull mass; appendages are judged separately (bbox allowance).
