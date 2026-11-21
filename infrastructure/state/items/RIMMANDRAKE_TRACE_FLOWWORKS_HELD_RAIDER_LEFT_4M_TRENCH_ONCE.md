## spec
Seen once, live on game b, 2026-11-21, sc_pit_trap_raid on the old 1-wide trench staging (`51e9d9ce4a`), evidence
`design/concepts/FlowWorks/version/in_game/visit_2/evidence/exp/sc_pit_trap_raid_20261121T0823_gameb_fixed.json`.

Expected (bar `drained_hole_is_a_prison`, his ruling FLOWWORKS_PIT_FALL_ONLY_FORCED_1): a raider the 4 m spiked trench
holds stays held until a warden takes him or a comrade's fetch takes him out by a way the player can read.

Observed: raider Human21236 read `ProofTrap ... held=True last=Human21236@63,60_t=243_fall=10.8` at tick 302 and
`VERDICT Allowed held=True` at 63,60. At tick 1202 he read `VERDICT NotHeld held=False cell=63,59`: one square south, out
of the trench. The live raid was still on the map and the warden had been downed. No read was taken between the two, so
how he left (his own climb, a comrade's fetch, a carry) is UNMEASURED.

Not seen since: on the passage staging (`58cfa254e8`) two held raiders stayed held for 1,200 ticks with nobody capturing
(`D:\ClaudeWork\rimmandrake\testpilot_pit_trap_raid\exp4_a.json`), and four full scene runs held both captives.

Class: MOD or EXPECTATION (a comrade's fetch is a feature), undecided.

First experiment: stage the old 1-wide 4 m trench with the live raid left on the map (no drive-off), and read
`ProofTrap` and the job of the held raider and of every free raider every 30 ticks until he reads NotHeld.

## verify
Live: the experiment above on any free game (bridge held; flowworks tier). Answered when a read names how he left; fixed
(if MOD) when a held raider in a 4 m trench stays held over 5 such runs, or leaves only by a fetch the player can read.
Acceptance test: none offline, the cause is known only from a live read (live-app behaviour).

## refs
file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py
file: src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs

## criteria
- A live read names how a raider held in a 4 m trench left it; if no fetch took him, he stays held.
