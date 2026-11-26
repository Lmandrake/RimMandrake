#!/usr/bin/env python3
"""selftest_generated_paths_ignored.py — derived files a program rewrites in every clone are ignored, never tracked.

RIMMANDRAKE_IGNORE_SEAT_QUEUES_AND_MODSET_SNAPSHOTS (2026-11-16): the seat clone held 15 untracked rimflow queue
projections (one per runner seat, rendered on every claim: CLAUDE_ARCHMAGI_OFFLINE1.md ...) and modset_builder's
ModsConfig before-tier snapshots (copies of the live mod list, 31 of them tracked), so it was never clean.
Hand-written queue files (CHECK_CLOSED.md, DECIDE_ARCHIVE.md) stay tracked.

`--at REV` replays the rules of an older commit (its root .gitignore and its tracked files): the class guard of
OPS_SEAT_CLONE_DIRT_RESTORE_VTLF is shown red on the 2026-11-26 instance with `--at 5dd0966a39^`, the parent of the
rule for modset_builder's <marker>.stale-<UTC> rename.
"""
import fnmatch
import os
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

IGNORED = [
    "infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE1.md",
    "infrastructure/state/queue/CODEX_STEVEDESKTOP_HUGETHINGS.md",
    "infrastructure/state/queue/BENCH.md",
    "deployed/config/ModsConfig.before-tier-pyrelands.xml",
    "deployed/config/ModsConfig.before-tier-mods__mandrake_rm_flowworks__mandrake_rm_patches.xml",
    "deployed/config/ModsConfig.swap-active.json",
    "deployed/config/ModsConfig.swap-active.ratchet_pilot.stale-20261019.json",
    "deployed/config/ModsConfig.swap-active.json.stale-20261126T171600Z",
]
KEPT = [
    "infrastructure/state/queue/CHECK_CLOSED.md",
    "infrastructure/state/queue/DECIDE_ARCHIVE.md",
    "deployed/config/Mod_1516158345_Bubbles.BEFORE-altitude-2026-08-11.xml",
]


DERIVED = ["deployed/config/ModsConfig.before-tier-*", "deployed/config/ModsConfig.swap-active*", "infrastructure/state/queue/"]


def ignored(path, root=ROOT):
    # --no-index: judge the rule itself, even for a path that is (still) tracked
    return subprocess.run(["git", "-C", root, "check-ignore", "-q", "--no-index", path]).returncode == 0


def replay_root(rev, tmp):
    """A bare work tree holding only REV's root .gitignore, so check-ignore judges that commit's rules."""
    rules = subprocess.run(["git", "-C", ROOT, "show", "%s:.gitignore" % rev], capture_output=True, check=True).stdout
    subprocess.run(["git", "init", "-q", tmp], check=True)
    with open(os.path.join(tmp, ".gitignore"), "wb") as f:
        f.write(rules)
    return tmp


def main(argv):
    rev = argv[argv.index("--at") + 1] if "--at" in argv else None
    with tempfile.TemporaryDirectory() as tmp:
        root = replay_root(rev, tmp) if rev else ROOT
        bad = ["not ignored: " + p for p in IGNORED if not ignored(p, root)]
        bad += ["ignored but hand-written: " + p for p in KEPT if ignored(p, root)]
    if rev:
        # ls-tree takes no glob: list the folders and match here (a glob pathspec there reads 0 of 31 at 71edba5965^)
        names = subprocess.run(["git", "-C", ROOT, "ls-tree", "-r", "--name-only", rev, "--", "deployed/config",
                                "infrastructure/state/queue"], capture_output=True, text=True, check=True).stdout.split()
        tracked = [n for n in names if any(fnmatch.fnmatch(n, d) or n.startswith(d) for d in DERIVED)]
    else:
        tracked = subprocess.run(["git", "-C", ROOT, "ls-files", "--"] + DERIVED, capture_output=True, text=True).stdout.split()
    keep = set(KEPT)
    bad += ["tracked derived file: " + p for p in tracked if p not in keep]
    if bad:
        print("FAIL\n  " + "\n  ".join(bad[:12]) + ("\n  ... %d more" % (len(bad) - 12) if len(bad) > 12 else ""))
        return 1
    print("PASS: %d derived paths ignored and untracked, %d hand-written kept%s" % (len(IGNORED), len(KEPT),
                                                                                 " at %s" % rev if rev else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
