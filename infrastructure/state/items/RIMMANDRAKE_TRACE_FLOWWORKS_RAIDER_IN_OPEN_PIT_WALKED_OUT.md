## spec
Design Version: FlowWorks 0.1.0 (a Problem against the locked bars if the cause is the mod).

Seen once, live on Steve1, 2026-11-23, build `1c053b325bc5`, on the 2-wide 4 m passage pit of sc_pit_trap_raid with the
raid left on the map (driver `design/concepts/FlowWorks/version/in_game/testpilot_20261123/trench.py`, run t6).

Expected (bar `drained_hole_is_a_prison`): a raider is either held by a 4 m pit square, or never stands on it. An open
pit is walked round.

Observed (`design/concepts/FlowWorks/version/in_game/testpilot_20261123/trench_t6_stray_raider.json`, key `holdTrace`):
free raider Human21297 stood at 60,59 until tick 602, then on pit square 60,60 from tick 632 to tick 1052 with the job
AttackMelee on a colonist about 20 squares away and no movement, then at 61,62 (the strip beside the pit) at tick 1082,
and walked on. The lids were gone by then: the deck gave way before tick 182, and run t18 of the same sitting read every
lid gone after the fall.

Player.log on Steve1 carries for the same run `Resolved path returned no nodes, request: ((60, 0, 60) ->
Thing_Human21239 ..., Touch, for Arkady)`, one NullReferenceException after it, and FlowWorks' own line `[FlowWorks]
reach residual: ... CanReach said yes, A* found nothing`. Six such lines came in about 20 runs, each from a first-row
pit square (59,60 or 60,60).

Not read: whether he was held. The trace of that run read only the raiders that were held at its start. The driver now
reads every hostile on a pit square (ProofTrap and ProofCover). Not seen again in 16 later runs.

Class: MOD or HARNESS (the pit's first row lies in the gap of the wall line), undecided.

Related, fixed: a comrade's fetch lifted a downed raider out of a 4 m pit from the rim (`d15dd762b231`). That was a
carry of a downed man. This raider was standing and had an attack job, so it is a different case.

## verify
Live, on any free game on the flowworks tier:
`python.exe design/concepts/FlowWorks/version/in_game/testpilot_20261123/trench.py <out.json> 2 1500`

Red when `holdTrace` has an `ONPIT` line (a hostile on a pit square that is not held: the line names his job, his trap
read and the lid state), or `holdLeft` is not empty, or Player.log gained a `Resolved path returned no nodes` line in the
run. Green: none of the three over 10 runs.

Acceptance test: none offline, live-app behaviour (the cause is known only from a live read).

## refs
file: design/concepts/FlowWorks/version/in_game/testpilot_20261123/trench.py
file: design/concepts/FlowWorks/version/in_game/testpilot_20261123/trench_t6_stray_raider.json
file: src/RimMandrake/FlowWorks/Source/Superdeep/RM_WallReach.cs
file: src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs

## criteria
- A live read names what the raider on the open pit square was (held, on a lid, a climber) and how he left it.
- If the cause is the mod: no raider stands on an open 4 m pit square unheld, and no `Resolved path returned no nodes`
  line comes from a pit square, over 10 runs.
