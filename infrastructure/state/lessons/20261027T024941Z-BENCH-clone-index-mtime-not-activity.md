A clone's .git/index mtime is not evidence of work: any read-only 'git status' (another agent's sweep, or the checker itself) refreshes it. leftovers.py first read all 66 scratch clones as 'active < 2 d' from index mtime; HEAD + logs/HEAD mtimes (plus porcelain status for dirty work, GIT_OPTIONAL_LOCKS=0 on every read) gave the true picture (2 of 66 old+pushed).
home: git-efficiency
