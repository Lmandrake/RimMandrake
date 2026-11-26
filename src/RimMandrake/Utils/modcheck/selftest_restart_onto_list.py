#!/usr/bin/env python3
"""selftest_restart_onto_list.py - modcheck puts a game it holds onto the list it composed, by itself
(RIMMANDRAKE_MAKE_MODCHECK_RESTART_GAME_ONTO_ITS_LIST_THREE_HAND_WORKAROUNDS).

Three runs on 2026-11-25 did by hand what `run` now does when its caller holds the game's lock
(design/specs/2026-11-25-bottle-loop-map-wide/live_sitting.sh): stop the game, deploy, start it on the composed list.
And a composed list on Archmagi named kutte.stairs (from ModsConfig.MINIMAL.xml), which no folder on Archmagi holds,
so every composed run there read 'mod_not_installed'. The list writer now drops a base-list id that this host cannot
load, with a note, and keeps every id of the mods under test.

Offline, with stubs: no game, no lock, no real ModsConfig. The live acceptance is
design/specs/2026-11-26-modcheck-restart-onto-list/accept_live.py.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import runner  # noqa: E402

FAILS = []


def check(ok, msg, detail=""):
    print(("ok    " if ok else "FAIL  ") + msg + ("" if ok else "  %s" % (detail,))[:900])
    if not ok:
        FAILS.append(msg)


CONFIG = """<?xml version="1.0" encoding="utf-8"?>
<ModsConfigData>
  <version>1.6</version>
  <activeMods>
    <li>ludeon.rimworld</li>
    <li>ludeon.rimworld.anomaly</li>
    <li>brrainz.harmony</li>
    <li>kutte.stairs</li>
    <li>mandrake.rm.flowworks</li>
    <li>mandrake.rm.newmod</li>
  </activeMods>
  <knownExpansions>
    <li>kutte.stairs</li>
  </knownExpansions>
</ModsConfigData>
"""


def t_prune_drops_a_base_id_no_folder_holds():
    d = tempfile.mkdtemp(prefix="st_restart_")
    p = os.path.join(d, "ModsConfig.xml")
    with open(p, "w", encoding="utf-8") as f:
        f.write(CONFIG)
    installed = {"brrainz.harmony", "mandrake.rm.flowworks"}
    gone = runner.prune_uninstalled(["mandrake.rm.newmod"], config_path=p, installed=installed, alias={})
    act = runner.active_mods(p)
    check(gone == ["kutte.stairs"], "prune drops the base-list id that no install root holds", gone)
    check("kutte.stairs" not in act and "brrainz.harmony" in act and "mandrake.rm.flowworks" in act,
          "prune keeps every installed id", act)
    check("ludeon.rimworld.anomaly" in act, "prune keeps a DLC id (every DLC is assumed)", act)
    check("mandrake.rm.newmod" in act, "prune keeps an id of the mods under test even with no folder yet (deployed "
          "after the list is written)", act)
    with open(p, encoding="utf-8") as f:
        text = f.read()
    check("<knownExpansions>\n    <li>kutte.stairs</li>" in text, "prune touches only <activeMods>", text)
    with open(p, "w", encoding="utf-8") as f:
        f.write(CONFIG)
    gone = runner.prune_uninstalled([], config_path=p, installed=None, alias={}, _scan=lambda: None)
    check(gone == [] and "kutte.stairs" in runner.active_mods(p),
          "a blind install scan (None) prunes nothing: could not look is not 'not installed'", gone)
    with open(p, "w", encoding="utf-8") as f:
        f.write(CONFIG)
    gone = runner.prune_uninstalled([], config_path=p, installed={"brrainz.harmony", "mandrake.rm.flowworks",
                                                                  "mandrake.rm.biomes", "mandrake.rm.newmod"},
                                    alias={"kutte.stairs": "mandrake.rm.biomes"})
    check(gone == [], "a folded id held through its composed mod stays", gone)


class Calls:
    """A scripted _call: each argv is recorded; the answer is the first rule whose words are all in the argv."""

    def __init__(self, rules):
        self.rules = rules
        self.seen = []

    def __call__(self, argv, timeout=None, env=None):
        self.seen.append(list(argv))
        line = " ".join(str(a) for a in argv)
        for words, rc, out in self.rules:
            if all(w in line for w in words):
                if callable(out):
                    out = out()
                return subprocess.CompletedProcess(argv, rc, out, "")
        return subprocess.CompletedProcess(argv, 0, "", "")

    def verbs(self):
        out = []
        for a in self.seen:
            s = " ".join(str(x) for x in a)
            for v in ("game_lock.py mine", "stop --instance", "--force", "game_instance.py pid", "launch"):
                if v in s:
                    out.append(v)
                    break
        return out


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.t += s


def t_restart_only_on_a_game_this_process_holds():
    c = Calls([(["game_lock.py", "mine"], 1, "ArchSmall: HELD by BENCH for 'x': not this process's\n")])
    deployed = []
    r = runner.restart_onto_list([("Mock", None)], ["not loaded: a.mod"], game="b", _call=c,
                                 _deploy=lambda m: deployed.append(m))
    check(not r["restarted"] and "not this process" in r["refused"] and c.verbs() == ["game_lock.py mine"]
          and not deployed, "a game another driver holds is never stopped", (r, c.seen))
    c = Calls([(["game_lock.py", "mine"], 2, "ArchSmall: COULD NOT LOOK: the lock is UNREADABLE\n")])
    r = runner.restart_onto_list([("Mock", None)], ["x"], game="b", _call=c, _deploy=lambda m: None)
    check(not r["restarted"] and "COULD NOT LOOK" in r["refused"] and len(c.seen) == 1,
          "a lock that could not be read is never read as mine", (r, c.seen))


def t_restart_stops_deploys_launches_in_that_order():
    order = []
    up = ["50252\n"]

    def pid():
        return up.pop(0) if up else ""
    c = Calls([(["game_lock.py", "mine"], 0, "ArchSmall: MINE\n"), (["game_instance.py", "pid"], 0, pid),
               (["launch"], 0, "started game b, bridge on port 5175 after 40 s\n")])
    orig = c.__call__

    def call(argv, timeout=None, env=None):
        order.append(" ".join(str(a) for a in argv))
        return orig(argv, timeout)
    ck = Clock()
    r = runner.restart_onto_list([("Mock", None)], ["not loaded: a.mod"], game="b", _call=call,
                                 _deploy=lambda m: order.append("DEPLOY %s" % [x for x, _ in m]), _sleep=ck.sleep,
                                 _clock=ck)
    idx = {k: next((i for i, s in enumerate(order) if k in s), -1)
           for k in ("game_lock.py mine", "stop --instance b", "DEPLOY", "launch b --wait")}
    check(r["restarted"] and -1 not in idx.values()
          and idx["game_lock.py mine"] < idx["stop --instance b"] < idx["DEPLOY"] < idx["launch b --wait"],
          "mine, stop, deploy (game down), launch --wait: in that order", (r, order))
    check(not any("--force" in s for s in order), "a game that exits on the soft stop is not force-stopped", order)
    check(r.get("game") == "ArchSmall" and r.get("why") == ["not loaded: a.mod"] and r.get("steps"),
          "the record names the game, why, and each step", r)


def t_a_game_that_ignores_the_soft_stop_is_forced_once():
    c = Calls([(["game_lock.py", "mine"], 0, "MINE\n"), (["--force"], 0, "SUCCESS\n"),
               (["game_instance.py", "pid"], 0, lambda: "" if forced() else "50252\n"),
               (["launch"], 0, "started\n")])

    def forced():
        return any("--force" in " ".join(a) for a in c.seen)
    ck = Clock()
    r = runner.restart_onto_list([("Mock", None)], ["x"], game="b", _call=c, _deploy=lambda m: None, _sleep=ck.sleep,
                                 _clock=ck)
    check(r["restarted"] and forced() and ck.t >= runner.STOP_PATIENCE_S,
          "a game still up after the stop patience gets one --force stop, then the restart goes on", (r, ck.t))
    c = Calls([(["game_lock.py", "mine"], 0, "MINE\n"), (["game_instance.py", "pid"], 0, "50252\n")])
    ck = Clock()
    r = runner.restart_onto_list([("Mock", None)], ["x"], game="b", _call=c, _deploy=lambda m: None, _sleep=ck.sleep,
                                 _clock=ck)
    check(not r["restarted"] and "still running" in r["refused"] and "launch" not in c.verbs(),
          "a game that outlives the forced stop: no launch, the refusal says so", (r, c.verbs()))


def t_a_refused_stop_or_launch_is_named():
    envs = []
    c = Calls([(["game_lock.py", "mine"], 0, "MINE\n"), (["launch"], 0, "started\n")])

    def call(argv, timeout=None, env=None):
        envs.append((" ".join(str(a) for a in argv), env))
        return c(argv, timeout)
    saved = {k: os.environ.get(k) for k in ("RIMFLOW_SEAT", "WSLENV")}
    os.environ["RIMFLOW_SEAT"], os.environ["WSLENV"] = "BENCH", "RM_GAME_INSTANCE"
    try:
        runner.restart_onto_list([("Mock", None)], ["x"], game="b", _call=call, _deploy=lambda m: None)
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
    stop_env = next((e for a, e in envs if "stop --instance" in a), None) or {}
    check(stop_env.get("RIMFLOW_SEAT") == "BENCH" and "RIMFLOW_SEAT" in (stop_env.get("WSLENV") or "").split(":"),
          "the stop's wsl.exe child is given the seat through WSLENV (its bridge gate refuses a seatless call)",
          [(a[-60:], (e or {}).get("WSLENV")) for a, e in envs])
    c = Calls([(["game_lock.py", "mine"], 0, "MINE\n"), (["launch"], 1, "no port line after 3600 s\n")])
    r = runner.restart_onto_list([("Mock", None)], ["x"], game="b", _call=c, _deploy=lambda m: None)
    check("left stopped" in (r["refused"] or ""), "a refusal after the stop says the game is left stopped", r)
    c = Calls([(["game_lock.py", "mine"], 0, "MINE\n"), (["stop", "--instance"], 3, "REFUSED: his OWNER hold\n")])
    r = runner.restart_onto_list([("Mock", None)], ["x"], game="b", _call=c, _deploy=lambda m: None)
    check(not r["restarted"] and "OWNER hold" in r["refused"] and "launch" not in c.verbs(),
          "a refused stop: no deploy, no launch, the refusal is named", (r, c.verbs()))
    c = Calls([(["game_lock.py", "mine"], 0, "MINE\n"), (["launch"], 1, "no port line after 3600 s\n")])
    r = runner.restart_onto_list([("Mock", None)], ["x"], game="b", _call=c, _deploy=lambda m: None)
    check(not r["restarted"] and "no port line" in r["refused"], "a failed launch is named", r)


def t_a_deploy_that_meets_held_dlls_is_tried_again():
    def hung(m):
        raise subprocess.TimeoutExpired(["deploy_custom_mods.py"], 10800)
    c = Calls([(["game_lock.py", "mine"], 0, "MINE\n")])
    ck = Clock()
    try:
        r = runner.restart_onto_list([("Mock", None)], ["x"], game="b", _call=c, _deploy=hung, _sleep=ck.sleep, _clock=ck)
        ok = not r["restarted"] and "TimeoutExpired" in (r["refused"] or "")
    except subprocess.TimeoutExpired:
        ok, r = False, "raised"
    check(ok, "a hung deploy is a named refusal, never an escape with the game down", r)
    tries = []

    def deploy(m):
        tries.append(1)
        if len(tries) < 3:
            raise RuntimeError("deploy of Mock FAILED: cp: Invalid argument")
    c = Calls([(["game_lock.py", "mine"], 0, "MINE\n"), (["launch"], 0, "started\n")])
    ck = Clock()
    r = runner.restart_onto_list([("Mock", None)], ["x"], game="b", _call=c, _deploy=deploy, _sleep=ck.sleep, _clock=ck)
    check(r["restarted"] and len(tries) == 3, "a deploy refused while the exiting game holds its DLLs is tried again",
          (r, tries))
    tries.clear()

    def never(m):
        tries.append(1)
        raise RuntimeError("deploy of Mock FAILED: no About.xml")
    c = Calls([(["game_lock.py", "mine"], 0, "MINE\n"), (["launch"], 0, "started\n")])
    r = runner.restart_onto_list([("Mock", None)], ["x"], game="b", _call=c, _deploy=never, _sleep=ck.sleep, _clock=ck)
    check(not r["restarted"] and "no About.xml" in r["refused"] and len(tries) == runner.DEPLOY_TRIES
          and "launch" not in c.verbs(), "a deploy that keeps failing: no launch, the last error is named", (r, tries))


def hooks(log, owns=True, gap=("not loaded: a.mod",), restarted=True, deploy_fails=0):
    fails = [deploy_fails]

    def deploy(m):
        log.append("deploy")
        if fails[0]:
            fails[0] -= 1
            raise RuntimeError("deploy of Mock FAILED: Hum.dll is in use")
    return {"swap": lambda: log.append("swap"), "ids": lambda m: log.append("ids") or ["a.dep", "a.mod"],
            "compose": lambda ids: log.append("compose"), "prune": lambda ids: log.append("prune") or [],
            "owns": lambda: log.append("owns") or owns, "gap": lambda ids: log.append("gap") or list(gap),
            "restart": lambda m, why: log.append("restart") or {"restarted": restarted, "why": why,
                                                                "refused": None if restarted else "stop refused"},
            "deploy": deploy}


def t_prepare_restarts_only_when_the_running_load_is_not_the_list():
    log = []
    ids, rec = runner.prepare_live_list([("Mock", None)], keep=False, _hooks=hooks(log))
    check(ids == ["a.dep", "a.mod"] and rec["restarted"] and log == ["swap", "ids", "compose", "prune", "owns", "gap",
                                                                      "restart"],
          "held game on another list: compose, prune, then restart (which deploys with the game down)", log)
    log = []
    ids, rec = runner.prepare_live_list([("Mock", None)], keep=False, _hooks=hooks(log, gap=()))
    check(rec is None and log == ["swap", "ids", "compose", "prune", "owns", "gap", "deploy"],
          "held game already on the list: no restart, deploy as before", log)
    log = []
    ids, rec = runner.prepare_live_list([("Mock", None)], keep=False, _hooks=hooks(log, owns=False))
    check(rec is None and "restart" not in log and "gap" not in log and log[-1] == "deploy",
          "a game this process does not hold: never restarted (the old path)", log)
    log = []
    ids, rec = runner.prepare_live_list([("Mock", None)], keep=True, _hooks=hooks(log))
    check(rec is None and log == ["ids", "deploy"], "MODCHECK_KEEP_MODLIST: the caller's list, no swap, no restart",
          log)
    log = []
    ids, rec = runner.prepare_live_list([("Mock", None)], keep=False, _hooks=hooks(log, restarted=False))
    check(rec and not rec["restarted"] and log[-1] == "deploy",
          "a refused restart deploys as before; the run's load check then reads it UNMEASURED", log)
    log = []
    ids, rec = runner.prepare_live_list([("Mock", None)], keep=False, _hooks=hooks(log, gap=(), deploy_fails=1))
    check(rec and rec["restarted"] and log[-2:] == ["deploy", "restart"],
          "a deploy refused by the running game (held DLL) on a held game: restart, which deploys with it down", log)
    log = []
    os.environ["MODCHECK_STALE_KEEP_COMPOSED"] = "1"
    try:
        ids, rec = runner.prepare_live_list([("Mock", None)], keep=False, _hooks=hooks(log))
    finally:
        os.environ.pop("MODCHECK_STALE_KEEP_COMPOSED", None)
    check(rec is None and "owns" not in log and "restart" not in log,
          "MODCHECK_STALE_KEEP_COMPOSED (the SteveDesktop worker restarts its own game): never restarted here", log)
    log = []
    try:
        runner.prepare_live_list([("Mock", None)], keep=False, _hooks=hooks(log, owns=False, deploy_fails=1))
        raised = False
    except RuntimeError:
        raised = True
    check(raised, "a failed deploy on a game this process does not hold still raises", log)


def main():
    os.environ.pop("MODCHECK_STALE_KEEP_COMPOSED", None)
    t_prune_drops_a_base_id_no_folder_holds()
    t_restart_only_on_a_game_this_process_holds()
    t_restart_stops_deploys_launches_in_that_order()
    t_a_game_that_ignores_the_soft_stop_is_forced_once()
    t_a_refused_stop_or_launch_is_named()
    t_a_deploy_that_meets_held_dlls_is_tried_again()
    t_prepare_restarts_only_when_the_running_load_is_not_the_list()
    print("FAIL %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001 - a missing function is the red reading of this test, exit 1
        print("FAIL  %s: %s" % (type(e).__name__, e))
        sys.exit(1)
