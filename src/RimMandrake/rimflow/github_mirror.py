#!/usr/bin/env python3
"""github_mirror.py — one-way mirror of rimflow queue items to GitHub issues.

🔑 The Projects v2 board (github_project.py) is the durable sync of this same
mirror onto a real GitHub project. Run it after `--apply`, or pass
`--apply --with-project` here to chain it in one command.

QUEUE_GITHUB_MIRROR_1 pilot. ⭐ events.jsonl STAYS the truth; GitHub is a
VISUALIZER. Nothing here ever writes the ledger, and nothing in the ledger
ever reads GitHub. Deleting every mirrored issue loses nothing.

Scope, deliberately small:
  - OPEN items (proposed/ready/doing) are mirrored as open issues.
  - An item that goes terminal (done/dropped/superseded) after being mirrored
    gets its issue closed. Historical items never mirrored stay unmirrored —
    a pilot does not need 2,600 events of backfill.
  - Labels: seat:<owner>, needs:<needs>, state:blocked when blocked.
  - Issue title = the item ID; the full one-line ask goes in the body (GitHub
    truncates titles well below our titles' length, and the ID is the name
    the owner ruled queue items carry).

The mirror map (which item is which issue number, and what we last pushed)
lives beside the ledger and is committed — it is provenance, not cache.

Default is DRY RUN: prints the plan, touches nothing. --apply executes via
the `gh` CLI, which must be installed and authenticated (`gh auth login`).
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rimflow import model

REPO = "Lmandrake/RimMaster"
MAP_PATH = os.path.join(model.LEDGER, "github_mirror_map.json")
LABELS = {  # label -> (color, description)
    "seat:BENCH":    ("1d76db", "rimflow: owned by the BENCH window"),
    "seat:FOUNDRY":  ("5319e7", "rimflow: owned by the FOUNDRY window"),
    "seat:OWNER":    ("f9d0c4", "rimflow: held by the owner"),
    "needs:offline": ("0e8a16", "workable with the game down"),
    "needs:deploy":  ("fbca04", "needs a deploy slot"),
    "needs:game-up": ("d93f0b", "needs the game running"),
    "needs:bridge":  ("e99695", "needs the bridge"),
    "needs:harvest": ("c2e0c6", "needs a log harvest"),
    "needs:owner":   ("b60205", "needs the owner"),
    "state:blocked": ("000000", "rimflow says blocked"),
}


def desired_state(item):
    """What the issue for this item should look like."""
    labels = ["seat:%s" % (item.owner or "FOUNDRY"), "needs:%s" % item.needs]
    if item.blocked:
        labels.append("state:blocked")
    body = (item.title or "(no title)") + \
        "\n\n---\n`rimflow` item `%s` — the ledger is the truth; this issue is a mirror. " \
        "Close/claim/drop through `rimflow`, never here." % item.id
    if item.closed_sha:
        body += "\nClosed at `%s`." % item.closed_sha
    if item.superseded_by:
        body += "\nSuperseded by `%s`." % item.superseded_by
    return {
        "title": item.id,
        "body": body,
        "labels": sorted(labels),
        "open": item.open,
    }


def fingerprint(want):
    return hashlib.sha1(json.dumps(want, sort_keys=True).encode()).hexdigest()[:12]


def gh(args, apply_, plan):
    if apply_:
        r = subprocess.run(["gh"] + args, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit("gh %s\nFAILED: %s" % (" ".join(args), r.stderr.strip()))
    plan.append("gh " + " ".join(args))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true",
                    help="execute via gh (default: dry run, print the plan)")
    ap.add_argument("--ensure-labels", action="store_true",
                    help="also create the label set on the repo")
    ap.add_argument("--with-project", action="store_true",
                    help="after applying, also sync the Projects v2 board "
                    "(runs github_project.py --apply)")
    args = ap.parse_args()

    world = model.replay()
    mmap = {}
    if os.path.exists(MAP_PATH):
        with open(MAP_PATH) as f:
            mmap = json.load(f)

    plan = []
    if args.ensure_labels:
        for name, (color, desc) in LABELS.items():
            gh(["label", "create", name, "-R", REPO, "--color", color,
                "--description", desc, "--force"], args.apply, plan)

    for item in sorted(world.items.values(), key=lambda i: i.id):
        want = desired_state(item)
        fp = fingerprint(want)
        have = mmap.get(item.id)

        if have is None:
            if not item.open:
                continue            # never mirrored, already terminal: skip
            create = ["issue", "create", "-R", REPO, "--title", want["title"],
                      "--body", want["body"]]
            for lb in want["labels"]:
                create += ["--label", lb]
            if args.apply:
                r = subprocess.run(["gh"] + create, capture_output=True, text=True)
                if r.returncode != 0:
                    sys.exit("gh %s\nFAILED: %s" % (" ".join(create), r.stderr.strip()))
                number = int(r.stdout.strip().rsplit("/", 1)[-1])
            else:
                number = None
            plan.append("gh " + " ".join(create[:6]) + " …")
            mmap[item.id] = {"number": number, "fp": fp, "open": True}
            continue

        if have.get("fp") == fp:
            continue                # nothing changed since last push

        num = str(have["number"])
        if not want["open"] and have.get("open"):
            gh(["issue", "close", num, "-R", REPO,
                "--comment", "rimflow: item went terminal."], args.apply, plan)
        elif want["open"]:
            edit = ["issue", "edit", num, "-R", REPO, "--body", want["body"]]
            for lb in want["labels"]:
                edit += ["--add-label", lb]
            gh(edit, args.apply, plan)
        have.update({"fp": fp, "open": want["open"]})

    if args.apply:
        with open(MAP_PATH, "w") as f:
            json.dump(mmap, f, indent=1, sort_keys=True)

    mode = "APPLIED" if args.apply else "DRY RUN — nothing touched"
    print("%s: %d action(s), %d open item(s) in ledger, map holds %d"
          % (mode, len(plan), len(world.open_items()), len(mmap)))
    for line in plan:
        print("  " + line)

    if args.apply and args.with_project:
        proj = os.path.join(os.path.dirname(os.path.abspath(__file__)), "github_project.py")
        r = subprocess.run([sys.executable, proj, "--apply"])
        if r.returncode != 0:
            sys.exit("github_project.py --apply failed (exit %d)" % r.returncode)


if __name__ == "__main__":
    main()
