# RIMMANDRAKE_FORECAST_ON_SHARED_PLANNER_DROPIN_MIRROR_DEADMAN

## spec
Slice 4 of `03-merged.md` section 5: `pipe next [30m]` calls the tick's own decide/prioritise/admit from the tree the
live unit runs from (critique 19's stated limit); a systemd prefix drop-in on the live run prefixes (`rm-detached-`,
`rm-role-`) checking a store-written permit file, unreadable store = closed (probed only on `rm-probe-` so far,
02m-remeasure claim 12); a belt exporting `acts` to the repo ledger and `mod_owner_hold.json` as the store's mirror.

## verify
Acceptance test: `python3 -c "import sys; sys.path.insert(0,'src/RimMandrake/rimflow'); import control as C; assert hasattr(C,'forecast') and hasattr(C,'export_acts')" && ls ~/.config/systemd/user/rm-detached-.service.d/  (exit 1 at fb5f65e497: watched 2026-11-18 1:25 PM PST)`

## criteria
The acceptance command above passes, and the builder's new selftest (written first, watched failing) passes.

## refs
file: src/RimMandrake/rimflow/control.py
file: design/specs/2026-11-18-pipeline-control-surface/03-merged.md
