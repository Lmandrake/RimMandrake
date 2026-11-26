# Polish: maturation dispatch reads

- `src/RimMandrake/rimflow/maturation_dispatch.py` lines 194 and 3973: the comments call `CLONE_STALE_MIN = 5.0` the
  OPS_DISPATCH_CLONE_BEHIND_UNSTICK alarm's threshold (`> 5`). Since 254f69e4e5 the alarm line is 15 min
  (`ops_watch_rules.json`); 5 min is only the tick's own launch stop. Correct both comments at the file's next change
  (not done 2026-11-26: the live run of RIMMANDRAKE_UNSTICK_TICK_CLONE_TWO_LINES_BLOCK_EVERY_PULL held the file).
