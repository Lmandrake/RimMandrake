#!/usr/bin/env python3
"""launch_ready.py - launch RimWorld once through Steam and report READY only on a CURRENT-process receipt.

LAUNCHER_READY_HARDEN_OLD_LOG_LINES_LIE (2026-10-10). The old launch_and_wait.sh grepped Player.log for the
GABP marker after "seeing the log truncate"; it could print "log truncated" when nothing truncated, accept the
previous run's marker, and its exit code was wrong both ways ("TIMEOUT after 273s" on a load that came up at
1005 s). This replaces it. launch_and_wait.sh is now a thin wrapper around this file.

READY requires ALL of, in order:
  1. every pre-existing RimWorldWin64 killed by PID (not image name) and seen gone      else KILL_FAILED
  2. the old Player.log MOVED to an archive (so no old line can be read again)           else LOG_NOT_ROTATED
  3. exactly one new process whose start time is after the launch                       else LAUNCH_NO_PROCESS /
                                                                                              DUPLICATE_PROCESS
  4. a 'Bridge token:' line in a Player.log written after the launch, while that process
     stays alive                                                                         else PROCESS_EXITED /
                                                                                              DEADLINE_ALIVE
  5. the bridge port's LISTENING socket is owned by that PID                              else LISTENER_NOT_OURS
  6. rimbridge/ping answers through python.exe with this run's token                    else DISPATCHER_SILENT
  7. an audit of THIS run's log: 'Resetting mods config' -> MODS_RESET; the ModsConfig after load holding only
     ludeon.* -> CORE_ONLY. The first exception is recorded in the receipt, never fatal by itself.

Deadlines come from load_policy.json (one policy, shared with belt_watchdog). Past the warn threshold it says so
once; past the deadline it ends the ATTEMPT with DEADLINE_ALIVE and leaves the process running - a clock is not
evidence of a hang (stall verdicts belong to belt_watchdog's evidence).

    python3 src/RimMandrake/bridgetools/launch_ready.py              # launch, wait, print one verdict line
    python3 src/RimMandrake/bridgetools/launch_ready.py --no-kill    # refuse (ALREADY_RUNNING) if a game is up

Exit 0 READY; 1 any failure; 2 DEADLINE_ALIVE (process still running, not ready). The receipt JSON is written to
D:\\ClaudeWork\\rimmandrake\\scratch\\launch_receipts\\ and its path printed. DO NOT run this without holding the bridge.
"""
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
sys.path.insert(0, UTILS)

SLACK_S = 5.0                       # WSL vs Windows clock skew allowance for start-time / mtime comparisons
POLL_S = 2.0
TOKEN_RE = re.compile(r"\[RimBridge\]\s*Bridge token:\s*([0-9A-Za-z._\-]+)")
PORT_RE = re.compile(r"\[RimBridge\].*?on port\s+(\d+)")
EXC_RE = re.compile(r"^[^\s].*?(?:Exception|Could not resolve|Error while).*$", re.M)
RESET_MARK = "Resetting mods config"
FAIL_EXIT = {"READY": 0, "DEADLINE_ALIVE": 2}
SCRATCH = rm_str("scratch")


def exit_code(r):
    return FAIL_EXIT.get(r["verdict"], 1)


def _token(text):
    m = None
    for m in TOKEN_RE.finditer(text or ""):
        pass
    return m.group(1) if m else None


def _port(text):
    m = None
    for m in PORT_RE.finditer(text or ""):
        pass
    return int(m.group(1)) if m else None


def _first_exception(text):
    m = EXC_RE.search(text or "")
    return m.group(0)[:300] if m else None


def run(env, pol, kill_existing=True, log=print):
    r = {"verdict": None, "policy": pol.get("name"), "steps": []}

    def done(verdict, why=""):
        r["verdict"] = verdict
        r["why"] = why
        log("launch_ready: %s%s" % (verdict, (" - " + why) if why else ""))
        return r

    def step(s):
        r["steps"].append([round(env.now(), 1), s])

    # 1. pre-existing game: kill by PID, wait for it to be gone
    old = env.list_game_procs()
    if old:
        if not kill_existing:
            return done("ALREADY_RUNNING", "pids %s; rerun without --no-kill to replace it" % [p["pid"] for p in old])
        for p in old:
            env.kill_pid(p["pid"])
        step("killed %s" % [p["pid"] for p in old])
        t_k = env.now()
        while env.list_game_procs():
            if env.now() - t_k > pol["kill_existing_grace_s"]:
                return done("KILL_FAILED", "pids %s survived %ds" % (
                    [p["pid"] for p in env.list_game_procs()], pol["kill_existing_grace_s"]))
            env.sleep(POLL_S)

    # 2. archive the old log so no old line can ever be read as this run's
    r["archived_log"] = env.archive_log()
    text, _mt = env.read_log()
    if text is not None:
        return done("LOG_NOT_ROTATED", "Player.log still present after archive -> %s" % r["archived_log"])
    step("archived log")

    # 3. launch once, find exactly one new process
    t0 = env.now()
    r["launched_at"] = t0
    env.launch()
    step("launched")
    proc = None
    while proc is None:
        new = [p for p in env.list_game_procs() if p["start"] >= t0 - SLACK_S]
        if len(new) > 1:
            return done("DUPLICATE_PROCESS", "pids %s" % [p["pid"] for p in new])
        if new:
            proc = new[0]
            break
        if env.now() - t0 > pol["launch_to_process_s"]:
            return done("LAUNCH_NO_PROCESS", "no RimWorldWin64 started within %ds of the Steam launch "
                        "(Steam closed, update, dialog, or launch rejected)" % pol["launch_to_process_s"])
        env.sleep(POLL_S)
    r["pid"], r["proc_start"] = proc["pid"], proc["start"]
    step("process %s" % proc["pid"])

    # 4. token line from THIS run while THIS process lives
    r["warned"] = False
    token = text = None
    while True:
        procs = env.list_game_procs()
        mine = [p for p in procs if p["pid"] == proc["pid"] and abs(p["start"] - proc["start"]) < 1]
        others = [p for p in procs if p["pid"] != proc["pid"]]
        if not mine:
            return done("PROCESS_EXITED", "pid %s gone %ds after launch" % (proc["pid"], env.now() - t0))
        if others:
            return done("DUPLICATE_PROCESS", "pids %s alongside %s" % ([p["pid"] for p in others], proc["pid"]))
        text, mtime = env.read_log()
        if text is not None and mtime is not None and mtime >= t0 - SLACK_S:
            if RESET_MARK in text:
                r["first_exception"] = _first_exception(text)
                return done("MODS_RESET", "this run's log says '%s' - RimWorld fell back to a reduced list; read "
                            "the FIRST exception: %s" % (RESET_MARK, r["first_exception"]))
            token = _token(text)
            if token:
                break
        el = env.now() - proc["start"]
        if el > pol["process_to_bridge_warn_s"] and not r["warned"]:
            r["warned"] = True
            log("launch_ready: WARN no bridge token %ds after process start (warn threshold %ds): investigate "
                "with belt_watchdog; nothing is killed" % (el, pol["process_to_bridge_warn_s"]))
        if el > pol["process_to_bridge_deadline_s"]:
            r["first_exception"] = _first_exception(text)
            return done("DEADLINE_ALIVE", "pid %s alive, no bridge token after %ds; attempt ended, process LEFT "
                        "RUNNING - run belt_watchdog for evidence before any kill" % (proc["pid"], el))
        env.sleep(POLL_S)
    r["token_seen"] = token
    r["port"] = _port(text) or 5174
    step("token")

    # 5. the listener belongs to our process
    owner = env.listener_pid(r["port"])
    r["listener_pid"] = owner
    if owner != proc["pid"]:
        return done("LISTENER_NOT_OURS", "port %s listener pid %s, game pid %s" % (r["port"], owner, proc["pid"]))

    # 6. the dispatcher answers a trivial call
    t_d = env.now()
    while True:
        ok, detail = env.ping(r["port"], token)
        if ok:
            break
        if env.now() - t_d > pol["bridge_to_dispatcher_s"]:
            return done("DISPATCHER_SILENT", "rimbridge/ping: %s" % detail)
        env.sleep(POLL_S)
    step("ping")

    # 7. audit this run's log and the list the game actually started with
    text, _mt = env.read_log()
    r["first_exception"] = _first_exception(text)
    if text and RESET_MARK in text:
        return done("MODS_RESET", "this run's log says '%s'" % RESET_MARK)
    active = env.active_mods()
    r["active_count"] = None if active is None else len(active)
    if active is not None and active and all(a.lower().startswith("ludeon.") for a in active):
        return done("CORE_ONLY", "ModsConfig holds only %s - the full list was reset" % active)
    return done("READY", "pid %s, port %s, %s active mods, %ds from launch%s" % (
        proc["pid"], r["port"], r["active_count"], env.now() - t0,
        "; first exception: %s" % r["first_exception"][:120] if r["first_exception"] else ""))


# ---------------------------------------------------------------------------------------------- the real world

def _ps(cmd, timeout=60):
    p = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", cmd],
                       capture_output=True, text=True, timeout=timeout)
    return p.stdout.replace("\r", "")


class RealEnv:
    def __init__(self):
        import game_paths
        self.log_path = game_paths.PLAYER_LOG
        self.modsconfig = game_paths.MODS_CONFIG
        self.archive_dir = os.path.join(SCRATCH, "playerlog_archive")

    def now(self):
        return time.time()

    def sleep(self, s):
        time.sleep(s)

    def list_game_procs(self):
        out = _ps("Get-Process RimWorldWin64 -ErrorAction SilentlyContinue | ForEach-Object { '{0}|{1}' -f "
                  "$_.Id, ([DateTimeOffset]$_.StartTime).ToUnixTimeMilliseconds() }")
        procs = []
        for line in out.split("\n"):
            if "|" in line:
                a, b = line.strip().split("|", 1)
                procs.append({"pid": int(a), "start": int(b) / 1000.0})
        return procs

    def kill_pid(self, pid):
        subprocess.run(["taskkill.exe", "/PID", str(pid), "/F"], capture_output=True, timeout=60)

    def archive_log(self):
        if not os.path.exists(self.log_path):
            return None
        os.makedirs(self.archive_dir, exist_ok=True)
        dst = os.path.join(self.archive_dir, "Player.%s.log" % time.strftime("%Y%m%dT%H%M%S"))
        shutil.move(self.log_path, dst)
        return dst

    def launch(self):
        subprocess.run(["cmd.exe", "/c", "start", "", "steam://rungameid/294100"], cwd="/mnt/c",
                       capture_output=True, timeout=60)

    def read_log(self):
        try:
            mt = os.path.getmtime(self.log_path)
            with open(self.log_path, encoding="utf-8", errors="replace") as fh:
                return fh.read(), mt
        except OSError:
            return None, None

    def listener_pid(self, port):
        out = _ps("Get-NetTCPConnection -LocalPort %d -State Listen -ErrorAction SilentlyContinue | "
                  "Select-Object -ExpandProperty OwningProcess" % int(port)).split()
        return int(out[0]) if out and out[0].isdigit() else None

    def ping(self, port, token):
        try:
            p = subprocess.run(["python.exe", "rimbridge_client.py", "--port", str(port), "--token", token,
                                "--timeout", "20", "--call", "rimbridge/ping"], cwd=UTILS, capture_output=True,
                               text=True, timeout=60)
        except (OSError, subprocess.TimeoutExpired) as e:
            return False, str(e)
        return p.returncode == 0, (p.stdout + p.stderr).strip()[-200:]

    def active_mods(self):
        import xml.etree.ElementTree as ET
        try:
            am = ET.parse(self.modsconfig).getroot().find("activeMods")
            return [li.text.strip() for li in am.findall("li") if li.text]
        except (OSError, ET.ParseError, AttributeError):
            return None


def main(argv=None):
    import argparse
    import load_policy
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-kill", action="store_true", help="refuse if a game is already running")
    ap.add_argument("--profile", choices=("full", "minimal"), help="override the profile chosen from ModsConfig")
    a = ap.parse_args(argv)
    pol_all = load_policy.load()
    n = load_policy.active_count_from_modsconfig()
    name = a.profile or load_policy.profile_name(n, pol_all)
    pol = dict(pol_all["profiles"][name], name=name)
    print("launch_ready: profile %s (%s active mods in ModsConfig): warn %ds, deadline %ds, no kill on deadline"
          % (name, n, pol["process_to_bridge_warn_s"], pol["process_to_bridge_deadline_s"]))
    r = run(RealEnv(), pol, kill_existing=not a.no_kill)
    try:
        d = os.path.join(SCRATCH, "launch_receipts")
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, "launch_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(r, fh, indent=1)
        print("launch_ready: receipt %s" % path)
    except OSError as e:
        print("launch_ready: receipt NOT written: %s" % e)
    return exit_code(r)


if __name__ == "__main__":
    sys.exit(main())
