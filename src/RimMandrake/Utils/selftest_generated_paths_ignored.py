#!/usr/bin/env python3
"""selftest_generated_paths_ignored.py — derived files a program rewrites in every clone are ignored, never tracked.

RIMMANDRAKE_IGNORE_SEAT_QUEUES_AND_MODSET_SNAPSHOTS (2026-11-16): the seat clone held 15 untracked rimflow queue
projections (one per runner seat, rendered on every claim: CLAUDE_ARCHMAGI_OFFLINE1.md ...) and modset_builder's
ModsConfig before-tier snapshots (copies of the live mod list, 31 of them tracked), so it was never clean.
Hand-written queue files (HUMAN.md, CHECK_CLOSED.md, DECIDE_ARCHIVE.md) stay tracked.
"""
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

IGNORED = [
    "infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE1.md",
    "infrastructure/state/queue/CODEX_STEVEDESKTOP_HUGETHINGS.md",
    "infrastructure/state/queue/BENCH.md",
    "deployed/config/ModsConfig.before-tier-pyrelands.xml",
    "deployed/config/ModsConfig.before-tier-mods__mandrake_rm_flowworks__mandrake_rm_patches.xml",
    "deployed/config/ModsConfig.swap-active.json",
    "deployed/config/ModsConfig.swap-active.ratchet_pilot.stale-20261019.json",
]
KEPT = [
    "infrastructure/state/queue/HUMAN.md",
    "infrastructure/state/queue/CHECK_CLOSED.md",
    "infrastructure/state/queue/DECIDE_ARCHIVE.md",
    "deployed/config/Mod_1516158345_Bubbles.BEFORE-altitude-2026-08-11.xml",
]


def ignored(path):
    # --no-index: judge the rule itself, even for a path that is (still) tracked
    return subprocess.run(["git", "-C", ROOT, "check-ignore", "-q", "--no-index", path]).returncode == 0


def main():
    bad = ["not ignored: " + p for p in IGNORED if not ignored(p)]
    bad += ["ignored but hand-written: " + p for p in KEPT if ignored(p)]
    tracked = subprocess.run(["git", "-C", ROOT, "ls-files", "--", "deployed/config/ModsConfig.before-tier-*",
                              "deployed/config/ModsConfig.swap-active*", "infrastructure/state/queue/"],
                             capture_output=True, text=True).stdout.split()
    keep = set(KEPT)
    bad += ["tracked derived file: " + p for p in tracked if p not in keep]
    if bad:
        print("FAIL\n  " + "\n  ".join(bad[:12]) + ("\n  ... %d more" % (len(bad) - 12) if len(bad) > 12 else ""))
        return 1
    print("PASS: %d derived paths ignored and untracked, %d hand-written kept" % (len(IGNORED), len(KEPT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
