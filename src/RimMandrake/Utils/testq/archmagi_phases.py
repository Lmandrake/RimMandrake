#!/usr/bin/env python3
"""archmagi_phases.py - the worker's phase commands on Archmagi (TESTQ_ARCHMAGI_LANE_BUILD_BACKFILL).

The testq Archmagi backfill runs the same worker.py as SteveDesktop, locally, with these as its TESTQ_CMD_DEPLOY /
LOAD / DOWN / STATUS. Archmagi's game is the owner's: the lane borrows it while nobody drives it, and never changes
what is loaded or whether it runs.

  archmagi_phases.py deploy MOD [MOD...]   plan only (deploy_custom_mods.py, no --apply). No drift: exit 0. Drift:
                                           prints `REFUSED: ...` and exits 3 - the worker reads that as REFUSED/DEPLOY
                                           and the dispatcher hands the job back for SteveDesktop.
  archmagi_phases.py load                  never launches: a running game prints `already running (pid N)`; none
                                           prints `REFUSED: ...` (REFUSED/LOAD; the dispatcher backs the lane off).
  archmagi_phases.py down                  never stops the owner's game: `REFUSED: ...`, exit 3 (a hang is then
                                           INVALID/HANG at once, with no restart-and-retry).
  archmagi_phases.py status                `running pid=N` or `stopped` (worker.game_gone reads it).

The game's pid comes from powershell.exe Get-Process (full /mnt/c path, as rw_game.sh does). TESTQ_ARCHMAGI_PID
replaces that probe (tests: a number, or "" for no game).
"""
import os
import subprocess
import sys

# The worker runs a phase command in the runner clone (cwd); the dispatcher runs a COPY of this file from outside the
# clone, because a job pinned to an older sha has no archmagi_phases.py of its own. So the repo is the cwd.
REPO = os.getcwd()
PS = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
EX_REFUSED = 3


def game_pid():
    """-> the running RimWorldWin64 pid as a string, '' when none runs, None when it cannot be told."""
    fake = os.environ.get("TESTQ_ARCHMAGI_PID")
    if fake is not None:
        return fake.strip()
    try:
        r = subprocess.run([PS, "-NoProfile", "-NonInteractive", "-Command",
                            "(Get-Process RimWorldWin64 -ErrorAction SilentlyContinue | Select-Object -First 1).Id"],
                           capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    out = r.stdout.replace("\r", "").strip()
    return out if out.isdigit() or out == "" else None


def cmd_deploy(mods):
    if not mods:
        print("REFUSED: deploy needs at least one mod")
        return EX_REFUSED
    args = []
    for m in mods:
        args += ["--mod", m]
    try:
        r = subprocess.run([sys.executable, os.path.join(REPO, "src", "RimMandrake", "Utils", "deploy_custom_mods.py")]
                           + args, capture_output=True, text=True, timeout=600, cwd=REPO)
    except (OSError, subprocess.SubprocessError) as e:
        print("REFUSED: the deploy plan could not run: %s" % e)
        return EX_REFUSED
    text = (r.stdout or "") + (r.stderr or "")
    if r.returncode == 0:
        print("deploy: no drift for %s; the owner's game is kept" % " ".join(mods))
        return 0
    why = "drift found" if "Drift found" in text else "the deploy plan failed (exit %d)" % r.returncode
    print("REFUSED: %s for %s; the archmagi lane never deploys under the owner's game: %s"
          % (why, " ".join(mods), text.strip()[-300:].replace("\n", " | ")))
    return EX_REFUSED


def cmd_load():
    pid = game_pid()
    if pid:
        print("already running (pid %s)" % pid)
        return 0
    if pid is None:
        print("REFUSED: cannot tell whether RimWorld runs (powershell probe failed); the archmagi lane never launches")
    else:
        print("REFUSED: no RimWorld running on Archmagi; the archmagi lane never launches the owner's game")
    return EX_REFUSED


def cmd_down():
    print("REFUSED: the archmagi lane never stops the owner's game")
    return EX_REFUSED


def cmd_status():
    pid = game_pid()
    if pid:
        print("running pid=%s" % pid)
        return 0
    if pid == "":
        print("stopped")
        return 3
    print("unknown: the powershell probe failed")
    return 2


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in ("deploy", "load", "down", "status"):
        print("usage: archmagi_phases.py deploy MOD... | load | down | status")
        return 2
    verb, rest = argv[0], argv[1:]
    if verb == "deploy":
        return cmd_deploy(rest)
    return {"load": cmd_load, "down": cmd_down, "status": cmd_status}[verb]()


if __name__ == "__main__":
    sys.exit(main())
