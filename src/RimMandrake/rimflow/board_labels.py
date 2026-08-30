#!/usr/bin/env python3
"""board_labels.py — push the INFERRED effort/importance tiers onto the mirrored
GitHub issues as labels, so they're visible and filterable on GitHub itself, not
only in tickets_board.html.

Additive only: never touches the seat:/needs:/state:blocked labels github_mirror.py
already owns, never edits an issue's body or title, and only labels issues that are
still OPEN on GitHub (closed/historical issues are left alone — no need to keep
relabeling something already done).

Default is DRY RUN. --apply executes via `gh`.
"""
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from board_viz import build_tickets, GH_REPO

EFFORT_COLORS = {"S": "c5e0d8", "M": "9fd0bd", "L": "5fae5a", "XL": "2f7a3a"}
IMPORTANCE_COLORS = {"low": "e6ddf5", "medium": "b78ae0", "high": "8a4fc9", "critical": "5a2e8f"}


def gh(args, apply_, plan):
    if apply_:
        r = subprocess.run(["gh"] + args, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit("gh %s\nFAILED: %s" % (" ".join(args), r.stderr.strip()))
    plan.append("gh " + " ".join(args))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    tickets = build_tickets()
    plan = []

    for tier, color in EFFORT_COLORS.items():
        gh(["label", "create", "effort:%s" % tier, "-R", GH_REPO, "--color", color,
            "--description", "inferred effort tier (see tickets_board.html)", "--force"],
           args.apply, plan)
    for tier, color in IMPORTANCE_COLORS.items():
        gh(["label", "create", "importance:%s" % tier, "-R", GH_REPO, "--color", color,
            "--description", "inferred importance tier (see tickets_board.html)", "--force"],
           args.apply, plan)

    for t in tickets:
        if not t["issue"] or not t["gh_open"]:
            continue
        gh(["issue", "edit", str(t["issue"]), "-R", GH_REPO,
            "--add-label", "effort:%s" % t["effort"],
            "--add-label", "importance:%s" % t["importance"]],
           args.apply, plan)

    mode = "APPLIED" if args.apply else "DRY RUN — nothing touched"
    print("%s: %d action(s) over %d open mirrored issue(s)" %
          (mode, len(plan), sum(1 for t in tickets if t["issue"] and t["gh_open"])))
    for line in plan:
        print("  " + line)


if __name__ == "__main__":
    main()
