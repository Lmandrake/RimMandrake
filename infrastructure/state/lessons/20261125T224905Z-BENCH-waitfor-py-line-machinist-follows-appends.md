waitfor.py line (Machinist) follows appends to one open file: it never sees a match in a file that git replaced (a checkout or fast-forward writes a new inode), even with --from-start. Measured 2026-11-25: it timed out after 50 min watching /home/mandrake/rm/dispatch/src/RimMandrake/rimflow/work_bundle_monitor.py for a def that the deploy had held for most of that time. To wait for a commit to reach a clone, test git merge-base --is-ancestor <sha> HEAD instead.
item: RIMMANDRAKE_BUILD_TEMPORARY_WORK_BUNDLE_MONITOR_DAILY
home: infrastructure/state/facts/tool_traps.md
