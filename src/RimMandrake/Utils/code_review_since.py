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

Every such commit is checked (one batched `git cat-file` per path; distinct
blobs hashed once), so no history simplification can hide a reviewed state. Exit 0 when every path passes, 1 when any fails, 2 on a usage or
git error. Read-only.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
HEX = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
# replacement refs would let `cat-file` hand back other bytes than the tree holds
GIT_ENV = dict(os.environ, GIT_NO_REPLACE_OBJECTS="1")
REC_DIR = os.path.join(ROOT, "infrastructure", "state", "code_review")


def git(*args, inp=None):
    r = subprocess.run(["git", "-C", ROOT] + list(args), input=inp,
                       capture_output=True, env=GIT_ENV)
    if r.returncode != 0:
        sys.stderr.write("FAIL: git %s: %s" % (" ".join(args), r.stderr.decode(errors="replace")))
        sys.exit(2)
    return r.stdout


def clean_marks():
    """{(path, sha256): [record, ...]} for every clean mark in every shard."""
    out = {}
    try:
        names = sorted(os.listdir(REC_DIR))
    except FileNotFoundError:
        return out  # no ledger yet: nothing is clean
    for n in names:
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
                if not isinstance(rec, dict):
                    continue
                if (rec.get("verdict") == "clean" and isinstance(rec.get("sha256"), str)
                        and isinstance(rec.get("path"), str)):
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


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--after", action="append", required=True,
                    help="a commit the review must postdate (repeatable)")
    ap.add_argument("paths", nargs="+")
    a = ap.parse_args()
    paths = []
    for p in a.paths:  # ledger keys are repo-relative, '/'-separated
        try:
            rel = os.path.relpath(os.path.abspath(p), ROOT).replace(os.sep, "/")
        except ValueError:  # another Windows drive
            rel = ".."
        if "\n" in p or "\r" in p:
            print("FAIL: a path with a line break cannot go through git's line protocol: %r" % p)
            return 2
        if rel == ".." or rel.startswith("../"):
            print("FAIL: %s is outside the repository" % p)
            return 2
        paths.append(rel)
    afters = [git("rev-parse", "--verify", x + "^{commit}").decode().strip() for x in a.after]
    for x in afters:
        if subprocess.run(["git", "-C", ROOT, "merge-base", "--is-ancestor", x, "HEAD"], env=GIT_ENV).returncode:
            print("FAIL: --after %s is not in HEAD's history" % x[:10])
            return 2
    desc = descendants_of_all(afters)
    if not desc:
        print("FAIL: no commit descends from every --after")
        return 2
    marks = clean_marks()
    bad = 0
    for path in paths:
        # every descendant's blob for this path, one batched call; distinct
        # blobs only (the same bytes sit at most of these commits)
        spec = "".join("%s:%s\n" % (c, path) for c in sorted(desc)).encode()
        blobs = {}  # blob id -> one commit holding it ("<id> missing" lines skip)
        for c, line in zip(sorted(desc), git("cat-file", "--batch-check=%(objectname) %(objecttype)", inp=spec).decode().splitlines()):
            f = line.split(" ")
            # a hit is exactly "<hex id> blob"; a miss echoes the query, then "missing"
            if len(f) == 2 and f[1] == "blob" and HEX.fullmatch(f[0]):
                blobs.setdefault(f[0], c)
        hit = None
        for blob, c in blobs.items():
            h = hashlib.sha256(git("cat-file", "blob", blob)).hexdigest()
            recs = marks.get((path, h))
            if recs:
                hit = (c, recs[-1])
                break
        if hit:
            c, rec = hit
            rv = rec.get("reviewer") if isinstance(rec.get("reviewer"), dict) else {}
            who = rv.get("job") or rv.get("kind") or "?"
            print("PASS  %s  (content at %s, clean mark %s by %s)" % (path, c[:10], rec.get("ts", "?"), who))
        else:
            bad += 1
            print("FAIL  %s  (no clean mark on any of its %d distinct version(s) after the --after set)"
                  % (path, len(blobs)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
