# Sitting 2 (acc_20261009b) log

- start: skeleton created 23:51
- 23:52 tier acc_20261009b committed (wasterun not installed until deploy)
- 23:54 bridge taken, game pid 22100 killed, deploy plan running -> Transient/belt_sitting2_deploy_plan.txt
- 23:55 companion deployed via build.py --gm --apply (no refusal)
- 23:57 per-mod --apply running (-> Transient/belt_sitting2_deploy_apply.txt); queue saved Transient/belt_sitting2_acceptance_queue.txt
- 00:01 deploy done (23 mods + composed biomes 68 files pruned); tier acc_20261009b applied (57 active); launching
- 00:04 game up, bridge token; smoke starting
- 00:04 SMOKE: 29 census lines all missing 0, 0 'Harmony patch failed'. Exceptions: 489x 'post-long-event' NRE (RaceProperties.AnyPawnKind in ThingDef.ResolveIcon; sitting1 had 2) + 13 RSW_Jawa_Spawn_* ConfigErrors NRE (donor races absent?) + 3 DoorsExpanded type missing (Absorbed_Lumi_BlastDoors). Investigating after quicktest start
- 00:08 FINDING: tier b load -> quicktest map gen died (raceless PawnKind NRE in BiomeDef.CommonalityOfAnimal; 489 ResolveIcon NREs; rsw.patches needs StarWarsRaces' RimMandrake_ColonyPawnKind parent, absent). Retry: drop rsw.patches (FORCE_DISTURBANCE A1 stays UNMEASURED), add ashkarrflora+alphaanimals+mlie.* donors
- 00:10 RELOAD OK (tier b w/o rsw.patches, +donors, 58 mods): SMOKE 32 census lines all missing 0, 0 'Harmony patch failed', post-long-event NRE 489->1. quicktest map up (TemperateForest). census -> Transient/belt_sitting2_census.txt. Starting L1 reads
- 00:12 L1 recorded PASS: BAZAAR_PRICE_ENGINE_1.A1, CATHEDRAL_MECHANOID_PASS_VERBS_1.A1, EMPIRE_ESCALATION_LADDER_1.A4, NINEFOLD_FAVOUR_ODDS_BUILD_1.A1, RUSTCATHEDRAL_BASE_FINISH_BUILD_1.A4, WARCASKET_DEPENDENCY_DOWNLOAD_URL_1.A2, ELDER_TREASURE_PROOF_HOOK_1.A1, ELDER_TREASURE_TAG_TABLE_1.A1, PATCHAPPLIER_FORCED_MISS_PROBE_1.A1, HARMONY_PATCH_RESILIENCE_1.A2, SETTINGS_OPEN_SMOKE_HOOK_1.A1+A2, MOVING_DUNES_BUILD_1.A3 (gate: MatBases.Sand shader Custom/Snow has no _Color; MaterialColor tint dead). FAIL: DUNES_TINT_GATE_PROOF_1.A1 (hasColorProp=False, reproduced twice; the shipped tintMode MaterialColor paints nothing). SALVAGE_WRECKAGE A1 UNMEASURED (RUT_FoundrySalvageCache held)
