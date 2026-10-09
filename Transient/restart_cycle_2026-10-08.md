# Restart cycle 2026-10-08
18:37 started
18:37 bridge held by BENCH; running full dry-run plan -> /home/mandrake/.seat-tmp/plan.txt
18:42 plan read (/home/mandrake/.seat-tmp/plan.txt). In FULL list with drift: SWBestiary 81+/116~, UtinniPatches 57+/19~, FlowWorks 1+ (runtime json), small ArtOverrides, Aftermath/Bacta/Droidworks/Inhabited/PlantGrowth/Shiro/Whisperbird etc. `-` lines are deliberate repo deletions / runtime outputs: --apply without --prune. No src/ in-flight tracked edits.
NOTE: live ModsConfig.xml is a 16-mod list (UNRECOGNISED, 14:11) -- not FULL (614). Will back it up and `modlist_swap.py --restore --apply` after closing the game so the relaunch is the full list.
18:41 game pid 7416 killed; ./game down
18:42 FULL list restored (backup live 16-mod at ~/.seat-tmp/ModsConfig.16mod.bak.xml + PRESWAP in modlists/). 16 mods applied VERIFIED in sync (SWBestiary 197, UtinniPatches 76, FlowWorks 1 json, + small overrides/Aftermath/Bacta/Droidworks/Inhabited/PlantGrowth)
18:42:47 launched via steam (log was 24606)
18:52 polling Bridge token (literal grep, MEASURE_ALLOW_SCAN=1); live=FULL confirmed
19:01 still loading, log 920KB
19:02 Bridge token seen (~12.5 min after launch ~18:49:30); ./game up
19:04 census: 378/379 registered (jawa/revoke = quoted name only); new tools kill_hostiles, shade_probe, world_tile_cache_reset registered. Starting quicktest map for plant read (script Transient/plant_override_verify_2026-10-08.py)
19:09 plant override: state read (jawa/thing_graphic, 56 plants, all variants A.. resolved to our file names 256x256, badTex false) + screenshots read: ivy/blue/bramble/red all our art. Next: log triage, close items
19:15 Log (vs documented baselines; prior log was the 16-mod run, not comparable): first exception = ConfigErrors NRE of CannibalPirate / PirateYttakin (donor pirate defs, line 1219); xref EmptyAICore x2; patch ops failed 6 vs 5 (Caverns one gone; NEW: UtinniPatches BMT_GreyLady statBases + BMT_Thrumbungus drawSize, likely from the d074b131a caverns cut); ConfigErrors 34 lines vs 17 (RM_FE_Ground_*/Ash_* double-logged, guy762 weapons, RR_*). Not triaged further.
19:15 Closed JAWABENCH_DLL_REDEPLOY_1 and DONOR_PLANT_OVERRIDE_VERIFY_1; bridge released. Game left UP on the FULL list at a scratch quicktest map. DLL artifact is gitignored (nothing to push).
