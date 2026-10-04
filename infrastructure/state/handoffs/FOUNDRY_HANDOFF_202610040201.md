# FOUNDRY_HANDOFF_202610040201 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202609301338`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The harness, not the mods, made most of tonight's RED: of ~35 FAIL/UNMEASURED I read from run17, the majority were instrument artifacts of `jawa/get_defs` (it CANNOT read System.Type fields such as thingClass/workerClass/size; it renders BiomeAnimalRecord rows and modExtensions WITHOUT their def/class names; it truncates every list at 64 items) and builder content that landed AFTER the deploy (DLLs and defs committed 18:14-18:35 while the game held the 18:13 deploy). Read `jawa/biome_probe` for rosters, `jawa/get_def` `extra.thingClass`, and never trust a RED whose evidence is a name-search over a get_defs dump. Before believing any suite result compare `git log --since=<deploy time> -- src/<Mod>` with the load time.

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
Nothing needs a ruling. Flag: two content bugs fixed outright that change shipped behaviour: (1) `WildAnimals_Greentide.xml` used `<Operation>` inside `<operations>` so ALL FIVE Greentide donor-roster patches were silently dropped by the loader (now `<li>`, so those rosters will appear next load); (2) BlueDesert's ten native charge hediffs now use `RimMandrake.BlueDesert.HediffCompProperties_GatedExplodeOnDeath`, so "Native detonations off" finally stops a krissek blast (DLL rebuilt, needs the next deploy). Also 67 missing-texture paths in the load log are owed art (Ancient* airlock/terminal family, RM_SunShield, RSW_Ossik/Kudda/Ikee/Thurra/Vosska/Khorrak/Ommok/Ulgga/Vozzik, Ashwallow, RUT_BrineBattery, RUT_GreentideAnt).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `run17d` — situational_rerun (WeepingStones, TheForge, LeaningScrub, Cauldron, Bacta, BrainWorms, BlueDesert) was started 19:02 by `setsid` on load 11 and keeps running with nobody watching; at 19:18 WeepingStones was 15 min in, spending ~17 s per `ordered_job` on a paused clock (queue orders now fixed to waitTicks=0 for the next run) and will hit its 1500 s suite budget around 19:27, which EXITS the whole runner (exit 4) so TheForge..BlueDesert will not run; NEXT: run `python3 src/RimMandrake/Utils/belt_watchdog.py`, then `python3 src/RimMandrake/Utils/modcheck/live_queue/record_summaries.py WeepingStones TheForge LeaningScrub Cauldron Bacta BrainWorms BlueDesert` once `Transient/belt_rerun17d_20261003.txt` has a verdict line; if it exited at WeepingStones relaunch TheForge,LeaningScrub,Cauldron,Bacta,BrainWorms,BlueDesert as `setsid nohup python.exe src/RimMandrake/Utils/modcheck/live_queue/situational_rerun.py --bland-world --mods ...` (this clone, foreground-safe via setsid) and WeepingStones last.
- Load 11 content is STALE for builders' later commits (KeelHoist DLL with RM_PitBuyerProof/RM_ChanceChuteProof, TheSump free-tier move: 18 defs not live, FeverWood ProofRaid, the BlueDesert gated-charge DLL, 11 ConfigError fixes, Greentide roster patch); NEXT: when `git status --short src/` shows nothing mid-edit run `python3 src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes --apply --prune` plus plain `--apply --prune --mod KeelHoist --mod Cuisine --mod SWBestiary --mod ScarlandsLadder --mod UtinniPatches`, close the game by PID (ModsConfig already lists keelhoist, utinnistatues, unfinishedline), launch via `powershell.exe Start-Process 'steam://rungameid/294100'`, run `preflight.py` under python.exe to reach Playing, set Prefs.RunInBackground true via jawa/static_call, then rerun KeelHoist, TheSump, FallLineArrivals, AcousticScanner, Webwork, LanternDeeps, NightsideIce, Greentide, TheRot, FeverWood, RustCathedral, Miasma, BlueDesert.
- `BLUEDESERT_THAW_YIELD_1` (not filed) — 23 blue-ice blocks gave 179 ice (7.8/block vs mineableYield 15, ratio ~0.52); NEXT: spawn 4 vanilla MineableSteel (yield 40) beside 4 RM_BlueIceMineable, same miners, compare the ratios to see whether 0.5 is a global difficulty factor.
- `BLUEDESERT_COLD_WAX_ON_ARM_1` (not filed) — warm cold wax never reads Ruined in the ON arm although the OFF arm ruins in the same room; NEXT: poke it live with comp_read on CompTemperatureRuinable (ruinedPercent) in both arms.
- `BLUEDESERT_FLORA_HARNESS_1` (not filed) — palefloss etc. cannot be planted: `jawa/set_plants` checks the map OUTDOOR temperature (CanEverPlantAt, palefloss max growth -1 C) and the bland tile is temperate, so flora/flora_chain/flora_warm/vhaulk_road are UNMEASURED; NEXT: either a cold bland tile in bland_world.py or a companion tool that sets plant growth on a spawned plant.
- `BACTA_BASE_OUTLANDER_STOCK_1` — RESOLVED as an instrument artifact (get_defs list cap 64; the Bacta suite now says UNMEASURED at a 64-row read); NEXT: only if the owner cares, prove the two rows exist via a static_call that counts the live stockGenerators.
- `CAULDRON_STEEL_YIELD_1` (not filed) — martyr tree 351 steel vs 6 expected is still unproven (map loot stacks pollute list_things); NEXT: after Cauldron reruns, diff steel stack ids on an empty pad.
- `WEEPINGSTONES_STOCK_JOBS_1` (not filed) — job_stock/feed/harvest/cull FAIL "the job never ran" on a possibly stale DLL (the designator was still listed with the setting off); NEXT: read the load-12 WeepingStones summary before touching the script.
- Builder-owned script gaps seen live: LanternDeeps/Miasma/Webwork/TheRot/Nightside need a GENERATED biome map for most chains (the bland map is Grasslands) and NightsideIce's shivven/breach proofs REFUSE for want of a powered heater and open ice; Greentide: a Droidworks ImperialLaborDroid strikes colonists mid-chain (surprise colonist_damaged) and the swallow chain's tick cap; RustCathedral roster/attitude/think-tree checks read get_defs (same instrument class as above); AssailantSalvage 11 art paths owed; AcousticScanner gizmo needs the sounder claimed (script fixed, unverified live). NEXT: file one `rimflow file --for FOUNDRY` item per mod (GENERATED_BIOME_MAP_HARNESS_1 first: a tile-biome map generator in bland_world.py would unlock ~60 UNMEASURED components) and hand the Greentide droid surprise to the Greentide builder.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
`jawa/get_defs` cannot read Type fields and omits BiomeAnimalRecord names, modExtension class names, and everything past item 64 of a list (filed: lessons 20261004T012758Z). Verse.Log stops at 1000 messages so Player.log AND drain_log go blind mid-run: the rimdrive session now resets it every 40 s and the watchdog names it (filed: lessons). `jawa/ordered_job waitTicks>0` on a paused clock burns the tool timeout per order (filed: lessons). An unnamed colony re-raises the naming dialog every ~600 ticks: bland_world now calls `jawa/name_colony` (filed: lessons). A dry-run `fire_incident` that cannot fire returns success=false WITH canFireNow=false (filed: lessons). `list_things` does not list pawns (use list_pawns kindDef). `jawa/damage` on a corpse-leaving blast: the pawn row vanishes, read `results[].dead`. `git pull --rebase` refuses with a dirty tree and `--autostash` is hook-blocked: land with `./publish -m x <already-committed path>` which pushes local commits. In zsh a command in a variable (`$B --call ...`) is not word-split and prints nothing, and `pkill -f` kills your own shell: use a script file and kill by PID (see: memory).

## Commits

```
767e8f466 ledger: RUSTCATHEDRAL_COVERAGE_GAPS_1 closed, RUSTCATHEDRAL_GOODWILL_FLOOR_1 filed; builder log
93d35e461 RUSTCATHEDRAL_COVERAGE_GAPS_1: hum ladder, hysteresis and watched pricing proven via static_call
ed634a1ad ledger: WEBWORK_COVERAGE_GAPS_1 closed; builder log
2daab1f9a WEBWORK_COVERAGE_GAPS_1: nest, relay and emergent spawn proven through static_call proofs
1f8020489 AssailantSalvage: wire 6 landed artpipe sprites, airlock icons use own art; script reads thingClass via get_def
ced305fa4 FeverWood foul-pool test orders the job with count=amount like the real WorkGiver (it consumed 1, not 5)
50b6d696c Greentide script: clear hostile pawns at site setup
493b9d181 FeverWood script: modExtension class names are unreadable via get_defs -> UNMEASURED, not FAIL
55b442900 run17 fixes: TheRot ProofCut hits the belly, workerClass via static_call; Miasma bones proof kills an adult
35e4e96d7 Greentide/Pyrelands scripts: a watched run uses the budgeted t.wait_ticks, not the Ultrafast poll (BudgetExceeded in the swallow chain)
216c0b3ff builder log: r28 blocked/unblocked survey
fe5b5dae1 ledger: SWBESTIARY_COVERAGE_GAPS_1 closed; builder log
6fd805f4f SWBESTIARY_COVERAGE_GAPS_1: every def resolves live; the five untouched toggles round-trip
70e78addd ledger: THESUMP_COVERAGE_GAPS_1 closed; builder log
526a4b6c1 THESUMP_COVERAGE_GAPS_1: tar vault and kethrel shell proven through static_call proofs
1d4386312 settings round-trip (second boilerplate form): Int32 fields get an int; TheRot workerClass is UNMEASURED (get_defs cannot read Type fields)
7426ad040 ledger: WRECKEDMACHINES and MIASMA coverage gaps closed; builder log
02051d7a3 Webwork/LanternDeeps scripts: read rosters via biome_probe, hatcher by comp class, front-creep by its field (get_defs omits names/classes)
05e0b2c27 MIASMA_COVERAGE_GAPS_1: decay cell, glaze and balm proofs; live def-load checks
34af71ba5 selftests green again: Bacta mock learns comp_read + pawn_health permanent; LeaningScrub mock lists wardens as pawns; live session resets Verse.Log every 40 s
... 1120 more: git log --oneline d8806cba9..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/belt_bridge_log_20261003.md   <-- mine (belt bridge agent); now committed
 M Transient/modcheck/live_queue/situational_rerun/Abyss_summary.json   <-- mine (belt bridge agent); now committed
 M Transient/modcheck/live_queue/situational_rerun/Cauldron_summary.json   <-- mine (belt bridge agent); now committed
 M Transient/modcheck/live_queue/situational_rerun/LeaningScrub_summary.json   <-- mine (belt bridge agent); now committed
 M Transient/modcheck/live_queue/situational_rerun/Miasma_summary.json   <-- mine (belt bridge agent); now committed
 M Transient/modcheck/live_queue/situational_rerun/TheForge_summary.json   <-- mine (belt bridge agent); now committed
 M Transient/modcheck/live_queue/situational_rerun/WeepingStones_summary.json   <-- mine (belt bridge agent); now committed
 M Transient/modcheck/live_queue_results.jsonl   <-- mine (belt bridge agent); now committed
 M infrastructure/state/modcheck_status.json   <-- mine (belt bridge agent); now committed
?? Transient/belt_deploy_done   <-- mine (belt bridge agent); now committed
?? Transient/belt_deploy_prune.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_deploy_prune_c.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_harvest3_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_harvest5_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_harvest6_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_harvest7_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_harvest8_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_harvest9_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_rerun10_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_rerun11_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_rerun12_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_rerun13_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_rerun14_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_rerun15_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_rerun16_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_rerun17a_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_rerun17b_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_rerun17c_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_rerun1_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_rerun2_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_rerun3_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_rerun4_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_rerun5_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_rerun7_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_rerun8_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/belt_rerun9_20261003.txt   <-- mine (belt bridge agent); now committed
?? Transient/mc_matrix_live_20261002/shots/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/mc_matrix_live_20261002/shots_pass1/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/fixtures.json   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/live_queue/J1_situational_rerun/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/live_queue/J2_abort_proof/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/live_queue/situational_rerun/AcousticScanner_summary.json   <-- mine (belt bridge agent); now committed
?? Transient/modcheck/live_queue/situational_rerun/AssailantSalvage_summary.json   <-- mine (belt bridge agent); now committed
?? Transient/modcheck/live_queue/situational_rerun/Bacta_summary.json   <-- mine (belt bridge agent); now committed
?? Transient/modcheck/live_queue/situational_rerun/BlueDesert_summary.json   <-- mine (belt bridge agent); now committed
?? Transient/modcheck/live_queue/situational_rerun/BrainWorms_summary.json   <-- mine (belt bridge agent); now committed
?? Transient/modcheck/live_queue/situational_rerun/FallLineArrivals_summary.json   <-- mine (belt bridge agent); now committed
?? Transient/modcheck/live_queue/situational_rerun/FeverWood_summary.json   <-- mine (belt bridge agent); now committed
?? Transient/modcheck/live_queue/situational_rerun/Greentide_summary.json   <-- mine (belt bridge agent); now committed
?? Transient/modcheck/live_queue/situational_rerun/KeelHoist_summary.json   <-- mine (belt bridge agent); now committed
?? Transient/modcheck/live_queue/situational_rerun/LanternDeeps_summary.json   <-- mine (belt bridge agent); now committed
?? Transient/modcheck/live_queue/situational_rerun/NightsideIce_summary.json   <-- mine (belt bridge agent); now committed
?? Transient/modcheck/live_queue/situational_rerun/TheRot_summary.json   <-- mine (belt bridge agent); now committed
?? Transient/modcheck/live_queue/situational_rerun/TheSump_summary.json   <-- mine (belt bridge agent); now committed
?? Transient/modcheck/live_queue/situational_rerun/UnfinishedLine_summary.json   <-- mine (belt bridge agent); now committed
?? Transient/modcheck/live_queue/situational_rerun/UtinniStatues_summary.json   <-- mine (belt bridge agent); now committed
?? Transient/modcheck/live_queue/situational_rerun/Webwork_summary.json   <-- mine (belt bridge agent); now committed
?? Transient/modcheck/surprises/20261002T204803/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261002T214905/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261002T223026/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261002T224507/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T010023/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T013800/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T014105/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T015159/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T015759/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T021239/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T021858/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T022509/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T023949/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T024304/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T025756/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T030536/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T031622/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T031958/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T033439/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T034108/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T034626/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T034854/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T035052/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T093854/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T095210/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T095537/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T095713/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T100623/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T104256/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T104624/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T105425/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T111441/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T112016/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T113847/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T122744/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T122746/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T123005/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T123152/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T123814/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T132212/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T132447/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T132959/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T133606/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T134902/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T135330/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T140142/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T144326/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T152945/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T164456/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T165757/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T173440/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T182403/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T183237/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T183952/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/modcheck/surprises/20261003T184150/   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/northstar/ExplosiveGrowth_20261003T101654Z.json   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/northstar/FloodedCanyon_20261003T101943Z.json   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? Transient/northstar/Greentide_20261003T102251Z.json   <-- generated by the belt runs/sessions, deliberately left uncommitted (evidence dirs and config backups)
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml   <-- mine (belt bridge agent); now committed
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   <-- mine (belt bridge agent); now committed
?? deployed/config/ModsConfig.before-tier-flowworks.xml   <-- mine (belt bridge agent); now committed
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   <-- mine (belt bridge agent); now committed
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   <-- mine (belt bridge agent); now committed
?? deployed/config/ns_flowworks_backup.20261002T070221.json   <-- mine (belt bridge agent); now committed
```

