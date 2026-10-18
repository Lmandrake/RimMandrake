#!/usr/bin/env python3
"""conversations_land.py — land every new or changed `conversations/*.md` record, by explicit path.

Owner, 2026-10-18 (BUILDUP_BUILD_CLONES_STOP_BREEDING, Q3): *"the next handoff plays catchup and takes as long
as it takes"*. ~/dev/Lodestar/bin/conversations.py writes the records and never commits them, and the Lodestar
sweep runs this repo at send-off, so before this nothing ever committed them (46 dirty, 15 tracked, 2026-10-18).

    conversations_land.py            list what would land
    conversations_land.py --apply    land them: land.sh -m (temp index from origin/main — never this clone's
                                     index, never a peer's staged work), in batches of 200 paths

Called by src/RimMandrake/Utils/handoff.py when it writes a handoff skeleton (the catch-up), and by `--check`
as a gate. A seat whose handoff runs through ~/dev/Lodestar/bin/handoff.py runs this right after
`conversations.py` (design/RimMandrake/GIT_WORKFLOW.md). Records are append-mostly and never pruned.
"""
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
LAND = os.path.join(ROOT, "src", "RimMandrake", "Utils", "land.sh")
BATCH = 200


def pending(root=ROOT):
    r = subprocess.run(["git", "-C", root, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--",
                        "conversations"], capture_output=True, text=True)
    out = []
    for rec in r.stdout.split("\0"):
        if len(rec) > 3 and rec[3:].startswith("conversations/") and rec[3:].endswith(".md") and rec[:2] != " D":
            out.append(rec[3:])
    return sorted(out)


def land(paths, root=ROOT):
    """-> (exit code, last PUBLISHED line)."""
    last = ""
    for i in range(0, len(paths), BATCH):
        chunk = paths[i:i + BATCH]
        msg = ("conversations: catch-up %d record(s)\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n"
               "Claude-Session: https://claude.ai/code/session_01QobXckUXJ6LnxbpPwWBirk" % len(chunk))
        r = subprocess.run([LAND, "-m", msg, *chunk], cwd=root, capture_output=True, text=True)
        if r.returncode:
            sys.stderr.write(r.stderr[-800:])
            return r.returncode, last
        last = r.stdout.strip()
    return 0, last


def main(argv=None):
    apply_ = "--apply" in (argv if argv is not None else sys.argv[1:])
    p = pending()
    for x in p:
        print("  " + x)
    if not p:
        print("conversations/: nothing to land")
        return 0
    if not apply_:
        print("%d record(s) would land (--apply lands them)" % len(p))
        return 0
    rc, last = land(p)
    print(("landed %d record(s): %s" % (len(p), last)) if rc == 0 else "REFUSED: land.sh exited %d" % rc)
    return rc


if __name__ == "__main__":
    sys.exit(main())
