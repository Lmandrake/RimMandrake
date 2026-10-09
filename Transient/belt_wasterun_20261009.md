# WARCASKET waste run - working notes 2026-10-09

## Status
- started

## Findings

## Design

## Stubs
- Found: Warcasket mod (src/RimMandrake/Warcasket) has RM_CaskBay, Wastepack (Biotech) + RM_HalfExtractedCore as cargo, RM_HazardCasks category, kernel-style testable C#, settings class RM_WarcasketSettings. No XML player-choice node exists in vanilla quests (<choices> = random pick). So destination choice needs C# gizmo.
- Plan: new campaign mod src/RimUtinni/WasteRun (mandrake.rut.wasterun), RUT_ prefix, depends on mandrake.rm.warcasket. One QuestScriptDef RUT_WasteRun; branch signals per destination; C# = gizmo comp on RM_CaskBay + DisposeWaste QuestPart + incident worker.
- wrote Source/WasteRunKernel.cs, WasteRunSettings.cs
- C# comp/incident/questnode written; building
- XML written (quest, incident, history events, patch, About)
