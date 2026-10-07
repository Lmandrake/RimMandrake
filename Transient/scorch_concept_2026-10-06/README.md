# Scorched pits — concept art and in-game redesign (2026-10-06)

Owner: "those look ridiculous" (black starburst grid + dark rim). Goal: GPT concept scorch → study → implement.

## Progress
- skeleton created
- captured unburned dry pits (screenshot mode, rootSize 5): `dry_stone_D3_crop.png`, `dry_dirt_D3_crop.png` (1024x800, ~78 px per cell); `shoot.py` is the capture helper
- GPT edits run: 3 styles x stone/dirt -> concept_*_v{1,2,3}.png
- concepts done: `concept_stone_v1..3.png`, `concept_dirt_v1..3.png`, overview `concepts_contact.png` (v1 soot gradient, v2 heavy char+embers+debris, v3 cooled ash+heat tint). GPT re-framed slightly (canvas 1419x1108 for 5 of 6), fine for study.

## What the concepts say sells "post-fire" (study)
1. **The floor turns GREY, not dark-brown.** Desaturated ash (mid grey with pale flecks) mottled with near-black char in soft irregular patches, char heaviest along the walls. Darkening the existing brown (round 1) reads as "a deeper pit", not burned.
2. **Grain, not flat colour.** Every concept's ash/char has fine granular texture; vertex-colour quads cannot carry that — a real texture is needed.
3. **The rim halo is smoke-shaped:** dark at the lip, feathering out ~1-1.5 cells in lumpy, cloud-like, uneven lobes (stronger on some sides). Never a ring of even width, never stamped shapes.
4. **The far wall face carries soot plumes** - dark vertical streaks hanging from the rim and climbing from the floor (v3 dirt is the clearest).
5. Optional accents: a warm ochre/rust heat tint near the walls (v3), a few pale ash flakes / char lumps (v2). No starbursts anywhere; embers only for a fresh burn.
- implemented round 3 (ash/soot textures via TerrainFadeRough, lobed halo, plumed faces; starbursts deleted); building
- build OK, selftests 106/106; deploying (game restart)

## Design (round 3, implemented)
- **Approach:** keep the SectionLayer (`SectionLayer_RMExcavationWalls`), replace vertex-colour char + starburst meshes with two real
  textures drawn with the game's own `TerrainFadeRough` shader: vertex alpha = coverage, and the shader's `RoughAlphaAdd`
  breaks every coverage edge up exactly the way soil fades into grass. World-space UVs (1 repeat / 3 cells): no per-cell stamps.
- **Textures** (made from the concepts via GPT edit, made seamless + desaturated offline): `src/RimMandrake/FlowWorks/Textures/Terrain/FlowWorks/RM_Scorch_Ash.png`
  (grey ash, char mottling, flakes) and `RM_Scorch_Soot.png` (charcoal soot). Raw GPT output in `src/RimMandrake/FlowWorks/art_source/scorch_2026-10-06/`.
- **Floor:** ash over ~80-100% (`AshCover`), soot at the walls (within ~0.45 cell) and in soft high-noise patches (`CharCover`),
  a faint rust heat tint in a band off the walls (`HeatTint`, vertex colour).
- **Faces:** soot texture on the north face heaviest at the foot, a band under the rim, vertical plumes from noise stretched up the
  face (`FaceSoot`); side faces get a soot gradient.
- **Halo:** undug cells within 2 cells of a burned cell get soot whose reach (0.45-1.4 cells) is set by domain-warped low-frequency
  noise (`HaloCover`) — lumpy lobes, darkest at the lip, different on each side.
- **Deleted:** blast-mark starbursts, black-patch vertex quads, ash flecks (and their math/selftests).
- Render queues: ash 2444, soot 2445, tint 2446 (over faces/light/joints, under the near-lip occluder).
- game relaunched; rebuilding review map
- round 3 live look 1: big step up; fixes: softer ash texture, sooted face to the rim, patchy heat tint, uneven lip. Redeploying
- r3d accepted (overview r3d_overview.png); building full keeper save

## Result
- In game: `r3d_stone_D3_crop.png`, `r3d_dirt_D3_crop.png`, all 8 scorched stations `r3d_overview.png`.
- Side by side (unburned | previous starbursts | GPT concept | now): `side_by_side.png`.
- Keeper save: `RM_fw_review_20261006f` (visuals + gallery).
- Selftests 106/106 (`Scorch_ash_floor_char_walls_lobed_halo` replaces the two starburst cases).
- Still short of the concepts: wall plumes are softer than concept dirt v3's drips, the heat tint is barely visible, and
  there is no debris (char lumps / flakes). Those are the next knobs (`FaceSoot`, `HeatTint`), and debris would need its own sprites.
