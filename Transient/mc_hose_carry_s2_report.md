# Hose carry S2 (reel state) report

## Status
started Sun Oct  4 23:03:16 PDT 2026

## Reading

## Changes

## Build/selftest

## Commits

## For S3

### Reading (done)
- Design read in full. Plan: reel gets carry/trail/carrier/wound/pending fields; `laid` kept in sync (= Laid|Dropped) so
  every existing reader is unchanged. Empty trail = planned route (HoseMath.Lay, byte-identical). LayAlong(route) used
  only for a non-empty trail; LayAlong(empty) delegates to Lay. TryLay/ReelIn keep signatures (DEV + probe staging).
- Auto-retract on a cut stays INSTANT in S2 (validation --live relies on it); the animated Retracting auto-wind is S3/S4.
Transient: comp rewrite in progress 23:05:57
- 23:07:56 CompHoseReel/HoseMath/MapComp/HoseProbe edited; next: selftest row 6 + build
- 23:09:10 selftest_messyconduit 646/646 (row 6 mutation-verified); build ok; running run_selftests

## Result
- Source commit 283b6f6d3 (6 files). DLL + .srchash built from it (source 283b6f6d3997), committed in the publish below.
- selftest_messyconduit.py 646/646 (row 6 mutation-verified: flipping its first assertion fails it). run_selftests.py 177/178:
  the one failure is northstar_matrix/selftest.py C2 "existing live shots ... wire UNMEASURED (no aligned OFF pairs)",
  which reads Transient/messy_conduit_live_* PNGs another writer has modified in this tree; no hose code is involved.
- Not deployed (the main window holds the game). Not live-tested: validation_hose.py --live/--maze/--relay need a game.
  Why they should stay green: probe `lay` -> TryLay (same relay/loop/install logic, now via ResolveTarget) and the
  hose lies on the PLANNED route (empty trail -> LayAlong -> HoseMath.Lay, byte-identical: row 6); the lay key only
  gains a trail hash suffix, empty for planned hoses; the corridor auto-retract is still instant.

## What S3 can rely on (CompHoseReel)
- State: `carry` (HoseCarryState), `trail` (List<IntVec3>, empty = planned route), `carrier` (Pawn), `wound`, `pending`
  (HosePendingOrder None/Deploy/Move/Retract) + `pendingAt`. `laid` kept = carry is Laid|Dropped. `HoseOut`, `EndCell`,
  `TrailLength()`, `IsBringBack(cell)`.
- Orders (MP sync points): OrderDeploy(cell), OrderMove(cell), OrderRetract(), CancelOrder(), DevLayInstant(cell). Each
  returns null or the refusal reason. Nothing executes them in S2.
- Job API: BeginCarry(p) (Stored->Carrying from the reel cell toward pendingAt; Laid/Dropped->Carrying, a planned hose's
  route made explicit), CarrierStep(p, cell) -> TrailStep (end the job on Stowed or Stretched; Stretched clears the order
  and messages), FinishCarry(p, target) -> Laid, DropCarry(p, keepPending=true) (idempotent), BeginWind(p),
  WindBy(p, cells) -> true when Stored, StopWind(p) -> Dropped with a shortened trail. All idempotent and carrier-checked.
- Holder check every 30 ticks (map component): drops the end if the carrier is null/dead/despawned/off-map/downed/
  in a non-Roaming mental state/burning/asleep, or `CompHoseReel.HoldsReel(p, reel)` is false. The default is "CurJob
  targetA is this reel"; S3 should set it to its driver-type test.
- Drawing: a Carrying/Retracting reel with a trail is drawn by re-laying along the trail (LayAlong) on every trail change,
  which is S3's "ugly but correct" draw. S4 owns the live tail and retract clip.
- Probe: `order:rx,rz=deploy:x,z|move:x,z|retract|cancel`, `settrail:rx,rz=laid|dropped;x,z;...`, `gizmos:rx,rz`.
  Census adds carry, carrier{id,name,pos}, trail{count,pulled,last,planned}, pending, pendingAt, wound. endKind is S4's.
- Left for later stages: animated auto-retract (a winder-less Retracting reel reels in at once in S2), the reel's
  deployed art while Carrying (Graphic_HoseReel reads `laid`), the route+length preview under the mouse while targeting
  (§12 setting, S5), and autoResumeDroppedHose (HoseSettings, S5).
