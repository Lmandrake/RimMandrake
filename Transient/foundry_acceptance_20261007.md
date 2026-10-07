# FOUNDRY acceptance sweep 2026-10-07 (owner AFK)
- 00:55 start. Live list = FULL (612 active mods, parsed ModsConfig via ET), not minimal; presence reads are a superset check.
- 01:05 get_defs/get_def FAIL live: TypeLoadException LaidPiece (GSS asm loaded != JawaBench build ref). L1 via get_defs UNMEASURED on this load. Remedy: kill, rebuild JawaBench --gm vs deployed GSS (00:06), relaunch same 612 list.
- 00:57 launched via steam (612 list)
- 01:19 ROOT CAUSE: JawaBench TerrainTools (get_def/get_defs) throws TypeLoadException(LaidPiece) unless mandrake.rm.gimmesomeslack is loaded; owner list lacks GSS. Added GSS to live ModsConfig (backup Transient/ModsConfig_before_foundry_acc_20261007.xml), relaunched.
- 01:50 L1 get_defs sweep: 33 criteria PASS recorded (full-613+gss), 1 FAIL (WRECKED_DISTILLATION A1), 6 UNMEASURED (owning mod not in live list), 12 criteria need non-def reads (log/state/settings) left open. Results Transient/foundry_l1_results_20261007.json
- 01:49 full-list quicktest start FAILS: first exception NRE ReadingPolicyDatabase.GenerateStartingPolicies <- GenTypes.SameOrSubclassOf (null type) in Game ctor, 613 list (cascade after). Not isolated. Pivot: L2 via modcheck tier runs (NightsideIce etc).
- 01:58 deployed biomes compose (21 files) with game down; modcheck runner._wsl_path fixed for UNC; rerunning modcheck NightsideIce
- 02:14 L2 (modcheck on minimal+biomes+GSS): NightsideIce 21 PASS/2 FAIL(site)/5 UNMEAS, CreatureBehaviors 0 FAIL/5 UNMEAS; fixed NightsideIce limit=10 script bug, modcheck runner UNC path + seat. Live list restored FULL. Releasing bridge.
