# FOUNDRY belt bridge sweep 2026-10-08
Bridge held by FOUNDRY since 02:16Z. Game was DOWN at start.

## Milestones

### STOP-WORK REPORT (what FOUNDRY touched live before the owner's stop order, ~19:24-19:27 PDT)
- Bridge was held by FOUNDRY at start; game read DOWN, then `./game` measured RimWorldWin64.exe RUNNING/LOADING (someone else's launch; Player.log mid-load of workshop patches).
- I RAN `taskkill /F /IM RimWorldWin64.exe` (PID 1448). That was very likely BENCH's Giant Trees review load. It is dead; BENCH must relaunch.
- Deploy pass 1 (game running): plain `--apply` wrote 76 files; 2 DLLs failed (ShipVermin, StructureInjections, Errno 22). `--compose biomes --apply` wrote 27 DLLs. Logs: Transient/belt_deploy_plain_20261008.txt, belt_deploy_biomes_20261008.txt.
- Deploy pass 2 (after kill): plain `--apply` partial (4 "!" lines), biomes REFUSED, nothing written (28 "!" lines). Logs: *_plain2_*, *_biomes2_*.
- NOT touched: ModsConfig.xml, Steam, modset_builder, bridge tools. No ledger writes beyond the pre-existing dirty FOUNDRY.jsonl.
- Net: Mods folder now holds today's repo state for most mods (incl. the 27 biome DLLs); BENCH's list may load newer content than it expected.

## Offline prep for the next run
Order: (1) `rimflow bridge take`; ./game down; kill game FIRST. (2) `deploy_custom_mods.py --apply`, then `--compose biomes --apply` (check the biomes refusal text in belt_deploy_biomes2 first). (3) `modset_builder.py --tier acc_harness --apply` (BRIDGE, gimmesomeslack, luminouspigment, wreckedmachines, droidworks, falllinearrivals, unfinishedline, rut.patches, titaniccreatures; dlc on), launch via Steam. (4) `rimflow next --acceptance --seat FOUNDRY`: L1 reads first (20 items), then L2 on one quicktest map, `rimflow verify --criterion`. (5) `modcheck run` x5 mods; (6) flowworks `validation_v2.py --live --fresh-map` on the flowworks tier (expect 59/0/0). (7) belt_watchdog.py every 5 min.

Decision strings (Player.log): "Bridge token:" = up; first exception = first `Exception`/`NullReferenceException` line, not the loudest; `0 MakeThing stuff=null` after WhisperSarlaccSign (LIVE_ROUND2 A3); `[RM CreatureBehaviors] instant job loop` (A2); no `ConfigError` for RUT_EmpireRungDef (EMPIRE_ESCALATION A4).

Criteria-to-check (from rimflow next --acceptance, first items):
- MOD_OPTIONS_RETROFIT_1 A1 L1 full-list Mod Settings opens no red errors (needs full list, not acc_harness); A2/A3 L2.
- JAWA_SWIM_HOOD_KEEP_1 A1 L1 state-read Apparel_Head.CanDrawNow on swimming hooded Jawa; A2 L2 gauntlet; A3 L4 owner.
- MOVING_DUNES_BUILD_1 A3 L1 tint gate by live load; A1/A2 L2 sand moves / cache reveals.
- LIVE_ROUND2_FIXES_PROOF_1 A3 L1 log grep; A1/A2 L2 Stillsand quicktest (MirrorBeam burn, soorrak loop).
- DEBUG_ACTION_ENUM_CRASH_1 A2 L1 jawa/debug_action_yielders in loaded game.
- GRAFFITI_NORTHSTAR_BRIDGE_TOOLS_1 A1 L1 five tools in live tool list.
- LASSO_CHERRYPICKER_REMOVAL_1 A1/A2 L1 config reconcile; A3/A4 L2 full list.
- FORCE_DISTURBANCE_REFLAVOR_1 A1 L1 defs resolve with Force text.
- EMPIRE_ESCALATION_LADDER_1 A4 L1 six rung defs load; A5-A9 L2 quicktests.
Full list: re-run `rimflow next --acceptance --seat FOUNDRY` (only first ~9 of 20 L1 items captured here).
