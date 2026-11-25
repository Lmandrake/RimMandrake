# Polish list beside `boundary.md` (BRIDGE v2.0)

A record of minor points that are not significant (`CLAUDE.md` §Code is clean when its promises are tested). Nobody works them.

## CALM PROFILE (fresh read of 5f1549339b, 2026-11-25)

- `JawaBenchCalmProfile.Weather`: the condition is registered before its entry is written; a `TransitionTo` that throws leaves the forced weather with no entry.
- `JawaBenchCalmProfile.Gate`: the before value is always "off"; a gate that `jawa/scene_gate` armed first is released at leave and reads as put back.
- `Gate.TakeBack` shares the allow list with `allowIncidents`: with RaidEnemy in both and one firing, the exception reads "closed UNUSED".
- `certified` is taken on the caller's word by the tool; only `calm_profile.arm_args` fills it from the certificate.
- The second-driver path inside `Session.Arm` logs its breach at tick -1 (the tool checks first, so nothing reaches it).
- `Breaches.SinkFaults++` is outside the lock.
- `prove_ordered_rescue.py` R5 prints the ticks before and after but does not compare them, and does not check the reason (the reason is a fixed non-empty string in `JawaBenchForce.cs`).
- `prove_ordered_rescue.py` R3: a hostile that fails to spawn reads FAIL (exit 1); the docstring calls a missing scene NO VERDICT (exit 2).
- `prove_tap_certificate.py` `judge_job`: the think-tree route now also accepts a queued `WorkGiverDef:<defName>` row as evidence (real tree rows are plentiful).
- `JawaBenchCast.cs` `Giver()`: with no node, `workGiverDef` now wins over `j.jobGiver`; no reader depends on the old order.
- A held incident's `caller` names Harmony's replacement (`...IncidentWorker.TryExecute_Patch4`), not the real caller, when the call came from a tool (live, 2026-11-25).
