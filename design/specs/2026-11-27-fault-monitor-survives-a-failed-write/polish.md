# Polish: the fault monitor's failed writes
- `src/RimMandrake/Utils/testq/fault_monitor.py` `rerun_job` (`write_json("fault_reruns.json")`, `S.dump` of the pending job), called by `ingest.py:799`. risk: an ENOMEM on the Windows drive in the ingest unit raises out of `ingest_group`, so the quarantined job is not queued again in that run; the guard here covers the tick only.
- `src/RimMandrake/Utils/testq/fault_monitor.py` `quarantine_move` and `release` call `T.move` (`testq.py`), which writes the record to the drive. risk: the same ENOMEM kills the ingest unit between the copy and the delete; whether `T.move` leaves a half-moved record is not measured.
- `src/RimMandrake/Utils/testq/testq.py` `cmd_pause` / `cmd_resume`, called from `fault_monitor.py` `lane_pause`, `lane_resume`, `periodic_reboot`: their file writes are not guarded. risk: an ENOMEM there, inside `step`, kills the tick after the lane was paused and before `fault_state.json` is written, so the next tick finds a pause of ours with no state.

## (fresh read, WB-pipeline-read-utils-20261128-092119, 2026-11-28)
- `src/RimMandrake/Utils/testq/fault_monitor.py` `worker_busy` does not ask Steve2 under `steve2.stop`; no impact today, `steve_running()` still holds the drain.
- `src/RimMandrake/Utils/testq/fault_monitor.py` an OSError from `ensure_dirs`/`_qdir` on the lock path is labelled `fault_monitor.lock`.
- `src/RimMandrake/Utils/testq/fault_monitor.py` `mirror_merge` decides 'nothing new' by equal length; wrong only for a mirror with duplicate or blank lines, which this file never writes.
- `src/RimMandrake/Utils/testq/fault_monitor.py` `state_streak` keeps 30 s of slack. risk: an average timer delay of 10 s or more per tick ends the unit one tick early (AccuracySec=10s).
