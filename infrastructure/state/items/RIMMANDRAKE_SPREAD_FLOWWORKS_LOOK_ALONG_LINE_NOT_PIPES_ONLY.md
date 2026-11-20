# RIMMANDRAKE_SPREAD_FLOWWORKS_LOOK_ALONG_LINE_NOT_PIPES_ONLY

From his FlowWorks walk of 2026-11-20: `design/RimMandrake/validation_holding/flowworks_walk_20261120.md` row #12 (his words, the picture, the station).

## spec

A look picked on one element of a water line does not spread along the line. The pipe's Choose style restyles only pipes of the same def (`PipeLook.RunOf`, `src/RimMandrake/FlowWorks/Source/Machinery/PipeLook.cs:126,135`); a tank or pump restyles itself or the selected ones (`CompTankLook`, `:254`); the sprinkler head has no look button [measured]. The 2026-10-23 ruling (PIPE_STYLE_PRUNE_WHOLE_RUN_ONLY) covered the pipe run only; machines following the pick is new scope, so check with the Conductor whether it belongs in FlowWorks 0.1.0.

## verify

A tank, pipe, pump, pipe, sprinkler head line; pick Futuristic on one pipe via its button; read each part's current look from its own Choose style menu.

## criteria

Acceptance test: every part of the line reads Futuristic. Red today (tank, pump and head keep their own look), predicted from the code, not yet watched red: the game was his.
