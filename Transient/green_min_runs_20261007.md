# GREEN-MIN live runs 2026-10-07 (FOUNDRY)

Setup: tier `acc_green_min` (36 mods, added to modset_builder.py, uncommitted), game killed and relaunched via Steam 19:00-19:05Z, then `modcheck run <Mod>` per mod with MODCHECK_SKIP_DEPLOY=1 RIMFLOW_SEAT=FOUNDRY. Driver log: `Transient/green_min_runs_20261007.log`. All mods ran on ONE shared bland map in sequence, so later runs saw earlier runs' leftovers (the cause of three site FAILs below). A first pass of Abyss..TitanicCreatures aborted in `emit_verify` (seat env missing under python.exe) after writing results; those earlier JSONs are noted where they matter.

Classes: harness | site | mod | unmeasured.

## Abyss
- result: `/home/mandrake/rm/foundry/Transient/modcheck/Abyss_20261007T190743Z.json`
- PASS 17 / FAIL 0 / UNMEASURED 0, all_green=True; earlier pass: Abyss_20261007T190620Z.json
- classification:
  - (first run 190620Z only) cryptid/clear_pocket_around_nothing FAIL -> site: dirty pocket on the shared map; the identical code PASSED on the rerun (190743Z, 17/17). Final run has no FAIL.

## Scarlands
- result: `/home/mandrake/rm/foundry/Transient/modcheck/Scarlands_20261007T190810Z.json`
- PASS 16 / FAIL 2 / UNMEASURED 25, all_green=False; earlier pass: Scarlands_20261007T190646Z.json
- classification:
  - warscar_mark/mark_accrues_and_pays -> site: Human833 already carried a heavy mark (0.898) because my aborted first batch pass (190646Z) had accrued on the same colonist; the clean first run PASSED all 4 mark components. Cause is cross-run contamination by this session, not the mod.
  - chatrak_snap/snap_stage_0_2 -> site: 'armed 2' instead of 'armed 1' because the first pass's chatraks were still on the map; the clean first run PASSED all 7 snap components. Also 9 PASS->UNMEASURED vs the clean run (tracking line etc.) for the same reason.
  - Authoritative result for Scarlands: the clean first pass Transient/modcheck/Scarlands_20261007T190646Z.json = 26 PASS / 17 UNMEASURED / 0 FAIL (not recorded in modcheck_status; the rerun is).

## ShipVermin
- result: `/home/mandrake/rm/foundry/Transient/modcheck/ShipVermin_20261007T190817Z.json`
- PASS 17 / FAIL 0 / UNMEASURED 11, all_green=False; earlier pass: ShipVermin_20261007T190657Z.json
- classification:
  - (first run 190657Z) alert/absent_with_no_mynock_present_with_mynocks FAIL -> site: leftover alert from a mynock elsewhere on the shared map; the final run reads it UNMEASURED ('no clean baseline'). Final run: 0 FAIL; 11 UNMEASURED are the unreachable debug action 'Force nest spawn attempt (click wreck)' (harness: label never proven live) and 5 not_driven stubs.

## TitanicCreatures
- result: `/home/mandrake/rm/foundry/Transient/modcheck/TitanicCreatures_20261007T190833Z.json`
- PASS 18 / FAIL 3 / UNMEASURED 8, all_green=False; earlier pass: TitanicCreatures_20261007T190704Z.json
- classification:
  - defs_resolve/every_shipped_def_resolves -> MOD: Player.log 'Type RM_CrushRuleDef is not a Def type or could not be found' and same for RM_TitanicTierDef. The classes are in namespace RimMandrake.TitanicCreatures but the XML roots (Defs/CrushRuleDefs/RM_CrushRules.xml, Defs/TitanicTierDefs/RM_TitanicTierDef.xml) use the bare name, so all 5 defs never load; the mod logs 'No RM_TitanicTierDef found ... Falling back to hardcoded defaults'.
  - crush_rules/rules_read_back_as_the_xml_says -> MOD: same root cause ('No def TYPE named RM_CrushRuleDef').
  - wake/t1_beast_trails_rubble_and_tramples_plants -> MOD (consequence, not separately proven): crush table is empty so nothing matches and nothing is ever crushed; Elephant crushed 0 of 6 plants while trailing 4 filth.

## Warcasket
- result: `/home/mandrake/rm/foundry/Transient/modcheck/Warcasket_20261007T191536Z.json`
- PASS 36 / FAIL 2 / UNMEASURED 5, all_green=False
- classification:
  - defs_and_load/no_warcasket_log_errors -> MOD (About.xml metadata): game warning 'Warcasket dependency (mandrake.rm.biomes) needs to have <downloadUrl> and/or <steamWorkshopUrl> specified' from the modDependencies entry in About.xml. Cosmetic; the check also counts it.
  - core_and_cask_bay/loose_core_doses_nearby -> SITE: KeyError 'Human86770' - the probe pawn is missing from list_pawns; the shared map was full of mauled/bled-out pawns (chatrak manhunters from the Scarlands snap proof earlier in the same batch). The 5 downstream components went UNMEASURED.

## GizkaStowaway
- result: `/home/mandrake/rm/foundry/Transient/modcheck/GizkaStowaway_20261007T191543Z.json`
- PASS 27 / FAIL 0 / UNMEASURED 10, all_green=False
- classification:
  - No FAIL. 10 UNMEASURED left as the script reports them.

## OasisMaker
- result: `/home/mandrake/rm/foundry/Transient/modcheck/OasisMaker_20261007T191720Z.json`
- PASS 20 / FAIL 1 / UNMEASURED 4, all_green=False
- classification:
  - site_growth/fast_settings_finish_an_oasis -> HARNESS: wait budget. The comp advances one ring per CompTickRare (250 ticks); inspect after 2500 ticks reads 'Working: ring 7 of 8.' - progressing correctly, just not finished. Not a mod defect.

## RiverColors
- result: `/home/mandrake/rm/foundry/Transient/modcheck/RiverColors_20261007T191723Z.json`
- PASS 2 / FAIL 0 / UNMEASURED 0, all_green=True
- classification:
  - No FAIL, GREEN.

## ScarlandsLadder
- result: `/home/mandrake/rm/foundry/Transient/modcheck/ScarlandsLadder_20261007T191726Z.json`
- PASS 5 / FAIL 0 / UNMEASURED 0, all_green=True
- classification:
  - No FAIL, GREEN.

## ShokkweaveEconomy
- result: `/home/mandrake/rm/foundry/Transient/modcheck/ShokkweaveEconomy_20261007T191730Z.json`
- PASS 4 / FAIL 2 / UNMEASURED 0, all_green=False
- classification:
  - silk_scatter/silk_scatter_places_knots and nest_scatter/nest_scatter_places_nests -> SITE: GenStep_ScatterWebworkSilk returns early unless map.Biome.defName == 'RUT_Webwork' (Source/GenStep_ScatterWebworkSilk.cs:32); run_genstep returned success and placed 0 (0->0) on the bland map, and the script never retiles to Webwork. Map biome was not read back, so this is inferred from code + zero placement.

## LeaningScrub
- result: `/home/mandrake/rm/foundry/Transient/modcheck/LeaningScrub_20261007T193012Z.json`
- PASS 45 / FAIL 3 / UNMEASURED 20, all_green=False
- classification:
  - patches/dead_venomvine_fuels_fire -> UNMEASURED (harness-shaped): inspect_string(Campfire101863) returned NOTHING MATCHED after wait_ticks(10000) - the campfire no longer existed, cause not established; no evidence about the mod's fuel filter.
  - dripping/dripping_survives_harvest -> HARNESS: the regex 'growth[^0-9]*(\d+)%' matched the line 'Growth rate: 100%'. The actual inspect was ['30% grown','Growth rate: 100%'], i.e. the mod behaved correctly (dropped to 30%).
  - sweetline/scratch_drops_coat -> SITE: 'REFUSED: no sweetline tree on this map' (list_things empty at tick 407186 after the chain's time jumps); the fixture tree was gone, so the mechanism was not exercised.

## GelatinousSlime
- result: `/home/mandrake/rm/foundry/Transient/modcheck/GelatinousSlime_20261007T193712Z.json`
- PASS 65 / FAIL 1 / UNMEASURED 1, all_green=False
- classification:
  - antidote/antidote_clears_film_and_poisons -> UNMEASURED: awake patient still at exactly 0.55 after UseItem; the order was accepted but the chain never checks the use completed or the item was consumed, and the loop raises on the first failing patient so the coma patient was never evaluated. Mod defect not excluded; needs a re-probe that reads job completion and the antidote stack.

## GravshipLanding
- result: `/home/mandrake/rm/foundry/Transient/modcheck/GravshipLanding_20261007T193717Z.json`
- PASS 10 / FAIL 0 / UNMEASURED 0, all_green=True
- classification:
  - No FAIL, GREEN.

## Stillsand
- result: `/home/mandrake/rm/foundry/Transient/modcheck/Stillsand_20261007T193741Z.json`
- PASS 43 / FAIL 1 / UNMEASURED 62, all_green=False
- classification:
  - site/site_stillsand_map -> HARNESS: jawa/world_commit failed at WorldDrawLayer_Rivers.RegenerateNow ('InvalidOperationException: Collection was modified') so the Stillsand map was never built; 62 of 106 components are UNMEASURED as a result. Engine/bridge redraw failure, not the mod.

## Pyrinth
- result: `/home/mandrake/rm/foundry/Transient/modcheck/Pyrinth_20261007T193746Z.json`
- PASS 11 / FAIL 1 / UNMEASURED 6, all_green=False
- classification:
  - ore_and_donor_identity/mineable_ore_yield_matches_xml -> HARNESS: get_defs asked for 'mineableThing' on ThingDef, which is not a ThingDef field (it is building.mineableThing); the tool answered '(no such field)' and the script compared that string to 'DV_Pyrinth'.

