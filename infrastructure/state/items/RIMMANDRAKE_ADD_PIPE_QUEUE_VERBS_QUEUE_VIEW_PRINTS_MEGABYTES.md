# RIMMANDRAKE_ADD_PIPE_QUEUE_VERBS_QUEUE_VIEW_PRINTS_MEGABYTES

## spec
Slice 3 of `03-merged.md` section 5: `pipe queue [top|bottom|move|drop|add]` in the control store (membership and
order separate, critique 23), read by the tick's ordering; compact defaults for `rimflow queue CONDUCTOR` (printed
1,569,453 bytes, measured 2026-11-18 in `02m-remeasure.md`) and `detached_helper.py status` (82,663 bytes), running and
today only, with `--full`.

## verify
Acceptance test: `RM_CONTROL_DB=/tmp/acc3.db python3 src/RimMandrake/rimflow/control.py queue top Graffiti --why t && test $(python3 src/RimMandrake/rimflow/cli.py queue CONDUCTOR | wc -c) -lt 20000  (exit non-zero at fb5f65e497: watched 2026-11-18 1:25 PM PST)`

## criteria
The acceptance command above passes, and the builder's new selftest (written first, watched failing) passes.

## refs
file: src/RimMandrake/rimflow/control.py
file: design/specs/2026-11-18-pipeline-control-surface/03-merged.md
