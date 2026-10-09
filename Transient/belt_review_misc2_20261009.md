# Belt review misc 2 2026-10-09 (FOUNDRY helper)

## Task 1/2 done (landed f2cd1b802)
- CompContactVenom.cs:~72 inspect line listed all colonists in contact map-wide -> now filtered to Position == parent.Position. FIXED, EH DLL+srchash rebuilt.
- RM_MapComponent_ChillGardenDefense.cs:9-15 orphan XML-doc summary describing RM_GardenOffenseKind sat on the class (wrong doc). DELETED. Full pass otherwise zero findings.
- WasteRunProof.cs full pass: zero findings.
- mark-clean: ChillGardenDefense, WasteRunProof, CompContactVenom (records in infrastructure/state/code_review/FOUNDRY.jsonl, landed with task 3).

## Task 3 (full-file passes)
- Elder trade (RM_ElderTradeUtility, RM_GameComponent_BrineElders, RM_ElderEconomyKernel, RM_ElderTreasureExtension, Dialog_OfferToElder, RM_Building_BrineElder): 
  - RM_ElderEconomyKernel.cs FindRecord: no null-entry guard (ForgetSeen has one); Deep-scribed list can hold null. FIXED.
  - RM_Building_BrineElder.cs:70 dead const JacketDisturbanceRadius (unused; the live one is on the MapComponent). cosmetic, FIXED.
- GradientAxis (MapComponent, Extension, GenStep, Repaint):
  - RM_MapComponent_GradientAxis.cs TickShift: Array.Clear(surgeApplied) at recede end can hit null if ApplyDeltaToAllCells returned early (delta==0) before EnsureGrid. FIXED.
  - RM_GradientAxisExtension.cs ConfigErrors: waterBands.Count after NullOrEmpty check -> NRE if null. FIXED.
- RM_MapComponent_Excavation.cs (full 1442 lines): ApplyFillTerrain dereferenced `fluid` unguarded (callers pass ActiveFluid which can be null: FillIn else-branch, ApplyRain, Displace credited loop). FIXED with early return. Everything else (Scribe symmetry, grid bounds, palette compaction, byte arithmetic) clean.
- LuminousPigmentMod.cs (reachable: csproj line 50): ApplySettings -> `research.IsFinished` / Find.ResearchManager deref Current.Game; with pressGate==Buildable that threw at main-menu startup and aborted the rest of ApplySettings. FIXED: Current.Game != null guard. Note (not fixed, design): a Buildable gate is therefore only applied by a mid-game settings write, not at game load; nothing else finishes the project. Candidate follow-up, left to owner/design.
- ApplyCuisineRecipeVisibility mutates ThingDef.recipes after ThingDef.AllRecipes may be cached; live toggle may need restart. UNVERIFIED, not changed.

## Landed
f2cd1b802 (task 1/2), 79f5c4dc5 (task 3 fixes, DLLs EH/DI/FlowWorks/LuminousPigment rebuilt; diving fuzz OK; full run_selftests 343/347, only unrelated selftest_items_glob_live red + 1 UNMEASURED). 
mark-clean: ChillGardenDefense, WasteRunProof, CompContactVenom, the six Elder files, four GradientAxis files, Excavation, LuminousPigmentMod.
NOTE: FlowWorks DLL on origin now rebuilt from origin sources; the shared tree carries a peer's uncommitted FlowWorks edits + DLL, which will need a rebuild after merge.

