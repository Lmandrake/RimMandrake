# Readable roads and rivers on the world map (2026-10-20)

Owner, 2026-10-20: *"Let's keep working on these biome and mountain and river and road issues. It is absolutely not
ready yet."* The in-game audit (`worldmap_in_game_audit_2026-10-20.md` §5) found all record links live but roads hard
to read (tan dirt on tan sand, the highway as short grey dashes) and rivers "barely changed". Code:
`src/RimMandrake/BiomesShell/Source/RM_WorldPaths.cs` (Baroque Biomes, Mod Settings "Planet: readable roads and
rivers", default on). Offline tools: `src/RimMandrake/Utils/worldpaths/` (`crossings.py <save>` → `design.py` →
`preview.py <save> desert|coast`), writing under the agent storage root `rimmandrake\scratch\riverroad\`.

## 1. How 1.6 draws them (RimSage source, resources.assets read with UnityPy)

- **Roads**: `WorldDrawLayer_Roads`, one mesh on `WorldMaterials.Roads` (shader `Custom/Roads`, SrcAlpha/OneMinusSrcAlpha,
  queue 3540, 0.02 above the surface). For each `RoadWorldLayerDef` by `order` (Outline 0, Dirt 100, Stone 200, Gravel
  300, Asphalt 400) a road tile emits strips from each edge midpoint to the centre, **vertex-coloured** with the layer's
  `color`. Width is `RoadDef.worldRenderSteps[layer].width`: a fraction of the hex edge on each side of the midpoint,
  alpha 1 on the centre line, 0 at the side. In game the edge is hard (worldlook3 `H_coast_close.png`), so the Outline
  layer shows as a dark casing round the next layer. Roads are not drawn on water-covered tiles. No texture is involved,
  so there is no art to generate: the look is colours and widths.
- **Rivers**: `WorldDrawLayer_Rivers`, two meshes: `RiversBorder` (queue 3520, width `widthOnWorld`, `_Alpha` 0.8) and
  `Rivers` (3530, width `widthOnWorld − 0.2`, specular), shader `Custom/Rivers`, both coloured with ONE hard-coded
  `riverColor` (73,82,100). `RiverDef` has no colour field. A creek at the vanilla 0.2 has no water mesh at all.
- **Our FlowWorks River Colours** (`src/RimMandrake/FlowWorks/Source/RiverColors/RM_RiverColors.cs`, the owner's
  2026-09-06 gradient, red headwater → brackish jungle → toxic terminus) is a `GeneratePaths` prefix that replaces
  `riverColor` per tile. It joined the live list on 2026-10-16, when it merged into FlowWorks. Before that it was a standalone mod that was not on the September list.
  Its three biome anchors (`AB_OcularForest`, `AB_FeraliskInfestedJungle`, `Wasteland`) match no tile of the dev world,
  so every river is coloured by elevation alone. Most river tiles therefore get the brackish olive-khaki middle colours.
- **Screen model** (fitted on the 2026-10-20 shots, day side, within ~5% for faces and paths alike): screen channel =
  1 − (1 − c)^2.5. Check: the model puts the gradient at t = 0.75 at (171,179,131). The river measured over Greentide in
  `H_coast_close.png` is (170,182,145).

## 2. What changed since September

Both September lists (`ModsConfig.FULL.PRECAPTURE.20260910_233444.xml`, `…20260911_131149.xml`) and today's list have
no mod that defines or patches RoadDef, RiverDef or RoadWorldLayerDef. A scan of every mod in all three lists found only
vanilla Core's defs. The mods that patch the world path layers (AlienWorlds, Worldbuilder, MapModeFramework) are in all
three lists. Road values were vanilla then and are vanilla now. Three things changed:

1. **The faces.** The 2026-10-18 palette faces are paler and closer to the dirt-road colour. Vanilla dirt against
   Stillsand on screen differs by ΔE 14.6. In the September shots, the same vanilla roads and the vanilla blue-grey
   rivers (measured (130,150,184) in `B_scald_and_seas`) crossed darker, greener faces.
2. **River colour.** FlowWorks' gradient replaced the vanilla blue-grey. Its olive middle colours sit on Greentide's
   green.
3. **The highway** is fragmented in the record itself (153 tiles in 46 pieces of 1-9 tiles). No look fixes that. It is a
   routing question for the record.

## 3. Values (casing WCAG ≥ 3 and fill ΔE76 ≥ 20 against p10/mean/p90 of every land face the tier crosses)

| layer | vanilla | new (vertex) | on screen |
|---|---|---|---|
| Outline (casing, every road) | 0.1 grey | (0.05, 0.04, 0.035) | (30,24,21) |
| Dirt | (0.5, 0.4, 0.3) | umber (0.30, 0.16, 0.07) | (150,90,42) |
| Stone | 0.4 grey | slate (0.15, 0.25, 0.25) | (85,130,130) |
| Gravel (highway fill) | 0.5 grey | gold (0.80, 0.50, 0.00) | (250,209,0) |
| Asphalt (centre line) | 0.3 grey | (0.10, 0.07, 0.05) | dark line |

| road | vanilla Outline/fill(/Asphalt) | new |
|---|---|---|
| DirtPath | 0.35 / 0.20 | 0.46 / 0.26 |
| DirtRoad | 0.55 / 0.40 | 0.62 / 0.42 |
| StoneRoad | 0.55 / 0.40 | 0.64 / 0.44 |
| AncientAsphaltRoad | 0.65 / 0.50 / 0.25 | 0.78 / 0.58 / 0.10 |
| AncientAsphaltHighway | 0.95 / 0.80 / 0.55 | 1.00 / 0.80 / 0.14 |

Rivers `widthOnWorld`: Creek 0.2→0.32, River 0.4→0.46, LargeRiver 0.6→0.62, HugeRiver 0.8→0.82. Rivers are drawn with
a copy of the ROAD material at their own queues (3520/3530), so they get the same hard edge and roads still cross over
them. The bank is the water colour × 0.22. The water colour stays FlowWorks' gradient. Only a river left in vanilla
`riverColor` gets azure (0.06, 0.33, 0.85).

Worst case per tier (proposed): dirt on Flooded Canyon has casing 7.0 and fill ΔE 26.9. Stone on Cauldron has casing 6.2
and fill ΔE 21.5. The highway on Abyss has casing 4.8 and fill ΔE 106. Vanilla fails every tier on fill ΔE (5-10). The
river BANK clears WCAG ≥ 3.4 on every face at every gradient position. The river WATER at the owner's middle and
terminus colours (t ≥ 0.5) stays within ΔE 9.5-19 of the faces it crosses, so on those stretches only the bank carries
the line. Darker anchors in the same hues would clear it (search: jungle about #1F1F00-#2E2E00, terminus about
#00293D). That is a change to his palette, so it is his decision and is not made here.

## 4. Not covered

The night side (lighting is not modelled), the Perlin wiggle on roads, and the river shader's own specular are not in
the offline preview. The live check decides.
