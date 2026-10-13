# Pond hollow: three looks (POND_HOLLOW_DESIGN_THREE_LOOKS_ONE_BED)

Owner, 2026-10-13: "Show me the hollow options." Options from `infrastructure/state/items/POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE.md`.

- `pond_hollow_three_looks.png` (sha256 f3e3bec02c86…): one drained pond (rim depth 2, middle depth 4, about 20x14 cells, sand around it) drawn three ways: (a) dug-channel ground, (b) cracked lakebed, (c) mud stays.
- `render_mockup.py`: rebuilds the PNG. Offline, no game.

## Sources
- Vanilla textures (Core `resources.assets`, cached at `D:\Luke\dev\RimMandrake\observed\inventory\bundle_textures\ludeon.rimworld.core\`):
  Sand da8975a1f5c2, Gravel 7cceae13f5c2, Mud 94eafed313a3, Naked_Male_south 57b37b2c54bd, Male_Average_Normal_south 8ea346c40f13.
- (a) uses the `RM_Channel_Mid` and `RM_Channel_Superdeep` defs as they stand (`src/RimMandrake/FlowWorks/Defs/Canals/TerrainDefs/FlowWorks_Terrain.xml`): vanilla Gravel tinted (0.78,0.75,0.70) and (0.38,0.36,0.33).
- (b) **concept art, not installed**: `concept_lakebed_shallow.png` (e3a231b5cabb) and `concept_lakebed_deep.png` (d909ad8bd66f), generated with Codex image_gen on 2026-10-13. The mockup scales their brightness down to the vanilla textures' level so (b) does not look better than it would in game.
- Wall faces and sink are approximate, using the live numbers in `RM_WallFaceMath` (NorthByDrop, SideByDrop, SouthLiningByDrop, FootDarkness) and `pitSinkPerLevel` 0.3, which puts the deep colonist 1.2 cells lower. Faces between the rim and the middle use Mud as the ground they cut through. The scale is 32 px per cell, and one terrain texture repeat is taken as 8 cells. Both are approximate.

## Final tiles (LAKEBED_ART_BUILD_CRACKS_WITH_CHARACTER, 2026-10-13)
- `pond_hollow_lakebed_final.png`: the same sheet with look (b) drawn from the INSTALLED tiles at their own brightness (no rescale): `python3 render_mockup.py src/RimMandrake/FlowWorks/Textures/Terrain/FlowWorks`.
- Tiles: `Terrain/FlowWorks/RM_Lakebed_Shallow` (sha a198bacee5d8, mean lum 0.375, sat 0.27) and `Terrain/FlowWorks/RM_Lakebed_Deep` (sha 9c07841eb18e, lum 0.235, sat 0.34); vanilla for comparison: Sand 0.428, PackedDirt 0.349, Mud 0.232. 1024x1024 RGB, seamless, made by `src/RimMandrake/Utils/art/lakebed_textures.py` (procedural, no copied pixels), installed with `art.py install`. No TerrainDef uses them yet.
