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

Cause (2026-11-24): a raider in climbing gear, by design (vision line 5: ladders, climbing gear and jumps are the ways in and
out). Human21297 is Bagdark, a Thrasher (8 % wear RM_ClimbingGear); each of his two stands is one 450-tick step (vanilla
MaxMoveTicks, the cap on the gear's price for a 4 m step). `gear_climber.py`, live on ArchBig and ArchSmall, no raid: in gear he steps in and
out in 450 to 480 ticks and is never held, and walks round an open pit on a fresh path; without gear he never enters, and is held
when put in. Human21297's own gear in t6 was not read [guess ~95%]. The "no nodes" line names Arkady, who is no raider of t6, and
is vanilla's line for any path not found.

Related, fixed: a comrade's fetch lifted a downed raider out of a 4 m pit from the rim (`d15dd762b231`). That was a
carry of a downed man. This raider was standing and had an attack job, so it is a different case.

## verify
`python3 design/concepts/FlowWorks/version/in_game/testpilot_20261123/selftest_on_pit.py` (the driver's label, and the live
receipt of `gear_climber.py`).

Acceptance test: none offline, live-app behaviour (the cause is known only from a live read).

## refs
file: design/concepts/FlowWorks/version/in_game/testpilot_20261123/trench.py
file: design/concepts/FlowWorks/version/in_game/testpilot_20261123/trench_t6_stray_raider.json
file: src/RimMandrake/FlowWorks/Source/Superdeep/RM_WallReach.cs
file: src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs

## criteria
- A live read names what the raider on the open pit square was (held, on a lid, a climber) and how he left it.
- No raider WITHOUT climbing gear stands on an open 4 m pit square unheld (`trench.py` names a geared one CLIMBER, not ONPIT).
