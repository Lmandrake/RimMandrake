# Map awareness build — progress log (FOUNDRY subagent, 2026-10-10)

Owner decisions (card 2026-10-10): full programme incl. origin recorder; unexpected visitor => record + remove, redo only on EVIDENCE of disruption (CLEAN / DISRUPTED / INDETERMINATE).

## Status
- [x] reading
- [x] tickets filed: VISITOR_DETECTORS_MEND_NAME_THE_STRANGER, THING_LOOKUP_BUILD_OWNER_IS_NOT_PAINTER, INCIDENT_JOURNAL_BUILD_CALLED_IS_NOT_FIRED, PAWN_ORIGIN_BUILD_SAY_ORIGIN_UNKNOWN, MAP_AWARENESS_PROVE_ON_A_QUIET_MAP (needs bridge)
- [x] Phase 1 (python harness) fadddb0dd
- [x] Phase 2 + 3 (companion C#) 1955bd4b6 -- built, NOT deployed
- owed: skills/ curation fold-in of skills/rimbridge/references/first_look.md (pointer only added)

## Log
- 10:59 read design+reviews+charter+naming+tps/health records; read modcheck detectors/watch/snapshot. Next: helpers/suite/runner + C# survey.
- 11:00 RimSage verified: DebugSettings.logRaidInfo/noAnimals exist; WildAnimalSpawnerTick (Map.cs:968); TryExecute early-return; Pawn.SpawnSetup:2616; LookTargets has NO ToString override (letter_list lookTargets useless). Tickets filed+claimed.
- 11:03 selftest_awareness.py written; RED (imports contract/scene_report missing)
- 11:08 phase1 code drafted (contract.py, scene_report.py, detectors/watch/helpers/suite/fake edits); iterating selftest
- 11:10 phase1 selftest_awareness 43/43 green; running full run_selftests
- 11:17 PHASE 1 PUBLISHED fadddb0dd (ledger 25e07e5d2) via land.sh; implemented recorded. Known red selftests not mine: hugethings_footprint, one_path_seam (scenes/l1_sweep, vanilla_beast_routes), items_glob_live (3 done items in items/). Starting phase 2.
- 11:19 phase2/3 design fixed; verified via RimSage: ContentFinder.Get last-mod-first, ModContentHolder.Get pure dict, PawnRenderTree.BodyGraphic forces setup (guard on Resolved), UniqueIDsManager.nextThingID private (reuse detection), CompSpawnerPawn.TrySpawnPawn, CompHatcher.Hatch, Hediff_Pregnant.DoBirthSpawn. Writing JawaBenchAwarenessCore.cs (pure) + harness.
- 11:22 AwarenessSelfTest 47/47 green; sabotage (eviction + non-idempotent pop) turns it red (recorded below)
- 11:26 C# hooks+tools written (JawaBenchAwareness.cs, JawaBenchAwarenessTools.cs), wired spawn_pawn/fire_incident/fire_quest/raid_shape_fire/incident_schedule/letter_list; building
- 11:28 companion built OK (build.py --gm, plan only, NOT deployed: game up). tool_metadata 389==389, tps_record PASS, core 47/47. Running full selftests before committing phase 2+3.
- 11:34 PHASE 2+3 PUBLISHED 1955bd4b6; implemented recorded for 3 C# items; full selftests 365/370 (3 red not mine). Committing ledger shard.
- 11:35 done; ledger e736b66ff.
