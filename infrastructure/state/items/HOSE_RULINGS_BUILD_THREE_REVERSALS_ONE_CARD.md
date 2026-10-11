# HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD

Rulings #1, #2, #3, #8 of `design/RimMandrake/gss_flowworks_rulings_2026-10-11.md`.

## state
- **#1/#8 rigid pipe, looks half — built 830f2c8d0.** `RM_UniversalPipe` (defName kept; old `RM_LiquidHose` saves alias
  to it) is the rigid pipe; the flexible line is the hose reel's hose and keeps the name "hose". Four looks
  (Scrapper/Industrial/Modern/Futuristic) through the shared `_Shared/StylePicker/StylePickerCore.cs` (FlowWorks instance
  `Source/Machinery/PipeLook.cs`), `RM_UniversalPipe_<Look>` Basic-linked ThingStyleDefs, "Choose style" for one pipe or
  its run, `pipeDefaultLook` setting. Owned atlas art: art subagent, `RimMandrake/FlowWorks/Pipe/<Look>/` (placeholder =
  tinted vanilla conduit atlas). Absorbs the duplicate RIGID_PIPE_BUILD_WIRE_STYLE_PICKER.
- **#3 text half — built.** A hose end in water reads "lying in <water> (no intake: filling a tank takes a pump)"; the
  reel's inspect names its free end and the faction of a coupled tank; the dev flow gizmo no longer says "no pump yet".
  Audit: no free intake path into any tank exists (every TryAddLiquid caller is a pump, machine output, adapter, hand
  pour, ruin stock or the ruled tank->hose feed). Nozzle intake (hose-port step 9) stays unbuilt.
- **HELD (owner order 2026-10-11, liquid-network design pass):** #2 off-hose drain, the flow side of #3, pipe interop with
  other pipe networks ("plugs into other pipe networks cleanly"), tank->hose feed changes.

## criteria
- A1 L0: SelfTest cases `PipeStyles_*`, `HoseText_*` ok.
- A2 L2: bridge map: the pipe build button opens the four-look menu; a picked look survives blueprint -> frame ->
  building -> save/load; an unstyled pipe draws the default look; "whole connected run" restyles the run.
- A3 L2: a reel with its end in a pond reads "lying in ... (no intake ...)"; one coupled to another faction's tank names it.
- A4 L4: owner judges the four pipe atlases.
- A5 L4: the held flow half (#2, #3 flow, interop) after the network design lands.
