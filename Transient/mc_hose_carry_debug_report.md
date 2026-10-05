# Hose carry live debug — 2026-10-04

Goal: `validation_hose.py --carry` green (FLOWWORKS_HOSE_DEPLOY_DRAG_1, S3 follow-up).

## Starting state
Run 20261004T233651 (DLL from 3fd249d54): CR0-CR3, CR4a, CR5b PASS; FAIL CR4b, CR5, CR6.

## Cycles

### Cycle 0 — read Player.log of the failing run (no code change)
One root cause for all three FAILs. Loading `RM_hosecarry_..._carrying`:
`Exception in SetupToils for pawn Maffrand driver=JobDriver_CarryHoseEnd (toilIndex=4)` — NRE in
`GenGrid.Standable` <- `JobDriver_CarryHoseEnd.WalkEndMode()` <- `MakeNewToils`. Vanilla runs SetupToils at load
BEFORE the pawn is spawned, so `pawn.Map` is null; `WalkEndMode()` (and `SetDownTicks()`) were evaluated while
BUILDING the toils (`Toils_Goto.Goto(DestInd, WalkEndMode())`, `Toils_General.Wait(SetDownTicks())`).
Consequences: the job ended Errored -> `OnFinish` read Errored + order-still-mine as "unreachable" -> `DropCarry(keepPending:false)`
-> CR4b saw Dropped/pending None. Then the error-recover JobDriver_Wait also NRE'd ("pawn is now jobless").
- CR5 FAIL was a cascade: pending None, so the work path had no order to resume (Dropped->Carrying->Dropped was the
  pre-save resume then the load drop).
- CR6 FAIL was a cascade: the pawn was left jobless/broken by the failed error-recover job, so the retract job never ran.

### Cycle 1 — fix: read the map when the toil STARTS, not when toils are built
`JobDriver_CarryHoseEnd`: the walk toil is a custom toil whose initAction picks the end mode and calls
`pather.StartPath` (same as Toils_Goto, minus the construction-time read); the set-down Wait sets
`ticksLeftThisToil`/`defaultDuration` from `SetDownTicks()` in its initAction (vanilla assigns ticksLeft from
defaultDuration before initAction, RimSage `JobDriver.TryActuallyStartNextToil`); `WalkEndMode` returns Touch if
`pawn.Map` is null. Selftests 646/646. Live run `validation_hose_carry_20261004T234240.json`: **9 PASS, 1 SKIP (CR5c, S4)**.
CR4b after load: Carrying, carrier kept, pending Deploy kept — the design §11 path (the saved driver resumes at its toil).
CR5: resumed 60 ticks, Laid at (106,68) in 300. CR6: Laid -> Retracting -> Stored in 750 ticks. No new exceptions in Player.log
(only the pre-existing startup `Default constructor not found for type System.String` def-load line).

### Cycle 2 — regression sweep (fresh map, after 3824a232d)
`--live` 12/12, `--relay` 9/9, `validation_style_hose.py --live` 6 PASS + R4 UNMEASURED (needs `--save NAME`, by design).
`--maze` 6 PASS 2 FAIL, reproduced on a second fresh map. Both FAILs were the CHECK, not the mod (no baseline maze
result was ever committed, so nobody had seen them):
- M5: the script destroyed the maze walls with `categories="Buildings"`; the bridge refuses that ("Not a ThingCategory:
  Buildings", valid is `Building`) and removed nothing, so the re-lay correctly read "no route". Fixed to `Building`.
  Second layer: with walls really gone it still read "no route" because `RM_MapComponent_Hoses.World()` is cached per
  TICK and M4's check had built it this tick with the walls up; the script now ticks 2 before re-laying (as M1 does after
  building). Finding for the mod owner: a lay/check in the same tick as a map edit sees the pre-edit world.
- P1: `build_batch` of `RM_LiquidTank` (FlowWorks, absent on the messyconduit tier) answers `success: true, placed: 0`;
  the guard read only `success`, so it graded a tank that was never built. Now RECORD/SITE when `placed` is 0 — the
  branch the script already had for this case. P1 stays unmeasured on this tier (needs FlowWorks loaded).
Re-run `validation_hose_maze_20261004T235424.json`: 7 PASS + P1 RECORD.

## Theories (incl. false ones)
- FALSE (briefed suspicion): CR5's drop-after-pickup was the 30-tick holder check / HoldsReel not matching the work-giver
  job, or the pawn still drafted from CR3. The log shows neither: the job died in SetupToils on load.
- FALSE: CR6 retract toils/WindBy/reachability broken. Untouched code passed once the pawn's job tracker was not wrecked.
- No check changed. CR4b's check (Carrying or Dropped, trail kept, pending Deploy kept) already matched §11.

## Result
`--carry` green at 3824a232d (9 PASS, CR5c SKIP = S4). Regression sweep clean after d8ab7ed3f (maze check fixes).
Still owed — S4: live drawing during carry, `endKind` in the census (un-SKIPs CR5c), HoseEnds/HoseEvents, animated
winder-less auto-retract. S5: HoseJobTuning onto the settings page, review stations 43-47, CR7 (gizmos without DevMode).
Also open: maze P1 (reel couples to tank) is unmeasured on the messyconduit tier and needs a FlowWorks-loaded tier; the
per-tick `World()` cache means a same-tick edit+lay sees the old world.
