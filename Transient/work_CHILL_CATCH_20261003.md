# CHILL_FREE_TIER_CATCH_1 work notes (2026-10-03)
Item has no prose; spec = the_propane_lake_floor_sitting_agenda_2026-10-02.md Q2 (a) + housekeeping.
Choices:
- Seven new free-tier catch items RM_{Fessu,Krellik,Oddu,Oovu,Iliss,Tarnn,Zhiil}Catch added to TerminalBiomes/Defs/ThingDefs_Items/RM_TheChillCatch.xml (Grey precedent RM_*Catch; text/stats copied from RUT_ originals, ban-2 "not kyber" intact). RUT_ originals untouched (frozen twin keeps them).
- fishTypes in RM_TheChill.xml now all RM_*Catch, no MayRequire on the rows (same weights as before).
- Art: artpipe has none for any catch item (only pawn art, which exists in the free mod). All 9 catch items point texPath at the creature's own free-mod pawn art (Things/Pawn/Animal/RM_X/RM_X) instead of campaign-only houseplant sprites. No art job queued; real item icons stay owed.
- Rare table: free tier gets RM_RareChillCatches (Chemfuel x10-20 w4, RM_OdduCatch x4-6 w1) in new file ThingSetMakerDefs/RM_ChillRareCatch.xml; the duplicate-named TerminalBiomes/.../RUT_RarePropaneCatches.xml is deleted, so RUT_RarePropaneCatches now exists ONLY in the frozen campaign mod (no same-defName collision).
- Zhiil: catch added; it still has no floor body (CHILL_ZHIIL_FLOOR_BODY_1, Q3) - validation exempts it explicitly.
- the_propane_lakes.json fish block amended (list + corrected ruling).
- NOT touched (outside item/ frozen): RM_TheChillFloorLife.xml comments, RM_TheChillFlora.xml (RUT_AuroraGlass harvest), RUT_ files, RUT_PropaneCatch_Refining.xml recipe (campaign recipe takes RUT_ items only; RM_ catches are not refinable there - follow-up).
