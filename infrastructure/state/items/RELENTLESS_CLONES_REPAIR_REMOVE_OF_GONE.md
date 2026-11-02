# RELENTLESS_CLONES_REPAIR_REMOVE_OF_GONE

relentless.py release path (`shutil.rmtree(c)` after the bundle, about line 1194) journals `alarm remove_failed` when
the clone is already gone: all 77 remove_failed alarms in /home/mandrake/rm/relentless/store/journal.jsonl (measured
2026-11-02) are `[Errno 2] No such file or directory`, 59 of them on 2026-11-01. Its comment says "still present, so
still counted", which is false for ENOENT. The noise buries a real removal failure and floods the daily improvement
packet (agent_improve gather). Fix: treat FileNotFoundError as removed; keep the alarm for any other OSError.
## verify
A selftest_relentless row: release of a missing clone journals no alarm; release of an unremovable one still does.
