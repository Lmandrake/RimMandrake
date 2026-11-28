# WB-pipeline-read-utils-20261128-092119 state

20 reader tickets, 23 files. Plan: six parallel fresh readers (Opus) by file group, each reads file + boundary page + tests
once by src/RimMandrake/rimflow/roles/code_review.md, fixes a Problem test-first (then the file is flagged), else the file
is marked READ-CLEAN; then each covered ticket closes on its `fresh_reader.py holds` check.

Groups:
- A testq: steward.py, testq.py, steve_lane_sweep.py, lane_ticket.py
- B ops: testq/fault_monitor.py, ops_core/streams.py, restart_reconcile.py, scratch_reap.py
- C maturation: maturation_now.py, maturation_nonmod.py, owner_queue.py
- D control: rimflow/control.py, rimflow/list_dispatch.json, boundary_check.py, failure_counter_list.json, could_not_look_allowlist.json
- E art+deploy: art/artledger.py, deploy_listing.py, deploy_def_guard.py, deploy_custom_mods.py
- F launch+accounts: account_plan_sweep.py, launch_behind.py, focus_probe.py

Done (2026-11-28): all 23 files read once by six fresh readers.
- Problems fixed test first, then the file FLAGGED: control.py at 29358189ee58 (pipe off unit:<u> blocked nothing; same-day
  re-hold after a lift did not hold); testq.py, fault_monitor.py, scratch_reap.py test gaps at f20d80603709; launch_behind.py,
  focus_probe.py at 60634db0dbe5 (real start_guard untested; old-game hand-off read GREEN).
- The other 17 files: READ-CLEAN, marked at 60634db0db.
- Polish lines written beside each page; launch-behind page line on RmWin.Start corrected to WMI.
Next: close the 20 reader tickets on their holds checks.
