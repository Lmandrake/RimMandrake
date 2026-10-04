# FOUNDRY_HANDOFF_202610040742 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610040706`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The 'Cut by nobody' hits are NOT one biome's bug: 66 events across BlueDesert, Cauldron, FeverWood, WeepingStones, LeaningScrub and Aftermath, always Cut 1.0 about every 120 ticks with no instigator, on bland-world colonists; they create colonist_damaged surprises that leave many required checks UNMEASURED and probably explain LeaningScrub's lash_toggle_off_quiet FAIL. The companion now records an `origin` call-site stack on every instigator-less pawn hit and the detector carries it; read it from the first run after load 15.

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
Nothing needs a ruling. Round 6 got only as far as deploy and launch: no suite ran. Required checks proven at wrap: 28 of 1690 (owner bars 0 of 57); 265 more would be proven if run deploys were recorded fresh.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- LOAD_15 — launched 00:23 (plain+biomes --prune, companion with origin stacks, KeelHoist DLL fix), still cold-loading at 00:42, no runner live, bridge held by FOUNDRY; NEXT: wait for 'Bridge token:' in Player.log, run Transient/belt_setbg.py (RunInBackground), then python.exe situational_rerun.py --bland-world --retile --mods FeverWood and read the `origin` of its Cut-by-nobody events.
- CUT_BY_NOBODY_SOURCE — instrument ready, source unknown; NEXT: read origin stacks in Transient/modcheck/surprises/*/FeverWood* after that run and fix the def or DLL they name.
- FEVERWOOD_KURRETH_FACTION_FIXEDNAME — fixed in defs, unproven live; NEXT: confirm ant_theft/kurreth_column/ProofRaid pass in the same FeverWood run.
- KEELHOIST_PROOFSELL — NOTSOLD was a proof bug (slave keeps Faction; buyer is HostFaction), fixed f4387d7f6 and deployed; silver 0 unexplained; NEXT: rerun KeelHoist and read silverOnMap and sales= in the ProofSell string.
- WEEPINGSTONES_JOBS_NEVER_RAN — ordered_job accepted but feed/harvest/cull/stock deliver nothing in 1200 ticks (drivers look standard); NEXT: run WS and read Player.log for the first job exception after RM_FeedPoolPen starts.
- RERUNS_OWED — Aftermath, TheRot, Armoury, LeaningScrub, TheForge, Cauldron, BrainWorms, Bacta, BlueDesert, Contagion, TerminalBiomes plus new proofs (MovingDunes, RaidRedesigner, SeaShores, RustChrome, RestrainingBolts, GravshipLanding, Sump living map, UnfinishedLine, Warscar, NightsideIce, Abyss); NEXT: situational_rerun --bland-world --retile --mods <list> then record_summaries.py.
- DEEP_LAYER_BELT_HARNESS_1 — deep_proto.py unrun; NEXT: run it with the game up and write bland_world.enter_deep().
- LEANINGSCRUB_GRELLSPINE — not investigated; NEXT: after the Cut source is known, rerun LeaningScrub and read the colonist hediff def.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
python.exe works with the WSL UNC path as cwd, so situational_rerun launches from /home/mandrake/rm/foundry directly; deploy_custom_mods dry-run takes ~2 min and compose-biomes ~8 min (see: this file).

## Commits

```
4130b0d61 GizkaStowaway: Plague reachable at caps 4-5 (bands clamped below the cap, no stage skips)
e09fec2a1 selftest_utinnipatches_dump: no deepcopy of the 26k-row ThingDef dump (flaked under 16 workers)
9bf470fef ledger: PLANETPRESETPRIME_COVERAGE_GAPS_1 closed
b9b18e365 PlanetPresetPrime: signatures_static against decompiled engine + MLP source (PLANETPRESETPRIME_COVERAGE_GAPS_1 offline)
0417d5c9d detectors: colonist_damaged evidence carries the call-site origin stack
10117344d ledger: MANDRAKEPATCHES_COVERAGE_GAPS_1 closed
7fcf4b4f1 MandrakePatches: fix_effects_vs_dump_static (MANDRAKEPATCHES_COVERAGE_GAPS_1 offline)
f4387d7f6 KeelHoist: rebuild DLL (ProofSell host-faction)
518858f65 KeelHoist ProofSell: a humanlike slave is held by the buyer as HostFaction (its Faction stays its own); report both
4b4d9878a JawaBench damage_log: origin call-site stack on instigator-less pawn hits (finds 'Cut by nobody')
66fdc4310 ledger: UTINNIPATCHES_COVERAGE_GAPS_1 closed
718d96fe8 UtinniPatches: shipped defs vs load-14 dump + greatbole ladder state machine (UTINNIPATCHES_COVERAGE_GAPS_1 offline)
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/belt_bridge_log_20261003.md   generated by the belt runs; evidence uncommitted by design
 M Transient/belt_builder_log_20261003.md   generated by the belt runs; evidence uncommitted by design
 M Transient/belt_rerun17d_20261003.txt   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/AcousticScanner_summary.json   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/AssailantSalvage_summary.json   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/Bacta_summary.json   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/BlueDesert_summary.json   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/BrainWorms_summary.json   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/Cauldron_summary.json   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/FallLineArrivals_summary.json   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/FeverWood_summary.json   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/Greentide_summary.json   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/KeelHoist_summary.json   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/LanternDeeps_summary.json   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/LeaningScrub_summary.json   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/Miasma_summary.json   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/NightsideIce_summary.json   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/RustCathedral_summary.json   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/TheForge_summary.json   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/TheRot_summary.json   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/TheSump_summary.json   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/Webwork_summary.json   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue/situational_rerun/WeepingStones_summary.json   generated by the belt runs; evidence uncommitted by design
 M Transient/modcheck/live_queue_results.jsonl   generated by the belt runs; evidence uncommitted by design
 M infrastructure/state/modcheck_status.json   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_deep_proto.py   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_deploy_done   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_deploy_prune.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_deploy_prune_c.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_deploy_r5_biomes.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_deploy_r5_plain.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_deploy_r5_plain2.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_deploy_r5_plain3.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_deploy_r6_biomes.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_deploy_r6_done   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_deploy_r6_plain.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_gitprobe.py   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_harvest10_20261003.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_harvest11_20261003.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_harvest3_20261003.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_harvest5_20261003.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_harvest6_20261003.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_harvest7_20261003.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_harvest8_20261003.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_harvest9_20261003.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_probe.py   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_rerun19a_20261003.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_rerun19b_20261003.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_rerun20a_20261003.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_rerun20b_20261003.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_rerun20c_20261003.txt   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_setbg.py   generated by the belt runs; evidence uncommitted by design
?? Transient/belt_sum.py   generated by the belt runs; evidence uncommitted by design
?? Transient/mc_matrix_live_20261002/shots/   generated by the belt runs; evidence uncommitted by design
?? Transient/mc_matrix_live_20261002/shots_pass1/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/fixtures.json   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/live_queue/J1_situational_rerun/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/live_queue/J2_abort_proof/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/live_queue/situational_rerun/Aftermath_summary.json   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/live_queue/situational_rerun/Armoury_summary.json   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/live_queue/situational_rerun/GizkaStowaway_summary.json   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/live_queue/situational_rerun/SWBestiary_summary.json   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261002T204803/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261002T214905/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261002T223026/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261002T224507/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T010023/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T013800/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T014105/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T015159/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T015759/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T021239/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T021858/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T022509/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T023949/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T024304/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T025756/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T030536/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T031622/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T031958/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T033439/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T034108/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T034626/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T034854/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T035052/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T093854/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T095210/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T095537/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T095713/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T100623/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T104256/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T104624/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T105425/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T111441/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T112016/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T113847/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T122744/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T122746/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T123005/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T123152/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T123814/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T132212/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T132447/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T132959/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T133606/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T134902/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T135330/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T140142/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T144326/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T152945/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T164456/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T165757/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T173440/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T182403/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T183237/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T183952/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T184150/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T190148/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T191839/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T192451/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T194007/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T194943/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T201005/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T201136/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T205147/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T205344/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T205937/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T211515/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T213133/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T222819/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T224934/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T225211/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T225411/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T230013/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T233831/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T234227/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T234333/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T234759/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261003T235900/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261004T000303/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261004T000608/   generated by the belt runs; evidence uncommitted by design
?? Transient/modcheck/surprises/20261004T001458/   generated by the belt runs; evidence uncommitted by design
?? Transient/northstar/ExplosiveGrowth_20261003T101654Z.json   generated by the belt runs; evidence uncommitted by design
?? Transient/northstar/FloodedCanyon_20261003T101943Z.json   generated by the belt runs; evidence uncommitted by design
?? Transient/northstar/Greentide_20261003T102251Z.json   generated by the belt runs; evidence uncommitted by design
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml   generated by the belt runs; evidence uncommitted by design
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   generated by the belt runs; evidence uncommitted by design
?? deployed/config/ModsConfig.before-tier-flowworks.xml   generated by the belt runs; evidence uncommitted by design
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   generated by the belt runs; evidence uncommitted by design
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   generated by the belt runs; evidence uncommitted by design
?? deployed/config/ns_flowworks_backup.20261002T070221.json   generated by the belt runs; evidence uncommitted by design
```

