#!/usr/bin/env python3
"""publish_line_measure.py: for recent commits on origin/main that changed pipeline files, which pipeline tests the
door would select (publish.pipeline_selection), and why each one stays after the read records (door_reads.relation):
touched, no record, ran another version of a .py, other unknown, or left out. One row per commit, then the totals.
Read-only: it reads the door-reads store and git; it runs no test. Used by publish_line.md (same folder).

    python3 design/specs/2026-11-26-slow-actions/publish_line_measure.py [N commits, default 25]
"""
import collections
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
import publish as P  # noqa: E402
import door_reads as DR  # noqa: E402


def git(*a):
    return subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True, check=True).stdout


def main(n=25):
    cfg = P.load_tests_cfg() if hasattr(P, "load_tests_cfg") else json.load(
        open(os.path.join(ROOT, "src", "RimMandrake", "Utils", "pipeline_tests.json")))
    store = os.path.join(P.RM_ROOT, P.DOOR_READS)
    shas = [s for s in git("log", "--format=%H %s", "-400", "origin/main").splitlines() if " ledger:" not in s
            and " conversations:" not in s][:n * 3]
    tot = collections.Counter()
    rows = 0
    for line in shas:
        sha, subj = line.split(" ", 1)
        changed = [p for p in git("diff", "--name-only", sha + "^", sha).splitlines() if p]
        sel = P.pipeline_selection(ROOT, changed, cfg)
        if not sel:
            continue
        blobs = DR.tree_blobs(lambda *a: subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True), sha + "^")
        c = collections.Counter()
        for t in sel:
            ans, why = DR.relation(store, t["test"], set(changed), blobs)
            k = ("touched" if ans == "touched" else "left out" if ans == "not touched" else
                 "no record" if why.startswith("no record") else "another version" if "another version" in why else
                 "other unknown")
            c[k] += 1
        tot.update(c)
        tot["selected"] += len(sel)
        rows += 1
        print("%s %4d selected: %s | %s" % (sha[:10], len(sel), dict(c), subj[:70]))
        if rows >= n:
            break
    print("TOTAL over %d commits: %s" % (rows, dict(tot)))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 25)
