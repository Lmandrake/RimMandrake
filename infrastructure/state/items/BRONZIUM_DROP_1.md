## spec
Split out of MATERIAL_MERGES_CLEANUP_1 on 2026-10-09 (FOUNDRY). Spec: `design/RimMandrake/canon_materials_design_2026-10-09.md`
§3.10; bronzium owner-typed: *"Too close to just bronze. Lame. Drop from game."*

**What goes:** `KOTOR_AlloyBronzium`, `KOTOR_MineableBronzium`, `KotORChunk_bronzium` and its slag
   recipe, the junk-pile `mineableThing` that yields it
   (`Absorbed_KotorCore_KotORResource_JunkPile.xml`), and the bronzium light battle armor
   (`Absorbed_KotorWeapons_Apparel_KotORArmor_lgtbattlearmor.xml`). `absorption_content_fixes.py` names it too.

Bronzium exists at runtime only from the donor `guy762.mm.kotorcore` (Armoury's absorbed copies in
`src/RimStarWars/Armoury/Defs/Absorbed_KotorCore/` are DEPLOY_HOLD'd), so the cut is Cherry Picker entries for the
donor defs plus a scoped patch for the junk pile's `mineableThing`; the absorbed copies are edited to match.
Save migration (design §5): the exported ship (`The_Utinni.xml`) carries 4 bronzium-stuffed things; re-stuff them in
the layout export and alias the old stuff through RM_DefAliasDef.

## criteria
- B1 L0: no def, recipe, mineable, junk pile or apparel names bronzium in the shipped load
- B2 L0: the save check for each bronzium defName is written here, with the mapping used
- B3 L1: one minimal-list load shows no cross-reference errors naming a bronzium def

## verify

The supervisor's live round runs this line on a game-up sitting (LIVE_PROOFS_POPULATE_CLEAN_BUILDS_FIRST). The donor junk
pile and RSW_Durasteel must resolve first, so the load had both the donor and Armoury: a log silent about bronzium in a
load without them is not a pass. "ronzium" matches Bronzium and bronzium in any defName, recipe or patch file.
live-proof B3: python3 src/RimMandrake/Utils/live_def_check.py --has ThingDef/KOTOR_MineableJunk --has ThingDef/RSW_Durasteel && python3 src/RimMandrake/Utils/live_log_check.py --absent ronzium
