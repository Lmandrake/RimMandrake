# Bridge art — census, sheet, GPT review (2026-10-21)

Owner, live 2026-10-21 ~21:05 PDT: "Please make a sheet with all your bridge art on it, then send it too to GPT for review and improvement suggestions."

## Census
Searched every Defs/Patches XML under src/ for defNames/labels matching bridge|plank|ford|jetty|span (plus the drawbridge texture manifest and artpipe jobs). **128 sheet rows**: 76 defs (24 ThingDef/TerrainDef + 52 ThingStyleDef) + 52 drawbridge manifest rows.

| defName | type | texPath | file |
|---|---|---|---|
| RM_DrawbridgeGate | ThingDef | Things/Building/Door/DoorSimple_Mover | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_Drawbridge.xml |
| RM_DrawbridgeWinch_Steel | ThingDef | Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionAnchor_Steel | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_Drawbridge.xml |
| RM_DrawbridgeWinch_Timber | ThingDef | Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionAnchor_Timber | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_Drawbridge.xml |
| RM_RaidPlank | ThingDef | Things/Item/Resource/WoodLog | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_Drawbridge.xml |
| RM_RaidPlank_Laid | ThingDef | Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionDeck_Timber_Atlas | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_Drawbridge.xml |
| RM_PitCover_PlankLattice | ThingDef | Things/Building/FlowWorks/Canals/RM_PitCover_PlankLattice | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_PitCovers.xml |
| RM_SuspensionAnchor_Heavy | ThingDef | Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionAnchor_Heavy | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionBridges.xml |
| RM_SuspensionAnchor_Rope | ThingDef | Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionAnchor_Rope | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionBridges.xml |
| RM_SuspensionAnchor_Steel | ThingDef | Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionAnchor_Steel | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionBridges.xml |
| RM_SuspensionAnchor_Timber | ThingDef | Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionAnchor_Timber | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionBridges.xml |
| RM_SuspensionDeck_Heavy | ThingDef | Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionDeck_Heavy_Atlas | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionBridges.xml |
| RM_SuspensionDeck_HeavyGrated | ThingDef | Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionDeck_HeavyGrated_Atlas | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionBridges.xml |
| RM_SuspensionDeck_Rope | ThingDef | Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionDeck_Rope_Atlas | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionBridges.xml |
| RM_SuspensionDeck_Steel | ThingDef | Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionDeck_Steel_Atlas | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionBridges.xml |
| RM_SuspensionDeck_SteelGrated | ThingDef | Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionDeck_SteelGrated_Atlas | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionBridges.xml |
| RM_SuspensionDeck_Timber | ThingDef | Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionDeck_Timber_Atlas | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionBridges.xml |
| RM_SuspensionJetty_Heavy | ThingDef | Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionJetty_Heavy | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionBridges.xml |
| RM_SuspensionJetty_Steel | ThingDef | Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionJetty_Steel | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionBridges.xml |
| RM_SuspensionRailing | ThingDef | Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionRailing_Edge | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionBridges.xml |
| RM_SuspensionTower | ThingDef | Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionTower | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionBridges.xml |
| RM_SuspensionWreck | ThingDef | Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionWreck | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionBridges.xml |
| RM_FordStones | TerrainDef | Terrain/Surfaces/RM_FordStones | src/RimMandrake/FlowWorks/Defs/Rivers/RM_FordStones.xml |
| RM_HeavyMushroomBridge | TerrainDef | (inherited) | src/RimMandrake/TheRot/Defs/TerrainDefs/RM_RotSporeKit_Terrain.xml |
| RM_MushroomBridge | TerrainDef | (inherited) | src/RimMandrake/TheRot/Defs/TerrainDefs/RM_RotSporeKit_Terrain.xml |
| RM_Suspension{Deck,Anchor,Jetty,Railing,Tower,Wreck}_*_{Scrapper,Industrial,Modern,Futuristic} (52) | ThingStyleDef | RimMandrake/FlowWorks/SuspensionBridge/<Look>/RM_Suspension<Part>[_Atlas] | src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionStyles.xml |
| DB_* (52 rows: winch / raised leaf face-underside-edge / gate open-closed / planks, timber+steel+four looks; raid plank item/laid/end; 3 gizmo icons) | texture manifest (C#-drawn, no def; renders NOT installed) | Things/Building/FlowWorks/Drawbridge/RM_Drawbridge* | src/RimMandrake/FlowWorks/art_source/Drawbridge/drawbridge_art_manifest.json |

Not bridge art (excluded): RM_ShipPart_BridgeConsole (a ship's bridge), RM_RestringSpan (GimmeSomeSlack designation, no art), RM_Duckboards / RM_Glasswalk (Sump walkways on vanilla WoodFloor / WaterDeepRamp textures), genes matching "span". GimmeSomeSlack has no bridge defs. Placeholders in the census: RM_DrawbridgeWinch_* reuse the suspension anchor texture; RM_DrawbridgeGate reuses vanilla DoorSimple_Mover; RM_RaidPlank reuses vanilla WoodLog; RM_RaidPlank_Laid reuses the timber deck atlas — the commissioned drawbridge renders (DB_* rows) are the intended art, not yet installed.


## Sheet
- URL: http://localhost:34285/?t=agm0IJxtds-7iaAsdM9uhQ
- Native path: `\\wsl.localhost\Ubuntu\home\mandrake\rm\bench\Transient\biome_ffar\all_bridge_art_sheet_2026-10-21.html` (decisions: `all_bridge_art_sheet_2026-10-21.decisions.json` beside it)
- Built by `art_sheet.py --subjects <76 defs> --textures src/RimMandrake/FlowWorks/art_source/Drawbridge/drawbridge_art_manifest.json --name all_bridge_art` — art_sheet.py gained `--subjects` + `--textures` together this sitting (`subjects_with_textures`, selftest `selftest_subjects_with_textures.py`), because the drawbridge renders live only in a texture manifest.
- 128 rows; `scaled_review_gate.py check` PASS; `game_art.py deliver` OK (stamp v1); `sheet_freshness.py verify` exit 0 (FRESH, 128 rows).
- Already-ruled rows collapsed: **0** — no bridge row has an owner ruling on any other sheet (the suspension four-looks sheet 2026-10-21, the drawbridge art sheet 2026-10-20, awaiting_pick and flowworks_owner_walk sheets all hold prefill only).
- Superset of `Transient/biome_ffar/suspension_four_looks_sheet_2026-10-21.html` (all 54 of its rows are here) and of `drawbridge_art_sheet_2026-10-20.html` (all 52 rows).
- 28 rows show no picture: 26 drawbridge renders that never landed (image-service 429s / 2 failed jobs) and RM_MushroomBridge / RM_HeavyMushroomBridge (TerrainDefs — the subject resolver reads ThingDefs only; their texture is RotSporeKit/Terrains/MushroomBridge/MushroomBridge).


## GPT findings per piece
GPT (gpt-6.1-sol via `gpt_consult.py -i`, two calls, 10 + 5 true-scale contact sheets in `Transient/pile_2026-10-21/bridge_art_gpt/`). Its replies verbatim below; numbers are `#n` on the named contact sheet. In the drawbridge reply GPT abbreviated: **B1/B2** = `6_drawbridge_base_p1/p2.png`, **L1/L2** = `7_drawbridge_looks_p1/p2.png`, **M** = `8_plank_ford_misc_p1.png`. A DB row may hold candidates of several looks (render_match is a substring).

### Suspension bridge (base tiers + four looks)

Atlas grids are expected. These judgments concern the art within each variant, with priority given to the 32 px/cell appearance. No DB pieces appear in these sheets.

**1_suspension_base_p1.png**

- **#1 Heavy anchor:** ok
- **#2 Rope anchor:** ok
- **#3 Steel anchor:** ok
- **#4 Timber anchor:** ok
- **#5 HeavyGrated deck:** Fine, dark mesh loses its supporting structure at play scale. Redraw with fewer, thicker bars and a clearly heavier perimeter.
- **#6 Heavy deck:** ok
- **#7 Rope deck:** ok
- **#8 SteelGrated deck:** Thin, uniform lines read as screening. Strengthen the frame and alternate substantial bearing bars with finer crossbars.
- **#9 Steel deck:** ok
- **#10 Timber deck:** ok
- **#11 Heavy jetty:** ok
- **#12 Steel jetty:** ok

**1_suspension_base_p2.png**

- **#13 Railing:** Posts and handrail nearly disappear beside the pawn. Thicken both; give posts distinct caps and short southward height.
- **#14 Tower:** ok
- **#15 Wreck:** ok

**2_scrapper_p1.png**

- **#1 Heavy anchor:** Small tapered fitting lacks Heavy’s grounded mass. Add a broad salvaged mounting shoe, oversized bolts, and a thicker cable connection.
- **#2 Steel anchor:** Reads as the same wooden fitting. Replace its central body with visibly welded steel plates; retain rope only as improvised binding.
- **#3 Timber anchor:** Timber is barely identifiable at play scale. Enlarge the wooden mounting block and show an unmistakable end-grain face.
- **#4 HeavyGrated deck:** Fine rusty lines become brown noise. Use fewer welded bars, uneven spacing, and a substantial scrap-channel frame.
- **#5 Heavy deck:** Dense straps and small patches compete with the walking surface. Consolidate into broader planks and two or three large repairs.
- **#6 SteelGrated deck:** Same weight as HeavyGrated. Use a slimmer angle-iron frame and simpler mesh while preserving a continuous walkable surface.
- **#7 Steel deck:** Reads predominantly as timber. Introduce broad, flush scrap-sheet panels with restrained welds and exposed steel edges.
- **#8 Timber deck:** ok
- **#9 Heavy jetty:** ok
- **#10 Steel jetty:** Visually duplicates Heavy’s wooden platform. Use a lighter steel perimeter and recognizable sheet-metal walking surface.
- **#11 Railing:** Rope and tiny lashings vanish. Enlarge the main rope and use fewer, chunkier lashings/posts.
- **#12 Tower:** Reads as a frontal wooden cabinet; its cap lacks a clear top plane. Redraw a broad saddle top, foreshortened front, and short visible south face.

**2_scrapper_p2.png**

- **#13 Wreck:** ok

**3_industrial_p1.png**

- **#1 Heavy anchor:** Compact plug silhouette undersells Heavy. Widen the ground plate, enlarge the housing, and use fewer, larger fasteners.
- **#2 Steel anchor:** Identical mass to Heavy. Give it a narrower bolted shoe and clearly exposed steel tensioning hardware.
- **#3 Timber anchor:** Entirely reads as steel. Add a substantial timber sleeper beneath the industrial clamp, with visible grain and end caps.
- **#4 HeavyGrated deck:** Fine bars and miniature hazard marks disappear. Thicken bearing bars and reserve warning paint for broad perimeter sections.
- **#5 Heavy deck:** Repeated tread highlights shimmer into texture noise. Reduce tread density and establish large plates inside a heavier frame.
- **#6 SteelGrated deck:** Heavy and Steel have the same silhouette. Slim the perimeter and reduce cross-bracing; retain readable bearing bars.
- **#7 Steel deck:** Tread detail overwhelms plate construction. Simplify to broad steel sheets, sparse tread marks, and clear seams.
- **#8 Timber deck:** Indistinguishable from steel flooring. Restore timber boards, reinforced with riveted steel straps.
- **#9 Heavy jetty:** Walkable, but dense bright tread competes with its outline. Enlarge plates and sparsify tread; retain the substantial edge.
- **#10 Steel jetty:** Duplicates Heavy. Reduce frame width and border hardware to communicate lighter construction.
- **#11 Railing:** Tiny alternating warning squares flicker at play scale. Use longer paint bands and thicker posts.
- **#12 Tower:** Tall frontal panel reads as a locker. Show the saddle’s upper surface and projecting base; shorten the uninterrupted front elevation.

**3_industrial_p2.png**

- **#13 Wreck:** ok

**4_modern_p1.png**

- **#1 Heavy anchor:** Small red fitting lacks a heavy mounting silhouette. Add a broad painted housing and substantial exposed mounting plate.
- **#2 Steel anchor:** Same girth as Heavy. Use a compact rectangular steel bracket with a thinner shoe and restrained red accents.
- **#3 Timber anchor:** No visible timber construction. Put the painted tensioner on a clearly exposed wooden sleeper.
- **#4 HeavyGrated deck:** Bright fine mesh resembles fencing. Add a broad red structural frame and fewer, stronger bearing bars.
- **#5 Heavy deck:** ok
- **#6 SteelGrated deck:** Same construction weight as HeavyGrated. Narrow the red frame and simplify the mesh into readable bar groups.
- **#7 Steel deck:** Duplicates Heavy’s panel construction. Use thinner edge channels and smaller, cleaner panel divisions.
- **#8 Timber deck:** Painted metal completely replaces the timber identity. Expose broad timber boards between clean red steel edge channels.
- **#9 Heavy jetty:** ok
- **#10 Steel jetty:** Exact Heavy silhouette. Reduce edge girth and corner blocks; preserve the clear, flat walking surface.
- **#11 Railing:** Red handrail reads, but supports are weak. Thicken and simplify the silver posts into distinct upright silhouettes.
- **#12 Tower:** Frontal red-and-grey cabinet appearance. Redraw the top saddle as a visible horizontal plane, with a shorter south face and grounded base.

**4_modern_p2.png**

- **#13 Wreck:** Large tan wooden fragments dilute the Modern identity. Replace some with folded grey panel backs and broken red edge channels.

**5_futuristic_p1.png**

- **#1 Heavy anchor:** Bright, narrow fitting reads lightweight. Add a broad white ground shoe and heavier housing; confine teal to recessed seams.
- **#2 Steel anchor:** Same silhouette as Heavy. Make a compact exposed-metal bracket with smaller white covers.
- **#3 Timber anchor:** Timber tier disappears entirely. Expose a wooden mounting sleeper beneath the white tensioner.
- **#4 HeavyGrated deck:** Near-white mesh loses structural hierarchy. Darken recesses and enlarge the frame and primary bearing bars.
- **#5 Heavy deck:** Dense cyan lines suggest illuminated equipment panels. Use broad matte floor plates, darker seams, and sparse recessed teal strips.
- **#6 SteelGrated deck:** Similar weight to HeavyGrated; fine bars dominate. Use a slim dark frame and fewer readable silver bars.
- **#7 Steel deck:** Duplicates Heavy and retains the luminous grid. Simplify panel divisions and reduce border thickness.
- **#8 Timber deck:** Reads as another white metal floor. Restore visible timber boards with discrete sci-fi reinforcement fittings.
- **#9 Heavy jetty:** Cyan cross and long inset panels suggest a display or glazed lid. Use matte walking panels, stronger perimeter structure, and restrained seam lighting.
- **#10 Steel jetty:** Duplicates Heavy’s girth. Slim the frame and corner fittings while simplifying the luminous markings.
- **#11 Railing:** Pale supports merge with the bright handrail. Use darker, thicker posts beneath one clear teal rail.
- **#12 Tower:** Frontal appliance silhouette; bright panels flatten its volume. Expose the saddle top, shorten the front face, and darken the recessed underside.

**5_futuristic_p2.png**

- **#13 Wreck:** ok

**TOP 5 findings overall**

1. **Styled towers need camera correction.** Their frontal elevations obscure the horizontal saddle and make them resemble cabinets.
2. **Heavy, Steel, and Timber identities collapse.** Styled sets repeatedly reuse the same silhouette; several Timber pieces show no wood.
3. **Fine detail exceeds play-scale readability.** Mesh, tread, rivets, and lashings need fewer, larger marks and stronger structural outlines.
4. **Some floors need clearer walking surfaces.** Scrapper detail becomes layered clutter; Futuristic lighting suggests equipment rather than flooring.
5. **Styled anchors need visible mounting structure.** Their small tapered bodies communicate fittings more strongly than grounded bridge anchors.

**RANKED REDRAW LIST**

1. **All styled p1 #12 towers:** Rebuild around a visible saddle top, foreshortened front, and projecting ground base.
2. **Industrial/Modern/Futuristic p1 #8 Timber decks:** Restore unmistakable wooden boards with look-specific reinforcement.
3. **All styled p1 #1–3 anchors:** Establish distinct heavy shoe, light steel bracket, and timber sleeper silhouettes.
4. **Futuristic p1 #5, #7, #9–10:** Replace luminous grids with matte walkable plates and sparse recessed lighting.
5. **Scrapper p1 #5, #7:** Simplify repairs into broad flush surfaces; make Steel visibly metallic.
6. **Base p1 #5, #8; all styled p1 #4, #6:** Rebuild grating with readable bearing bars and differentiated frame weights.
7. **Industrial p1 #5, #7, #9:** Reduce tread sparkle and enlarge plate divisions.
8. **All styled p1 #10; Modern p1 #7:** Reduce structural girth to distinguish Steel from Heavy.
9. **Base p2 #13; all styled p1 #11:** Thicken handrails/posts and simplify small decoration.
10. **Modern p2 #13:** Replace prominent timber debris with broken painted-panel construction.

### Drawbridge, raid plank, lattice, ford

Judging the **32 px/cell insets** first. Raised leaves can legitimately tower above pawns; their height must match the bridge’s span. Atlas grids are expected. Sheet abbreviations below also identify pieces in the final lists.

**6_drawbridge_base_p1.png — B1**

- **#1 DB_Gate_Timber_Closed:** ok
- **#2 DB_Gate_Timber_Open:** ok
- **#3 DB_LeafUp_Steel_Edge:** Edge and chain become fragile lines at play scale. Give the edge a continuous dark outline, lighter thickness strip, and distinct hinge block; simplify chain links.
- **#4 DB_LeafUp_Steel_Face:** Narrow blade silhouette undersells a cell-wide crossing; rivets dominate the surface. Widen the deck face within its footprint and use fewer, larger fasteners.
- **#5 DB_LeafUp_Timber_Edge:** Thin brown edge disappears against earth. Strengthen the outer contour and hinge; separate wood from iron with broad value changes.
- **#6 DB_LeafUp_Timber_Face:** ok
- **#7 DB_LeafUp_Timber_Underside:** Appears dramatically shorter than #6, breaking the shared leaf geometry. Match face, underside, and edge lengths for the same span; retain the underside’s diagonal bracing.
- **#8 DB_Planks_Steel:** Reads as stacked metal plates with a chain across them. Narrow, tapered surface and deep end layers weaken walkability. Redraw a flat, parallel-sided deck covering most of the footprint; remove the crossing chain and compress edge thickness.
- **#9 DB_Winch_Steel:** Strong silhouette, but copper patches and improvised construction read Scrapper. Assign this candidate to Scrapper; a generic steel version needs regular steel framing and restrained patchwork.
- **#10 DB_Winch_Steel:** White/teal clearly reads Futuristic. Camera is low and lateral, emphasizing machinery sides. Raise the viewpoint to expose housing tops; consolidate small vents and rings.
- **#11 DB_Winch_Steel:** Industrial identity works. Dense drum detail merges at 32 px. Simplify to a dark chain mass, clear drum rims, and broad hazard markings.
- **#12 DB_Winch_Steel:** Nearly frontal presentation compresses depth into a tall machinery face. Show more top surfaces and a clear ground base; enlarge the drum silhouette relative to its fittings.

**6_drawbridge_base_p2.png — B2**

- **#13 DB_Winch_Steel:** Modern red paint reads clearly, but frontal housing and tiny controls flatten the mechanism. Raise the camera slightly; simplify controls and retain the red frame as its defining shape.
- **#14 DB_Winch_Timber:** Strong diagonal, isometric presentation clashes with the cardinal gates. Roof dominates the drum and spreads beyond the cell. Redraw with aligned axes, shallower roof, and an exposed timber-supported spool.
- **#15 DB_Winch_Timber:** Black steel shed overwhelms the timber tier; wood is effectively invisible. Expose substantial timber uprights and crossmembers, reduce the roof, and reserve steel for drum and fittings.
- **#16 DB_Winch_Timber:** Large pitched roof makes a miniature house silhouette. Lower/remove the roof and enlarge the visible spool; keep timber beams thick enough to survive reduction.
- **#17 RM_DrawbridgeGate:** Pale panel reads as a sealed hatch, with weak gate mechanics. Add a readable hinge/roller and threshold, clearer frame depth, and stronger separation between panel and supports.
- **#18 RM_DrawbridgeWinch_Steel:** Tiny paired bases and long cables read as anchor posts. Add visible winding drums, axle/crank, and broader bases; give cables clear attachment points.
- **#19 RM_DrawbridgeWinch_Timber:** Same anchor-post problem; rope is clearer than the machinery. Build recognizable timber spool supports with iron collars and a visible crank.

**7_drawbridge_looks_p1.png — L1**

- **#1 DB_Futuristic_Winch_Steel:** Same low-camera issue as B1 #10. Expose more white housing tops and simplify internal rings; retain teal as broad accents.
- **#2 DB_Industrial_Gate_Closed:** Industrial palette works, but dense mesh becomes dark noise. Replace fine mesh with broad steel panels or coarse grating; preserve riveted posts and hazard corners.
- **#3 DB_Industrial_Winch_Steel:** Same as B1 #11: simplify drum/chain detail into larger masses.
- **#4 DB_Industrial_Winch_Timber:** Same as B2 #15: expose timber structure and reduce the steel roof.
- **#5 DB_Modern_Gate_Open:** Side supports are chunky relative to the passage, while fine roller detail disappears. Slim the inward-facing posts and simplify the overhead mechanism into clear painted blocks.
- **#6 DB_Modern_Planks:** Reads as a narrow road ramp or stacked bridge module. Perspective taper, raised bands, and layered end impede flooring readability. Use straight-down, parallel-sided panels with shallow seams and flush end joints.
- **#7 DB_Modern_Winch_Steel:** Same as B2 #13: show more housing top, simplify controls, preserve the red frame.
- **#8 DB_Scrapper_Gate_Closed:** ok
- **#9 DB_Scrapper_LeafUp_Edge:** Thin rusty edge and chain disappear into the terrain. Strengthen the perimeter, hinge, and a few large patch silhouettes; remove tiny surface scratches.
- **#10 DB_Scrapper_LeafUp_Face:** Appears substantially shorter than its edge and underside companions. Match their hinge-to-tip length for the same span; retain the patched, irregular construction.
- **#11 DB_Scrapper_LeafUp_Underside:** ok
- **#12 DB_Scrapper_Winch_Steel:** ok

**7_drawbridge_looks_p2.png — L2**

- **#13 DB_Scrapper_Winch_Timber:** Scrapper materials work; diagonal camera and roof-heavy silhouette repeat B2 #14. Align the structure to the gate camera, shrink the canopy, and expose the drum and timber supports.

**8_plank_ford_misc_p1.png — M**

- **#1 DB_Icon_Raise:** ok
- **#2 DB_RaidPlank_LaidEnd:** Raised rings, rope, and heavy end fittings suggest an upright hatch. Flatten the lighting, recess the fittings, and place rope along the margin of a continuous walking surface.
- **#3 DB_RaidPlank_Laid:** Handle-like rope and strong board relief suggest a door panel. Use straight-down plank shading, shallow metal straps, and an edge-mounted rope loop.
- **#4 RM_FordStones:** ok
- **#5 RM_FordStones:** ok
- **#6 RM_PitCover_PlankLattice:** Reads as a loose debris pile; dark openings undermine safe footing. Square the outer frame to the cell, flatten the perspective, and arrange wider boards into a deliberate load-bearing lattice.
- **#7 RM_RaidPlank:** Round cut end, diagonal pose, and foliage read as a loose log. For the deployed crossing, redraw a flattened, broad walking top aligned with travel; retain bark along the sides.
- **#8 RM_RaidPlank_Laid:** ok
- **#9 RM_RaidPlank:** Twisted, tapering branch silhouette gives little usable tread. Redraw the deployed form as a straighter split trunk with a continuous flat top and restrained protrusions.

**1. TOP 5 findings overall**

1. **Walkability is the biggest failure:** steel/Modern decks, loose logs, and the lattice need continuous, flat tread surfaces.
2. **Camera conventions vary:** lateral machinery, diagonal sheds, and frontal gates need one shared orthographic camera.
3. **Raised-leaf geometry needs coordination:** face, edge, and underside must share span, width, hinge, and attachment positions.
4. **Small detail consumes the silhouettes:** prioritize drum, frame, hinge, and deck edges before chains, mesh, rivets, and scratches.
5. **Look and tier need separate material cues:** Industrial timber still needs visible timber; Scrapper patchwork should remain distinct from regular steel construction.

**2. RANKED REDRAW LIST — worst first**

1. **B1 #8; L1 #6:** Replace stacked/tapered modules with broad, flat, parallel-sided walking decks.
2. **M #7, #9:** Give deployed log crossings a continuous flattened tread aligned with travel.
3. **B1 #7; L1 #10:** Match raised-leaf lengths and hinge positions across all corresponding views.
4. **M #6:** Rebuild the debris silhouette as a squared, structurally readable lattice.
5. **B2 #14; L2 #13:** Remove diagonal presentation and roof dominance; expose the timber winch mechanism.
6. **B2 #15–16; L1 #4:** Reveal timber supports and reduce shed-like canopies.
7. **B2 #18–19:** Add recognizable drums, axles, cranks, and grounded bases.
8. **B1 #10, #12; B2 #13; L1 #1, #7:** Standardize the camera and expose more machinery top surfaces.
9. **M #2–3:** Flatten deck relief and move raised hardware outside the walking tread.
10. **B1 #3–5; L1 #9:** Strengthen leaf contours, width, hinges, and major material divisions.
11. **B2 #17; L1 #5:** Clarify gate operation and passage with simpler, better-proportioned framing.
12. **B1 #11; L1 #2–3:** Replace fine mesh and chain detail with readable graphic masses.
13. **B1 #9:** Establish its Scrapper assignment before producing a separate regular-steel variant.


## Sample images
GPT image edits (codex $imagegen), REFERENCE ONLY — nothing installed:
- `Transient/pile_2026-10-21/bridge_art_gpt/sample_tower_industrial.png` — Industrial tower rebuilt around a visible cable saddle and projecting base (GPT's #1 finding).
- `Transient/pile_2026-10-21/bridge_art_gpt/sample_drawbridge_planks_steel.png` — steel drawbridge deck as a flat, parallel-sided tread plate (walkability, drawbridge #1).
- `Transient/pile_2026-10-21/bridge_art_gpt/sample_raidplank_laid.png` — laid raid plank as lashed flat planks instead of logs (drawbridge #2).


## Ranked redraw list
Merged from both replies, worst first (GPT's ranking, Claude's merge):
1. All styled suspension **towers** (Scrapper/Industrial/Modern/Futuristic #12) — camera correction: visible saddle top, foreshortened front, projecting base; they read as cabinets.
2. **Drawbridge lowered decks / planks** (B1 #8, L1 #6) — broad flat parallel-sided walking deck, hardware off the tread.
3. **Raid plank laid / laid end** (M #7, #9) — continuous flattened tread along travel, not loose logs.
4. **Timber decks in Industrial/Modern/Futuristic** (#8) — show wood; today the look erases the timber tier.
5. **Styled anchors** (#1–3 on each look) — distinct heavy shoe / steel bracket / timber sleeper silhouettes, visible mounting.
6. **Raised-leaf views** (B1 #7, L1 #10, B1 #3–5) — face, edge and underside must share span, width and hinge positions.
7. **Futuristic decks** (#5, #7, #9–10) — matte walkable plates, sparse lights; luminous grids read as machinery.
8. **Pit-cover plank lattice** (M #6) — squared readable lattice, not debris.
9. **Timber winch** (B2 #14, L2 #13, B2 #15–16) — drop the diagonal shed view and the roof; expose drum and crank.
10. **Scrapper decks** (#5, #7) — simplify the patchwork; Steel visibly metallic.
11. **Grated decks, base + styled** (base #5, #8; styled #4, #6) — readable bearing bars, frame weight per tier.
12. **Steel vs Heavy girth** (styled #10, Modern #7), **railings** (base p2 #13, styled #11), **Modern wreck** (Modern p2 #13), **drawbridge gate** (B2 #17), fine mesh/chain detail (B1 #11, L1 #2–3).

