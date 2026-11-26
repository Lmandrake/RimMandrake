# polish: scratch_reap.py (beside boundary.md)

- `src/RimMandrake/Utils/scratch_reap.py` act(): each DELETE or ARCHIVE row calls Ctx.refresh(), which makes a new
  Live(now), a full scan of /proc. At nice 19 under host load 27 to 38 on 14 cores, one row took 819 s (a 3.8 KB
  session) and a 0-byte row took 187 s (rm-scratch-reap run 2026-11-26 11:02 PST: 3,660 s, apply 2,199 s for 46 rows,
  6 min of CPU). A Live that is reused for a few seconds, or a scan of only the processes that could hold that path,
  would cut this. risk: none to any promise today (61 min against the 6 h line); a heavier load or more rows would make
  the hourly runs back to back again.
