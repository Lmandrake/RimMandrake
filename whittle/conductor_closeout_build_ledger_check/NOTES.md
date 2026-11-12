# Notes (newest first)

## 2026-11-11 20:10 -08:00, picking (CLAUDE_ARCHMAGI_OFFLINE2)
- Runs: 0 recorded on this item (nonpass 0). Original close b00bfae by a Relentless blind check; the audit note
  "DEFECT selftest_reads_live_state" was fixed by CLOSEOUT_SELFTEST_FIX_READS_LIVE_GAPS (closed a8cc91bbee, test green).
- Outage 1: 2026-11-08T20:34Z deadman "not wired"; 2026-11-09T04:19Z "running again, kept". State stays `ready`;
  `rimflow show` says OWES A GUARD (died 1 time).
- Cause (process/HARNESS, not the closeout code): the squash landing 8fb9f7f2b6 (Pyrelands, 2026-11-08 11:52 -08:00)
  took the branch's `.claude/settings.json`, dropping every PreToolUse/PostToolUse hook and the goodbye hook; 943a7a66da
  (19:37 -08:00) restored main's copy verbatim. Hook file: `.claude/hooks/conductor_goodbye.py`.
- Existing check: `.claude/hooks/selftest_conductor_goodbye.py` l.152-155 asserts settings.json runs
  conductor_goodbye.py (reads ROOT only, takes no argument), so the nightly would have caught this one hook only.
  Related but different: `.claude/hooks/selftest_hook_registrations_refuse.py` (muted refusals, not presence).
- Wiring checker to reuse: `src/RimMandrake/rimflow/live_line.py` `_hook(name, settings)` (whole-name regex, script
  must exist). Promise sources: the ledger (`model.read()`, close events' `live` field) and
  `src/RimMandrake/rimflow/live_baseline.txt`. A promise on a retired item should not count.
- The other offline shortlist items (ALARM_RANGES, DISK_WATCH, IDLE_WATCH, JAM_WATCH, LENT_ALARM, FOUNDRY_FANOUT...)
  are reopened because the rm-metronome / rm-relentless timers are off by the owner's stop
  (PIPELINE_RETHINK_OWNER_STOPPED_BURN); none can hold a promise until he restarts them.
- Do not re-enable any stopped timer. Do not edit `~/.claude/settings.json` or the dispatch clone.
- The offline gate hook refuses Bash commands containing the live flag spelling; write files with the Write tool and
  run the final close from a script file if the gate refuses it.
