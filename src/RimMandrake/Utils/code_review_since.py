#!/usr/bin/env python3
"""code_review_since.py: was each file fully reviewed CLEAN after given commits?

    python3 src/RimMandrake/Utils/code_review_since.py --after <sha> [--after <sha> ...] <path> [<path> ...]

`code_review_status.py check` answers "is the file on disk CLEAN now". On a file
other items keep editing, "now" never holds still, so a review item that owes
"a full-file review after commits X, Y" cannot be proven with it. This answers
that question instead, from history:

    PASS when some `clean` mark in infrastructure/state/code_review/*.jsonl
    carries the sha256 of the path's bytes at a commit C in HEAD's history
    that has every --after commit as an ancestor (C may be an --after itself).

Candidate commits are the ones that touched the path (full history, merges
included) plus every --after and HEAD, all filtered to "descends from every
--after". Exit 0 when every path passes, 1 when any fails, 2 on a usage or
git error. Read-only.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
REC_DIR = os.path.join(ROOT, "infrastructure", "state", "code_review")


def git(*args, inp=None):
    r = subprocess.run(["git", "-C", ROOT] + list(args), input=inp,
                       capture_output=True)
    if r.returncode != 0:
        sys.stderr.write("FAIL: git %s: %s" % (" ".join(args), r.stderr.decode(errors="replace")))
        sys.exit(2)
    return r.stdout


def clean_marks():
    """{(path, sha256): [record, ...]} for every clean mark in every shard."""
    out = {}
    for n in sorted(os.listdir(REC_DIR)):
        if not n.endswith(".jsonl"):
            continue
        with open(os.path.join(REC_DIR, n), encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith(("<<<<<<<", "=======", ">>>>>>>")):
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("verdict") == "clean" and rec.get("sha256") and rec.get("path"):
                    out.setdefault((rec["path"], rec["sha256"]), []).append(rec)
    return out


def descendants_of_all(afters):
    """Commits reachable from HEAD that have every `after` as an ancestor."""
    sets = []
    for a in afters:
        s = set(git("rev-list", "--ancestry-path", a + "..HEAD").decode().split())
        s.add(a)
        sets.append(s)
    common = set.intersection(*sets)
    # an `after` that is not itself a descendant of the others drops out here
    return common


def blob_sha256(commit, path):
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (commit, path)],
                       capture_output=True)
    if r.returncode != 0:
        return None  # path absent at that commit
    return hashlib.sha256(r.stdout).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--after", action="append", required=True,
                    help="a commit the review must postdate (repeatable)")
    ap.add_argument("paths", nargs="+")
    a = ap.parse_args()
    afters = [git("rev-parse", "--verify", x + "^{commit}").decode().strip() for x in a.after]
    for x in afters:
        if subprocess.run(["git", "-C", ROOT, "merge-base", "--is-ancestor", x, "HEAD"]).returncode:
            print("FAIL: --after %s is not in HEAD's history" % x[:10])
            return 2
    desc = descendants_of_all(afters)
    if not desc:
        print("FAIL: no commit descends from every --after")
        return 2
    marks = clean_marks()
    bad = 0
    for path in a.paths:
        touched = git("rev-list", "--full-history", "HEAD", "--", path).decode().split()
        # a merge TREESAME to its side parent drops out of `touched`; the
        # afters and HEAD cover the content such a merge brought in
        head = git("rev-parse", "HEAD").decode().strip()
        cands = [c for c in touched if c in desc] + [x for x in afters if x in desc] + [head]
        hit = None
        seen = set()
        for c in cands:
            h = blob_sha256(c, path)
            if h is None or h in seen:
                continue
            seen.add(h)
            recs = marks.get((path, h))
            if recs:
                hit = (c, recs[-1])
                break
        if hit:
            c, rec = hit
            who = (rec.get("reviewer") or {}).get("job") or (rec.get("reviewer") or {}).get("kind") or "?"
            print("PASS  %s  (content at %s, clean mark %s by %s)" % (path, c[:10], rec.get("ts", "?"), who))
        else:
            bad += 1
            print("FAIL  %s  (no clean mark on its content at any of %d commit(s) after the --after set)"
                  % (path, len(seen)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
