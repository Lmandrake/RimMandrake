# RIGID_PIPE_BUILD_WIRE_STYLE_PICKER

Owner rulings 2026-10-11 #1 and #8 (`design/RimMandrake/gss_flowworks_rulings_2026-10-11.md`).

## spec
- The rigid universal pipe is `RM_UniversalPipe` (defName kept; old `RM_LiquidHose` saves alias to it). The flexible line
  is the hose reel's hose and keeps the name "hose". Reading of ruling #1: the pipe the Q1 default produced IS the rigid
  pipe the owner asked for; what changes is its art (styled looks) and its interop. Card question owed if he meant a
  third, separate part.
- Four looks (Scrapper/Industrial/Modern/Futuristic) picked on the build button through the shared
  `_Shared/StylePicker/StylePickerCore.cs` (FlowWorks instance `Source/Machinery/PipeLook.cs`), `RM_UniversalPipe_<Look>`
  ThingStyleDefs with Basic-linked atlases (`Defs/Machinery/RM_UniversalPipeStyles.xml`); "Choose style" gizmo for one
  pipe or its connected run; `pipeDefaultLook` setting. Built 830f2c8d0.
- Art: owned atlases per look at `RimMandrake/FlowWorks/Pipe/<Look>/UniversalPipe_Atlas` (art subagent, art ledger);
  placeholder = tinted vanilla conduit atlas.
- HELD by the owner's 2026-10-11 order: pipe flow semantics and interop with other pipe networks wait for the
  liquid-network design pass.

## criteria
- A1 L0: `selftest_flowworks_stock.py` cases `PipeStyles_*` ok (830f2c8d0: 181/181).
- A2 L2: on a bridge map the build button opens the four-look menu; a picked look survives blueprint -> frame -> building ->
  save/load; an unstyled pipe draws the default look; "whole connected run" restyles every cardinal neighbour.
- A3 L4: owner judges the four pipe atlases.
