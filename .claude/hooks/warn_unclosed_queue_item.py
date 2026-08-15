#!/usr/bin/env python3
"""PreToolUse/Bash hook — warn when a commit removes a queue item with no `Closes:`.

WHY
===
Measured 2026-08-14: 124 item IDs had ever existed, 51 were still filed, and
`state: done` had been written three times in the whole project history. Items
did not get closed, they got deleted or renumbered, so the board's numerator
could never rise while its denominator shrank. `derive_matrix.py` now counts
closed work from a `Closes: <ID>` trailer instead — read back out of the closing
commit's parent, where the item still exists.

That only works if the trailer is actually written. A commit that removes an
item heading and forgets it loses the record permanently: the next commit's
parent no longer holds the item, so nothing can recover its row afterwards.

WARN, NOT BLOCK — owner's call, 2026-08-15
==========================================
The standing order is to commit and push the moment an item is done. A hook that
refuses a commit costs more than the miscount it prevents, and a seat that hits
it mid-flow will work around it. So this prints and always exits 0.

WHAT IT CHECKS
==============
For `git commit` naming a path under infrastructure/state/queue/, diff the
working tree against HEAD, collect every `## <ID>` heading being REMOVED, and
warn about any whose ID does not appear in a `Closes:` trailer in the -m text.

A heading that is removed AND re-added — a retitle — is not a removal and does
not warn. `state: dropped` needs no exemption: dropping keeps the item in the
queue with a reason line, so its heading is never removed at all.
"""
import json
import os
import re
import subprocess
import sys

QUEUE = "infrastructure/state/queue/"
HEADING = re.compile(r"^([+-])## ([A-Z][A-Z0-9-]*)\b")
CLOSES = re.compile(r"^Closes:\s*([A-Z][A-Z0-9-]*)\s*$", re.M)


def git(root, *args):
    try:
        p = subprocess.run(["git", "-C", root, *args],
                           capture_output=True, text=True, timeout=8)
    except (OSError, subprocess.SubprocessError):
        return None
    return p.stdout if p.returncode == 0 else None


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        return 0
    cmd = (ev.get("tool_input") or {}).get("command") or ""
    if "git" not in cmd or "commit" not in cmd:
        return 0

    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    paths = [p for p in re.findall(r"[\w./-]+\.md", cmd) if QUEUE in p]
    if not paths:
        return 0

    # The tree, not the index: `git commit <path>` commits the working tree at
    # that path regardless of what is staged.
    diff = git(root, "diff", "HEAD", "--", *paths)
    if not diff:
        return 0
    removed, added = set(), set()
    for ln in diff.splitlines():
        m = HEADING.match(ln)
        if m:
            (removed if m.group(1) == "-" else added).add(m.group(2))
    gone = removed - added                      # a retitle is not a removal
    if not gone:
        return 0

    # `state: dropped` needs no exemption: dropping KEEPS the item in the queue
    # with a reason line, so its heading never appears as a removal here.
    missing = sorted(gone - set(CLOSES.findall(cmd)))
    if not missing:
        return 0

    print("⚠ queue item(s) removed with no `Closes:` trailer: %s"
          % ", ".join(missing), file=sys.stderr)
    print("  The item is about to leave the queue. Without the trailer the board",
          file=sys.stderr)
    print("  cannot count it and its row cannot be recovered later.", file=sys.stderr)
    print("  Add to the commit message:  Closes: %s" % missing[0], file=sys.stderr)
    print("  Dropping it instead? Set `state: dropped` with one line of why.",
          file=sys.stderr)
    return 0                                     # never a gate


if __name__ == "__main__":
    sys.exit(main())
