# Notes (newest first)

## 2026-11-11 setup (CLAUDE_ARCHMAGI_FWLIVE)
- Runs so far: 0 (nonpass tail 0). Mode whittle. No blocked_reason.
- Code: `src/RimMandrake/FlowWorks/Source/Drilling/Building_LiquidDrill.cs` — `WhyNot()` state (~l.90-112),
  `BlockText` (inspect sentence), `DynamicDrawPhaseAt` draws `OverlayTypes.QuestionMark` for every block except
  None/SwitchedOff/Unpowered/OutletBrimming (vanilla draws the power-off icons), DebugActions at ~l.301 ("Give this map a
  subsurface yield...", lists LiquidDefs with a canalFluid) and ~l.340 ("Clear subsurface yield").
  Pure math: `Source/Drilling/RM_DrillSurveyMath.cs`. Keys: `Languages/English/Keyed/FlowWorks_Keys.xml` l.102-123.
- Defs: `Defs/Drilling/ThingDefs/RM_LiquidDrill.xml` holds RM_LiquidDrill and RM_LiquidTap (same thingClass).
  Outlet = the cell it faces; needs a dug (excavated) channel there (PlaceWorker_DrillNeedsExcavatedOutlet). The
  `liquidDrillingEnabled` setting must be on.
- Built DLL at b26a96a424 carried peers' drawbridge/river WIP; deploy today's tree, not that one.
- No proof script exists for this item. Site: a dev quicktest colony on the small `flowworks` tier
  (`modset_builder.py --tier flowworks --apply`). Stage via bridge: spawn RM_LiquidTap (god mode), excavate the outlet
  cell, run the debug yield (or set the survey component directly if the dialog cannot be driven), toggle the comp.
- Evidence must be proportional: one staged run that shows each bullet, then a naive judge. Not an audit.
- Classify any failure MOD / SITE / HARNESS (skill `live-debugging-proof-harness`).
- The item still reads `owes A2 L4`. If close refuses on an L3 pass, record verify at L3 with the captures and note the
  re-levelling (Conductor triage note 2026-10-29 on the item) rather than inventing machinery.
