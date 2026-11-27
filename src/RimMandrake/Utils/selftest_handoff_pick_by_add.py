"""
Selftest: `handoff.py --wake` picks the handoff that was WRITTEN last, and an edit of an old handoff never changes the pick.

RIMMANDRAKE_FIX_WAKE_HANDOFF_PICK_EDITED_OLD_FILE_WON: previous_handoff() ranked each file by the last commit that
touched it (--diff-filter=AM). A later commit that edited an old handoff (a typo fix, a cull note, a pointer answered)
made that old file the "newest", and --wake showed it as the predecessor. The rank is now the commit that ADDED the file.

Runs in a temp git repo: no network, no real ledger.
  1. old handoff added, then newer handoff added -> newer is picked
  2. a later commit edits the old handoff -> newer is still picked, and its timestamp is its add time
  3. a handoff moved from items/ to handoffs/ (pure rename) keeps its add time from items/
"""

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ["RIMFLOW_SEAT"] = "BENCH"

import handoff  # noqa: E402

fails = []


def check(ok, what):
    print(("  ok   " if ok else "  FAIL ") + what)
    if not ok:
        fails.append(what)


def git(root, *args, when=None):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")
    if when:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = when
    subprocess.run(("git",) + args, cwd=root, env=env, check=True, capture_output=True)


def write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)


OLD = "BENCH_REBOOT_HANDOFF_202611010000.md"
NEW = "BENCH_REBOOT_HANDOFF_202611100000.md"
MOVED = "BENCH_REBOOT_HANDOFF_202609010000.md"
H = "infrastructure/state/handoffs/"
ITEMS = "infrastructure/state/items/"

with tempfile.TemporaryDirectory() as root:
    git(root, "init", "-q", "-b", "main")
    write(root, ITEMS + MOVED, "# moved\n")
    git(root, "add", ".")
    git(root, "commit", "-qm", "moved: add in items/", when="2026-09-01T00:00:00Z")
    os.makedirs(os.path.join(root, H), exist_ok=True)
    git(root, "mv", ITEMS + MOVED, H + MOVED)
    git(root, "commit", "-qm", "move handoffs out of items/", when="2026-09-19T00:00:00Z")
    write(root, H + OLD, "# old\n")
    git(root, "add", ".")
    git(root, "commit", "-qm", "old", when="2026-11-01T00:00:00Z")
    write(root, H + NEW, "# new\n")
    git(root, "add", ".")
    git(root, "commit", "-qm", "new", when="2026-11-10T00:00:00Z")

    real_root, real_h = handoff.ROOT, handoff.HANDOFFS
    handoff.ROOT, handoff.HANDOFFS = root, os.path.join(root, H)
    try:
        print("handoff: the pick is the handoff added last")
        name, ts = handoff.previous_handoff()
        check(name == NEW and ts == "2026-11-10T00:00:00Z", "newer handoff picked before any edit (%s, %s)" % (name, ts))

        print("handoff: an edit of an old handoff does not change the pick")
        write(root, H + OLD, "# old\n\nedited later\n")
        git(root, "commit", "-qam", "edit old", when="2026-11-20T00:00:00Z")
        name, ts = handoff.previous_handoff()
        check(name == NEW, "after an edit of the old file, the newer handoff is still picked (%s)" % name)
        check(ts == "2026-11-10T00:00:00Z", "and its timestamp is its add time, not the edit's (%s)" % ts)

        print("handoff: a pure rename keeps the add time from items/")
        times = handoff._corpus_add_times()
        check(times.get(MOVED) == "2026-09-01T00:00:00Z",
              "a handoff moved out of items/ keeps its items/ add time (%s)" % times.get(MOVED))
    finally:
        handoff.ROOT, handoff.HANDOFFS = real_root, real_h

if fails:
    print("FAIL: %d check(s)" % len(fails))
    sys.exit(1)
print("PASS")
