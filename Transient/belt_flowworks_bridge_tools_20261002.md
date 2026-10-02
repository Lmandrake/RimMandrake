# BELT: FlowWorks bridge tools 2026-10-02

Status: DONE (built+deployed, NOT live-proven)

## Steps
- 06:53 step1: read plan sec8 (owed: excavation_rect, flowworks_pulse, pit_report) + existing tools; settings via existing mod_settings_field
- 06:53 step2: design: jawa/flowworks_pulse (reflection DoPulse on RM_MapComponent_Excavation - DoPulse is THERE, private; not Flood_FlowWorks), jawa/flowworks_excavation_rect, jawa/flowworks_pit_report -> new file JawaBenchFlowWorksPulseTools.cs
- 06:55 step3: wrote src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchFlowWorksPulseTools.cs (3 tools); csproj is SDK default-compile (no Compile line needed)
- 06:55 step4: build.py --gm --apply: Build succeeded 0 warn/0 err, deployed to C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench; 3 new names present in deployed DLL
- 06:56 step5: selftest_tool_metadata 1/1 (359 tools DLL==source); tool_schemas.json refreshed (+10 tools, 0 removed/changed); wrote src/RimMandrake/bridgetools/prove_flowworks_pulse.py (P1-P5) for FOUNDRY live run
