# FOUNTAIN_ART_FINISH_WAITS_FOR_A_FAVOURITE — finish the picked fountain design's art

Parent: `FOUNTAIN_LOOP_BUILD_PUMPS_ITS_OWN_RAIN`. Candidates A (tiered bowl), B (spout pillar), C (cairn spring) are on
the pre-reviewed sheet `Transient/fountain_20261023/fountain_v1_candidates_sheet_2026-10-23.html` (pinned; GPT round
and fixes in `Transient/fountain_20261023/gpt/record.md`). The pick may be delegated to a judge agent
(`design/RimMandrake/art_judge_brief.md`, logged `--why "delegated: art …"`).

## spec
- From the picked master (`Transient/fountain_20261023/raw/<X>_v2.png`, 1024x1536): a DRY variant by edit (same
  stone, empty basin floor visible, no falling water) — the state drawn when the fountain is off / backed up / dry.
- Three overlay frames of the moving water only (curtains/arcs/jet + spillway sheet), real alpha, registered on the
  same canvas, cycled by a `Graphic_Flicker`-style graphic while Playing (`RM_FireFrames` pattern).
- Ship each at 256x384 with `src/RimMandrake/FlowWorks/art_source/Fountain/ship.py`; camera check with
  `basin_ratio.py`; install through `art.py install` only when the `RM_Fountain` def exists.

## verify
- dry + frames pass `validate_sprite.py --describe` (alpha, corners, fringe) and register: the frame stack over the dry
  base reproduces the playing picture (overlay diff check at 32 px/cell).
- a judge agent (fresh Opus) reads the frames looping at true scale before any human sees them.
