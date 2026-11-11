# Fresh read-only pilot diagnosis after three non-pass runs

Primary stayed the only live driver. The bridge was released while diagnosing;
the restored calm map was paused and sane. Pilot read source and receipts only.

Failures 1/2 were HARNESS: Identity(string) given zero bridge arguments, then
unknown WorkTypeDef BedRest. Failure 3 was SITE: random Colonist generation
produced a pawn with Warden disabled. No MOD behavior had yet been exercised.

Bundled repairs based on supported source contracts:
- Bounded six candidates at each warden position; Baseliner xenotype; draft
  immediately; require successful enabled readBack>0 for Warden, Doctor, Patient,
  PatientBedRest; record raw checks and vanish rejected candidates. The existing
  pick_hauler in northstar/climb_proof.py uses the same rejection pattern.
- OFF capture may return success:false when the accepted job aborts immediately.
  Require accepted=true and requestedJobDef=RM_CaptureDown before testing that
  prisoners remain uncaptured. An unattempted order is not a valid control.
- Care(start) must return ordered=True before any feeding/tending advance.
- Pin raiders to Baseliner too; random xenotypes confound body/food/recovery.
- Spawn three verified ten-meal stacks with jawa/spawn_batch, then read back the
  inventory rather than assuming the spawn call supplied enough food.

Strict fake faults now cover unavailable workers, first candidate rejection,
insufficient food, refused care order, unattempted OFF order, and expected OFF
immediate abort, in addition to existing behavior/cleanup fault controls.
Next: one measured gameplay attempt; inspect first new Player.log exception on
failure and classify the failing state before changing MOD code.
