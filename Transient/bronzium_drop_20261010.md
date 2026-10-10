# BRONZIUM_DROP_1 report 2026-10-10

Owner decision (question card): bronzium-stuffed ship things re-stuffed to RSW_Durasteel.

- B2 save check: The_Utinni export `design/Jawa/worldbuilding/ship_build/exported/Gravship_v2_ring_2026-09-12.xml` lines 25608, 25643, 35536, 35553 `stuffDef` KOTOR_AlloyBronzium -> RSW_Durasteel (plain XML in repo, edited). Mapping: KOTOR_AlloyBronzium -> RSW_Durasteel via RM_DefAliasDef in `src/RimMandrake/EnvironmentalHazards/Defs/Misc/RM_MaterialMerges_Aliases.xml`. Other bronzium defNames (MineableBronzium, KotORChunk_bronzium, guy762_LgtBattleArmor_bronzium) are not in the start save or ship export; no alias needed.
- Armoury absorbed copies (DEPLOY_HOLD): deleted KOTOR_MineableBronzium, KOTOR_AlloyBronzium, KotORChunk_bronzium, KotORRecipe_BronziumFromSlag (Metals2), the junk-pile yield entry (JunkPile; remaining weights not renormalised, PROVISIONAL), and guy762_LgtBattleArmor_bronzium.
- Donor runtime: new `src/RimStarWars/Armoury/Patches/RSW_BronziumDrop.xml` removes the junk-pile li, recipe and the four defs (success=Always). PROVISIONAL substitute for Cherry Picker.
- OWED (not in repo): Cherry Picker config entries cutting KOTOR_MineableBronzium, KOTOR_AlloyBronzium, KotORChunk_bronzium, KotORRecipe_BronziumFromSlag, guy762_LgtBattleArmor_bronzium, if the patch route is not preferred.
- Left alone: weapon part `guy762_KotORpartCore_bronzium` (absorption_content_fixes.py) -- not on the item's list; owner call.
- B3 (L1 minimal-list load) not run: no game. Item not marked implemented.
