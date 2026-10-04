# FOUNDRY_HANDOFF_202610040454 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610040201`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->

`situational_rerun --bland-world --retile` (new, default off) re-tiles the bland map to each suite's own biome (bland_world.SUITE_BIOMES) and unlocked most generated-biome-map UNMEASURED: Webwork 17P/3F/10U to 21P/1F/3U, Miasma 13/2/10 to 23/1/8, TheRot 30/3/44 to 59/1/17, Nightside 8/5/16 to 22/3/3, TheSump 3/3/32 to 29/0/11 after redeploy, RustCathedral 32P/0F/11U, FeverWood 83P/2F/15U. Always pass --retile for biome suites; the second run after a load used to die UNMEASURED (13 bland candidates spent) and now reuses the current map.

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->

Nothing needs a ruling. Load 12 is current as of 20:20 deploy (biomes 94 files + plain 153).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->

- FEVERWOOD_PROOFRAID_NRE — ProofRaid static_call throws NullReferenceException staging the kurreth column (2 FAIL); NEXT: read RM FeverWood ProofRaid C# for a null faction/map assumption on the bland map, fix content or script.
- BELT_WATER_HARNESS_1 / BLUEDESERT_FLORA_PLANT_REFUSAL_1 / DEEP_LAYER_BELT_HARNESS_1 — filed; Miasma return proof and Greentide vurrak need water, BlueDesert flora still refuses 8 plants at tile -5 C, LanternDeeps Deep proofs need a Deep map; NEXT: `rimflow next --seat FOUNDRY` and take BELT_WATER_HARNESS_1 (paint water via jawa/set_terrain_batch in bland_world).
- Real-content candidates seen: TheRot swallow cut-out (200 dmg, 134 dealt, not released), Greentide churnmud swallow did not fire in 3200 t, FallLineArrivals (anywhere_allows dry-run false, feral drift-in), Webwork/KeelHoist fixed in script; NEXT: builders read Transient/modcheck/live_queue/situational_rerun/<Mod>_summary.json before touching.
- Not rerun on load 12: WeepingStones, TheForge, LeaningScrub, Cauldron, Bacta, BrainWorms (recorded RED from load 11, current content); NEXT: relaunch with `setsid nohup python.exe src/RimMandrake/Utils/modcheck/live_queue/situational_rerun.py --bland-world --retile --mods <list>` only after builders' later commits are deployed (compare git log vs load time).
- GAME_STATE — no runner live, game UP on load 12, bridge held by FOUNDRY; NEXT: run `./game` to measure, then launch the next suite run.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->

jawa/get_defs and get_def resolve a custom def type ONLY by its full namespaced name (RimMandrake.RustCathedral.Hum.RM_BiomeAttitudeDef), and cap think-tree depth at ~3 (see: Transient/belt_bridge_log_20261003.md). A bland map's GateOpen is open by design (player-parent map). `sleep` over 120 s in one foreground call backgrounds the command.

## Commits

```
60002f939 ledger: LORESTAGES_COVERAGE_GAPS_1 closed
3825ecaea LoreStages: offline_mechanism chain (real-DLL SelfTest proves stage rewrite/reset; toggle-off and save/load paths read from C#) + selftest
77821d2ae ledger: ABYSS_FREE_TIER_BODY_1 closed, split ABYSS_CRAGS_ART_ON_PORTED_DEFS_1; coverage notes
c0a26af6c paint list: RM_Abyss wildPlants are MayRequire'd, not unguarded
abb13ecc6 Abyss: invented creature labels move to the free tier (Abyss_Rename.xml -> mandrake.rm.abyss); About no longer calls the guarded wildPlants unguarded
5e4826a89 AssailantSalvage: wire RUT_AncientBlackBox art (lit casing, top-down) as Graphic_Single like its _Off sibling
4d76ae9de Observatory S2: obs_summary.py reads call telemetry (calls/min, p50/p95, retries, hangs, time timeline)
aedc00eca UtinniPatches: static bars for settings-gated patch ops and the planet-wide Infestation ban + selftest
225f61780 RustChrome: static bar for the 14 Tier-1 UI overrides (present, non-blank, vanilla-sized) + selftest
aa9eb1bc0 Observatory S1/S2: run identity, deploy fingerprint, modal check, non-blocking per-call telemetry
0cc5651d4 Observatory S0: required-check manifest, proven-checks report, normative measurement rules
81dd493bb ledger sync: land 2026-10-03 rulings (audio, provisional numbers, woolamander, run-report headline); unblock list struck
68fff6af0 Sound sourcing options doc: no item is stalled on sourcing any more (vanilla ships as final, 2026-10-03)
3fce5edd0 Land owner rulings 2026-10-03: run reports lead with required checks proven; provisional numbers; vanilla audio final
7c03869bc cast_assignment.csv: restore CRLF line endings lost in 589690135
589690135 Woolamander is a walking resident, not a flier: delete the flier/migrant text
897801f28 artpiped: building-sprite facing jobs get a top-down building clause, not the creature side-profile one
be80b396b ledger+builder log: PATCH_MAYREQUIRE_RESIDUE_FINDMOD_1
6b8171267 Patches: 43 inert Operation-level MayRequire guards -> PatchOperationFindMod (24 files) + sweep selftest
68f4be650 RustCathedral script: custom def type needs its full name; roster animals via biome_probe; think tree depth-limited is UNMEASURED
... 38 more: git log --oneline 9273b5e8e..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/belt_bridge_log_20261003.md   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/belt_rerun17d_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue/situational_rerun/AcousticScanner_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue/situational_rerun/AssailantSalvage_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue/situational_rerun/Bacta_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue/situational_rerun/BlueDesert_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue/situational_rerun/BrainWorms_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue/situational_rerun/Cauldron_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue/situational_rerun/FallLineArrivals_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue/situational_rerun/FeverWood_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue/situational_rerun/Greentide_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue/situational_rerun/KeelHoist_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue/situational_rerun/LanternDeeps_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue/situational_rerun/LeaningScrub_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue/situational_rerun/Miasma_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue/situational_rerun/NightsideIce_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue/situational_rerun/RustCathedral_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue/situational_rerun/TheForge_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue/situational_rerun/TheRot_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue/situational_rerun/TheSump_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue/situational_rerun/Webwork_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue/situational_rerun/WeepingStones_summary.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M Transient/modcheck/live_queue_results.jsonl   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M infrastructure/state/modcheck_status.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M src/RimMandrake/FloodedCanyon/Defs/ThingDefs_Races/RM_IrqitTarruq.xml   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
 M src/RimMandrake/FloodedCanyon/Source/RM_TarruqHushPatch.cs   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/belt_deploy_done   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/belt_deploy_prune.txt   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/belt_deploy_prune_c.txt   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/belt_harvest3_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/belt_harvest5_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/belt_harvest6_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/belt_harvest7_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/belt_harvest8_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/belt_harvest9_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/belt_rerun18a_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/belt_rerun18b_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/belt_rerun18c_20261003.txt   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/belt_sum.py   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/mc_matrix_live_20261002/shots/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/mc_matrix_live_20261002/shots_pass1/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/fixtures.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/live_queue/J1_situational_rerun/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/live_queue/J2_abort_proof/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261002T204803/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261002T214905/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261002T223026/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261002T224507/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T010023/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T013800/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T014105/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T015159/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T015759/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T021239/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T021858/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T022509/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T023949/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T024304/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T025756/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T030536/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T031622/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T031958/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T033439/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T034108/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T034626/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T034854/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T035052/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T093854/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T095210/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T095537/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T095713/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T100623/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T104256/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T104624/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T105425/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T111441/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T112016/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T113847/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T122744/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T122746/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T123005/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T123152/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T123814/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T132212/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T132447/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T132959/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T133606/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T134902/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T135330/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T140142/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T144326/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T152945/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T164456/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T165757/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T173440/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T182403/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T183237/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T183952/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T184150/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T190148/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T191839/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T192451/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T194007/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T194943/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T201005/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T201136/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T205147/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T205344/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T205937/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T211515/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/modcheck/surprises/20261003T213133/   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/northstar/ExplosiveGrowth_20261003T101654Z.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/northstar/FloodedCanyon_20261003T101943Z.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? Transient/northstar/Greentide_20261003T102251Z.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? deployed/config/ModsConfig.before-tier-flowworks.xml   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
?? deployed/config/ns_flowworks_backup.20261002T070221.json   mine (belt bridge agent) or generated by the belt runs; evidence dirs deliberately uncommitted
```

