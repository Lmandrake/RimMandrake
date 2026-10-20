# Gravship / founders remap vs dropped mods, 2026-10-20 (FOUNDRY helper, offline)

## 1. Layout defs outside the PAINT closure (MEASURED: layout vs newest dump filtered to the 83 PAINT mods)
Layout `design/Jawa/worldbuilding/ship_build/exported/Gravship_v2_ring_2026-09-12.xml`.
| def | n | donor (wave) | replaced by |
|---|---:|---|---|
| AG_RustedTile (floor) | 892 | sarg.alphagenes (W1) | guy762_FloorTiles_DivotedTile_rust (ours) |
| UCScaffoldTile (floor) | 229 | nephlite.orbitaltradecolumn (W2) | guy762_FloorTiles_XGrate_iron (ours) |
| OuterRim_AurebeshWord* (9 kinds) | 10 | neronix17.outerrim.furnitureanddecor (W2) | dropped (floor decals, no owned art) |
| AM_DamagedEmptyShelves | 1 | xmb.ancienturbanruins.mo (W2) | AncientShelf (Odyssey) |
| VFE_LargeAdvancedBattery | 1 | vanillaexpanded.vfepower (W2) | Battery (Core, 1x2 for 2x2) |
| RG_BoulderRockMediumSandstone / Marble | 1+1 | regrowth.botr.core (W1) | CollapsedRocks (Core) |
| Spaceports_ShuttleLandingPad | 1 | zal.spaceports (on 374 list, NOT in PAINT) | dropped |
| VHGE_GasGeyser | 1 | vanillaexpanded.helixiengas (on 374 list, NOT in PAINT) | dropped |
| 10 storage special-filter keys x14 hoppers (AM_*, MOAS_*, SurvivalTools_*, AllowDetThings, AllowNotDetThings, GR_Allow*) | 140 | W1/W2 or not in PAINT | key entries removed |
No Wave 3 def is named. Everything else (guy762 floors, VGE pipes, VFEFactory, Core/Odyssey) is inside the closure.
Floors are cosmetic: proposals until the owner agrees. Table `design/RimMandrake/world_remake_2026-10-19/ship_remap_S10b.json`; tool `src/RimMandrake/Utils/ship_remap.py`; result `...ship_build/exported/Gravship_v2_ring_2026-09-12.paint.xml` (3275 foundation, 2747 terrain, 1989 things, roundtrip clean); guard `src/RimMandrake/Utils/selftest_ship_paint_closure.py`.

## 2. Founders (6 fragments) - defs outside the closure
Backstories (4): VBE_ClonedHeir (Nekko childhood), VBE_Standardbearer (Tobb adulthood), VBE_GiftedBurnout (Yeku childhood) - all `vanillaexpanded.vanillabackstoriesexpanded` (Wave 2 HOLD); VQE_PowerArchitect02 (Nekko adulthood, `vanillaquestsexpanded.generator`). The other 8 are Core.
PORTED: `src/RimUtinni/PawnFlavor/Defs/Founders/Backstories_Founders.xml` = RUT_Jawa_FounderClonedHeir / FounderStandardbearer / FounderGiftedBurnout / FounderPowerArchitect (text, skills, traits verbatim; private spawn category RUT_Jawa_Founders; the donor's VQE_GenetronComponent possession NOT carried).
**NEXT (`FOUNDER_BACKSTORY_RUT_PORT`)**: deploy PawnFlavor, then change the 4 `<childhood>/<adulthood>` lines in founder_NekkoCaptainVok / founder_TobbKeeperNkik / founder_YekuFirst fragments to the RUT_ names (importer has no backstory remap).
NOT in the task but MEASURED, also dropped and named by the fragments: AG_FrailSkin/Stinky/SurvivalInstinct_High/TableResistance/UnderdevelopedTeeth (Alpha Genes W1, all 6), AS_*Passion x8 + VSE_Critical/Natural/Major/Minor (Alpha Skills / Vanilla Skills Expanded W1), face addons Brow*/Lid*/Mouth*/Skin* (facial-animation packs W2, cosmetic), AA_EyeBody (Alpha Animals). Genes/passions need an owner call (drop or port) before S11.
