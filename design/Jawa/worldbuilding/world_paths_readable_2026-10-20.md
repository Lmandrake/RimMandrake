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
- **Our FlowWorks River Colours** (`src/RimMandrake/FlowWorks/Source/RiverColors/RM_RiverColors.cs`) is a `GeneratePaths`
  prefix that replaces `riverColor` per tile. It joined the live list on 2026-10-16, when it merged into FlowWorks. Since
  2026-10-20 it colours by biome (§6).
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
| Stone | 0.4 grey | grey-brown (0.18, 0.15, 0.12) | (99,85,69) |
| Gravel (highway fill) | 0.5 grey | old asphalt (0.08, 0.08, 0.085) | (47,47,50) |
| Asphalt (centre line) | 0.3 grey | worn pale grey (0.42, 0.41, 0.38) | (189,186,177) |

| road | vanilla Outline/fill(/Asphalt) | new |
|---|---|---|
| DirtPath | 0.35 / 0.20 | 0.46 / 0.26 |
| DirtRoad | 0.55 / 0.40 | 0.62 / 0.42 |
| StoneRoad | 0.55 / 0.40 | 0.64 / 0.44 |
| AncientAsphaltRoad | 0.65 / 0.50 / 0.25 | 0.78 / 0.58 / 0.14 |
| AncientAsphaltHighway | 0.95 / 0.80 / 0.55 | 1.00 / 0.80 / 0.20 |

Rivers `widthOnWorld`: Creek 0.2→0.32, River 0.4→0.46, LargeRiver 0.6→0.62, HugeRiver 0.8→0.82. Rivers are drawn with
a copy of the ROAD material at their own queues (3520/3530), so they get the same hard edge and roads still cross over
them. The bank is the water colour × 0.22. The water colour is FlowWorks' (§6). Only a river left in vanilla
`riverColor` gets the same blue-grey (0.08, 0.16, 0.30).

Worst case per tier, and the river water: §6.

## 4. Not covered

The night side (lighting is not modelled), the Perlin wiggle on roads, and the river shader's own specular are not in
the offline preview. The live check decides.

## 5. Live check, 2026-10-20 evening (FOUNDRY, 325-mod list, `ASHKARR_DEV_START_2026-10-20_PARITY`)

Images: `D:\ClaudeWork\rimmandrake\scratch\live5\` (`P_desert_roads_ON/OFF.png`, `P_coast_close_ON/OFF.png`,
`R_85_pair.png` (top off, bottom on), `V_rivers_85.png` after the darker FlowWorks river colours, `V_umbra_roads.png`, `V_slime_roads.png`).
- Player.log: `readable world paths ON (startup): 5 road layer colours, 12 road widths, 4 river widths, river material swap on`.
- ON (before §6): dark casing, umber dirt, slate stone, gold highway. Rivers draw with dark banks, and the bank is darker than the water.
- Toggle (`jawa/mod_settings_field` `worldReadablePaths` false, `RM_WorldPaths.Apply`, `jawa/world_commit lazy`): the vanilla
  pale roads and faint gradient rivers come back. Toggling on restores the readable look. Both directions redraw live.
- **Rivers read as dashes: fixed (`e7adc75e3`).** The river data was whole: `world_links_validate` gave 0 asymmetric, 0 non-adjacent,
  and 1,568/1,568 record links present. The 326 river links form 11 connected pieces, the same in the record and the U4 file.
  The cause was the border blend in `RM_WorldLook.cs`. Its overlays sat at `blendLift` +0.01 above the terrain, the same height
  as `WorldDrawLayer_Rivers.FinalizePoint` (+0.01), and they write depth. On every biome-border tile (7,567 of them) the overlay
  won the depth test and hid the river, and the hill blots under it too (+0.005). Roads sit at +0.02 and were not hidden.
  `blendLift` is now 0.003. Live check, same view, only that value changed:
  `D:\ClaudeWork\rimmandrake\scratch\riverdashes\rd_before_4271.png` (dashes) and `rd_after_lift003_4271.png` (whole lines).
  Wide view: `rd_after_wide_16490.png`.
- Roads now draw on RUT_Umbra and RM_GelatinousSlime (`UMBRA_SLIME_ROADS_VERIFY_FINALLY_DRAWN`).

## 6. Roads in earth tones, rivers as water (2026-10-20, after the owner looked)

Owner, 2026-10-20, looking at the in-game map: *"Strangely I see what looks like a blue road on the Scald's shore towards
the Anvil. Looks like a river, but it isn't. And the river is shown brown and red. Odd colors for roads and rivers."*

- **The blue "road" is a StoneRoad.** In `ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R2.rws` the roads touching the
  Scald's shore are StoneRoad (all but 3 of 33 links). A 69-tile stone-road network runs from 9 Scald-shore tiles into
  19 Anvil tiles. Its slate fill (0.15, 0.25, 0.25) draws as teal (85,130,130) inside the dark casing, which looks like a
  river with a bank.
- **The brown and red rivers are FlowWorks' gradient.** Its anchors match no tile, so every river is coloured by
  elevation within its own network: red (#E0311C) at the top, olive-brown (#2E2E00, darkened by card that same day) in
  the middle, dark blue-teal at the bottom. RM_WorldPaths only darkens the bank to water × 0.22, so a red river gets a
  maroon bank. Both colours come from the gradient.
- **Now.** Roads use earth tones under the dark casing: umber dirt, grey-brown stone (0.18, 0.15, 0.12) on screen
  (99,85,69). No road layer is blue or teal.
  **The ancient highway is old asphalt, not gold.** Owner, 2026-10-20 (card on the highway's 46 pieces): *"Instead of
  the strange yellow highlights it should show as old asphalt broken from long ago"*. Fill is dark grey-black (0.08, 0.08,
  0.085), on screen (47,47,50). Down its middle runs a pale worn stripe (0.42, 0.41, 0.38), widths 0.20 on the highway and
  0.14 on the ancient road. The road layers take one flat colour each, so the worn look is that stripe, not patches. The
  record's broken pieces are the intended look and are not joined. The fill difference is at least 39.2 and its own
  contrast at least 3.6:1 (worst on Abyss). It sits 21.8 from stone. Rivers are blue-grey water (0.08, 0.16, 0.30) on
  screen (47,90,150). They take a tint only inside a biome whose sheet says its water is not clean: RM_Contagion blood red
  (R-H7 "the red water"), RM_Miasma brackish, RM_Wasteland toxic green (the dead-river salt basins), RM_RustCathedral
  verdigris (the captured coolant river). The tint stops at the biome border, so the Contagion's water reaches the
  lowlands clean. This replaces the 09-06 elevation gradient and the "Darken, same hues" card of the same day. The
  Mod Settings switch and the colour sliders stay. The sliders use new scribe keys.
- **Contrast** (`design.py`, every crossed land face at p10, mean and p90): stone has a fill dE of at least 22.3 (on The
  Forge) and casing at least 5.0:1. Water has a fill dE of at least 44.0 and bank at least 5.2:1. Each tint against its
  own biome has a fill dE of at least 37.9 and bank at least 5.9:1. Dirt and stone differ by dE 31.9. All PASS. Table:
  `D:\ClaudeWork\rimmandrake\scratch\pathcolors\contrast_2026-10-20.txt`.
- **Preview** (offline; live on the left, proposed on the right; desert, Scald shore, Anvil, Miasma river):
  `D:\ClaudeWork\rimmandrake\scratch\pathcolors\preview_paths_2026-10-20.png`
  (`preview.py <save> desert,scald,anvil,toxic`).
