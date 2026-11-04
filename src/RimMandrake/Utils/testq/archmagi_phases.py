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
                                           The lane keeps whatever list is loaded (MODCHECK_KEEP_MODLIST), and the
                                           owner's list is no longer kept full (owner 2026-10-24: leave ModsConfig on
                                           whatever tier serves the work), so a running game whose list is not the
                                           full list (ModsConfig.FULL.LATEST.xml, ids and order, read from the RUNNING
                                           game by jawa/running_mods) is REFUSED too: a full-list job never runs, and
                                           is never recorded, on a minimal tier.
  archmagi_phases.py down                  never stops the owner's game: `REFUSED: ...`, exit 3 (a hang is then
                                           INVALID/HANG at once, with no restart-and-retry).
  archmagi_phases.py status                `running pid=N` or `stopped` (worker.game_gone reads it).

The game's pid comes from powershell.exe Get-Process (full /mnt/c path, as rw_game.sh does). TESTQ_ARCHMAGI_PID
replaces that probe (tests: a number, or "" for no game). TESTQ_ARCHMAGI_RUNNING (a file of packageIds, one a line;
a missing file = the bridge could not be asked) replaces the jawa/running_mods read, TESTQ_ARCHMAGI_FULL_LIST the
intended list.
"""
import os
import subprocess
import sys

# The worker runs a phase command in the runner clone (cwd); the dispatcher runs a COPY of this file from outside the
# clone, because a job pinned to an older sha has no archmagi_phases.py of its own. So the repo is the cwd.
REPO = os.getcwd()
PS = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
EX_REFUSED = 3
FULL_LIST = os.path.join("infrastructure", "state", "modlists", "ModsConfig.FULL.LATEST.xml")


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


def running_ids():
    """-> (ids, None) of the RUNNING game's mods in load order (jawa/running_mods, read-only), or (None, why)."""
    fake = os.environ.get("TESTQ_ARCHMAGI_RUNNING")
    if fake is not None:
        try:
            with open(fake, encoding="utf-8") as f:
                return [x.strip() for x in f if x.strip()], None
        except OSError as e:
            return None, "running list unreadable (%s)" % e
    ids, why = _ask_bridge()
    if ids is None and "from WSL" in (why or ""):     # RimBridge binds Windows loopback: ask from python.exe
        ids, why = _ask_from_windows()
    return ids, why


def _ask_from_windows():
    import glob
    import json
    import shutil
    exe = shutil.which("python.exe") or next(iter(sorted(glob.glob(
        "/mnt/c/Users/*/AppData/Local/Microsoft/WindowsApps/python.exe"))), None)
    if not exe:
        return None, "the bridge is unreachable from WSL and no python.exe was found"
    try:
        me = subprocess.run(["wslpath", "-w", os.path.abspath(__file__)], capture_output=True, text=True,
                            timeout=30).stdout.strip()
        r = subprocess.run([exe, me, "running-ids"], capture_output=True, text=True, timeout=120, cwd=REPO)
        last = [ln for ln in r.stdout.replace("\r", "").splitlines() if ln.startswith("{")][-1:]
        d = json.loads(last[0]) if last else {"why": "python.exe printed no reply (exit %d): %s"
                                                     % (r.returncode, (r.stderr or "").strip()[-200:])}
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        return None, "python.exe running-ids failed (%s: %s)" % (type(e).__name__, e)
    return (d["ids"], None) if isinstance(d.get("ids"), list) and d["ids"] else (None, d.get("why") or "no ids")


def _repo_utils():
    """Import from the runner clone's Utils (this file may be a copy outside it)."""
    utils = os.path.join(REPO, "src", "RimMandrake", "Utils")
    if utils not in sys.path:
        sys.path.insert(0, utils)


def _ask_bridge():
    _repo_utils()
    try:
        from rimbridge_client import RimBridge, resolve_endpoint
        host, port, token = resolve_endpoint(None, None, None)
        if not token:
            return None, "no bridge token in Player.log"
        with RimBridge(host, port, token, timeout=60.0, client_name="archmagi_phases.py") as b:
            r = b.call("jawa/running_mods", {"assembly": "", "details": False})
    except Exception as e:      # noqa: BLE001 - any failure to ask is "cannot show", never a match
        return None, "jawa/running_mods failed (%s: %s)" % (type(e).__name__, e)
    raw = r.get("packageIds") if isinstance(r, dict) else None
    if not isinstance(raw, list) or not raw or not all(isinstance(x, str) and x.strip() for x in raw):
        return None, "jawa/running_mods gave no usable packageIds (%r)" % (str(r)[:200],)
    return [x.strip() for x in raw], None


def full_list_problem():
    """-> None when the running game's list IS the full list (ids and relative order), else why not."""
    path = os.environ.get("TESTQ_ARCHMAGI_FULL_LIST") or os.path.join(REPO, FULL_LIST)
    _repo_utils()
    try:
        import modmanifest
        intended = modmanifest.read_modsconfig(path)
    except Exception as e:      # noqa: BLE001
        return "the full list is unreadable (%s: %s)" % (type(e).__name__, e)
    ids, why = running_ids()
    if why:
        return "cannot show the running list is the full list: " + why
    c = modmanifest.compare(intended, ids)
    if not c["clean"]:
        return "the running list is not the full list (running %d vs %s %d): %s" % (
            len(ids), os.path.basename(path), len(intended), "; ".join(c["problems"])[:300])
    return None


def cmd_load():
    pid = game_pid()
    if pid:
        prob = full_list_problem()
        if prob:
            print("REFUSED: %s; the archmagi lane never swaps the owner's list" % prob)
            return EX_REFUSED
        print("already running (pid %s), the full list loaded" % pid)
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
    if argv and argv[0] == "running-ids":        # internal: the python.exe half of running_ids()
        import json
        ids, why = _ask_bridge()
        print(json.dumps({"ids": ids} if ids else {"why": why}))
        return 0 if ids else 2
    if not argv or argv[0] not in ("deploy", "load", "down", "status"):
        print("usage: archmagi_phases.py deploy MOD... | load | down | status")
        return 2
    verb, rest = argv[0], argv[1:]
    if verb == "deploy":
        return cmd_deploy(rest)
    return {"load": cmd_load, "down": cmd_down, "status": cmd_status}[verb]()


if __name__ == "__main__":
    sys.exit(main())
