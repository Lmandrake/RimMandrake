#!/usr/bin/env python3
"""Read a dispatch tick, two local lock files and the alarm path with temporary state."""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / "rimflow")]
TMP = Path(tempfile.mkdtemp(prefix="ingame_visit_owed_"))
os.environ.update({
    "RM_DATA_ROOT": str(TMP / "data"), "RM_OPS_WATCH_DIR": str(TMP / "ops"),
    "RM_MATURATION_DISPATCH_DIR": str(TMP / "dispatch"), "RM_STREAMS_BENCH": str(TMP / "clone"),
    "RM_OWNER_HOLD_FILE": str(TMP / "holds.json"), "RM_CONTROL_DB": str(TMP / "control.db"),
    "RM_PIPELINE_PAUSE_FILE": str(TMP / "pause.json"), "RM_RUN_VOIDS_FILE": str(TMP / "voids.json"),
    "RIMFLOW_LEDGER": str(TMP / "ledger.jsonl"), "RIMFLOW_DRIVER_LOCK": str(TMP / "ArchBig.json"),
    "RM_INSTANCES_ROOT": str(TMP / "instances"), "RM_GAME_INSTANCE": "a", "RM_GAME_INSTANCES": "a,b",
    "RM_HOST": "archmagi",
})
os.environ.pop("METRONOME_DEADLINE", None)

import ops_watch as OW  # noqa: E402
import maturation_dispatch as MD  # noqa: E402
import control  # noqa: E402

control.init(os.environ["RM_CONTROL_DB"])
KEY = "maturation.ingame_visit_owed_no_driver_min"
AID = "INGAME_VISIT_NO_DRIVER:" + KEY
NOW = 1795400000
ROOT = TMP / "clone"
LOCKS = (TMP / "ArchBig.json", TMP / "instances" / "b" / "DRIVER_LOCK.json")
READING = TMP / "dispatch" / "reading.json"
VERSION = ROOT / "design" / "concepts" / "FlowWorks" / "version"
FAILS = []


def check(ok, message):
    print(("ok   " if ok else "FAIL ") + message)
    if not ok:
        FAILS.append(message)


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data) + "\n", encoding="utf-8")


def dispatch(age=60, *, now=NOW, checks=("bridge", "testq", "failed"), held=False, live=None, **visit):
    write(TMP / "holds.json", {"holds": [{"mod": "FlowWorks", "date": "2026-11-22", "said": "wait"}] if held else []})
    write(VERSION / "stage_record.json", {"stage": "in_game"})
    write(VERSION / "test_table.json", {"tests": {"bridge": {}, "failed": {}, "omitted": {},
                                                 "testq": {"testq": {}}}})
    write(VERSION / "in_game" / "visit_1" / "rows.jsonl", {"test": "bridge", "verdict": "PASS"})
    write(VERSION / "in_game" / "visit_2" / "rows.jsonl", {"test": "failed", "verdict": "FAIL"})
    facts = {"FlowWorks": dict({"stage": "in_game", "visit": 2, "opened": OW.iso(NOW - age * 60),
                                "owed": "run", "to_run": list(checks), "testq": ["testq"],
                                "live_units": [] if live is None else live}, **visit)}
    rd = MD.tick(str(ROOT), dict(MD.load_cfg(), advancing=["FlowWorks"], ingame_enabled=False), False, now=now,
                 fx={"autonomy": False, "facts": lambda: facts, "account": lambda: (True, ""), "known": set,
                     "releases": lambda: [], "convergence": lambda r, d: d, "code": lambda: "tree"})
    write(READING, rd)
    return rd


def point():
    return OW.COLLECTORS["maturation"](NOW, OW.load_rules(), {}).get(KEY) or {}


def sample(now, rd=None, **visit):
    if rd is None:
        dispatch(now=now, **visit)
    else:
        write(READING, dict(rd, at=now))
    OW.run(now=now, families=["maturation"], rules=dict(OW.load_rules(), targets=[]))
    return OW.read_json(OW.ops_dir() / "status.json")["points"].get(KEY) or {}


def waited(rd, minutes):
    for lag in range(minutes, -1, -10):
        p = sample(NOW - lag * 60, rd)
    OW.series_path("maturation").unlink()
    return p


def state(p):
    return (p.get("x") or {}).get("state")


def t_only_owed_bridge_checks_wait():
    rd = dispatch()
    p = waited(rd, 60)
    check(state(p) == "waiting" and p.get("v") == 60 and p.get("m") == "MEASURED",
          "only-owed-bridge-checks-wait: both Arch locks free, expected waiting at 60 min, got %s/%s"
          % (state(p), p.get("v")))
    waiting = rd.get("ingame_testq", {}).get("FlowWorks", {}).get("bridge_checks")
    check(waiting == ["bridge"],
          "only-owed-bridge-checks-wait: earlier PASS leaves a check owed, current FAIL and testq exclude theirs (%s)"
          % waiting)
    for label, kw in (("all checked or testq", {"checks": ("failed", "testq")}),
                      ("owner hold", {"held": True}), ("blocked visit", {"blocked": ["a hold"]}),
                      ("exit met", {"owed": "exit met"})):
        dispatch(**kw)
        p = point()
        check(state(p) == "quiet" and p.get("m") == "MEASURED" and p.get("v") == 0,
              "only-owed-bridge-checks-wait: %s reads 0 quiet (%s)" % (label, state(p)))


def t_either_game_driving_the_mod_is_busy():
    rd = dispatch()
    for game, lock in zip(("ArchBig", "ArchSmall"), LOCKS):
        write(lock, {"seat": "BENCH", "purpose": "RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_VISIT_TWO",
                     "identity": {"platform": "nt", "pid": 42}, "heartbeat": OW.iso(time.time())})
        p = point()
        check(state(p) == "busy" and p.get("m") == "MEASURED" and p.get("v") == 0,
              "either-game-driving-the-mod-is-busy: %s reads 0 busy (%s)" % (game, state(p)))
        lock.unlink()
    rd["ingame_testq"]["Pyrelands"] = dict(rd["ingame_testq"]["FlowWorks"], opened=OW.iso(NOW - 2400))
    rd["mods"]["Pyrelands"] = dict(rd["mods"]["FlowWorks"])
    for lag in (2400, 1800, 1200, 600):
        sample(NOW - lag, rd)
    write(LOCKS[0], {"seat": "BENCH", "purpose": "FlowWorks in-game acceptance visit 2",
                     "identity": {"platform": "nt", "pid": 42}, "heartbeat": OW.iso(time.time())})
    p = sample(NOW, rd)
    check(state(p) == "waiting" and p.get("v") == 40,
          "either-game-driving-the-mod-is-busy: a driver covers only its mod")
    LOCKS[0].unlink()
    p = sample(NOW + 60)
    check(state(p) == "waiting" and p.get("v") == 0,
          "either-game-driving-the-mod-is-busy: a covered mod restarts even when another mod kept waiting")
    OW.series_path("maturation").unlink()
    dispatch()
    write(LOCKS[1], {"seat": "BENCH", "purpose": "OtherFlowWorks in-game acceptance visit 2",
                     "identity": {"platform": "nt", "pid": 42}, "heartbeat": OW.iso(time.time())})
    p = point()
    LOCKS[1].unlink()
    check(state(p) == "waiting", "either-game-driving-the-mod-is-busy: an unrelated hold leaves it waiting")


def t_undriven_clock():
    p = sample(NOW - 120)
    check(state(p) == "waiting" and p.get("v") == 0, "undriven-clock: the first observation starts at zero")
    write(LOCKS[0], {"seat": "BENCH", "purpose": "FlowWorks in-game acceptance visit 2",
                     "identity": {"platform": "nt", "pid": 42}, "heartbeat": OW.iso(time.time())})
    check(state(sample(NOW - 60)) == "busy", "undriven-clock: observed the driver before release")
    LOCKS[0].unlink()
    p = sample(NOW)
    check(state(p) == "waiting" and p.get("v") == 0,
          "undriven-clock: after a driver releases, expected waiting/0, got %s/%s" % (state(p), p.get("v")))
    p = sample(NOW + 600)
    check(state(p) == "waiting" and p.get("v") == 10,
          "undriven-clock: consecutive waiting for one visit keeps the start (%s)" % p.get("v"))
    p = sample(NOW + 660, visit=3)
    check(state(p) == "waiting" and p.get("v") == 0, "undriven-clock: a different visit restarts the clock")
    check(state(sample(NOW + 720, checks=())) == "quiet", "undriven-clock: observed that nothing was owed")
    p = sample(NOW + 780, visit=3)
    check(state(p) == "waiting" and p.get("v") == 0, "undriven-clock: work newly owed restarts the clock")
    LOCKS[1].write_text("broken", encoding="utf-8")
    check(sample(NOW + 840, visit=3).get("m") == "UNMEASURED", "undriven-clock: observed an unreadable lock")
    LOCKS[1].unlink()
    p = sample(NOW + 900, visit=3)
    check(state(p) == "waiting" and p.get("v") == 0, "undriven-clock: a blind reading breaks the wait")
    p = sample(NOW + 900 + OW.compose_max_age_s(OW.load_rules())[0] + 1, visit=3)
    check(state(p) == "waiting" and p.get("v") == 0, "undriven-clock: a stale previous reading breaks the wait")
    OW.series_path("maturation").unlink()


def t_live_pipeline_visit_is_busy():
    unit = "rm-bench-flowworks-in-game-visit"
    rd = dispatch(live=[unit])
    check(rd["mods"]["FlowWorks"]["stage"] == "in_game" and rd["mods"]["FlowWorks"]["live"] == [unit],
          "live-pipeline-visit-is-busy: the dispatch tick names the in-game unit")
    run = subprocess.run
    for life, expected in (("active", "busy"), ("not-found", "waiting"), ("unknown", "UNMEASURED")):
        def probe(cmd, **kw):
            if cmd[0] == "systemctl":
                if life == "unknown":
                    raise subprocess.TimeoutExpired(cmd, kw["timeout"])
                return subprocess.CompletedProcess(cmd, 0, life + "\n", "")
            return run(cmd, **kw)

        with patch.object(subprocess, "run", side_effect=probe):
            p = point()
        got = state(p) or p.get("m")
        check(got == expected and (p.get("v") is None if expected == "UNMEASURED" else p.get("m") == "MEASURED")
              and (expected != "busy" or p.get("v") == 0),
              "live-pipeline-visit-is-busy: %s in-game unit with free locks, expected %s, got %s"
              % ({"active": "an active", "not-found": "a not-found", "unknown": "an unknown"}[life], expected, got))
    dispatch(live="UNMEASURED")
    p = point()
    check(p.get("m") == "UNMEASURED" and p.get("v") is None,
          "live-pipeline-visit-is-busy: unreadable dispatch occupancy is UNMEASURED (%s)" % p.get("m"))
    rd = dispatch()
    rd["mods"]["FlowWorks"].update(decision="launched", unit=unit, launch={"rule": "decide_ingame"})
    write(READING, rd)
    with patch("role_launch.unit_state", return_value="active"):
        p = point()
    check(state(p) == "busy", "live-pipeline-visit-is-busy: a unit launched on this tick covers the visit")


def t_could_not_look_is_unmeasured():
    rd = dispatch()
    LOCKS[1].write_text("broken", encoding="utf-8")
    p = point()
    LOCKS[1].unlink()
    check(p.get("m") == "UNMEASURED" and p.get("v") is None and "ArchSmall" in (p.get("why") or ""),
          "could-not-look-is-unmeasured: unreadable ArchSmall (%s)" % p.get("m"))
    with patch.dict(os.environ, {"RM_GAME_INSTANCES": "a"}):
        p = point()
    check(p.get("m") == "UNMEASURED", "could-not-look-is-unmeasured: one missing Arch game (%s)" % p.get("m"))
    with patch.dict(os.environ, {"RM_HOST": "stevedesktop"}):
        p = point()
    check(p.get("m") == "UNMEASURED", "could-not-look-is-unmeasured: a different game host (%s)" % p.get("m"))
    rd["at"] = NOW - 1801
    write(READING, rd)
    p = point()
    check(p.get("m") == "UNMEASURED", "could-not-look-is-unmeasured: stale dispatch reading (%s)" % p.get("m"))
    rd["at"] = NOW
    rd["ingame_testq"]["FlowWorks"].pop("bridge_checks", None)
    write(READING, rd)
    p = point()
    check(p.get("m") == "UNMEASURED", "could-not-look-is-unmeasured: old dispatch schema (%s)" % p.get("m"))
    with patch.dict(os.environ, {"METRONOME_DEADLINE": "0"}):
        dispatch()
        p = point()
    check(p.get("m") == "UNMEASURED", "could-not-look-is-unmeasured: sense beat out of time (%s)" % p.get("m"))
    (VERSION / "in_game" / "visit_2" / "rows.jsonl").write_text("broken", encoding="utf-8")
    # The dispatch extractor must tell an unreadable row file from an empty one.
    rd = MD.ingame_testq(str(ROOT), {"FlowWorks": {"stage": "in_game", "visit": 2, "opened": OW.iso(NOW - 3600),
                                                   "to_run": ["bridge"]}}, {})
    write(READING, {"at": NOW, "ingame_testq": rd})
    p = point()
    check(p.get("m") == "UNMEASURED", "could-not-look-is-unmeasured: unreadable visit rows (%s)" % p.get("m"))


def t_alarm_crosses_and_reopens():
    rules = OW.load_rules()
    rd = dispatch()
    check(OW.target_state({KEY: waited(rd, 30)}, rules).get(AID) is False,
          "alarm-crosses-and-reopens: 30 min is clear")
    points = {KEY: waited(rd, 60)}
    check(OW.target_state(points, rules).get(AID) is True, "alarm-crosses-and-reopens: 60 min crosses the rule")
    log = TMP / "conductor.md"
    tg = next((t for t in rules["targets"] if t.get("key") == KEY), {})
    configured = tg.get("conductor_log") == "/mnt/d/ClaudeWork/rimmandrake/conductor/log.md"
    if tg:
        tg["conductor_log"] = str(log) if configured else None
    check(configured, "alarm-crosses-and-reopens: the configured sink is the Conductor log")
    calls = []

    def file(todo, conf):
        calls.extend(todo)
        return {a["name"]: None for a in todo}

    alarm = OW.run_alarms(points, rules, NOW, set(), file, open_ids=set()).get(AID) or {}
    name = alarm.get("item")
    if name:
        OW.run_alarms(points, rules, NOW + 60, {name}, file, open_ids=set())
    check(bool(name and name.startswith("OPS_INGAME_VISIT_DRIVE_") and len(calls) == 2
               and calls[1].get("reopen") and calls[1]["name"] == name),
          "alarm-crosses-and-reopens: the same alarm item reopens (%s)" % name)
    check(log.exists() and log.read_text(encoding="utf-8").count("ALARM " + (name or "?")) == 2,
          "alarm-crosses-and-reopens: opening and reopening write the temporary Conductor log")


def main():
    t_only_owed_bridge_checks_wait()
    t_either_game_driving_the_mod_is_busy()
    t_undriven_clock()
    t_live_pipeline_visit_is_busy()
    t_could_not_look_is_unmeasured()
    t_alarm_crosses_and_reopens()
    print("modules: %s %s" % (OW.__file__, MD.__file__))
    print("selftest_ingame_visit_owed: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return bool(FAILS)


if __name__ == "__main__":
    sys.exit(main())
