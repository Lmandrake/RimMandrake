# MATERIAL_MERGES_CLEANUP_1 — the approved material merges, and bronzium dropped

## spec
Spec: `design/RimMandrake/canon_materials_design_2026-10-09.md` §3.10 (what), §5 (save migration). Approved by
question card 2026-10-09; bronzium owner-typed: *"Too close to just bronze. Lame. Drop from game."* Evidence
for each pair: `design/RimMandrake/exotic_materials_census_2026-10-09.md` (+ `.csv`; re-run
`python3 src/RimMandrake/Utils/exotic_materials_census.py`). Parent: CANON_MATERIALS_BUILD_1.

1. **Chitin ladder:** Lantern Deeps `RM_*Chitin`, the Rot `RM_Rot*Chitin` and Bestiary `RSW_*Chitin` carry
   identical stats for weak/brittle, medium/tough, toxic, fragile, gray and crystal chitin. Fold to one set;
   repoint every `butcherProducts`/`leatherDef`/recipe/stuff reference. Pick the survivor per rung by what the
   most producers already name, and keep the tier rule (a franchise-free `RM_` survivor cannot be defined only
   in `RSW_`).
2. **The 7 `RUT_` duplicates:** `RUT_GlowerCrust`, `RUT_CathedralRoachShell`, `RUT_BrinePlate`,
   `RUT_SeepStone`, `RUT_SaltCameo`, `RUT_Hardwood`, `RUT_SweetlineWool` are removed and their producers point
   at the `RM_` twin. `RUT_Hardwood` is the C#-referenced one: move the code reference to
   `RM_GreatboleHardwood` first.
3. **Salt:** one common salt. `RM_SaltWhite`, `RM_SaltPink`, `RM_SaltViolet`, `RM_SaltAmber` stay as the
   premium curing set. `RM_RawSalt`, `RM_DeltaSalt`, `RM_SeepSalt`, `RM_KettlewickSalt`, `RM_Brine`,
   `RM_BrinePlate` become biome sources of the common salt (fold or produce it).
4. **Plasteel slag:** `ChunkSlagPlasteel_GT` (GravForge leavings) folds into `KotORChunk_plasteel`.
5. **Tibanna:** `KOTOR_Tibanna` and `RUT_TibannaGas` become one def. Beldon herds stay the only source
   (`TIBANNA_SOURCE_CUT_1`, ruled 2026-09-12); the pipe network consumes it.
6. **Bronzium dropped:** `KOTOR_AlloyBronzium`, `KOTOR_MineableBronzium`, `KotORChunk_bronzium` and its slag
   recipe, the junk-pile `mineableThing` that yields it
   (`Absorbed_KotorCore_KotORResource_JunkPile.xml`), and the bronzium light battle armor
   (`Absorbed_KotorWeapons_Apparel_KotORArmor_lgtbattlearmor.xml`). `absorption_content_fixes.py` names it too.

**Save migration (design §5).** For each removed defName, check the canonical start save and the exported ship
(`The_Utinni.xml`, which carries 4 bronzium-stuffed things) with the savegame tooling, grepping
`<def>NAME</def>`. Where present, map it to the survivor (back-compat defName mapping, or keep the old def
loadable and unproduced); re-stuff the ship's bronzium things in the layout export. Only what the world remake
carries (gravship, cargo, founders) must survive.

## criteria
- L1 L0: one chitin ladder; no two chitin defs share a stat vector; every former producer names a survivor
- L2 L0: none of the 7 `RUT_` duplicates is defined; their producers and C# references name the `RM_` def
- L3 L0: one common salt def plus the 4 premium Grey Sea salts; the other coarse salts produce or are the common salt
- L4 L0: `ChunkSlagPlasteel_GT` and one of the two tibanna defs no longer defined; beldons the only tibanna source
- L5 L0: no def, recipe, mineable, junk pile or apparel names bronzium
- L6 L0: the save check is written into this item, per removed defName: found / not found, and the mapping used
- L7 L1: one minimal-list load with the touched mods shows no cross-reference errors naming a removed def

## verify
Record with `rimflow verify MATERIAL_MERGES_CLEANUP_1 --criterion <ID> ...`. Selftests before commit.
