FlowWorks SelfTest full suite on origin/main a68f003b88 (+ liquidnet shrink) is red on 2 hose source pins unrelated to the liquid net: GptA_hoses_off_never_retract_on_obstacles (wants 'if (RM_HoseSettings.enabled && r.layKey != null' in RM_MapComponent_Hoses.cs; line 1328 now reads 'bool cut = RM_HoseSettings.enabled && r.layKey != null && ...') and A3 recycled world (wants 'CordWorld w = LegacyFrame ? World() : World(LayWorldMaxAge); if (r.trail.Count > 0 && ...' in TickRecheck). Whoever reshaped RM_MapComponent_Hoses.cs owes the pin updates. Evidence: D:\ClaudeWork\rimmandrake\liquidnet_shrink\full2.txt lines 742, 1026.
home: NONE

Update (rerun on origin/main 6c0a3a6435 + liquidnet shrink, D:\ClaudeWork\rimmandrake\liquidnet_shrink\full3.txt): now 4 red, all hose
source pins on files the liquidnet change does not touch: the 2 above, plus HoseBand_P5_newly_dug_square_replans_or_retracts_once
("the 250-tick corridor branch is not the re-plan-or-retract") and hose suite "map changes (a fogged map too) bump the version;
MapRemoved unhooks" (HoseCorridorVersions.cs reshaped upstream).
