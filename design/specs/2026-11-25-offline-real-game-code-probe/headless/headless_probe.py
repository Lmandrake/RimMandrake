#!/usr/bin/env python3
"""Does a headless RimWorld (-batchmode -nographics) load, answer the bridge, start a map and run ticks? (one measurement)

Item RIMMANDRAKE_REPLAY_ENUMERATED_SITUATIONS_IN_HEADLESS_REAL_GAME. Run with Windows python.exe on SteveDesktop (the bridge binds
Windows loopback):

    python.exe headless_probe.py [--game-dir D:\\SteamLibrary\\steamapps\\common\\RimWorld] [--work D:\\ClaudeWork\\rimmandrake\\scratch\\headless_probe]

It starts a game of its own: its own -savedatafolder (a fresh userdata holding only a small ModsConfig: Harmony, Core, the five
expansions, RimBridgeServer), its own -logfile, its own bridge port and token. It touches no other game's config or saves. It
reads the log until the bridge's port line, a dead process or the budget; then asks the bridge for the game info, starts a
quicktest map, steps 600 ticks and reads the tick again. It kills only the process it started. The reading goes to
<work>\\result.json and stdout.
"""
import argparse
import json
import os
import secrets
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))

PORT_LINE = "GABP server connected to GABS on port"
MODS = ["brrainz.harmony", "ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
        "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey", "brrainz.rimbridgeserver"]
VERSION_FROM = os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml")


def mods_config(path, mods):
    version = "1.6.4871 rev590"
    try:
        text = open(VERSION_FROM, encoding="utf-8").read()
        version = text.split("<version>", 1)[1].split("</version>", 1)[0]
    except (OSError, IndexError):
        pass
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="utf-8"?>\n<ModsConfigData>\n  <version>%s</version>\n  <activeMods>\n%s  </activeMods>\n'
                 '  <knownExpansions>\n%s  </knownExpansions>\n</ModsConfigData>\n'
                 % (version, "".join("    <li>%s</li>\n" % m for m in mods),
                    "".join("    <li>%s</li>\n" % m for m in mods if m.startswith("ludeon.rimworld."))))


def first_exception(text):
    for line in text.splitlines():
        if "Exception" in line or line.startswith("Error"):
            return line.strip()[:300]
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game-dir", default=r"D:\SteamLibrary\steamapps\common\RimWorld")
    ap.add_argument("--work", default=r"D:\ClaudeWork\rimmandrake\scratch\headless_probe")
    ap.add_argument("--port", type=int, default=5179)
    ap.add_argument("--budget-s", type=int, default=1200, help="hang guard on the load: 10x the ~2 min small-list load")
    ap.add_argument("--extra-mods", default="", help="comma-separated packageIds loaded after the base list")
    ap.add_argument("--then", default="", help="a command run once the map plays, with GABP_SERVER_PORT, GABP_TOKEN and "
                    "RIMBRIDGE_HOST set to this game; its exit and output tail are recorded")
    a = ap.parse_args()
    ud = os.path.join(a.work, "userdata")
    log = os.path.join(a.work, "Player.log")
    mods = MODS + [m for m in a.extra_mods.split(",") if m]
    mods_config(os.path.join(ud, "Config", "ModsConfig.xml"), mods)
    if os.path.exists(log):
        os.replace(log, log + ".prev")
    token = secrets.token_hex(16)
    env = dict(os.environ, GABP_SERVER_PORT=str(a.port), GABP_TOKEN=token)
    argv = [os.path.join(a.game_dir, "RimWorldWin64.exe"), "-batchmode", "-nographics", "-savedatafolder=" + ud, "-logfile", log]
    res = {"argv": argv[1:], "mods": mods, "steps": []}

    def step(name, ok, detail, t0):
        res["steps"].append({"step": name, "ok": ok, "s": round(time.time() - t0, 1), "detail": detail})
        print("%-5s %-28s %6.1f s  %s" % ("OK" if ok else "FAIL", name, time.time() - t0, detail), flush=True)

    t0 = time.time()
    proc = subprocess.Popen(argv, cwd=a.game_dir, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    res["pid"] = proc.pid
    try:
        text, up = "", False
        while time.time() - t0 < a.budget_s:
            text = open(log, encoding="utf-8", errors="replace").read() if os.path.exists(log) else ""
            if "%s %d" % (PORT_LINE, a.port) in text:
                up = True
                break
            if proc.poll() is not None:
                break
            time.sleep(2)
        step("process alive", proc.poll() is None, "exit %s" % proc.poll(), t0)
        step("bridge port line", up, "log %d lines; first exception: %s" % (text.count("\n"), first_exception(text)), t0)
        if up:
            from rimbridge_client import RimBridge
            with RimBridge(host="127.0.0.1", port=a.port, token=token, timeout=900.0) as b:
                info = b.call("rimworld/get_game_info", {})
                step("get_game_info", True, json.dumps(info)[:300], t0)
                r = b.call("rimworld/start_debug_game_ready", {"timeoutMs": 900000, "readiness": "mapData", "pauseIfNeeded": True})
                step("start_debug_game_ready", True, json.dumps(r)[:300], t0)
                # "map data" comes while the map's long event still runs (programState MapInitializing): wait for Playing
                state, t1 = None, time.time()
                while time.time() - t1 < a.budget_s:
                    info = b.call("rimworld/get_game_info", {})
                    state = (info.get("state") or {}).get("programState") if isinstance(info, dict) else None
                    if state == "Playing":
                        break
                    time.sleep(2)
                step("programState Playing", state == "Playing", "last state %s" % state, t0)
                if state == "Playing":
                    before = b.call("rimworld/get_game_info", {}).get("ticksGame")
                    b.call("rimworld/step_game_ticks", {"ticks": 600})
                    after = b.call("rimworld/get_game_info", {}).get("ticksGame")
                    ran = isinstance(before, int) and isinstance(after, int) and after > before
                    step("step_game_ticks 600", ran, "ticksGame %s -> %s" % (before, after), t0)
            if a.then and state == "Playing":
                cenv = dict(env, RIMBRIDGE_HOST="127.0.0.1")
                r = subprocess.run(a.then, shell=True, env=cenv, capture_output=True, text=True, stdin=subprocess.DEVNULL)
                out = (r.stdout or "") + (r.stderr or "")
                with open(os.path.join(a.work, "then_output.txt"), "w", encoding="utf-8") as fh:
                    fh.write(out)
                step("then", r.returncode == 0, "exit %d; tail: %s" % (r.returncode, " | ".join(out.strip().splitlines()[-4:])[:600]), t0)
    except Exception as e:  # the reading is the point: record where it stopped
        step("stopped", False, "%s: %s" % (type(e).__name__, str(e)[:300]), t0)
    finally:
        text = open(log, encoding="utf-8", errors="replace").read() if os.path.exists(log) else ""
        res["log_lines"] = text.count("\n")
        res["first_exception"] = first_exception(text)
        if proc.poll() is None:
            proc.kill()
        res["killed"] = True
        with open(os.path.join(a.work, "result.json"), "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1)
        print("result: %s" % os.path.join(a.work, "result.json"))
    return 0 if res["steps"] and all(s["ok"] for s in res["steps"]) else 1


if __name__ == "__main__":
    sys.exit(main())
