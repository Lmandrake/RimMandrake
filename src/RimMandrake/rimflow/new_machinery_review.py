#!/usr/bin/env python3
"""File and launch the blind Opus review of new pipeline machinery."""
import argparse
from fnmatch import fnmatch
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

import fresh_reader as FR
import time_budget

TOOL = "src/RimMandrake/rimflow/new_machinery_review.py"
ROLE = "src/RimMandrake/rimflow/roles/code_review.md"
CONFIG = "src/RimMandrake/Utils/pipeline_tests.json"
PREFIX = "Blind review of new machinery: "
RUN_KEYS = ("RM_ROLE_UNIT", "RM_DETACHED_UNIT", "CLAUDE_CODE_SESSION_ID", "CLAUDE_SESSION_ID", "CODEX_THREAD_ID")
NOT_NOW = "independent: the blind code review belongs to a fresh Opus run that did not write the machinery"


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True,
                          timeout=time_budget.CALL_S).stdout


def additions(root, commits):
    """Find matching paths added by the supplied commits and still on the local origin/main."""
    origin = git(root, "rev-parse", "--verify", "origin/main").strip()
    globs = json.loads(Path(root, CONFIG).read_text(encoding="utf-8"))["pipeline_files"]
    paths = set()
    for commit in commits:
        if not re.fullmatch(r"[0-9a-fA-F]{7,40}", commit):
            raise ValueError(f"expected a published commit SHA, got {commit!r}")
        sha = git(root, "rev-parse", "--verify", f"{commit}^{{commit}}").strip()
        try:
            git(root, "merge-base", "--is-ancestor", sha, origin)
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:
                raise ValueError(f"{commit} is not on origin/main") from e
            raise
        added = git(root, "show", "--format=", "--diff-merges=first-parent", "--no-renames", "--diff-filter=A",
                    "--name-only", "-z", sha, "--")
        paths.update(p for p in added.split("\0") if p and any(fnmatch(p, pattern) for pattern in globs))
    if paths:
        present = git(root, "--literal-pathspecs", "ls-tree", "-rz", "--name-only", origin, "--", *sorted(paths))
        paths.intersection_update(present.split("\0"))
    return sha, sorted(paths)


def _title(it):
    return (it.get("title") if isinstance(it, dict) else getattr(it, "title", None)) or ""


def is_review(it):
    return _title(it).startswith(PREFIX)


def parse_title(title):
    files, separator, writer = title.removeprefix(PREFIX).rpartition(" (written by ")
    if not title.startswith(PREFIX) or not separator or not writer.endswith(")"):
        return [], None
    try:
        paths, names = shlex.split(files), shlex.split(writer[:-1])
    except ValueError:
        return [], None
    return (paths, names[0]) if paths and len(names) == 1 and names[0] else ([], None)


def review_tickets():
    import model
    return {iid for iid, it in model.replay(model.read()).items.items() if is_review(it)}


def landed_refusal(iid, root):
    from detached_helper import origin_check
    return origin_check(iid, repo=root)


def submit(argv, root):
    return subprocess.run(argv, cwd=root, timeout=time_budget.LAUNCH_S).returncode


def file_review(root, commits, maker):
    sha, paths = additions(root, commits)
    owed = FR.owed_paths(sha, paths)
    if not owed:
        print("No review owed for new machinery.")
        return 0
    if not maker or not maker.strip():
        raise ValueError("supply the writing run's identity with --maker")
    iid = f"RIMMANDRAKE_FILE_NEW_MACHINERY_REVIEW_{sha[:10].upper()}_BLIND"
    if iid in review_tickets():
        refusal = landed_refusal(iid, root)
        if refusal:
            print(refusal)
            return 2
        print(f"Already filed: {iid}")
        return 0
    title = f"{PREFIX}{shlex.join(owed)} (written by {shlex.quote(maker)})"
    effect = "cmd:" + shlex.join(["python3", TOOL, "holds", *owed])
    return submit(FR.filing_argv(iid, title, effect, NOT_NOW, "the writing run files its blind machinery review"), root)


def boundaries(paths):
    """Find the pages and their registered tests without running them in the dispatcher."""
    import code_review_status as CRS

    root = Path(CRS.ROOT)
    result = {path: [] for path in paths}
    for page in sorted(root.glob("design/specs/*/boundary.md")):
        try:
            files = CRS.code_files(page)
        except CRS.BC.Unreadable:
            continue
        rel = page.relative_to(root).as_posix()
        for path in files.intersection(result):
            result[path].append((rel, CRS.PAGES.get(rel)))
    return result


def brief_text(iid, it):
    paths, maker = parse_title(_title(it))
    if not paths:
        raise ValueError(f"{iid} does not name its files and writer")
    pages = boundaries(paths)
    rows = []
    for path in paths:
        rows.append(f"- {path}")
        for page, tests in pages[path]:
            rows.append(f"  - {page}. Tests: {tests or 'none registered'}.")
        if not pages[path]:
            rows.append("  - No readable boundary page names this file.")
    files = "\n".join(rows)
    return f"""Blind code review of new pipeline machinery for {iid}.

You are the fresh reader for this first code review.
The writing run was {maker}. Before starting the review, verify that you are in a different run:
    python3 {TOOL} independent {shlex.quote(maker)}
If it refuses, stop and report the refusal.

Read and follow `{ROLE}`. Review these files as they stand on origin/main, against their pages and tests:
{files}
Do not read the diff, the writing run's notes, or its earlier findings.

Check each file with `python3 {TOOL} holds <path>` before reviewing it. Leave out files that already have a
review record. If you cannot read a record, report what failed.
After a clean read, record it with `python3 src/RimMandrake/Utils/code_review_status.py mark-clean <path>`.
Publish the changed review record shard under `infrastructure/state/code_review/` so the lane can read it.
For a significant finding, fix it test first, publish the fix and file its fresh reader. The fresh reader
records that file. Block this item on any fresh-reader tickets that are still open and name them in a
`LEFT OPEN:` note. The lane can close this item when the check holds.

Outcome check: {it['effect']}
"""


def main(argv=None, root=FR.REPO, env=None):
    env = os.environ if env is None else env
    identities = [env[key] for key in RUN_KEYS if env.get(key)]
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    file_cmd = commands.add_parser("file")
    file_cmd.add_argument("commits", metavar="SHA", nargs="+", help="this run's published commits, oldest first")
    file_cmd.add_argument("--maker", default=next(iter(identities), None))
    commands.add_parser("holds").add_argument("paths", nargs="+")
    commands.add_parser("independent").add_argument("maker")
    args = parser.parse_args(argv)
    if args.command == "holds":
        return FR.holds(None, args.paths)
    if args.command == "independent":
        if not identities or args.maker in identities:
            print(f"Refused: this review requires a fresh run distinct from {args.maker}.")
            return 2
        print(f"Independent reviewer: {identities[0]}")
        return 0
    try:
        return file_review(root, args.commits, args.maker)
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        print(f"Could not file the new machinery review: {getattr(e, 'stderr', None) or e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
