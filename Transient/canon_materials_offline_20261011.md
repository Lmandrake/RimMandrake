# CANON_MATERIALS_BUILD_1 — offline (L0) proof pass, 2026-10-11

Script: `src/RimStarWars/Armoury/prove_canon_materials.py` (run it; `--selftest` plants defects). Raw output:
`Transient/canon_materials_prove_output_20261011.txt`. `validate_patch.py` (all 5 material defs + 9 patches, `--defs` Data+Mods+workshop,
`--live` newest DefDump capture, 550 mods): `Transient/canon_materials_validate_patch_20261011.txt`.

| criterion | result | basis |
|---|---|---|
| L1 | PASS (L0) | stats equal the donor's (read from git `96be3c36c^`, parent `KOTOR_Metal` merged, 12 statBases) except sharp 0.9; forge route shape; **defect found and fixed** below |
| L2 | PASS (L0) | `durasteel_convert_static` + `durasteel_outerrim_static` clean, planted-defect selftests red-then-green |
| L3 | PASS (L0) | `canon_materials_audit.py`: 0 recipes with a broad filter admitting both; 143 fixed Plasteel entries in 57 files untouched; dangling/roster clean |
| L4 | PASS (L0) | kotor_Plasteel recipes, `Make_PlasteelGF`, `Make_PlasteelComposite` cut; Odyssey allowlist; plasteel + durasteel slag smelt recipes exist |
| L5 | OWED | no salvage-by-composition patch; `RSW_Duranium` not defined |
| L6 | PARTIAL | defined: Doonium, Phrik, Transparisteel (+Zersium). Not defined: Duranium, Stygium, Coaxium. No trader/Bazaar stock, no stygium donor conversion |
| L7 | OWED | `kotor_IngotBeskar_recipe` (+10x) still defined; no removal; beskar smelting not made destructive; beskar mineables not zeroed |
| L8 | OWED | prose not written (lacquer "never a ship", mindstone as droid-mind crystal). Mindstone text says droids dislike it, so it needs a rewrite, not a one-liner |
| L9 | OWED | a negative claim over every recipe/building; no census exists; "layout grading" is an HTML design page |
| L10 | OWED | one minimal-list load |

## Defect found and fixed (L1)
`RSW_DurasteelConvert_OuterRim.xml` redirected `LKDurasteel_Ore`'s `mineableThing` to `RSW_Durasteel` so it never names a dead def, which
left the ore a LIVE producer. The 2026-10-11 DefDump capture shows `LKDurasteel_Ore` scattering at 0.5 (yield 40), listed in Core's
`PreciousLump` and Odyssey's `Asteroid` / `Asteroid_NoRuins` (40~45 each); `KOTOR_MineableDurasteel` scattered at 0.15. The design table (§3.2)
and L1 both say these are zeroed. New `Patches/RSW_DurasteelProducersZeroed.xml` zeroes all of it (FindMod on LK; the donor's own patch shape,
workshop 3565716659 `LKOre_PatchesAsteroidOR.xml`, was read to match its shorthand `mineableCounts`); the absorbed `KOTOR_MineableDurasteel`
source is zeroed too. Proven offline by replaying the patch (lxml) on a fixture of that shape (planted empty patch leaves 9 findings, shipped leaves 0).
Not zeroed on purpose: Ideology `WorkSite_Mining` loot row and trader/faction stock (trade/raid, not mining).

## Instruments, with their probes
- def universe 71,869 names (capture + src); probes: present `Steel`, `Plasteel`, `ResourcesRaw`, `ElectricSmelter`, `RSW_Durasteel`; absent two junk names.
  (First run used `Smelter`, which is no defName: the probe failed and refused to proceed, which is the point of a probe.)
- reference resolution: 33 refs in 13 material-owned files, 0 unresolved. Textures: 10 texPaths, 0 unresolved (all `Things/Item/Resource/Steel`, a
  texPath the game's own Steel uses; no custom art exists to magenta-check).
- Capture reader first looked for `graphic.texPath` and reported 6 false misses; the key is `graphicData.texPath`.

## validate_patch residue (not defects)
3 patches report dead-op ERRORs (`RSW_DurasteelConvert*`, `RSW_PlasteelRecipesCut`, `RSW_Transparisteel_GlassFold`): the targets (donor durasteel,
`OuterRim_Durasteel`, `Make_PlasteelComposite`, our old glass melts) are already gone in the on-disk/live set, ops are `success=Always`.
Names verified against git history, none is a typo. Whether they hit at runtime is L10.
