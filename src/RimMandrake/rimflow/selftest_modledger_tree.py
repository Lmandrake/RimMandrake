#!/usr/bin/env python3
"""The REAL mod ledgers lint clean: worktree against origin/main (modledger.py lint).

    python3 src/RimMandrake/rimflow/selftest_modledger_tree.py

./publish runs it as a whole-tree check (publish_tree_checks.json), so a hand-edited or stale view, a shard edited in
place, a holder line in a judge's or the owner's shard, a stale fencing token or a finding with no proposed fix is
refused at the door. The refusals themselves are proven on fixtures by selftest_modledger.py; this test only points
the same lint at the tree, and says how many ledgers it saw (0 is a real answer before any mod is backfilled).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modledger as M                                            # noqa: E402

root = M.REPO_ROOT
mods = M.mods_with_ledgers(root)
findings, notes = M.lint(root, None, base="origin/main")
for n in notes:
    print("note: " + n)
for code, path, ln, detail in findings:
    print("FAIL  %s %s:%s %s" % (code, path, ln, detail))
print("modledger tree: %d mod ledger%s (%s), %d finding%s" % (len(mods), "" if len(mods) == 1 else "s",
                                                             ", ".join(mods) or "none yet", len(findings),
                                                             "" if len(findings) == 1 else "s"))
sys.exit(1 if findings else 0)
