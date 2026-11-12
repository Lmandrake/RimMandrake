A loop that execs a private copy of itself (loop.run.sh) never adopts a new loop.sh: only wc.py and the *.md briefs it re-reads each round reach a running unit. Fixes for running loops must ride wc.py/briefs (the PRE-PICKED shortlist bridge); loop.sh now re-execs itself at a round boundary when the clone's copy differs, but only loops started on it.
item: NONE
home: infrastructure/whittle_claude/loop.sh
