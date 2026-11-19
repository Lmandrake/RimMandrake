# RIMMANDRAKE_SEED_SCENE_LOOK_CALIBRATION_BRIM_PIT_PAIR

## spec
Child of `RIMMANDRAKE_FOLD_FRAME_JUDGE_INTO_PRELOOK`. `scene_look_judge_brief` is UNTESTED in
`infrastructure/state/judge_calibration.json` with no `free_check` and no `model_check` (read
`python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --no-run`, 2026-11-18), so no edit of the brief can ever
become CALIBRATED and its refusals never bind. Give it planted cases and a `model_check`, on the pattern of
`src/RimMandrake/rimflow/art_calibration.py` (art_judge_brief, CALIBRATED on 12 planted cases).

Planted cases that exist today, with the owner's own verdict (`D:\ClaudeWork\rimmandrake\conductor\scene_judge_20261112\`,
RESULT.md; owner 2026-11-12: *"Looks great at 1m water depth, but 2m water depth put the northern ladder behind the pit
wall art for some reason, silly looking."*):
- `crop_pit6.png` (the brim pit): pass 1 must answer ODD or WRONG; pass 2 with the bar "the north ladder is drawn in
  front of the pit wall, down to the water" must answer NO.
- `crop_pit3.png` (the 1 m pit, which he called correct): pass 2 with the same bar must answer YES. Pass 1 may raise a
  doubt (the 2026-11-12 naive judges did, on this cell): record it, do not plant it.
Copy the two crops into the repo's calibration corpus (small PNGs) so the check never depends on the scratch drive.

## criteria
- `model_check` runs pass 1 and pass 2 through `judge_cli.py`'s own prompts (OPEN_PROMPT, judge._PROMPT) on both crops;
  the row turns CALIBRATED only when every planted case ran and came out as planted, both ways, and FAILED otherwise.
  A judge that could not run is UNMEASURED for the case, never a pass.
- Acceptance test (offline): a selftest with a mock runner that answers the planted pair right (CALIBRATED), one wrong
  answer (FAILED), and one dead call (not CALIBRATED); watched failing on the base (no model_check registered).

## verify
- `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --model scene_look_judge_brief` (spends: four `claude -p`
  calls) prints CALIBRATED with the case count; `calibrate --no-run` then shows it.

## refs
file: design/RimMandrake/scene_look_judge_brief.md
file: src/RimMandrake/Utils/northstar_driver/judge_cli.py
file: src/RimMandrake/rimflow/art_calibration.py
file: infrastructure/state/judge_calibration.json
