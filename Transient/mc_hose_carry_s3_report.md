# Hose carry S3 (jobs) report

Status: STARTED Sun Oct  4 23:13:24 PDT 2026

## Files

## API used

## Build / selftest

## Live check (validation_hose.py --carry)

## Owed to S4/S5
- 23:13:29 read design + S2 report
- 23:13:34 read CompHoseReel + HoseProbe
- 23:14:42 engine API read (FloatMenuOptionProvider, WorkGiver_Scanner, Toil); writing drivers
- 23:15:52 defs written; reading validation_hose.py
- 23:17:34 4 .cs + csproj lines written; adding probe verbs
- 23:17:59 probe verbs added (colonists, pawn:, startjob:); building
- 23:18:09 BUILD OK; writing validation --carry
- 23:19:07 validation --carry written; running selftests

## Files (S3)
- NEW src/RimMandrake/MessyConduit/Defs/Hose/RM_HoseJobs.xml: JobDefs RM_CarryHoseEnd, RM_RetractHose (not casual-interruptible,
  not suspendable); WorkGiverDef RM_HoseOrders (Hauling, priorityInType 145 > Refuel 140 > HaulGeneral 15, Manipulation).
- NEW Source/Hose/Jobs/JobDriver_CarryHoseEnd.cs: also HoseJobDefOf, HoseJobTuning (grab 45 / set-down 30 / couple 90 ticks,
  wind 3 cells/s, autoResumeDroppedHose=true; plain statics for S5's settings page), HoseJobs (MakeCarry/MakeRetract/GiveForced,
  and the static ctor that sets CompHoseReel.HoldsReel to "curDriver is one of ours on this reel").
  Toils: [jump to walk if already carrying (load)] -> goto end (reel Touch when Stored, far Touch otherwise) -> grab wait ->
  BeginCarry + first step -> walk (Goto B, OnCell if standable else Touch; per-tick CarrierStep on Position change; reel cells
  skipped unless bringing it back) -> set-down/couple wait -> FinishCarry (bring-back target: then ReelIn).
  Stowed -> job Succeeded; Stretched -> Incompletable (reel already dropped + messaged). Finish action: DropCarry; pending
  CLEARED only when the job failed Incompletable/Errored while its own order was still current (path failure, message
  "could not reach"); draft/other order/downed keep it. FailOn: reel despawned, forbidden (unless forced), order no longer
  ours (cancel / re-order / retract), another holder.
- NEW Source/Hose/Jobs/JobDriver_RetractHose.cs: goto reel -> BeginWind -> wind toil (every 10 ticks WindBy(rate*10),
  rate = 3 cells/s x Manipulation clamped 0.3-1.5, progress bar) until Stored. Finish: StopWind -> Dropped shortened, order kept.
- NEW Source/Hose/Jobs/WorkGiver_HoseOrders.cs: PotentialWorkThingsGlobal = map component reels with a pending order (same
  faction); ShouldSkip when none. Static JobFor(pawn, reel, forced, out why) is shared by the WorkGiver, the float menu and
  the probe (forbidden, CanReserve, CanReach end+target at Danger.Some/Deadly-if-forced, allowed area unless forced).
- NEW Source/Hose/Jobs/FloatMenuOptionProvider_Hose.cs: drafted+undrafted, single select, needs Manipulation. Reel:
  "Carry hose out from" (Stored), "Pick up hose end of" + "Retract hose at" (Laid/Dropped); bare cell holding a free end:
  "Pick up hose end (reel at ..)". Each targets a cell, calls OrderDeploy/OrderMove/OrderRetract, then gives the job forced.
- Source/RimMandrake_MessyConduit.csproj: 4 Compile lines.
- Source/Hose/HoseProbe.cs (verbs only): colonists | pawn:id=draft|undraft|tp:x,z|stop | startjob:rx,rz=forced|work;pawnId.
- validation_hose.py: --carry (CR0-CR6 incl. CR4a/CR4b save/load, CR5b plump, CR5c endKind = SKIP until S4).
- 23:21:43 selftest_messyconduit 646/646; run_selftests running
- 23:31:58 run_selftests 177/178 (northstar_matrix/selftest.py, same Transient-PNG failure as S2); committing

## Result
- PUBLISHED 114c5a6b5 (source + DLL/.srchash built from that exact source + this report). Not deployed, not run live.
- Status: DONE (live run pending).

## Owed
- Live: deploy MessyConduit (DLL + NEW Defs/Hose/RM_HoseJobs.xml), then `python.exe validation_hose.py --carry` on a map with
  >=1 free colonist (scene at x78-114, z58-78; it teleports the first colonist beside the reel). Leaves two saves
  RM_hosecarry_<stamp>_{dropped,carrying}.rws. Unproven engine assumptions it will test: a toil's tickAction runs every
  tick for a walking pawn (CarrierStep relies on it); draft ends the forced job (CR3); a resumed driver after load keeps stepping.
- S4: live drawing (carry still re-lays along the trail per change), endKind (CR5c is SKIP until census has `endKind`),
  HoseEnds/HoseEvents, animated winder-less auto-retract.
- S5: HoseJobTuning statics -> HoseSettings page (handling-time slider, wind speed, autoResumeDroppedHose); review stations
  43-47; CR7 (gizmos without DevMode) row.
