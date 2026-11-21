# RIMMANDRAKE_TRACE_PYRE_HUNGRY_COLONIST_EATS_ONLY_OUTSIDE_CHAIN

Caused by RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO (Stage 6 visit 2, 2026-11-20). Class HARNESS (presumed,
unproven). sc_fire_sense decides no bar.

## spec

`fire_sense_hungry_eats_first` (chain fire_sense) FAILED in both visit-2 runs: jobs ["BeatFire",
"RM_PyreStepAwayFromFire", "BeatFire", "RM_PyreStepAwayFromFire", "Wait_MaintainPosture", "Skygaze"], then
["GotoWander"]; no Ingest (evidence/pv2_fire_sense.json, the second run overwrote the first; the first is in
Transient logs only). A clean-scene copy of the row
(design/concepts/Pyrelands/version/in_game/visit_2/scripts/hungry_exp.py, evidence/hungry_exp.json; same pad, offsets,
meal, Food 0.08, Firefighter 1, home area) ate first in both arms: no fire ["Ingest", "GotoWander"]; fire ["Ingest",
"BeatFire", ...]; Food 0.08 read back after the set, 0.91 at the end. So RM_PyreEatBeforeFireDuty works on this build in
a clean scene. What differs inside the chain is not found: the heat guard only removes Heatstroke, the row-start top-up
runs before H exists, and no governor code touches Food. Unread in the chain: H's Food just after the set and after the
first wait.

## verify

Run the chain with H's Food read after the set and at each poll.

## criteria

- The chain row and the clean scene agree, and the cause of any difference is named.

## Acceptance test

Live only. Red now: `... cli.py run ... --chains fire_sense` reads fire_sense_hungry_eats_first FAIL (2 of 2 runs,
2026-11-20). Green: the row PASS, or FAIL with H's Food reads showing H urgently hungry and not eating (then MOD).

## refs

file: src/RimMandrake/Pyrelands/validation.py
file: src/RimMandrake/Pyrelands/Defs/ThinkTreeDefs/RM_PyreEatBeforeFireDuty.xml
