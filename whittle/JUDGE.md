# Judge — Bedless pit prison (FlowWorks), 2026-11-10

Independent judge. Read: `whittle/STATEMENT.md`, `whittle/NOTES.md` (empty: "# Owner rulings"),
`whittle/evidence/*`, and the source `src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitPrisonCare.cs`,
`Source/Superdeep/RM_PitRooms.cs` (capture-down), `Source/RM_PitPrisonProof.cs`,
`northstar/concept_scenes.py` (`scene_hole_prison`), `northstar/selftest_hole_prison.py`.
Not read: DONE.md, BROADEN.md, builder transcript, final report. No bridge or game driven.

## The deciding fact

`whittle/evidence/final-status.json` records, in the builder's own words:
`loaded_DLL_identity = UNMEASURED: game never launched`, and `live_capture`, `live_feeding`,
`live_disabled_control`, `live_snapshot_restore`, `live_broaden_cases` all `UNMEASURED`.
`preflight-after.log` ends `VERDICT NO-GO O10,O13` (0Harmony.dll baseline drift; deployed
GimmeSomeSlack DLL differs from the repo). The final About.xml commit is not deployed. No file
was marked CLEAN by code review. The only behavioural tests are a fake bridge whose own
docstring says *"Fake game outcomes verify assertions/cleanup; they never prove game behavior"*,
plus offline `PitRoom_*` C# math cases. So no in-game behaviour in this statement is evidenced.

## Bullets

1. **Capture a downed raider from the rim of a drained D4 moat/pit with no bed; becomes a
   prisoner and stays in the hole — CANNOT TELL.** The code path exists: a
   `FloatMenuOptionProvider_CaptureDown` / `JobDriver_CaptureDown` walks to a lip cell and uses
   vanilla `CapturedBy`; `Room.IsPrisonCell` is postfixed true for an enclosed pit room; and
   `WorkGiver_Warden_TakeToBed.TryMakeJob` returns no job for a `Kept` prisoner. The scene
   asserts zero beds and depth/fill=0 before capture. But it never ran in a game; whether
   `CapturedBy` with no bed leaves `PrisonerIsSecure`/`Kept` true, and whether the pawn stays
   put, is unmeasured.

2. **Fed and kept by ordinary prisoner care without a bed; a remote prisoner bed does not pull
   the prisoner out — CANNOT TELL.** Patches cover `ShouldBeFed` (downed/medical-rest only),
   `GoodLayingStatusForTend`, `Reachability.CanReach` redirect to the rim, and `DeliverFood`
   targetC dropped into the hole; the scene's second capture deliberately places a
   prisoner-owned bed outside and asserts the warden's TakeToBed giver returns `none` and the
   pawn stays `kept`. The design is right and the test would catch the failure, but the
   remote-bed capture and the feed/ingest/tend rows were only answered by the fake bridge.
   No real ingestion, tend or no-transfer reading exists.

3. **With pit prisons disabled, bedless capture is refused and bed-based prisons still work —
   CANNOT TELL.** The scene flips `superdeepRoomsEnabled` off, requires `VERDICT SettingOff`
   and no prisoner after ordering `RM_CaptureDown`, then captures a separate raider with the
   vanilla `Capture` job into a ground bed and requires `prisoner=True inBed=True`. That is a
   proper control, distinguishing on from off. `live_disabled_control = UNMEASURED`: it was
   never run against the real game.

4. **A repeatable acceptance scene asserts starting conditions, distinguishes enabled from
   disabled, restores terrain/liquid/things/settings; relevant offline checks and a real game
   run support the claim — FALSE.** The scene half is well built (start-rect fingerprint over
   terrain, under-terrain, roof, depth, water, fluid and every thing; snapshot reload in
   `finally`; every changed setting restored and checked; fault-injection selftest
   `selftest_hole_prison.py` shows it fails on no-capture, off-captures, remote warp, no feed,
   escape, wet pit, bad snapshot and abort, and still restores). Offline checks are green
   (`offline-tests-stable.log`: PASS 2/2; `build-final.log`: 0 warnings, 0 errors). But the
   bullet demands a real game run, and there is none: the game never launched, preflight is
   NO-GO, and `live_snapshot_restore` is UNMEASURED.

## Verdict

The code and the acceptance scene look carefully designed, and the offline checks pass. None of
it has run in RimWorld. Three bullets cannot be told and the fourth is false on its own terms.
Also open: preflight NO-GO (O10, O13), undeployed About.xml, and no file reviewed CLEAN.

would show: no
