## spec
found-by: proof_restore_check.py (BENCH, 2026-10-26, systemic sweep from lesson infrastructure/state/lessons/20261026T161651Z-BENCH-proof-scene-restore-leak.md).
Tool: src/RimMandrake/Utils/proof_restore_check.py (selftest selftest_proof_restore_check.py; each hit below is counted under a BASELINE key there: lower or remove the count when fixed).

A live proof that changes a def or a Mod Settings field must undo it on EVERY exit path (finally / registered restore run on
INVALID, ERROR and throw), putting back the value it READ before the poke, never a hard-coded default. The hits below either
poke outside any try/finally that restores (unrestored-on-throw), restore a fixed literal/DEFAULTS value (restores-fixed-value),
or call Settings("reset") with nothing remembered (reset-loses-player-values). A leaked poke poisons every later test in the
running game and can overwrite the player's settings.

Filed, not fixed: FlowWorks was excluded from this sweep's edits (another batch owns it). Fix pattern: see 0a6567cce8 (C# restore delegate before the
poke, RunRestore on re-stage/INVALID/ERROR/Verdict finally) and this sweep's knockback_runner.py snapshot_settings/restore_settings.
A deliberate exception gets  on the hit line or the line above.

### hits (file:line kind target :: text), measured 2026-10-26 (55 hits)
- src/RimMandrake/FlowWorks/Source/Hose/HoseProbe.cs:167 unrestored-on-throw Prefs.DevMode :: `// CR7 staging: devmode:rx,rz=on|off sets the dev-mode flag so the gizmos verb can be read both ways. if (val == "on") Prefs.DevMode = true;`
- src/RimMandrake/FlowWorks/Source/Hose/HoseProbe.cs:167 unrestored-on-throw Prefs.DevMode :: `else if (val == "off") Prefs.DevMode = false;`
- src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_SuspensionProofs.cs:54 unrestored-on-throw DebugSettings.godMode :: `DebugSettings.godMode = god;`
- src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_SuspensionProofs.cs:584 unrestored-on-throw DebugSettings.godMode :: `DebugSettings.godMode = god;`
- src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_SuspensionProofs.cs:626 unrestored-on-throw DebugSettings.godMode :: `DebugSettings.godMode = true;`
- src/RimMandrake/FlowWorks/Source/RM_WaterLookProofs.cs:60 unrestored-on-throw RM_WaterLookSettings.deepWaterTintEnabled :: `RM_WaterLookSettings.deepWaterTintEnabled = kv[1] == "1";`
- src/RimMandrake/FlowWorks/Source/RM_WaterLookProofs.cs:64 unrestored-on-throw RM_WaterLookSettings.wetWallBandEnabled :: `RM_WaterLookSettings.wetWallBandEnabled = kv[1] == "1";`
- src/RimMandrake/FlowWorks/northstar/climb_proof.py:381 unrestored-on-throw raw :: `sset("pitRelativeClimbEnabled", True)`
- src/RimMandrake/FlowWorks/northstar/climb_proof.py:382 unrestored-on-throw raw :: `sset("superdeepCapturesOwnFaction", True)`
- src/RimMandrake/FlowWorks/northstar/climb_proof.py:383 unrestored-on-throw raw :: `sset("ladderPrisonDoorEnabled", True)`
- src/RimMandrake/FlowWorks/northstar/deep_lake_proof.py:255 unrestored-on-throw raw :: `sset(f, v)`
- src/RimMandrake/FlowWorks/northstar/deep_stone_live.py:109 unrestored-on-throw raw :: `sset(k, v)`
- src/RimMandrake/FlowWorks/northstar/depth_rebuild_proofs.py:292 unrestored-on-throw raw :: `fset(S_SW, "deepSwimEnabled", False)`
- src/RimMandrake/FlowWorks/northstar/depth_rebuild_proofs.py:295 unrestored-on-throw raw :: `fset(S_SW, "deepSwimEnabled", True)`
- src/RimMandrake/FlowWorks/northstar/depth_rebuild_proofs.py:340 unrestored-on-throw raw :: `fset(S_FW, "superdeepCapturesOwnFaction", True)`
- src/RimMandrake/FlowWorks/northstar/depth_rebuild_proofs.py:317 unrestored-on-throw raw :: `fset(S_SW, "shallowWaterDrowningEnabled", val)`
- src/RimMandrake/FlowWorks/northstar/droid_dig_live.py:181 unrestored-on-throw raw :: `sset(k, v)`
- src/RimMandrake/FlowWorks/northstar/flow_bignet_live.py:142 unrestored-on-throw raw :: `B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field="wetnessCutoffEnabled", value="True" if st.get("wetness0") is None else`
- src/RimMandrake/FlowWorks/northstar/flow_bignet_live.py:77 unrestored-on-throw raw :: `B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field="wetnessCutoffEnabled", value="False")`
- src/RimMandrake/FlowWorks/northstar/gravel_live.py:355 unrestored-on-throw raw :: `sset(k, v)`
- src/RimMandrake/FlowWorks/northstar/gravel_live.py:624 unrestored-on-throw raw :: `sset("digLabourMultiplier", 4.0)`
- src/RimMandrake/FlowWorks/northstar/gravel_live.py:626 unrestored-on-throw raw :: `sset("digLabourMultiplier", 1.0)`
- src/RimMandrake/FlowWorks/northstar/legacy_fill_live.py:143 unrestored-on-throw raw :: `sset("legacyFillFallbackEnabled", on)`
- src/RimMandrake/FlowWorks/northstar/liquid_checks.py:811 unrestored-on-throw raw :: `B.call("jawa/mod_settings_field", typeName=S_EG, action="set", field="spillWaterEnabled", value="False")`
- src/RimMandrake/FlowWorks/northstar/live_probes/fw_fluid_off.py:36 unrestored-on-throw raw :: `sset("rainFillsExcavationsEnabled", True)`
- src/RimMandrake/FlowWorks/northstar/live_probes/fw_fluid_off.py:37 unrestored-on-throw raw :: `sset("rainFillPerPulse", 1.0)`
- src/RimMandrake/FlowWorks/northstar/pipe_levelling_perf_proof.py:293 unrestored-on-throw raw :: `B.call("jawa/mod_settings_field", typeName=HS, action="set", field="maxLength", value="80", _answer=True)`
- src/RimMandrake/FlowWorks/northstar/pit_superdeep_walk.py:963 unrestored-on-throw raw :: `sset(S_FW, f, v)`
- src/RimMandrake/FlowWorks/northstar/pit_superdeep_walk.py:1201 unrestored-on-throw raw :: `sset(S_SWIM, "swimEnduranceHours", SWIM_ENDURANCE_FAST)`
- src/RimMandrake/FlowWorks/northstar/pit_superdeep_walk.py:1217 unrestored-on-throw raw :: `sset(S_SWIM, "swimEnduranceHours", saved_swim["swimEnduranceHours"])`
- src/RimMandrake/FlowWorks/northstar/pond_pump.py:230 unrestored-on-throw raw :: `sset(f, v)`
- src/RimMandrake/FlowWorks/northstar/pond_pump.py:298 unrestored-on-throw raw :: `sset(f, v)`
- src/RimMandrake/FlowWorks/northstar/pond_pump.py:305 unrestored-on-throw raw :: `sset(f, v)`
- src/RimMandrake/FlowWorks/northstar/raid_siege_live.py:115 unrestored-on-throw raw :: `B.call("jawa/mod_settings_field", typeName=RTS, action="set", field="raiderTrenchEnabled", value="False")`
- src/RimMandrake/FlowWorks/northstar/raid_siege_live.py:123 unrestored-on-throw raw :: `B.call("jawa/mod_settings_field", typeName=RTS, action="set", field="raiderTrenchEnabled", value="True" if trench0 is None else str(trench0)`
- src/RimMandrake/FlowWorks/northstar/scenarios_map.py:573 unrestored-on-throw raw :: `self.call("jawa/mod_settings_field", typeName=typ, action="set", field=field, value=str(value))`
- src/RimMandrake/FlowWorks/northstar/sheet_overflow_proof.py:709 unrestored-on-throw raw :: `sset(S_SHEET, "sheetOverflowEnabled", False)`
- src/RimMandrake/FlowWorks/northstar/sheet_overflow_proof.py:744 unrestored-on-throw raw :: `sset(S_SHEET, field, 2)`
- src/RimMandrake/FlowWorks/northstar/sheet_overflow_proof.py:841 unrestored-on-throw raw :: `sset(S_SHEET, field, 20)`
- src/RimMandrake/FlowWorks/northstar/sheet_overflow_proof.py:363 unrestored-on-throw raw :: `sset(S_SHEET, "sheetOverflowEnabled", True)`
- src/RimMandrake/FlowWorks/northstar/sheet_overflow_proof.py:529 unrestored-on-throw raw :: `sset(S_FW, "rainFillsExcavationsEnabled", True)`
- src/RimMandrake/FlowWorks/northstar/sheet_overflow_proof.py:529 unrestored-on-throw raw :: `sset(S_FW, "rainFillPerPulse", 1.0)`
- src/RimMandrake/FlowWorks/northstar/shovels_live.py:236 unrestored-on-throw raw :: `sset(S_FW, k, v)`
- src/RimMandrake/FlowWorks/northstar/shovels_live.py:357 unrestored-on-throw raw :: `sset(S_FW, "shovelRequired", False)`
- src/RimMandrake/FlowWorks/northstar/sprinkler_live.py:152 unrestored-on-throw raw :: `B.call("jawa/mod_settings_field", typeName=typ, action="set", field=field, value=str(value))`
- src/RimMandrake/FlowWorks/northstar/suspension_settings_live.py:119 unrestored-on-throw raw :: `sset("suspensionBridgesBuildable", False)`
- src/RimMandrake/FlowWorks/northstar/suspension_settings_live.py:122 unrestored-on-throw raw :: `sset("suspensionBridgesBuildable", True if b0 is None else b0)`
- src/RimMandrake/FlowWorks/northstar/suspension_settings_live.py:141 unrestored-on-throw raw :: `sset("suspensionWeightCollapse", False)`
- src/RimMandrake/FlowWorks/northstar/trench_cover_proof.py:176 unrestored-on-throw raw :: `sset(f, v)`
- src/RimMandrake/FlowWorks/northstar/water_scenes_walk.py:1530 unrestored-on-throw raw :: `w.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))`
- src/RimMandrake/FlowWorks/northstar/water_scenes_walk.py:1569 unrestored-on-throw raw :: `w.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))`
- src/RimMandrake/FlowWorks/northstar/water_scenes_walk.py:1581 unrestored-on-throw raw :: `w.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))`
- src/RimMandrake/FlowWorks/northstar/wet_costs_live.py:115 unrestored-on-throw raw :: `fset(field, True)`
- src/RimMandrake/FlowWorks/northstar/wet_costs_live.py:117 unrestored-on-throw raw :: `fset(field, False)`
- src/RimMandrake/FlowWorks/northstar/wet_costs_live.py:119 unrestored-on-throw raw :: `fset(field, True)`
