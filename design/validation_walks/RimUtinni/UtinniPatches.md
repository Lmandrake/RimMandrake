# UtinniPatches — validation walk
subject: src/RimUtinni/UtinniPatches  (packageId mandrake.rut.patches)
deps: mandrake.rsw.starwarsraces, Neronix17.OuterRim.Core, Neronix17.OuterRim.GalacticEmpire, Neronix17.OuterRim.RebelAlliance, Neronix17.OuterRim.GalacticDiversity, Neronix17.OuterRim.DroidDepot, Neronix17.Outland.Genetics, LazyFridayStudio.GenesExpandedEyes, guy762.StarWarsXenotypes, guy762.MM.KotORCore, guy762.KotORWeapons, sarg.alphabiomes, IronScruff.PrimordialGeysers, zylle.MoreVanillaBiomes, titans.fl, Dark.Signs, Nals.FacialAnimation, DanZinagri.FacialAnimationCompatabilityProject, ab.hoffa, 7f.alienworlds.tidallylocked, 7f.alienworlds, mandrake.rm.patches, mandrake.rsw.patches (all loadAfter; every patch is MayRequire/Conditional-guarded per About.xml)
list: full     # this mod's whole purpose is patching third-party defs across ~20 loadAfter mods; the minimal list cannot exercise it
status-hint: the Utinni campaign patch layer — factions, scenario, doctrine, and Ash'karr worldbuilding patches across the third-party mod stack; loads LAST of the three patch tiers.

## must be true
- Ash'karr's own content loads clean: 6 BiomeDefs (Jawa_BackgroundWater, RUT_GreySea, RUT_NightsideIce, RUT_PropaneLake, RUT_TheScald, RUT_TwilightSea), 8 FactionDefs (Jawa_AscendantHelix, Jawa_DeepwaterCompact, Jawa_FreeDroidEnclaves, Jawa_GeonosianFoundryHive, Jawa_HuttCartel, Jawa_Junkers, Jawa_IndigenousTribes, Jawa_WildsteamClan), and matching TerrainDefs (Jawa_SaltCrust, RUT_ScaldWater* x5).
- The planet name patch (JawaWorld_Name.xml) lands unconditionally (deliberately unguarded — see its own comment): RulePackDef NamerWorld's rulesStrings is replaced to `r_name->Ash'karr`, so a freshly generated world's name reads "Ash'karr".
- The ikee rename (Ikee_Rename.xml) is identity-only: ThingDef AA_Eyeling and PawnKindDef AA_Eyeling both carry label "ikee"; every stat field (ComfyTemperatureMax, foodType, trainability, wildness, baseBodySize) is untouched.
- Third-party faction reflavors are Conditional-guarded and produce a result even when their target mod is absent (silent no-op) or present (visible change): FactionDef Empire's label/leaderTitle/fixedLeaderKinds/royalFavorLabel (GalacticEmpire.xml) and FactionDef Mechanoid's label/description/factionIconPath (ForgottenArsenal.xml) only change when Neronix17.OuterRim.GalacticEmpire / the Forgotten Arsenal target mod is active.
- PawnKindDefs for the colonist roster (Jawa_Colonist, Jawa_Tribal_Scavenger, Jawa_Tribal_Slinger, Jawa_Tribal_Elder) and the faction roster (Jawa_Empire_Grunt, Jawa_Hutt_Grunt, etc.) exist and are assignable.
- ScenarioDef Jawa_UtinniStart and QuestScriptDef Jawa_TheClaim exist (the campaign's start scenario and its opening quest).
- LandmarkDef RUT_ComplexStructures, ThingDef Jawa_ClaimRumour, and the two RulePackDef namers (Jawa_NamerFactionBlackstar, Jawa_NamerFactionPirateWaster) load without error.

## the walk
1. [L] Player.log after load (full mod list) contains no "Config error in mandrake.rut.patches" and no XML error naming any file under Patches/ or Defs/
2. [D] def read-back: BiomeDef RUT_TheScald exists; BiomeDef RUT_GreySea exists; BiomeDef RUT_NightsideIce exists
3. [D] def read-back: FactionDef Jawa_AscendantHelix exists; FactionDef Jawa_HuttCartel exists; FactionDef Jawa_IndigenousTribes exists
4. [D] def read-back: TerrainDef Jawa_SaltCrust exists; TerrainDef RUT_ScaldWaterDeep exists
5. [D] def read-back: RulePackDef NamerWorld rulesStrings contains "r_name->Ash'karr" (the U+0027 apostrophe, not U+2019)
6. [B] jawa/world_info_get on the frozen Ash'karr worldfile (never a freshly generated world — worldgen is out of scope for this project) → world name = "Ash'karr" (confirms the patch's real effect landed on the shipped world, not just the def text)
7. [D] def read-back: ThingDef AA_Eyeling label = "ikee"; PawnKindDef AA_Eyeling label = "ikee"; ThingDef AA_Eyeling ComfyTemperatureMax unchanged from the pre-patch base value (identity-only, stats untouched)
8. [D] def read-back (with Neronix17.OuterRim.GalacticEmpire active): FactionDef Empire label changed from base "Empire"; leaderTitle, fixedLeaderKinds, royalFavorLabel all changed from base
9. [D] def read-back (with the Forgotten Arsenal target mod active): FactionDef Mechanoid label/description/factionIconPath changed from base
10. [B] jawa/list_factions → Jawa_AscendantHelix, Jawa_HuttCartel, Jawa_IndigenousTribes, Jawa_WildsteamClan, Jawa_Junkers, Jawa_DeepwaterCompact, Jawa_FreeDroidEnclaves, Jawa_GeonosianFoundryHive all present among instantiated factions
11. [D] def read-back: PawnKindDef Jawa_Colonist exists; Jawa_Tribal_Elder exists; Jawa_Empire_Grunt exists
12. [D] def read-back: ScenarioDef Jawa_UtinniStart exists; QuestScriptDef Jawa_TheClaim exists; ThingDef Jawa_ClaimRumour exists
13. [D] def read-back: LandmarkDef RUT_ComplexStructures exists; RulePackDef Jawa_NamerFactionBlackstar exists
14. [S] (human pass) load the frozen Ash'karr savegame under the full mod list and confirm it reads as intended visually (biome placement, faction territory colours) — never a fresh worldgen run, which is out of scope for this project; outside what a def read-back proves
