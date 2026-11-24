#!/usr/bin/env python3
"""pages_open.py: open the standing status pages as tabs of ONE Chrome window (./pages).

Tabs, in order: CODEBASE_NOW.html, MATURATION_NOW.html (STATUS_BOARD.html is the dead Relentless board and is not a tab), from the conductor
folder that rmpaths names. A missing page is named and the rest still open. Promises: design/specs/2026-11-19-standing-status-tabs/boundary.md.

    ./pages [--dry-run] [--show]
exit 0 all opened, 2 a page missing (others opened), 3 the launch failed.
--show starts the window normally; the default starts it minimized so it cannot take focus from the game.
A Windows Startup shortcut is made by pages_logon_shortcut.py (owner card, 2026-11-19: at every logon).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rmpaths  # noqa: E402

PAGES = ["CODEBASE_NOW.html", "MATURATION_NOW.html"]


def url_of(win_path):
    p = win_path.replace("\\", "/")
    return "file://" + p if p.startswith("/") else "file:///" + p


def plan(show=False):
    """-> (command list, [urls present], [names missing])."""
    here = str(rmpaths.rm_path("conductor"))
    win = rmpaths.rm_win("conductor")
    present, missing = [], []
    for n in PAGES:
        (present if os.path.isfile(os.path.join(here, n)) else missing).append(n)
    urls = [url_of(win.rstrip("\\/") + "\\" + n) for n in present]
    cmd = ["cmd.exe", "/c", "start", ""] + ([] if show else ["/min"]) + ["chrome", "--new-window"] + urls
    return cmd, urls, missing


def launch(cmd):
    return subprocess.run(cmd, cwd=str(rmpaths.rm_path("conductor")), timeout=60).returncode


def main(argv=None, launcher=launch):
    argv = sys.argv[1:] if argv is None else argv
    dry, show = "--dry-run" in argv, "--show" in argv
    cmd, urls, missing = plan(show)
    print(" ".join(c or '""' for c in (cmd[:-len(urls)] if urls else cmd)))
    for u in urls:
        print("  " + u)
    for n in missing:
        print("MISSING: %s (not opened)" % n)
    if dry:
        return 2 if missing else 0
    if not urls:
        print("nothing to open")
        return 2
    try:
        rc = launcher(cmd)
    except (OSError, subprocess.SubprocessError) as e:
        print("launch failed: %s" % e)
        return 3
    if rc:
        print("launch failed: exit %s" % rc)
        return 3
    print("opened %d tab(s) in one Chrome window" % len(urls))
    return 2 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
