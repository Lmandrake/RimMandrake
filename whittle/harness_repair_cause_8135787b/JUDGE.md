# Judge: HARNESS_REPAIR_CAUSE_8135787B

Judged 2026-11-11 by a fresh judge (CLAUDE_STEVEDESKTOP_OFFLINE6 judge pass). I read STATEMENT.md, NOTES.md, the item file and evidence/, re-ran both retest commands, and did not read DONE.md or BROADEN.md.

## Statement lines

1. **The class is recorded on this item (note) with its evidence before the fix: TRUE.**
   `rimflow show` has the ledger note at 2026-11-12T05:44:50Z, "CLASS: HARNESS (with a SITE trigger)". It cites the evidence: the sighting's modcheck.log lines 7-22, with a copy in `evidence/sighting_sprinkler_live_tail.txt`. That copy shows sprinkler_live rc=1 after 57 s, with a "starving" trigger on Harley inside safe_advance. The note also names the harness code it blames (validation_core.site_calm, retest.split_rows) and rules out ENVIRONMENT and MOD. The first fix commit, fc90cd1ff5, is dated 2026-11-11T21:48:13-08:00, which is 05:48:13Z, so the note came first. The earliest after-fix artifact, at 05:46:29Z, also comes after the note.

2. **`retest.py passed <re-run job> HARNESS_REPAIR_CAUSE_8135787B` exits 0 on a job run at the fix's sha: FALSE.**
   The re-run J20261112T060227Z-995858 was queued at 780f797c48 (`evidence/rerun_submit_forwarded.txt`). It has not run. I re-ran the check myself and got `UNMEASURED: J20261112T060227Z-995858 has no result yet`, exit=2. The Archmagi lane is paused until 2026-11-19T03:23Z (`evidence/negative_control_final.txt`). To settle this line, the job has to finish and the same command has to exit 0.

3. **The negative control exits 1: TRUE.**
   I re-ran `retest.py passed J20261106T011656Z-15b610 HARNESS_REPAIR_CAUSE_8135787B` at HEAD. It gave exit=1 with "still carries the cause: driver_undelivered: ...". This matches `evidence/negative_control_after_fix.txt` and `negative_control_final.txt`.

## Notes on the evidence

- The selftests (`selftests_after_fix.txt`, 10/10 green) and the mutation checks (`mutation_checks.txt`) show that the new tests catch the old behaviour. They are offline only. No live run anywhere shows that site_calm's feeding stops the starving GovernorStop on a long-used map. That is exactly what the re-run would show.
- In the mutation_checks "restore the old UPSTREAM regex" block, the selftest reports "1 FAILED" but `rc=0`. Either the runner's exit code is not wired, or rc was captured from the wrong command. It is worth a look, but it does not change the verdict.
- The fix makes site_calm feed any colonist whose Food is below 0.9. This is a staging fix (SITE), not a heal of the check. It is still a judgment call whether 0.9 is broader than the fault needs. The re-run is what will show it does not hide a real mod-side starvation.

The main criterion, a verdict from the re-run, has not been met. The item is offline-complete only and waits on the paused lane.

would show: no
