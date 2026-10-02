"""live_session.py -- take a north-star script from "authored" to "one live run recorded" in one command, so the
bridge never idles between scripts (design/RimMandrake/debug_process.md, "Keep the bridge busy").

Run from WSL (python3), repo root as cwd, bridge HELD (`rimflow bridge who`):

  python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod Warcasket --tier warcasket \
      --plan src/RimMandrake/Warcasket/northstar_plan.py [--deploy-mod Warcasket ...] [--compose]

Steps (each prints one line; any failure stops with the step name):
  1 stop the game (graceful taskkill, wait for exit)
  2 modset_builder --tier <tier> --apply            (backs ModsConfig up itself; the pre-session list is also
                                                     copied to deployed/config/ModsConfig.pre-session.<ts>.xml)
  3 deploy_custom_mods --compose biomes / --mod X --apply   (only what you name)
  4 launch via Steam, wait for `Bridge token:` in Player.log
  5 start a quicktest world (rimworld/start_debug_game_ready) unless --no-quicktest (the plan's own site prep,
    e.g. Pyrelands' northstar_site.py, builds its own)
  6 northstar_driver cli run (Windows python) -> Transient/northstar/<Mod>_<ts>.json, summary printed

It never restores the owner's mod list: that is `--restore` at the END of a batch (modset_builder --restore is
wrong after several tiers; the pre-session copy is the authority).
"""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
_UTILS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _UTILS not in sys.path:
    sys.path.insert(0, _UTILS)
from game_paths import MODS_CONFIG as MODSCONFIG, PLAYER_LOG  # noqa: E402


def say(step, msg):
    print("[%s] %s" % (step, msg), flush=True)


def sh(argv, timeout=600, cwd=ROOT):
    p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def running():
    rc, out = sh(["tasklist.exe"], timeout=60)
    return "RimWorldWin64" in out


def stop_game():
    if not running():
        return say("1 stop", "game not running")
    sh(["taskkill.exe", "/IM", "RimWorldWin64.exe"], timeout=60)
    t0 = time.time()
    while running() and time.time() - t0 < 90:
        time.sleep(2)
    if running():
        sys.exit("[1 stop] game still running after 90 s (not force-killing)")
    time.sleep(5)       # modset_builder refuses while Player.log was touched in the last 3 min of an exit
    say("1 stop", "game exited")


def launch_and_wait(budget=900):
    sh(["powershell.exe", "-NoProfile", "-Command", "Start-Process 'steam://rungameid/294100'"], timeout=60)
    t0 = time.time()
    time.sleep(20)
    while time.time() - t0 < budget:
        try:
            fresh = time.time() - os.stat(PLAYER_LOG).st_mtime < 90
            if fresh and running() and "Bridge token:" in open(PLAYER_LOG, encoding="utf-8", errors="replace").read():
                return say("4 launch", "bridge up after %d s" % (time.time() - t0))
        except OSError:
            pass
        time.sleep(3)
    sys.exit("[4 launch] no bridge token within %d s" % budget)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mod", required=True)
    ap.add_argument("--tier", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--deploy-mod", action="append", default=[])
    ap.add_argument("--compose", action="store_true", help="deploy_custom_mods --compose biomes --apply")
    ap.add_argument("--no-quicktest", action="store_true")
    ap.add_argument("--no-restart", action="store_true", help="game already up on the right tier")
    ap.add_argument("--extra", default="", help="extra args for the driver run")
    a = ap.parse_args()

    rc, who = sh(["python3", "src/RimMandrake/rimflow/cli.py", "bridge", "who"], timeout=120)
    if "FOUNDRY" not in who:
        sys.exit("bridge is not held by FOUNDRY: " + who.strip()[:120])

    if not a.no_restart:
        stop_game()
        pre = os.path.join(ROOT, "deployed", "config", "ModsConfig.pre-session.%s.xml" % time.strftime("%Y%m%dT%H%M%S"))
        if not glob.glob(os.path.join(ROOT, "deployed", "config", "ModsConfig.pre-session.*.xml")):
            shutil.copy(MODSCONFIG, pre)
            say("2 tier", "pre-session list saved -> %s" % os.path.relpath(pre, ROOT))
        rc, out = sh(["python3", "src/RimMandrake/Utils/modset_builder.py", "--tier", a.tier, "--apply"], timeout=300)
        if rc != 0:
            sys.exit("[2 tier] modset_builder failed:\n" + out[-600:])
        say("2 tier", re.findall(r"wrote\s+->.*", out)[-1] if re.findall(r"wrote\s+->.*", out) else "applied")
        for argv in ([["python3", "src/RimMandrake/Utils/deploy_custom_mods.py", "--compose", "biomes", "--apply"]] if a.compose else []) + \
                    [["python3", "src/RimMandrake/Utils/deploy_custom_mods.py", "--mod", m, "--apply"] for m in a.deploy_mod]:
            rc, out = sh(argv, timeout=600)
            tail = [l for l in out.splitlines() if l.strip()][-1:] or [""]
            if rc not in (0, 1):
                sys.exit("[3 deploy] %s failed:\n%s" % (" ".join(argv[2:]), out[-600:]))
            say("3 deploy", "%s -> %s" % (" ".join(argv[2:4]), tail[0].strip()[:100]))
        launch_and_wait()
    else:
        say("2-4", "--no-restart: assuming the game is up on %s" % a.tier)

    if not a.no_quicktest:
        rc, out = sh(["python.exe", "src/RimMandrake/bridgetools/prove_quicktest_world.py"], timeout=420)
        say("5 world", (out.strip().splitlines() or ["(no output)"])[-1][:140])
        if rc != 0:
            sys.exit("[5 world] quicktest world did not reach Playing:\n" + out[-500:])

    argv = ["python.exe", "src/RimMandrake/Utils/northstar_driver/cli.py", "run", "--mod", a.mod, "--plan", a.plan] + a.extra.split()
    t0 = time.time()
    rc, out = sh(argv, timeout=7000)
    log = os.path.join(ROOT, "Transient", "northstar", "%s_session_%s.log" % (a.mod, time.strftime("%Y%m%dT%H%M%S")))
    os.makedirs(os.path.dirname(log), exist_ok=True)
    open(log, "w", encoding="utf-8").write(out)
    say("6 run", "exit %s in %d s; log %s" % (rc, time.time() - t0, os.path.relpath(log, ROOT)))
    for line in out.splitlines():
        if line.startswith("component ") or re.match(r"^\w+: (GREEN|NOT GREEN|REFUSED)", line):
            print(line[:300])
    return rc


if __name__ == "__main__":
    sys.exit(main())
