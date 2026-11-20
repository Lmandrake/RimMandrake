# RIMMANDRAKE_RESTAGE_FLOWWORKS_REVIEW_SIGNS_OVER_UNBUILT_SCENES

From his FlowWorks walk of 2026-11-20: `design/RimMandrake/validation_holding/flowworks_walk_20261120.md` row #21 (his words, the picture, the station).

## spec

`src/RimMandrake/FlowWorks/northstar/owner_review_stage.py` signs scenes it did not build (staging log `design/concepts/FlowWorks/version/in_game/visit_2/evidence/owner_review_stage_full.log`): 11 sluice "held open" reads closed; 17 "0.2 m" is 0.5 m holes with 0.5 m of water; 24-27 the four looks were never picked (`objects_sheet.choose_look(run=True)` wants a "whole connected run" row, `northstar/objects_sheet.py:175`, which the pipe menu lost in PIPE_STYLE_PRUNE_WHOLE_RUN_ONLY, `Source/Machinery/PipeLook.cs:181`); 40-41 the trench shooter has no ranged weapon; 59-60 the jetties are dragged 4 squares out (`owner_review_stage.py:873`) past `JettyMaxCells` 2 (`Source/RM_SuspensionMath.cs:687`) and refused, and `proof()` (`:395-402`) notes only replies that start REFUSED, so "JETTY ok=False" went unseen [measured]. His request: two water heights across the closed sluices at 9 and 10, to open and watch level.

## verify

Offline first (selftest_owner_review_stage.py, mock game), then a restage on the calm site when the game is free.

## criteria

Acceptance test: selftest_owner_review_stage.py gains cases for a jetty drag within JettyMaxCells, an "ok=False" proof reply landing in NOTES, and choose_look picking a bare "<Look>" row (red on today's script: not yet run); the restaged map reads 11 open=True, 17 water 0.2 m, 24-27 four looks read back, 40-41 cover proof run, 59-60 jetty parts > 0, 9-10 two levels across the gate.
