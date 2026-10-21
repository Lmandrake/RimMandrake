# Painted-head envelope — measurements, rules and the Tabula Rasa findings (2026-10-20)

Steps 1 and 2 of `design/RimStarWars/head_parts_painted_vs_attached_2026-10-20.md`, owner-approved 2026-10-20
(*"I agree to all your proposed head efforts."*). Offline only; no shipped PNG was changed.
Status key: MEASURED / READ (decompiled or def source) / PROPOSED (an agent's number, the owner may move it) / UNMEASURED.

## How the game maps a head texture to the screen (READ)
- `HeadTypeDef.GetGraphic` builds a `Graphic_Multi` with draw size `Vector2.one`; the head node draws it on
  `HumanlikeMeshPoolUtility.GetHumanlikeHeadSetForPawn` = a **1.5 x 1.5** world-unit mesh (x Biotech life-stage
  `headSizeFactor`). The texture is stretched over that mesh whatever its pixel size, so **a head's drawn size is
  its alpha bbox as a fraction of its canvas, times the Big and Small head render scale** (next section; 1.0 for a
  pawn with no size offset). Vanilla is 128 px, ours 512 px; fractions compare directly.
  This answers the earlier UNMEASURED "canvas-to-world scale": the full canvas is 1.5 cells, and the canvas edge is
  a hard limit (nothing draws beyond it).
- Head position: `PawnRenderer.BaseHeadOffsetAt` = `BodyTypeDef.headOffset` (Male (0.04, 0.34), Female/Hulk
  (0.10, 0.34), Thin/Fat (0.09, 0.34)) x sqrt(bodySizeFactor). **No per-head-type offset or scale exists on
  `HeadTypeDef`**; its only geometry fields are `hairMeshSize`, `beardMeshSize`, `beardOffset`,
  `beardOffsetXEast`, `eyeOffsetEastWest` (AverageBase hair/beard (1.5,1.5); NarrowBase hair (1.3,1.5)).
- **Headgear uses the same head mesh** (`PawnRenderNode_Apparel.MeshSetFor`, `useHeadMesh`), so a hat covers the
  vanilla head extent in the same canvas frame; whatever we paint outside it shows around the hat.
  In vanilla, `DrawData.scale` varies only by child stage and `bodyTypeScales`, not head type; Big and Small
  multiplies it by body size (below).

## Canvas frame vs on screen: Big and Small scales the head with body size (READ + MEASURED 2026-10-20)
**The vanilla head box is the head of a body-size-1.0 pawn.** Every envelope ratio in this doc is in that CANVAS frame.
On screen, Big and Small (workshop 2925432336, `1.6/Base/Assemblies/BigAndSmall.dll`, ilspycmd decompile in
`D:\ClaudeWork\rimmandrake\scratch\headscale\bs\src\`) multiplies the head node's scale in a `RenderingPatches`
postfix by `BSCache.headRenderSize` (body node by `bodyRenderSize`). At default settings (no B&S settings file exists in
the live Config, so `headPowLarge` 0.8, `headPowSmall` 0.65, `visualLarger/SmallerMult` 1, `scaleBodyTypes` false), for
an adult humanlike with size offset o (`SM_BodySizeOffset` + `SM_Cosmetic_BodySizeOffset`, base body size 1):
- body = (1+o)^0.7 if o>0, (1+o)^0.75 if o<0; head = max(body-0.5, body^0.8) if body>1, else body^0.65;
  head x= `SM_HeadSize_Cosmetic` (a stat, base 1.0, that a gene's `statOffsets` can move: a per-species head-scale knob).
- Body types (Fat, Hulk, Thin) do NOT scale the head (`scaleBodyTypes` off). Head-slot apparel rides on the head node, so
  hats scale with the head (seen in `D:\ClaudeWork\rimmandrake\scratch\live5\PHONE_lineup_hat.png`).
- Implemented as `fit_head_canvas.bs_render_size()`; the selftest recomputes every species' value from it.

MEASURED: masked normalized cross-correlation of each shipped PNG, rescaled in 0.02 steps, against the live 2026-10-20
lineup (`D:\ClaudeWork\rimmandrake\scratch\live5\PHONE_lineup_bare.png`, 100.8 px per cell, so a x1.0 head mesh is
151 px; game launched 18:30, after the 18:04 install, so it shows the shipped art). Script
`D:\ClaudeWork\rimmandrake\scratch\headscale\match.py`.

| species | size source | body x | head x (formula) | head x (live, S/E/N) | NCC |
|---|---|---|---|---|---|
| Human | none | 1.00 | 1.00 | reference | |
| Lasat | `HalfJotunFrame` +0.75 (`BodySizeIsReal.xml`) | 1.48 | **1.369** | 1.36 / 1.36 / 1.36 | 0.71-0.95 |
| Mimbanese | none | 1.00 | 1.00 | 1.00 / 1.00 / 1.00 | 0.94-0.97 |
| Nelvaanian | `RSW_BodySizeGene_big` +0.20 (cosmetic when measured; real since SIZE_GENES_RECONCILE_LOST_IN_REGEN, same render) | 1.14 | **1.107** | 1.08 / 1.10 / 1.08 | 0.94-0.97 |
| Ortolan | none (Fat/Hulk do not scale it) | 1.00 | 1.00 | 1.00 / 1.00 / 1.00 | 0.94-0.96 |

So in game the on-screen skull is, in human-skull units (canvas ratio x engine scale; bbox includes appendages):

| species | south skull h / w | south bbox w / h | why it reads the way it does next to a human |
|---|---|---|---|
| Lasat | 1.37 / 1.27 | 2.02 / 1.72 | engine scale: the only real "bigger head" |
| Mimbanese | 1.00 / 0.78 | 0.81 / 1.02 | its skull is narrow (0.78 w) on a Thin body, and the human beside it wears hair, which spans ~1.5x its skull width (eyeballed from the screenshot, UNMEASURED by tool) |
| Nelvaanian | 1.10 / 0.72 | 1.04 / 1.28 | engine scale x1.11, narrow muzzle |
| Ortolan | 1.00 / 1.25 | 1.52 / 1.64 | NOT engine scale: a broad dome (1.25 w) plus pendulous ears (bbox 1.5 w, 1.6 h) on a Fat/Hulk body, as the canon "broad rounded dome continuous with the neckless body" asks |

**Correction to the live agent's reading:** the head follows body size only for the two species with a size offset
(Lasat, Nelvaanian). The Ortolan's "much larger" and the Mimbanese's "smaller" are the art's proportions, not a scale.

**The canon gives no head-to-human ratio** for any of the four (`design/RimStarWars/canon_references/{lasat,mimbanese,
nelvaanian,ortolan}/description.md`: Lasat >= 2 m, Nelvaanian 1.5 m F / 2 m M, Ortolan "squat", Mimbanese no number).
So the on-screen size is the owner's call. He ruled it by card (below, "Tune in the def").

**RULED 2026-10-20 7:25 PM PDT, owner by card: "How should head sizes be set?" -> "Tune in the def".** Option 1 below is
applied: a `SM_HeadSize_Cosmetic` statOffset on the head gene in `SW_Genes.xml`; art untouched (canvas 1.0), so the
on-screen skull = B&S head rule x multiplier. Targets are FOUNDRY's numbers from the brief (Lasat ~1.20, Nelvaanian
~1.05, Mimbanese and Ortolan 1.00); records in `head_envelope.json` `species_render`, recomputed from the defs by
`src/RimMandrake/Utils/art/selftest_head_scale_from_defs.py` (`species_size.py` prints every xenotype's size):

| species | real body size | render offset | B&S head rule | `SM_HeadSize_Cosmetic` | on-screen skull (was) |
|---|---|---|---|---|---|
| Lasat | 1.75 (`HalfJotunFrame`) | +0.75 | x1.369 | 0.88 (-0.12) | **1.20** (1.37) |
| Nelvaanian | 1.20 (`RSW_BodySizeGene_big`, now real) | +0.20 | x1.107 | 0.95 (-0.05) | **1.05** (1.11) |
| Mimbanese | 1.00 | 0 | x1.000 | 1.00 | 1.00 (1.00) |
| Ortolan | 1.00 (Fat/Hulk do not scale the head) | 0 | x1.000 | 1.00 | 1.00 (1.00) |

Making the Nelvaanian gene real does not move its sprite: B&S renders from mechanical + cosmetic offset together
(`BSCache`: `totalCosmeticSize` adds `SM_BodySizeOffset`). Mimbanese (narrow skull on Thin) and Ortolan (broad dome on
Fat/Hulk) read as art proportion, not scale, so they need no multiplier. Hats: `RenderingPatches` scales the
`PawnRenderNode_Head`, and head apparel is drawn under the head node, so the multiplier shrinks the hat with the skull
(READ, and seen in `PHONE_lineup_hat.png` for the body-size case). UNMEASURED in game until the live line-up.

**The options as they were weighed (option 1 taken):**
1. **Keep the art in the canvas frame (skull 1.0) and set the size in the def**: a `SM_HeadSize_Cosmetic` statOffset on
   the species' head gene (`RSW_LasatHead` etc. in `src/RimStarWars/StarWarsRaces/Defs/GeneDefs/SW_Genes.xml`) multiplies
   the head only. Example: Lasat -0.12 gives 1.369 x 0.88 = **1.20** human skulls (about its >= 2 m canon stature vs a
   1.8 m human, still under its x1.48 body). No art, hat or envelope change; reversible in one line. Then record
   `engine_head_scale` = formula x multiplier.
2. Or refit the art: set `onscreen_skull_target`; `fit --species S` then defaults its height ratio to target /
   engine scale (Lasat 1.0 -> canvas 0.730, Nelvaanian 1.0 -> 0.903) and `check` centres the size bands there. This
   costs a refit + `art install` and shrinks hats' fit relative to the head; prefer 1.
3. Do nothing: B&S's own head-grows-slower-than-body curve already keeps heads proportionate (Lasat head/body 0.93).

`lineup --onscreen` draws each species at its engine scale beside the human head box:
`D:\ClaudeWork\rimmandrake\scratch\headscale\lineup_onscreen.png`.

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
