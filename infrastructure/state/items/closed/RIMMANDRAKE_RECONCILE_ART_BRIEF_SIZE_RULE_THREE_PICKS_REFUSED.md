# RIMMANDRAKE_RECONCILE_ART_BRIEF_SIZE_RULE_THREE_PICKS_REFUSED

## spec

The first real calibration of the art judge brief (`refusal_contract.py calibrate --model art_judge_brief`, 2026-11-17,
results in `infrastructure/state/judge_calibration.json` art_judge_brief.last_run) read FAILED: 10 of 13 planted cases
came out as planted. All 6 owner-refused pictures were refused, his kept Gawpsack passed (E3), and the north-from-south
plant was refused on C1 with a rear-view redraw. Three pictures he picked were refused:

- regress_RM_DecayDrake_r2: D4 on all three facings, "three detached mounds of bubbling yellow mash on the ground around the feet".
  He PICKED r2 (criteria_ledger CL-035, owner_escalations_cauldron 2026-10-24).
- regress_RM_Durrok_r2: C2, south drawn much larger than north (opaque bbox 992x753 vs 727x687). He pooled r2 (CL-021),
  over the pipeline's F_SIZE_JUMP REGEN.
- regress_RM_Gawpsack_live: C2, north body 202x135 px vs south 158x123. He KEPT it (CL-030).

C2 ("one facing looking huge or small is REDO", source `rimworld-sprite-facings`) and D4 ("no backdrop, halo, ground
shadow or scenery", source `generating-rimworld-sprites`) carry no Owner line, and his picks contradict them on the
size jumps (two of the three) and on ground mash he accepted as part of the creature. That is a criterion question, not an
artist's rework: route it to the neutral criteria fixer (`refusal_contract.py repair`, `roles/criteria_fixer.md`), whose
diffguard decides whether a clarification (for example C2 measured at play zoom or within a stated tolerance; D4 naming
ground props the description asks for) can pass his picks without passing his refusals. Loosening a line he ruled
stays his. Found by RIMMANDRAKE_BUILD_ART_BRIEF_CALIBRATION_NOTHING_TO_RUN.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --model art_judge_brief` (spends, about
1.7M weighted tokens on Opus) writes `cases` "13 planted case(s) ran and came out as planted", and `calibrate --no-run`
reads `art_judge_brief  CALIBRATED`. Watched failing 2026-11-17: FAILED, came out the other way on the three cases above.

## criteria

- The brief's C2 and D4 lines are settled by the criteria fixer or by him, with his three picks as evidence.
- The brief reads CALIBRATED at its new text, all 13 cases as planted.

## correction 2026-11-19

His 2026-11-17 "Correct, not size." answered the question "did you refuse Peeper r2 because of its facing size?": he
purged it because he no longer wanted that animal. It was never a ruling about facing size, and the C2 rewording this
item closed on (a6deeef803) is undone. Owner 2026-11-19 5:40 AM PST: "Allow the Judge to bounce incorrectly sized
creatures". C2 refuses a facing size fault again; Peeper r2 is a planted refuse case again (C2 refuses it on size);
his Durrok r2 and Gawpsack picks were style calls ("I was undoubtedly expressing style decisions.") and are `taste`
rows, no planted case, because C2 may refuse both on size. The brief reads UNTESTED until
`refusal_contract.py calibrate --model art_judge_brief` runs on the new text (11 planted cases).

## refs

file: design/RimMandrake/art_judge_brief.md
file: src/RimMandrake/rimflow/art_calibration.py
file: infrastructure/state/judge_calibration.json
file: infrastructure/state/art_eval/criteria_ledger.jsonl
