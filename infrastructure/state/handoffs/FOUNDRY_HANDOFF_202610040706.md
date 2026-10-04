# FOUNDRY_HANDOFF_202610040706 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610040454`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The first live runs of the observatory found its OWN hooks broken, and the suites' instruments lying: the modal sweep scored the tool's normal "No open window" answer as a failed sweep (every verdict "unknown"), run identity read git as "unknown" under python.exe (so no deploy was ever "proven fresh"; fixed via wsl.exe, now records the sha), and `jawa/get_defs` cannot read a GenStep class or any System.Type field (it answers "(no such field)"), which FAILED loaded, correct defs in Armoury and LanternDeeps. The pattern that fixes the last one: assert the class from the shipped XML and prove the def loaded live. Also: `jawa/static_call` now returns six stack frames for a throwing proof (needs the companion deployed, done on load 14), and that is what exposed a REAL content bug that hid for two loads behind a bare NullReferenceException: `RM_FactionDef_KurrethSwarm` (and `RSW_Shokk_FeraliskBrood`) had no fixedName/factionNameMaker, so NameGenerator NREs when the lure lazily creates the faction and no kurreth raid could ever arrive in the real game. Fixed in the defs; NOT yet proven live (needs the next relaunch).

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
Nothing needs a ruling. FYI: Armoury's JumppackForMeleeAI FAILs (3) are a dead third-party mod (static-ctor HarmonyException, Invalid IL on JobGiver_AIFightEnemy.TryGiveJob patch 4) already triaged in FULL_LOAD_RESIDUE_TRIAGE_1; the Armoury jumppack feature cannot work on this list and the suite now says so honestly instead of cascading 16 other components to UNMEASURED.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- FEVERWOOD_KURRETH_FACTION_FIXEDNAME — defs fixed (fixedName on both hidden raider factions, static bar in FeverWood source_guards), not yet live; NEXT: after the next restart run `situational_rerun --bland-world --retile --mods FeverWood` and confirm ant_theft/kurreth_column no longer read "ProofRaid did not stage the column" (the lure_raid arms were UNMEASURED by surprises, so the faction path is still unproven end to end).
- BLAND_MAP_CUT_BY_NOBODY — NOT FeverWood-specific (it also hit Aftermath's colonist Human674 at tick ~345k): a repeating 1.0 "Cut" (hediffs Cut+Crack, every 120 ticks, no instigator) hit the 3 bland colonists across ~11 chains from the first tentacle chain and killed one (Hans, t4465); only the lash limb deals Cut in this mod and `list_things` found no Sekkulaath limb afterwards, so the source is unresolved; NEXT: run FeverWood once with `jawa/list_things` for RM_Sekkulaath_* + hediff read after each tentacle chain, or declare the lash's expected damage so it stops tainting later chains.
- DEEP_LAYER_BELT_HARNESS_1 — LanternDeeps creep/aurora/hydrocarbon/hush proofs need a real Lantern Deep pocket map (RM_LanternDeepGenerator.customMapComponents are attached only there); `src/RimMandrake/Utils/modcheck/live_queue/deep_proto.py` is the UNPROVEN route (spawn the 5x5 MapPortal RM_LanternDeepMineshaft, order EnterPortal, walk set_current_map); NEXT: run deep_proto.py with the game up on a bland map, record what map ids/biomes appear, then turn it into bland_world.enter_deep() with map_drop on restore.
- BLUEDESERT_FLORA_PLANT_REFUSAL_1 — not touched this round; NEXT: with --retile at -5 C read `jawa/set_plants` message for the 8 refused plants (OutdoorTemp vs tile temperature).
- RERUNS OWED — WeepingStones recorded RED on a clean load 14 (4 FAILs: feed/harvest/cull/stock jobs "never ran": decide if the job driver or the order is at fault before touching content); TheForge, Cauldron, BrainWorms, Bacta, BlueDesert, Contagion, TerminalBiomes, FeverWood not rerun on load 14; Aftermath needs one more run (raid fires at 400 points now; its letter opens a forcePause Dialog_NodeTree that the script now closes); NEXT: relaunch (builders' DLLs and the faction fix need a restart), then `situational_rerun.py --bland-world --retile --mods Aftermath,FeverWood,TheForge,Cauldron,BrainWorms,Bacta,BlueDesert`.
- LEANINGSCRUB_LOAD14 — clean rerun 32P/22U/2F: `flora_spawns` RM_Grellspine did not stand after set_plants; `lash_toggle_off_quiet` the colonist beside the stand gained a hediff with twitcherLashEnabled OFF (a real toggle leak, or a hediff from the retiled bland map; not read); NEXT: read Transient/modcheck/live_queue/situational_rerun/LeaningScrub_summary.json, then query the colonist's hediff def before touching the twitcher lash comp.
- KEELHOIST hutt_slave_pit lowered_prisoner_sold_for_silver — NOTSOLD (held 5->6, silver 0, faction none); NEXT: read RM_PitBuyer.cs sale path (sold requires p.Faction == pit.Faction) against a bland map where the pit has no faction.
- ANIMAL_TOLERANCES_DONOR_NOMATCH_1 — filed; the generator emits bare nomatch Adds on absent donor creatures (4 failed ops every load); NEXT: wrap donor rows in PatchOperationFindMod in design/Jawa/fauna/animal_tolerances.py and regenerate.
- GAME_STATE — game UP on load 14 with the JawaBench companion and plain+biomes deployed 23:12; bridge held by FOUNDRY; no runner live when this was written; NEXT: `./game` to measure, `rimflow bridge who`, then relaunch before the reruns above (the foreground is the owner's Chrome: RunInBackground is True, do not touch his windows).

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
The modal sweep and git identity hooks were silently broken (lessons filed). A suite that ran with a forcePause Dialog_NodeTree open (opened by Aftermath's raid) produced PASS/FAIL under a paused game for 4 suites; the sweep now covers Dialog_NodeTree and the taint is in obs_amendments.jsonl (filed: LESSONS 20261004T0648*). `get_defs`/`get_def` cannot read Type fields or name a GenStep class (filed: LESSONS). `socialPropernessMatters` is a ThingDef field, not an `<ingestible>` one (RM_VisslerArm, RM_QeshraRoe fixed). A TheRot rerun in the same game reads the accumulated navigator log and FAILed a working mechanic; now UNMEASURED precondition. `Transient/belt_*.py` probes are throwaways (belt_probe.py, belt_deep_proto.py, belt_gitprobe.py).

## Commits

```
eadbaecb3 TheRot script: a navigator log that already holds pings is a precondition (UNMEASURED), not a FAIL on a rerun
9374dc55b ledger: GIZKASTOWAWAY_COVERAGE_GAPS_1 closed
b5fd8a7d3 GizkaStowaway: behaviour_rules chain (4 triggers, replication stall/cap/interval, stages, chewing, cull guilt, sliders)
3b6b2a7d0 ledger: KEELHOIST_COVERAGE_GAPS_1 closed
fe2de69cb KeelHoist: static gate + cycle-time/Open Line/restraint formula bars (KEELHOIST_COVERAGE_GAPS_1 offline)
c3d8f79b8 Aftermath script: raid points 400 (120 read back as 78 and TryExecute refused at tick 345k)
8f58e5968 selftests: re-baseline two checks for a post-patch def dump
0e0b48cd8 FeverWood: name-source guard covers every hidden FactionDef under src/; selftest fixture fixed
bdc90542c ledger: STARWARSPATCHES_COVERAGE_GAPS_1 closed
3f4d5ac44 StarWarsPatches: patch_semantics_static chain (STARWARSPATCHES_COVERAGE_GAPS_1)
80ed5c305 ledger: PAWNFLAVOR_COVERAGE_GAPS_1 closed
64e1fcb00 PawnFlavor: static faction-wiring + def bars (PAWNFLAVOR_COVERAGE_GAPS_1)
9e058e48e lessons: faction fixedName NRE, modal sweep clean answer, Type fields unreadable
21d63254c Observatory: Dialog_NodeTree joins the modal sweep (it held LeaningScrub paused, forcePause)
1dba57999 ledger: PYRINTH_COVERAGE_GAPS_1 closed
783e0c758 Pyrinth: static behaviour bars over the effective XML (PYRINTH_COVERAGE_GAPS_1)
6c7ab2b36 deep_proto.py: unproven route to a Lantern Deep pocket map (DEEP_LAYER_BELT_HARNESS_1)
5fb948495 ledger: RUSTCHROME_COVERAGE_GAPS_1 closed
af98bb6ff Armoury script: Type-field wiring (driverClass/workerClass) asserted from the XML + def loaded live (get_defs cannot read Type fields)
5f62af382 RustChrome: DLL source stamp
... 61 more: git log --oneline 225f970aa..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/belt_bridge_log_20261003.md   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/belt_builder_log_20261003.md   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/belt_rerun17d_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/AcousticScanner_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/AssailantSalvage_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/Bacta_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/BlueDesert_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/BrainWorms_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/Cauldron_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/FallLineArrivals_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/FeverWood_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/Greentide_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/KeelHoist_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/LanternDeeps_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/LeaningScrub_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/Miasma_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/NightsideIce_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/RustCathedral_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/TheForge_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/TheRot_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/TheSump_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/Webwork_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/WeepingStones_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue_results.jsonl   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/obs_amendments.jsonl   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
 M infrastructure/state/modcheck_status.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_deep_proto.py   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_deploy_done   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_deploy_prune.txt   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_deploy_prune_c.txt   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_deploy_r5_biomes.txt   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_deploy_r5_plain.txt   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_deploy_r5_plain2.txt   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_deploy_r5_plain3.txt   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_gitprobe.py   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_harvest10_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_harvest11_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_harvest3_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_harvest5_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_harvest6_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_harvest7_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_harvest8_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_harvest9_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_probe.py   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_rerun19a_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_rerun19b_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_rerun20a_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_rerun20b_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_setbg.py   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/belt_sum.py   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/mc_matrix_live_20261002/shots/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/mc_matrix_live_20261002/shots_pass1/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/fixtures.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/live_queue/J1_situational_rerun/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/live_queue/J2_abort_proof/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/live_queue/situational_rerun/Aftermath_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/live_queue/situational_rerun/Armoury_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/live_queue/situational_rerun/GizkaStowaway_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/live_queue/situational_rerun/SWBestiary_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261002T204803/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261002T214905/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261002T223026/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261002T224507/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T010023/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T013800/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T014105/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T015159/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T015759/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T021239/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T021858/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T022509/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T023949/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T024304/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T025756/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T030536/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T031622/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T031958/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T033439/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T034108/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T034626/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T034854/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T035052/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T093854/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T095210/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T095537/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T095713/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T100623/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T104256/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T104624/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T105425/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T111441/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T112016/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T113847/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T122744/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T122746/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T123005/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T123152/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T123814/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T132212/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T132447/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T132959/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T133606/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T134902/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T135330/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T140142/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T144326/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T152945/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T164456/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T165757/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T173440/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T182403/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T183237/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T183952/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T184150/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T190148/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T191839/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T192451/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T194007/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T194943/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T201005/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T201136/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T205147/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T205344/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T205937/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T211515/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T213133/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T222819/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T224934/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T225211/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T225411/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T230013/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T233831/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T234227/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T234333/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T234759/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T235900/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261004T000303/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261004T000608/   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/northstar/ExplosiveGrowth_20261003T101654Z.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/northstar/FloodedCanyon_20261003T101943Z.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? Transient/northstar/Greentide_20261003T102251Z.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? deployed/config/ModsConfig.before-tier-flowworks.xml   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
?? deployed/config/ns_flowworks_backup.20261002T070221.json   mine (belt bridge agent) or generated by the belt runs; evidence uncommitted by design
```

