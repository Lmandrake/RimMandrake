# Canopy zoom — feasibility investigation (2026-10-18)

Item: `CANOPY_ZOOM_DIAGNOSE_SEE_THE_FOREST`. Investigation only; no mod code written.

## Owner's ask

Verbatim, 2026-10-18: *"I'd also like to investigate the ability to "scroll out" from the map enough that only
the top forest canopy is seen to show players just where they actually are on heavily forested maps."*

Context, same day (`design/RimMandrake/tree_size_proposal_2026-10-18.md` §Ruling): tiers Small 3-5 / Big 5-8 /
Giant 8-12 / Titanic 12-30+ cells of visual size, and *"Titanic trees should be seen only as the solid trunk"*.

**Verdict: FEASIBLE, and cheap at runtime.** The engine has no plant level-of-detail switch, but it gives us
every hook we need: a zoom value read every frame, map-mesh layers that a mod adds just by defining a class, and
a draw call per layer that a mod can gate. The zoom range itself is not the obstacle (vanilla already shows
120 cells top to bottom when fully zoomed out, and Camera+ is on the owner's list). The work is art (a separate
canopy picture per big tree) and one small C# mod. One real engine trap was found (§4.1: large canopies pop in
at the screen edge), with a known fix.

Source of every engine fact: decompiled RimWorld 1.6 via RimSage (`mcp__rimsage__*`), cited as `Class.Member`.
Facts not read from that source are marked UNVERIFIED.

## 1. CameraDriver zoom limits

- The map camera is **orthographic**: `CameraDriver.ApplyPositionToGameObject` sets
  `MyCamera.orthographicSize = RootSize`. `RootSize` is half the visible height in cells, so the screen shows
  `2 × RootSize` cells top to bottom. The camera's height is cosmetic:
  `rootPos.y = 15 + (RootSize - min)/(max - min) × 50`, i.e. 15 to 65 (`MinAltitude 15`, `MaxAltitude 65`,
  `NearClipPlane 0.5`). Every map altitude layer sits far below 15, so **nothing is ever "above the camera"**.
  Hiding a canopy at close zoom has to be a deliberate draw choice (§3).
- Limits come from `CameraMapConfig.sizeRange`, default `FloatRange(11, 60)` (7.2 to 60 on Steam Deck);
  `CameraMapConfig_SmoothZoom` sets min 8.2. `CameraDriver.CameraDriverOnGUI` clamps `desiredSize` to it.
  `CameraDriver.StartingSize = 24`.
- The range is a public field on a public config (`CameraDriver.config`), saved through
  `CameraMapConfig.ExposeData`, exposed by the dev dialog `Dialog_CameraConfig` ("ZoomRange" slider 0-100).
  Vanilla itself sets `Find.CameraDriver.config.sizeRange.max = 150` for a screenshot debug action
  (`DebugActionsMapManagement`, landmark screenshot loop). So a larger range is supported by the engine; a mod
  just writes the field.
- Pixels per cell: `CameraDriver.CellSizePixels = screenHeight / (RootSize × 2)`. At 1080p: 49 px/cell at
  size 11, 9 px/cell at size 60, 3.6 px/cell at size 150.
- Zoom bands: `CameraDriver.CurrentZoom` returns `Closest` (< min+1), `Close` (< 0.23·max), `Middle` (< 0.7·max),
  `Far` (< 0.95·max), else `Furthest`. **The bands are relative to `sizeRange.max`**, so any mod that changes the
  range moves every band. A canopy switch should key on `CellSizePixels` (absolute), not on `CurrentZoom`.
- Existing far-zoom behaviour in vanilla: `SilhouetteUtility.CanHighlightAny` turns on pawn dots/silhouettes only
  when `ZoomRootSize >= 0.9 × sizeRange.max`, fading in with `InverseLerp(0.85·max, max)`
  (`SilhouetteUtility.GetAlpha`); `SelectionDrawer` uses the same fade. These draw on the `Silhouettes` altitude
  layer, above everything, so pawns stay findable over any canopy.
- **Camera+** (`brrainz.cameraplus`, workshop 867467808) is installed and in the owner's full list
  (`infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`). Its README: "Maximum zoomed out factor", far-zoom
  dot/silhouette markers, and label hiding "based on screen-cell size". How it patches `CameraDriver` was NOT
  read (DLL not decompiled): UNVERIFIED. A second workshop mod, SimpleCameraSetting (`ray1203.SimpleCameraSetting`),
  edits the same `sizeRange` and says "Do not use it with camera+"; whether it is on the owner's list: not checked.
  **Consequence:** we do not need to ship a zoom-range change of our own; we must coexist with Camera+.

## 2. How plants render at distance

- **There is no zoom-dependent plant rendering in vanilla.** Every `CurrentZoom` / `ZoomRootSize` / `RootSize`
  reader in the source was listed (regex search): labels, bed/assignment overlays, stack labels, progress-bar
  motes, debug cells, the pawn render cache (`PawnRenderer`, `ZoomRootSize > 18`), camera shake, silhouettes,
  tick-rate of visual updates (`GenTicks.GetCameraUpdateRate`), an Undercave ambience. None touches plants.
- Trees are baked into a static mesh: `TreeBase` (`Data/Core/Defs/ThingDefs_Plants/Plants_Bases.xml`, inherited
  from `PlantBaseNonEdible`) is `drawerType MapMeshOnly`, `altitudeLayer Building`, shader `CutoutPlant`.
  `SectionLayer_ThingsGeneral.TakePrintFrom` calls `Thing.Print(layer)`; `Plant.Print` writes one square quad of
  side `drawSize.x × visualSizeRange.LerpThroughRange(growth)` (for `maxMeshCount 1`). The mesh is rebuilt only
  when a section is dirtied (`Section.TryUpdate`, flag `MapMeshFlagDefOf.Things`), never on zoom.
- Map meshes are 17×17-cell `Section`s (`Section.Size = 17`). **A `Section` builds one instance of every
  non-abstract `SectionLayer` subclass in the loaded assemblies** (`Section` constructor,
  `typeof(SectionLayer).AllSubclassesNonAbstract()`). So a mod adds a new map-mesh layer just by defining the class.
- Each layer draws through `MapDrawLayer.DrawLayer`, which a subclass can override (vanilla
  `SectionLayer_Things.DrawLayer` already gates on `DebugViewSettings.drawThingsPrinted` and on the gravship
  cutscene). **That override is the zoom switch:** draw the canopy layer only when `CellSizePixels` is below a
  threshold. Zooming changes no mesh, so it costs nothing.
- Use the `DrawLayer` override, not `MapDrawLayer.Visible`: `Section.RegenerateAllLayers` and
  `RegenerateDirtyLayers` skip a layer whose `Visible` is false. A layer that was hidden when the map loaded would
  be empty when it became visible, until something dirtied that section.
- To hide trunks or undergrowth at far zoom, the same pattern works in reverse: the plant prints nothing into
  `SectionLayer_ThingsGeneral` (a `thingClass` subclass of `Plant` overriding `Print`), and a layer of ours prints
  it and gates its own draw. Copy the vanilla filters from `SectionLayer_Things.Regenerate`: skip fogged things
  (unless `seeThroughFog`), things hidden by snow or sand depth (`hideAtSnowOrSandDepth`), plants on thin ice.

## 3. Titanic: trunk when close, canopy when far

The ruling *"seen only as the solid trunk"* and the ask *"only the top forest canopy is seen"* are the two ends
of one zoom switch:

| zoom | what draws | engine route |
|---|---|---|
| close (cell ≥ T px) | trunk sprite only; the colony under it stays visible | `Plant.Print` override in our `thingClass` prints the trunk quad into `SectionLayer_ThingsGeneral` |
| far (cell < T px) | canopy sprite over the trunk; the forest reads as a map | our `SectionLayer_Canopy` prints canopy quads; its `DrawLayer` runs only when `CellSizePixels < T` |
| between | crossfade | set the canopy material's colour alpha once per frame, like `SilhouetteUtility.GetAlpha`. Cutout shaders clip on alpha, so a true fade needs a transparent shader on the canopy layer: UNVERIFIED which vanilla shader fits (`ShaderDatabase.Transparent` is the candidate) |

- The trunk can be printed at every zoom: under the canopy it is hidden anyway. Only the canopy needs a switch.
- Choose the canopy altitude deliberately. Pawns draw at `Pawn` (23), above `Building` (15) where trees sit
  (`AltitudeLayer` order as recorded in `src/RimMandrake/Utils/plant_draw_layers.py`). If the canopy stays below
  `Pawn`, pawns show on top of the canopy, which is what "where they actually are" needs. If it sits higher, it
  hides pawns and only the silhouettes (above everything) mark them. Recommended: below `Pawn`.
- Giant (8-12) trees can use the same two-picture route if he wants them treated like Titanic. Small and Big
  keep vanilla drawing.
- The tree body (pathing, selection, cover) is unaffected; it stays the 1×1 cell plus HugeThings blockers
  (`design/RimMandrake/giant_footprint_design_2026-10-07.md`).

## 4. Performance risks

### 4.1 Pop-in at the screen edge (a real engine trap)

`SectionLayer_Things.Regenerate` grows a section's bounds by `thing.OccupiedDrawRect()`, and
`GenAdj.OccupiedDrawRect` uses `Thing.DrawSize`, which is `def.graphicData.drawSize` (`Thing.DrawSize`; `Plant`
does not override it: searched, only `Tornado` does). It **ignores `visualSizeRange`**. A tree sized the way the
tree proposal recommends (`drawSize 1`, size from `visualSizeRange`) keeps 1×1 bounds. `MapDrawer.DrawMapMesh`
draws a section only if the view overlaps `section.Bounds`, and `MapDrawLayer.RefreshSubMeshBounds` pads the
mesh bounds by only 2 cells. A canopy reaching 6-15 cells beyond its root's section would **vanish while still on
screen**, as soon as that section scrolls out of view. (Unity's own frustum culling by mesh bounds follows the
same rule; standard Unity behaviour, not read from source: UNVERIFIED here.)
Fix in our own layer: override `GetBoundaryRect` to cover the true canopy rect (vanilla `SectionLayer_SunShadows`
and `SectionLayer_EdgeShadows` both override it), so the section is drawn whenever any part of a canopy is in
view. Whether today's largest tree (`RM_VaultRoot`, 10.4 cells drawn) already pops at the edge: UNMEASURED; it
is the cheapest live check of this prediction.

### 4.2 Overdraw

Static mesh means no CPU per frame. The cost is GPU fill. Worked example (illustrative numbers, not measured):
200 Titanic trees with 20-cell canopies on a 250×250 map cover 80,000 cell-areas against 62,500 cells, about
1.3 layers deep; 9,000 small 4-cell trees add about 2.3. A few layers of alpha-tested quads is ordinary for a
desktop GPU at 1080p. Real frame cost on the owner's list: UNMEASURED.

### 4.3 Texture memory: the real cost

At the art ruling of 128 px per cell, a 30-cell canopy is 3,840 px square, about 15-20 MB compressed with
mipmaps per texture (estimate; RimWorld's import settings were not read: UNVERIFIED), times every variant. But
**the canopy is only ever seen zoomed out**, where a cell is 9 px or less (§1). Canopy art at 16-32 px per cell
(512-1024 px for 30 cells) loses nothing. The trunk is seen close and keeps full density. This needs a ruling,
since it is an exception to the 128 px rule.

### 4.4 Draw order and wind

- Inside one altitude layer, order between quads is hash-random (`plant_draw_layers.py` WHY note). Overlapping
  canopies will layer in arbitrary order. Probably harmless for foliage; it needs a look.
- `CutoutPlant` sways the top vertices with wind (`Plant.Print` passes per-vertex wind data). On a 30-cell quad
  that may look rubbery: UNVERIFIED. Our canopy layer can use a non-wind shader.

### 4.5 Regeneration

Cutting or growing one tree dirties its 17×17 section (`MapDrawer.MapMeshDirty`), so it regenerates one layer
for one section: cheap. A canopy layer with a widened `GetBoundaryRect` is drawn a little more often: negligible.

## 5. Design options

**A. Two-picture big trees with a zoom-gated canopy layer (RECOMMENDED).**
Titanic (and optionally Giant) trees get a trunk sprite and a canopy sprite. A `Plant` subclass prints the trunk;
a new `SectionLayer_Canopy` prints canopies, widens its bounds (§4.1) and draws only below a pixels-per-cell
threshold, with a crossfade. Mod Settings: on/off, threshold, fade width.
*Buys:* exactly the ask (zoomed out, the forest reads as a canopy map; pawns on top), and exactly the Titanic
ruling (zoomed in, solid trunk only). No per-frame cost, compatible with Camera+.
*Costs:* a second picture per big tree (low-density art, §4.3), one small C# mod plus its debug script
(standing rule), the art-density ruling.

**B. A generated "forest map" overlay at the furthest zoom.**
One global layer draws a canopy-coverage picture computed from tree positions (soft green blobs sized by tier),
shown only when fully zoomed out.
*Buys:* no new tree art; covers every tree on the map, ours and vanilla; nearly free to draw.
*Costs:* stylised rather than painted, so it reads as a map overlay, not the forest itself. It also does not
deliver "Titanic seen only as trunk". It can be layered onto A later.

**C. Zoom range only.**
Rely on Camera+ (already loaded) for a wider range, plus vanilla's far-zoom silhouettes.
*Buys:* zero work.
*Costs:* does not solve the ask. Trees draw at full size at every zoom, and a 12-30-cell Titanic canopy would
bury the colony when zoomed in, which breaks the trunk ruling.

**Recommendation: A**, built after the tier sitting fixes which trees are Titanic or Giant. B stays a later add-on.
Before building, run the one cheap live check: does `RM_VaultRoot` pop at the screen edge today (§4.1)?

## Sources

All read 2026-10-18 from decompiled RimWorld 1.6 via RimSage: `Verse.CameraDriver` (`CurrentZoom`,
`CameraDriverOnGUI`, `Update`, `ApplyPositionToGameObject`, `CurrentViewRect`, `CellSizePixels`, constants),
`Verse.CameraMapConfig`, `Verse.CameraMapConfig_SmoothZoom`, `Verse.Dialog_CameraConfig`,
`Verse.DebugActionsMapManagement`, `Verse.SilhouetteUtility`, `RimWorld.SelectionDrawer`, `Verse.GenTicks`,
`Verse.MapDrawer` (`DrawMapMesh`, `VisibleSections`, `MapMeshDirty`), `Verse.Section`, `Verse.MapDrawLayer`,
`Verse.SectionLayer`, `Verse.SectionLayer_Things`, `Verse.SectionLayer_ThingsGeneral`, `RimWorld.Plant.Print`,
`Verse.GenAdj.OccupiedDrawRect`, `Verse.Thing.DrawSize`, `Data/Core/Defs/ThingDefs_Plants/Plants_Bases.xml`.
Camera+: its `About/About.xml` and `README.md` in workshop folder 867467808 (DLL not decompiled).
