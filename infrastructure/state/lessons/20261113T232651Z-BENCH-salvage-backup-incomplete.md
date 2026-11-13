The 2026-11-13 wrapup-salvage backup (/mnt/d/ClaudeWork/backups/rimmandrake/wrapup-salvage-20261113) does not cover ralph_flowworks or ralph_graffiti at all, has an empty commits/ for ralph_gss and an older HEAD for ralph_pyrelands. 'commits on no remote' in the restart alarm counts commits past origin/main, not unpushed ones: flowworks/gss/pyrelands sit on GitHub ralph/* branches; only graffiti HEAD (1 commit) and the dirty files (flowworks 4, graffiti 27) exist nowhere else. Check git ls-remote before calling a backup complete.
item: NONE
home: NONE
