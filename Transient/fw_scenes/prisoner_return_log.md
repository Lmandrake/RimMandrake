# Prisoner return fix log (FOUNDRY offline, 2026-10-17)

Item: RIVER_SWEEP_FIX_COLONISTS_RETURN_AS_NPCS. Clone: /home/mandrake/rm/scratch/FOUNDRY/prisonerreturn

## Steps
- [ ] read context
- [ ] root cause (RimSage)
- [ ] fix
- [ ] tests
- [ ] build+publish

## Log
- context read: item + day4 report + sweep_identity_fix3.json (slave back at (215,0), an EDGE cell too; prisoner posAfter null).
- ROOT CAUSE (read, vanilla 1.6 via RimSage): RM_TakenPolicy.PickReturnCell = CellFinder.TryFindRandomEdgeCellWith (an edge cell).
  JobGiver_PrisonerEscape.ShouldStartEscaping: prisoner of player, secure, district.TouchesMapEdge (or open path within 25
  regions) -> Goto(exit spot, exitMapOnArrival); on an edge cell the exit spot is adjacent/self -> Pawn.ExitMap within ticks.
  RM_Patch_EscapeIntoCurrentIsSwept only takes it when on a current lane -> vanilla ExitMap: Notify_PrisonerEscaped,
  PassToWorld(Decide) -> not held, not booked, discardable. Slaves have no such job giver -> pass.
- code: kernel (VanillaPrisonerStartsEscape, IsSecureReturnCell, PickPrisonerReturn, ExitIsLostReturn, RM_TakenReturnGuard), Return() restore->pick->mark->spawn, JobGiver_PrisonerEscape guard patch, ExitMap lost-letter patch; harmony lint 0 missing. SelfTest case added. Running SelfTest.
- SelfTest 567/567 (new case ok). winbuild FlowWorks next.
- python: returns_home row 600-tick stay check (+2 mock shapes: escapes FAIL, stays PASS, stay re-read asserted); selftest_extensions PASS. sweep_identity_proof.py: SWEEP_<kind>_stays_600 row. Running oracle 3000.
- oracle 3000: 9 modes PASS 3000/3000. vv_shipped_matrix --skip-ep next.
- vv_shipped_matrix --skip-ep: VERDICT PASS. run_selftests --only next.
- run_selftests --only (32): 30/32; reds not mine: settings_screens SWBestiary#BeastMechanics (known), selftest_human_review uncovered walk bar still_water_one_surface_height (no file of mine touches walk bars). Committing source.
- push refused (DLL stamp guard): source+DLL ship together. fetch, rebuild on merged tree.
- winbuild on 0bf02772a (origin/main = see log): 0 warn 0 err. Committing DLL.
