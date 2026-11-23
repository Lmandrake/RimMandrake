## spec
Seen once, live on game b, 2026-11-21 (Test Pilot sitting on RIMMANDRAKE_TRACE_FLOWWORKS_MOAT_SWIMMERS_ONLY_IN_THE_CONTROL), scene_moat_raid, drained 3 m moat (6 notches).

Expected (a player's reading of "held in the pit, cannot climb out"): a raider standing on the floor of a 3 m pit cannot hurt a colonist who stands on the rim.

Observed: warden Human21242, spawned on plot square (64,62) and ordered RM_CaptureDown (accepted=True) on raider Human21193, who read `VERDICT Allowed held=True prisoner=False cell=64,61` (the square beside the warden, on the pit floor). The raider never became a prisoner in 900 ticks (reads at ticks 874 to 1714, cell 64,61 then 65,60), and at the end jawa/list_pawns read the warden downed=True, dead=False at (64,62). Every raider the pit did not hold had left the map before the order (the scene's drive-off), so only held raiders were hostile and near. In the same run the other warden took his captive prisoner in 120 ticks.

Not measured: who or what downed the warden. The damage log was not read in that run (cause UNMEASURED). The mod already pins the captive once the capture toil starts (JobDriver_CaptureDownPinned, PIT_CAPTURE_FIX_WARDEN_HURT_AT_LIP); the window before the pin (the walk and the wait at the lip) is the suspect, not a proven cause.

Class: MOD or EXPECTATION, undecided until the damage read.

First experiment: run scene_moat_raid until the row `MOAT_two_held_and_captured` reports `wardensDowned` above 0, keep the map (no reload), and read `jawa/damage_log thingId=<the downed warden>`: the instigator and the tick, against the tick the captive's job became RM_CaptureDownPinned.

## verify
Stage 6 check: sc_moat_raid, `python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_moat_raid --out <json>` (bridge held; flowworks tier). The row `MOAT_two_held_and_captured` carries `wardensDowned`; the item is answered when a damage read names what downed a warden, and fixed (if MOD) when `wardensDowned` reads 0 over 5 runs.
Acceptance test: none offline, the cause is known only from a live damage read (live-app behaviour).

## refs
file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py
file: src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitRooms.cs

## criteria
- A damage read names what downed the warden at the rim; if it is the held raider, no held raider hurts a warden on the rim before or during a capture.
