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
6. **Bronzium** moved to its own item, `BRONZIUM_DROP_1` (2026-10-09): it lives only in the donor
   `guy762.mm.kotorcore` (Armoury's absorbed copy is held), so dropping it is Cherry Picker / patch work plus the
   ship re-stuff, not a fold.

**Save migration (design §5).** For each removed defName, check the canonical start save and the exported ship
(`The_Utinni.xml`) with the savegame tooling, grepping
`<def>NAME</def>`. Where present, map it to the survivor (back-compat defName mapping, or keep the old def
loadable and unproduced); re-stuff the ship's bronzium things in the layout export. Only what the world remake
carries (gravship, cargo, founders) must survive.

## criteria
- L1 L0: one chitin ladder; no two chitin defs share a stat vector; every former producer names a survivor
- L2 L0: none of the 7 `RUT_` duplicates is defined; their producers and C# references name the `RM_` def
- L3 L0: one common salt def plus the 4 premium Grey Sea salts; the other coarse salts produce or are the common salt
- L4 L0: `ChunkSlagPlasteel_GT` and one of the two tibanna defs no longer defined; beldons the only tibanna source
- L6 L0: the save check is written into this item, per removed defName: found / not found, and the mapping used
- L7 L1: one minimal-list load with the touched mods shows no cross-reference errors naming a removed def

## build (2026-10-09, FOUNDRY)
Survivors: chitin RM_WeakChitin, RM_MediumChitin, RM_GrayChitin, RM_CrystalChitin (Lantern Deeps; its base also
carries RM_ChitinStuff), RM_FragileChitin, RM_ToxiChitin (Rot). RUT twins -> their RM_ def (RUT_Hardwood ->
RM_GreatboleHardwood; the greatbole campaign binding that swapped it in is gone; C# only named it in comments).
Common salt = RM_RawSalt ("salt"); delta, seep and kettlewick salt fold into it; RM_BoilBrineToSalt (Stillsand)
and RM_CrackBrinePlate (Wasteland) make brine and brine plates sources. ChunkSlagPlasteel_GT -> KotORChunk_plasteel.
RUT_TibannaGas -> KOTOR_Tibanna (beldon tap; TibannaEmbargo_CutDeepRoute.xml strips the deep-drill route).

## save check (L6)
Literal scan of CANONICAL_ASHKARR_START_2026-09-12.rws and Config/GravshipExport/The_Utinni.xml, 2026-10-09.
Every removed name is mapped in `src/RimMandrake/EnvironmentalHazards/Defs/Misc/RM_MaterialMerges_Aliases.xml`
(RM_DefAliasDef, ThingDef-scoped).

| removed | start save | ship | maps to |
|---|---|---|---|
| RM_RotWeakChitin / RM_RotMediumChitin | not found | not found | RM_WeakChitin / RM_MediumChitin |
| RSW_Weak/Fragile/Medium/Toxi/Gray/CrystalChitin | FOUND (all six) | not found | RM_ same rung |
| RUT_GlowerCrust | not found | not found | RM_GlowerCrust |
| RUT_CathedralRoachShell | FOUND | not found | RM_CathedralRoachShell |
| RUT_BrinePlate | FOUND | not found | RM_BrinePlate |
| RUT_SeepStone | FOUND | not found | RM_SeepStone |
| RUT_SaltCameo | not found | not found | RM_SaltCameo |
| RUT_Hardwood | FOUND | not found | RM_GreatboleHardwood |
| RUT_SweetlineWool | not found | not found | RM_SweetlineWool |
| RM_DeltaSalt / RM_SeepSalt / RM_KettlewickSalt | not found | not found | RM_RawSalt |
| ChunkSlagPlasteel_GT | not found | not found | KotORChunk_plasteel |
| RUT_TibannaGas | not found | not found | KOTOR_Tibanna |

## verify
Record with `rimflow verify MATERIAL_MERGES_CLEANUP_1 --criterion <ID> ...`. Selftests before commit.
