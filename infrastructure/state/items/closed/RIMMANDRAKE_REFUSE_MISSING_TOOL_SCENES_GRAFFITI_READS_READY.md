# RIMMANDRAKE_REFUSE_MISSING_TOOL_SCENES_GRAFFITI_READS_READY

## spec
Guard "Scenes can ask", part 1, of `design/specs/2026-11-15-cheap-guards-at-every-door.md` (section 3.4).
Protects against: an in-game visit (the bridge and an Opus driver) on scenes that stop at "MISSING TOOL".
Evidence: measured 2026-11-15, `maturation.py next Graffiti` counts 45 of 47 bars runnable while
`src/RimMandrake/Graffiti/validation.py` has 11 lines naming "MISSING TOOL", for six open probe tickets
(RIMMANDRAKE_PROBE_GRAFFITI_BREACH_PICK_HOOK_NEVER_READ_LIVE, ..._IDEO_REMOVAL_NO_TOOL_DELETES_ONE,
..._MARK_VARIANT_SAVED_BUT_UNREAD, ..._POOL_PICK_UNREADABLE_AT_A_CELL, ..._CLEAN_BREAK_GATE_FORCE_SKIPS_IT,
RIMMANDRAKE_PAINT_GRAFFITI_ROOFED_TWIN_RANDOM_ENEMY_WONT_DO) and Graffiti's scenes.json declares no `owed_parts_item`.
FlowWorks visit 1 (USD 21.68) read 12 of 31 checks UNMEASURED, some for the same reason.

Build `maturation.undeclared_stops(root, mod, tt, ended=None)` (read with `ast`, nothing imported or run) and count the
bars it lists as not runnable in `every_bar_has_a_check_that_runs`, beside the owed-scene-parts reading of 79483e1558.
Then make Graffiti honest in the same change: add `owed_parts_item` to each Graffiti scene that can reach one of those
raises, naming its probe ticket, and remake the test table. Graffiti's count of runnable bars will drop; that is the
point, and it is the truth today.

The builder does not edit the acceptance test; a clause believed wrong goes to the Conductor with the evidence.
A guard that cannot run says "did not run" and lets the work through; every refusal carries evidence, would_pass and
smallest_fix (standing_rulings.md, A refusal carries its path to pass).

## refs
file: src/RimMandrake/rimflow/maturation.py
file: design/concepts/Graffiti/scenes.json
file: src/RimMandrake/Graffiti/validation.py
file: src/RimMandrake/rimflow/acceptance/guard_scene_stops_accept.py
file: design/specs/2026-11-15-cheap-guards-at-every-door.md

## verify
python3 src/RimMandrake/rimflow/acceptance/guard_scene_stops_accept.py

## criteria
- A1: the acceptance test prints `PASS 10/10` and exits 0.
- A2: `maturation.py next Graffiti` before and after, pasted in the close note; after, every bar decided by a probe-gated scene reads not runnable and names its probe ticket.
- A3: the four maturation selftests stay green; `undeclared_stops` is run over every versioned mod and its output is in the close note (a mod it lists that is not Graffiti is filed down that mod's road back, not edited here).

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/guard_scene_stops_accept.py` exits 0 with `PASS 10/10`.
Watched failing at ed7e3b5389: `FAIL 3/10`, exit 1 (no `undeclared_stops`; the three that pass are "is not listed" clauses,
true when nothing is listed, which a correct build must keep). Not yet run against any implementation.
