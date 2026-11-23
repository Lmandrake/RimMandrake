## spec

Design Version: FlowWorks 0.1.0 (current, a Problem against the locked bars). Filed by the FlowWorks ticket sweep of 2026-11-22
(RIMMANDRAKE_SWEEP_FLOWWORKS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE), which merged these older tickets into this one, one
cause or one file group. Each old ticket's prose is in `infrastructure/state/items/closed/<ID>.md` and its history in
`rimflow show <ID>`; read the one you work on to its end before you build.

FlowWorks pit prison capture: three faults (prisoner flag backslides, warden downed beside the held raider, held raider read free one square out of a 4 m trench).

## merged tickets

- `PITCAPTURE_DIAGNOSE_PRISONER_FLAG_BACKSLIDES` (built): pit_prison_room capture_down_from_the_lip FAIL (valid) again in testq J20261101T083051Z-386617 (runner bd365feabd): {'held': 'True', 'prisoner': 'False', 'cell': '95,167'}, the symptom PIT_CAPTURE_FIX_HOSTILE_NOT_PRISONER closed on 2026-10-26; PASSed in J20261029/J20261031 between
  - sweep reading: a failure happened again: RUNNER testq J20261122T031148Z-227cc1 pit_prison_room capture_down_from_the_lip FAIL at 0ddc62aec6 (2026-11-22), finding FLOWWORKS_CAPTURE_DOWN_FROM_THE_LIP_FAILS_227CC1; vision line 4 (drained hole holds them as prisoners)
  - files: `src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitRooms.cs`
- `RIMMANDRAKE_PROBE_FLOWWORKS_WARDEN_DOWNED_BESIDE_HELD_RAIDER` (proposed): FlowWorks: a warden ordered to capture from the rim was downed while the raider the 3 m pit holds stood on the square beside him
  - sweep reading: seen once live 2026-11-21 (scene_moat_raid, 3 m drained moat): warden ordered RM_CaptureDown was downed beside a raider read held=True; cause UNMEASURED, needs a live jawa/damage_log read; the pre-pin window (walk and wait at the lip) is the suspect; merge target of the item-32 duplicate
  - its check: a damage read names what downed the warden; if a held raider, a held raider cannot hurt a colonist on the rim of a 3 m pit
  - files: `src/RimMandrake/FlowWorks/northstar/concept_scenes.py`, `src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitRooms.cs`
- `RIMMANDRAKE_TRACE_FLOWWORKS_HELD_RAIDER_LEFT_4M_TRENCH_ONCE` (proposed): FlowWorks: a raider the 4 m spiked trench held read NotHeld one square out of it 900 ticks later; how he left was not read
  - sweep reading: Seen once live 2026-11-21 (game b, sc_pit_trap_raid, old 1-wide trench 51e9d9ce4a): held raider read NotHeld one square out 900 ticks later, how unread; not seen on the passage staging (58cfa254e8); bar drained_hole_is_a_prison is a locked 0.1.0 experience bar, verdict none (state.md:442); MOD vs EXPECTATION undecided
  - its check: a live read every 30 ticks names how he left; if MOD, a held raider in a 4 m trench stays held over 5 runs or leaves only by a fetch the player can read
  - files: `design/concepts/FlowWorks/version/in_game/visit_2/evidence/exp/sc_pit_trap_raid_20261121T0823_gameb_fixed.json`

## his words (as recorded on the merged tickets)

- none recorded on these tickets

## verify

Acceptance test: none as one command, live only: each is a live read on a pit prison scene (each merged ticket above names its check).

## criteria

- Each merged ticket above is fixed with its check passing (red first where it is a fix), or dropped with its evidence.
- No locked 0.1.0 bar is loosened or edited by this work.

## refs

item: PITCAPTURE_DIAGNOSE_PRISONER_FLAG_BACKSLIDES
item: RIMMANDRAKE_PROBE_FLOWWORKS_WARDEN_DOWNED_BESIDE_HELD_RAIDER
item: RIMMANDRAKE_TRACE_FLOWWORKS_HELD_RAIDER_LEFT_4M_TRENCH_ONCE
