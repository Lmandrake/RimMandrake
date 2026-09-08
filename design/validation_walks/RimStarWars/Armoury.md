# Armoury — validation walk
subject: src/RimStarWars/Armoury  (packageId mandrake.rsw.armoury)
deps: brrainz.harmony, guy762.mm.kotorcore, oskarpotocki.vanillafactionsexpanded.core, adaptive.storage.framework, ebsg.framework, neronix17.outerrim.core (all hard per About.xml — absorbed content's Class= refs resolve to these frameworks with no MayRequire gate)
list: full     # About.xml's own note: without VEF/AdaptiveStorageFramework/EBSG present, several absorbed defs (SWPotF_RaceDef_ysalamir, guy762_SecretFloorPanel_BASE, guy762 implants) fail to load at all
status-hint: rebalances the whole mod list's weapon/armor damage ladder to setting physics via generated FindMod patches, plus a large absorbed KotOR content library and several small standalone C# comps (KoltoTank, MentalBreakBlocker, SecondaryMineableYield, MinePocket, JumppackForMeleeAI).

## must be true
- Generated ranged/armor/melee patches (Armoury_RangedDamage.xml, Armour_Ratings.xml, Armoury_MeleePower.xml, Armour_Penetration.xml) write their recorded values onto matched third-party defs when those source mods are active — result, not "applied" log text.
- RSW_Sonic_Cannon (native, not absorbed) loads as a working two-handed ranged weapon firing KotORSonicWave_heavy.
- The absorbed KotOR content trees (Defs/Absorbed_KotorCore, Absorbed_KotorWeapons, Absorbed_AdditionalMods) load with zero Config errors given the required frameworks are present.
- KoltoTankBase (thingClass KoltoTank.Building_KoltoTank) is a real, resolvable comp-backed building, not an inert defName.
- MentalBreakBlocker and SecondaryMineableYield's Harmony patches apply cleanly at startup.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rsw.armoury" and no XML error naming any Absorbed_KotorCore/Absorbed_KotorWeapons/Absorbed_AdditionalMods file   # load-time
2. [D] def read-back: ThingDef RSW_Sonic_Cannon exists; ParentName=KotORRangedMakeable_TwoHand, statBases/MarketValue=2600, verbs/li/defaultProjectile=KotORSonicWave_heavy
3. [D] def read-back: ThingDef KoltoTankBase exists; thingClass=KoltoTank.Building_KoltoTank
4. [D] patch result (requires Alpha Mechs active): ThingDef AM_Bullet_SniperTurret/projectile/damageAmountBase = 200 (Armoury_RangedDamage.xml's generated value)
5. [D] patch result (requires Alpha Genes active): ThingDef AG_Forsaken_Hood/statBases/ArmorRating_Sharp = 1.40 (Armour_Ratings.xml's generated value)
6. [L] Player.log contains "[MentalBreakBlocker] Harmony patch complete!"
7. [L] Player.log contains "[SecondaryMineableYield] Harmony patch complete!"
8. [B] jawa/get_def {defName: "RSW_Sonic_Cannon"} → returns a ThingDef with the same statBases as check 2, confirming it resolves at runtime not just on disk
9. [S] (human pass) sonic cannon sprite (reused kotorsonrifle_arkanian) and GenStep_ScatterLightsaberCrystals placement — visual only
