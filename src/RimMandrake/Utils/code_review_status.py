#!/usr/bin/env python3
"""code_review_status.py — the "clean or dirty" ledger CLAUDE.md's
"Code isn't clean until a review says so" policy actually points at.

A file is CLEAN only if it has an entry here AND zero commits have
touched it since the recorded commit. Anything else — no entry, or any
commit since — is DIRTY. There is no other way to earn CLEAN: fixing a
finding does not clean a file, only a full-file review returning zero
significant findings does, recorded here with `mark-clean`.

    python3 src/RimMandrake/Utils/code_review_status.py check <path> [<path> ...]
    python3 src/RimMandrake/Utils/code_review_status.py mark-clean <path> [--sha <sha>]
    python3 src/RimMandrake/Utils/code_review_status.py list

The log (`infrastructure/state/CODE_REVIEW_STATUS.json`) is owned by this
script — do not hand-edit it, the same convention as the ledger.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
LOG_PATH = os.path.join(ROOT, "infrastructure", "state", "CODE_REVIEW_STATUS.json")


def load():
    if not os.path.isfile(LOG_PATH):
        return {}
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data):
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def repo_rel(path):
    return os.path.relpath(os.path.abspath(path), ROOT).replace(os.sep, "/")


def git(args):
    return subprocess.run(["git"] + args, cwd=ROOT, capture_output=True, text=True)


def commits_since(sha, relpath):
    r = git(["log", "--oneline", f"{sha}..HEAD", "--", relpath])
    if r.returncode != 0:
        return None  # sha doesn't exist / bad ref
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    return lines


def cmd_check(paths):
    data = load()
    any_dirty = False
    for p in paths:
        rel = repo_rel(p)
        entry = data.get(rel)
        if entry is None:
            print(f"DIRTY  {rel}  (never marked clean)")
            any_dirty = True
            continue
        since = commits_since(entry["sha"], rel)
        if since is None:
            print(f"DIRTY  {rel}  (recorded sha {entry['sha']} not found — log is stale)")
            any_dirty = True
        elif len(since) > 0:
            print(f"DIRTY  {rel}  ({len(since)} commit(s) since clean at {entry['sha']} on {entry['date']}):")
            for line in since:
                print(f"         {line}")
            any_dirty = True
        else:
            print(f"CLEAN  {rel}  (clean at {entry['sha']} on {entry['date']})")
    return 1 if any_dirty else 0


def cmd_mark_clean(path, sha):
    rel = repo_rel(path)
    if not os.path.isfile(os.path.join(ROOT, rel)):
        print(f"FAIL: {rel} does not exist under the repo root.", file=sys.stderr)
        return 2
    if sha is None:
        r = git(["rev-parse", "--short", "HEAD"])
        if r.returncode != 0 or not r.stdout.strip():
            print("FAIL: could not resolve HEAD.", file=sys.stderr)
            return 2
        sha = r.stdout.strip()
    # Uncommitted changes to this exact file mean HEAD is not what will actually
    # ship - refuse rather than record a clean mark against a commit that
    # doesn't reflect what was reviewed.
    r = git(["status", "--porcelain", "--", rel])
    if r.stdout.strip():
        print(f"FAIL: {rel} has uncommitted changes. Commit first, then mark-clean.", file=sys.stderr)
        return 2
    r = git(["log", "-1", "--format=%ad", "--date=short", sha])
    date = r.stdout.strip() if r.returncode == 0 else "unknown"
    data = load()
    data[rel] = {"sha": sha, "date": date}
    save(data)
    print(f"CLEAN  {rel}  recorded at {sha} ({date})")
    return 0


def cmd_list():
    data = load()
    if not data:
        print("(empty — nothing has ever been marked clean)")
        return 0
    for rel in sorted(data):
        entry = data[rel]
        since = commits_since(entry["sha"], rel)
        state = "CLEAN" if since is not None and len(since) == 0 else "DIRTY (edited since)"
        print(f"{state:22s} {rel}  ({entry['sha']}, {entry['date']})")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_check = sub.add_parser("check", help="report CLEAN/DIRTY for one or more paths")
    p_check.add_argument("paths", nargs="+")

    p_mark = sub.add_parser("mark-clean", help="record a path as reviewed clean at a commit")
    p_mark.add_argument("path")
    p_mark.add_argument("--sha", default=None, help="defaults to current HEAD")

    sub.add_parser("list", help="show every recorded entry and its current state")

    args = ap.parse_args()
    if args.cmd == "check":
        sys.exit(cmd_check(args.paths))
    elif args.cmd == "mark-clean":
        sys.exit(cmd_mark_clean(args.path, args.sha))
    elif args.cmd == "list":
        sys.exit(cmd_list())


if __name__ == "__main__":
    main()
