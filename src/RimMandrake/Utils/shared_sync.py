#!/usr/bin/env python3
"""RETIRED 2026-10-02 — design/RimMandrake/git_workflow_plan_2026-10-01.md §2.6.

It existed only to move a multi-writer shared tree, which no longer exists: each seat works in
its own ext4 clone (/home/mandrake/rm/<seat>) with plain git, and /mnt/d becomes a read-only
mirror. Use `./publish -m "..." <paths>` (commit + pull --rebase + push) from your clone.
"""
import sys

if __name__ == "__main__":
    print("shared_sync.py is RETIRED (git_workflow_plan_2026-10-01.md §2.6). Work in your seat clone "
          "/home/mandrake/rm/<seat> and land with `./publish -m \"...\" <paths>`, or plain "
          "`git pull --rebase origin main && git push origin HEAD:main`.", file=sys.stderr)
    sys.exit(1)
