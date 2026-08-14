#!/usr/bin/env python3
"""backup_rimsort_rules.py — copy RimSort's rule databases into the repo.

    python3 src/RimMandrake/Utils/backup_rimsort_rules.py          # copy + report
    python3 src/RimMandrake/Utils/backup_rimsort_rules.py --check  # report only

WHY THESE FILES MATTER
======================
`userRules.json` holds the load-order constraints we author by hand. Measured
2026-08-13: 13 rules, **12 of them ours**. They are keyed by packageId and they
are the only record of *why* a mod sits where it sits. Lose them and the load
order still looks fine — until the next Sort discards every hand-fix, silently,
because a hand-fix that is not written back as a User Rule does not survive one.

They live outside the repo, on one disk, in an AppData directory nothing backs
up. That is the same exposure that cost this project a global CLAUDE.md.

WHY A COPY AND NOT A SYMLINK
============================
The owner asked for a "link". A symlink is the wrong tool here, twice over:

  * **Repo -> AppData** would track a symlink, whose blob is the target *string*.
    Git would back up a path, not the rules. That is not a backup.
  * **AppData -> repo** would work in principle, but RimSort is a Windows
    application reading a WSL-created link, and it REWRITES these files. If it
    cannot follow or cannot replace the link, the failure lands on the owner's
    tool mid-session, and the whole point of these rules is that they are needed
    exactly when a load is being prepared.

So: copy, tracked, diffable. The cost is that it must be re-run after editing
rules; the benefit is that a `git diff` shows precisely which constraint changed,
which a symlink would never have given us either.

WHAT IT DOES NOT DO
===================
It does not write back INTO RimSort. Restoring is a deliberate act, not something
a backup script should do by accident — and `ModsConfig.xml`/RimSort collisions
are a real hazard (read mtime before writing). Restore by hand, with RimSort shut.
"""
import filecmp
import json
import os
import shutil
import sys

# RimSort's own database directory. Windows path via the WSL mount; the Windows
# form is the same location and is what RimSort itself writes.
SRC = "/mnt/c/Users/Mandrake/AppData/Local/RimSort/dbs"
FILES = ("userRules.json", "ignore.json")


def repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != "/" and not os.path.isdir(os.path.join(d, ".git")):
        d = os.path.dirname(d)
    return d


def describe(path):
    """Rule/entry counts, so the report says what changed and not just that it did."""
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return "unreadable"
    if isinstance(data, dict):
        rules = data.get("rules", data)
        if isinstance(rules, dict):
            ours = sum(1 for k in rules if "mandrake" in str(k).lower())
            return "%d entries, %d ours" % (len(rules), ours)
        for v in data.values():
            if isinstance(v, list):
                return "%d entries" % len(v)
    return "ok"


def main():
    check_only = "--check" in sys.argv
    dest_dir = os.path.join(repo_root(), "deployed", "config", "rimsort")
    if not check_only:
        os.makedirs(dest_dir, exist_ok=True)

    if not os.path.isdir(SRC):
        print("RimSort db dir not found: %s" % SRC, file=sys.stderr)
        print("Nothing copied. Is RimSort installed for this user?", file=sys.stderr)
        return 2

    changed = 0
    for name in FILES:
        src, dest = os.path.join(SRC, name), os.path.join(dest_dir, name)
        if not os.path.isfile(src):
            print("  %-16s MISSING at source" % name)
            continue
        same = os.path.isfile(dest) and filecmp.cmp(src, dest, shallow=False)
        state = "unchanged" if same else ("differs" if os.path.isfile(dest) else "new")
        print("  %-16s %-10s %s" % (name, state, describe(src)))
        if not same:
            changed += 1
            if not check_only:
                shutil.copy2(src, dest)

    if check_only:
        print("\n--check: nothing written. %d file(s) differ." % changed)
    elif changed:
        print("\nCopied %d file(s) to deployed/config/rimsort/. "
              "Commit them — they are not backed up anywhere else." % changed)
    else:
        print("\nAlready in sync.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
