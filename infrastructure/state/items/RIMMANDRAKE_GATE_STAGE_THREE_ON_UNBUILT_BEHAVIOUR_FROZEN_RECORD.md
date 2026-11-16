# RIMMANDRAKE_GATE_STAGE_THREE_ON_UNBUILT_BEHAVIOUR_FROZEN_RECORD

## spec
Graffiti 0.1.0 moved offline_build -> blind_challenge (2026-11-16 13:37 PST) with a locked bar whose behaviour does not exist:
raider_pressure / inv_raider_future_marks (no raider-pressure code in src/RimMandrake/Graffiti/Source, 0 grep hits for
"pressure"; 8 settings ship, the bar wants 11; build item RIMMANDRAKE_BUILD_GRAFFITI_RAIDER_PRESSURE_LETTER_NAMES_THE_WALL
open). The Stage 3 exit (maturation.py, offline_build: every_bar_has_a_check_that_runs, table_version) counts a live-only bar
runnable when its scene entry exists, so an unbuilt behaviour passes Stage 3 and is first found at Stage 6. The spec's
Stage 3 purpose is "build/implement"; its exit text does not say "the behaviour exists".
Fix unknown, handed to the Conductor: the obvious data source, record.json `impl: absent`, is frozen at the lock and stale
for every mod (ExplosiveKnockback 7, FlowWorks 3, GimmeSomeSlack 2, LeaningScrub 5, Pyrelands 2 locked rows still read
absent, several since built), and an open `item` behind a decider is normal for every mod's live scenes. A gate needs a
live "behaviour built" signal per bar (e.g. the build item's implemented event) that does not exist yet; adding an exit
clause is a change to a stage exit marked HIS by agreement.

## verify
Acceptance test: none, the gate's data source is undecided (see spec).

## criteria
- A mod with a locked bar whose behaviour is unbuilt cannot leave Stage 3, by a signal that is live, not the frozen record.
