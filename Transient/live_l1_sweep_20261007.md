# Live L1 sweep 2026-10-07 (FOUNDRY helper) — list acc_l1x (34 mods, no mandrake.rm.biomes)

Rows: ID/criterion | verdict | evidence

Method: jawa/get_defs (with fields) over python.exe; Player.log (389 lines, 34-mod load) grep by def name. No game is loaded (programState Entry), so map-scoped tools answer "No current map".
Verified-recorded with `rimflow verify --config acc_l1x-34 --level L1` for every PASS/FAIL/partial row below.

## PASS (recorded)
- FORGE_ENRICHMENT_QUICKTEST_1 A5 | PASS | 8 RM_ForgeVoice_* SoundDefs, RM_FloatstoneKeelBrace, RM_SpunstoneBonding, RM_DhuvvoxRunSlowing resolve; 0 Player.log lines name any of the four (KeelBraceLink is a patch, not a def).
- SCALD_WATER_AGITATION_FLECKS_1 A1 | PASS | 6/6 Scald terrains/wreck hull resolve; tags carry RM_WaterAgitationLight/Heavy; EnvironmentalHazards settings waterAgitationEnabled=True present.
- FLOWWORKS_VISUAL_PRINCIPLES_1 A1 | PASS | LiquidDef RM_Liquid_Tar surfaceLook (Solid, tint .24 grey) and FluidDef RM_Fluid_Oil surfaceLook (Flow, tint .24/.17/.09) read back matching the generator.
- UTINNI_WORLDMAP_FLIGHT_ICON_1 A1 | PASS | WorldObjectDef Gravship expandingIconTexture=World/WorldObjects/Expanding/RUT_Utinni, texture=World/WorldObjects/RUT_UtinniCaravan.
- LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1 A1 | PASS | RM_VisslerArm has CompProperties_Rottable and ingestible foodType=Meat, preferability RawTasty.
- NORTHSTAR_COMPANION_GAPS_1 A1 | PASS | all six tools (pawn_census, pawn_roles, incident_queue_peek, incident_queue_remove, damage_log, thing_lineage) in tools/list (511 tools). A2 (data) needs a map.
- CAULDRON_ENRICHMENT_VISUALS_1 A1 | PASS | RM_Filth_DewBeads, 5 accent plants with RM_DewfallGraphicExtension, 2 trees with RM_AssayFlecksExtension, 2 terrains takeFootprints=true. (Ledger text of the criterion is truncated at 200 chars; I measured every Cauldron def the item names.)
- FORGE_WHITE_PLUME_FRONTS_1 A2 | PASS | ThingDef/Filth_Water resolves; all six settings (plumeFrontsEnabled, plumeObscureEnabled, plumeSoakEnabled, plumeHeatEnabled, plumeAdaptedExempt, plumeStrength) present on RM_TheForgeSettings. BlindSmoke is a GasType enum, not a def.
- ABYSS_LIGHTFALL_BROOD_WRECK_1 A8 | PASS | the item's defs resolve; 0 Player.log lines naming Abyss/Summ/Brood/salvage defs.
- RUSTCATHEDRAL_BASE_FINISH_BUILD_1 A3 | PASS | 9/9 named defs resolve (IncidentDef, SoundDef, JobDef, ThoughtDef, TraitDef, HumPrimer, CoolantEel Thing+PawnKind, GenStepDef). SEPARATE FINDING: log has "Config error in RM_LineCycleRoll: PrioritizeNewest is not supported with sustainers".
- RUSTCATHEDRAL_HULL_BOLTS_BUILD_1 A1 | PASS | ThingDef+PawnKindDef RM_HullBolt, ThoughtDef RM_HullBoltsSeen, 7 RM_CathedralWitnessDef.
- FEVERWOOD_BROOD_RANSOM_1 A2 | PASS | RM_SekkulaathYoungCask, RUT_SporefallDisplayTank Thing and GenStep each found=1 (mandrake.rut.patches loaded). Finding: textures missing for RM_SekkulaathSpleenChemicals and RM_SekkulaathCream.
- ABYSS_SHEET_DONOR_PORT_1 A4 | PASS | 15 of 15 ported defNames resolve and every label matches the item's table.
- SCARLANDS_MECHANICS_2 A1 | PASS | RUT_ScarlandsMark, RUT_ScariaIncubation, RUT_ScariaOnsetArming, RUT_ScarlandsMarkLock, RUT_SentinelDefend, RUT_SentinelGraveWard and 4 sprung-danger defs: 10/10 found.
- FLOWWORKS_CONTAINER_MATERIALS_1 A1 | PASS | RM_BottleEmpty/BarrelEmpty/BucketEmpty carry stuffCategories; 9/9 RM_Make_* recipes resolve; 0 log lines.
- GREENTIDE_BASE_PORT_BUILD_1 A3 | PASS | BiomeDef/RM_Greentide modExtensions include RM_LivingBoleBiomeExtension and RM_RootCausewayBiomeExtension.
- CONTAGION_GPT_ENRICHMENT_1 A1 | PASS | JobDef RM_SampleDraftprint, ThingDef RM_Draftprint, QuestScriptDef RM_HelixDraftprintContract resolve; 0 log lines.

## FAIL / partial (recorded)
- RAKATAN_ARCHOTECH_MACHINES_1 A1 | FAIL | defs resolve but the log carries "Config error in RM_WM_AutomatedSmelter_Refurbished: is minifiable but not in any thing category" (twice); criterion says loading clean. Fix: add thingCategories to the Refurbished smelter.
- SALVAGE_WRECKAGE_EVERYWHERE_1 A1 | partial | 21 of 24 resolve; RUT_FoundrySalvageCache (UtinniPatches, loaded) and RSW_Fresh* wrecks (StructureInjectionsSW, not loaded) absent; log carries "Config error in RM_LongShadeWreckSpeeder: graphicData defines a shadowInfo but staticSunShadowHeight > 0". Check whether RUT_FoundrySalvageCache is deployed.

## UNMEASURED
- GREENTIDE_BASE_PORT_BUILD_1 A2 | UNMEASURED (wrong list) | 17/17 listed defs resolve, but criterion needs the free-tier list without mandrake.rut.*; this list has them.
- GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1 A1 | UNMEASURED (partial) | RM_GreatboleSeed (Plantable) found; greatboleServantsEnabled=False default; the water-gated growth component is not def-readable. Finding: texture missing Things/Plant/RM_Greatbole/RM_Greatbole_a.
- FORGE_DHOKKUR_WAYS_1 A1 | UNMEASURED (partial) | RM_Dhokkur has CompProperties_DhokkurWays; RM_DhokkurPolishedTrail found; 8 dhokkur settings present; RM_MapComponent_DhokkurPaths is a class, not readable via get_defs.
- WARSCAR_CHOTRIX_SIGNS_1 A1 | UNMEASURED (partial) | RM_Filth_SettledFilm (RM_TrackSurfaceExtension), JobDef RM_ChotrixDragKill, ThinkTreeDef RM_Chotrix found; the raceOverrides print texPath is not readable.
- WARSCAR_AEROSOL_SCREEN_1 A1 | UNMEASURED (partial) | RM_AerosolScreen has RM_CompProperties_AerosolScreen; pollution sense and toxic-buildup Harmony patches not readable. Note RUT_ShieldGenerator logs a minifiable config error.
- RUSTCATHEDRAL_BASE_FINISH_BUILD_1 A4 | UNMEASURED | BiomeDef.wildAnimals not serialisable by get_defs; the no-swbestiary half needs a second list.
- WARSCAR_SHEET_DONOR_PORT_1 A2 | UNMEASURED | only AA_Helixien (label "bileworm") resolves as ThingDef; SW_Juggernautbeetles, SW_Electricgryllotalpa, SW_Electrictick, RG_Rimclaw not found under those names (donor mod def names unverified).
- RUSTCATHEDRAL_GOODWILL_FLOOR_1 A1 | UNMEASURED | BiomeDef/RM_RustCathedral modExtensions read, but the BiomeAttitude standing fields are a map component, not readable here.
- GRAFFITI_NORTHSTAR_BRIDGE_TOOLS_1 A1 | UNMEASURED | 5/5 tools listed; jawa/running_mods answers (34); the others return "No game loaded/map"; A2 trial needs a game.
- DEBUG_ACTION_ENUM_CRASH_1 A2 | UNMEASURED | debug_action_yielders returns (matched 3) but the criterion requires a loaded-game state; no game loaded.
- FORCE_DISTURBANCE_REFLAVOR_1 A1 | UNMEASURED | IncidentDef/GameConditionDef PsychicDrone/Soothe labels and letters are vanilla: the StarWarsPatches mod is not on this list. Needs acc_ list with it.
- UTINNI/others done above. EMPIRE_ESCALATION_LADDER_1 A4 | UNMEASURED | RUT_EmpireRungDef type absent: EmpirePursuit mod not loaded. Needs list with mandrake.rut.empirepursuit.
- BAZAAR_PRICE_ENGINE_1 A1 | UNMEASURED | TheBazaar not on the list; needs acc_biomes list with it.
- CATHEDRAL_MECHANOID_PASS_VERBS_1 A1 | UNMEASURED | RUT_CathedralPass absent; CathedralPass mod not active.
- NINEFOLD_FAVOUR_ODDS_BUILD_1 A1 | UNMEASURED | RUT_Ritual_NineFaults absent; Rites mod not active.
- JAWA_SWIM_HOOD_KEEP_1 A1 | UNMEASURED | needs a swimming Jawa (map and spawn).
- MOVING_DUNES_BUILD_1 A3 | UNMEASURED | tint gate needs a rendered map; RM_Dunes_Sand/BuriedCache defs resolve.
- LIVE_ROUND2_FIXES_PROOF_1 A3 | UNMEASURED | needs the genstep run on a map; log has 0 MakeThing lines but RSW_GenStep_WhisperSarlaccSign (StructureInjectionsSW) is not loaded.
- STILLSAND_FIXES_LIVE_PROOF_1 A1, A2 | UNMEASURED | A1 needs the full-list load log; A2 spawn_pawn needs a game.
- MOD_OPTIONS_RETROFIT_1 A1 | UNMEASURED | needs the full list (75 settings surfaces readable on this list, none opened).
- LASSO_CHERRYPICKER_REMOVAL_1 A1, A2 | UNMEASURED | Cherry Picker / Melee Animation not on this list.
- KINETIC_BLAST_WEAPONS_1 EK.load | UNMEASURED | explosiveknockback tier not loaded.
- WEEPINGSTONES_CONDENSER_QUESTS_1 C6 | UNMEASURED | slots RM_FactionSlot_CondenserBuyer/Settlers/Hunters resolve (preferredFactions RUT_Jawa_HuttCartel+Empire, OutlanderCivil, Pirate) but the free-mod-alone half needs a second list.
- LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1 A3 | UNMEASURED | needs modcheck run (forbidden).

## Other log findings on this list (not criteria)
- RM_Thurrock fails to load: type RimMandrake.EnvironmentalHazards.HediffCompProperties_PeriodicAreaAttackSecondary not found; RM_ThurrockShatter hediff unresolved.
- RUT_Greentide references terrain CypreJungleMud (absent donor).
- "Could not execute post-long-event action: NullReferenceException" once at startup.
