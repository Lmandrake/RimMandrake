#!/usr/bin/env python3
"""Offline selftest of the retired Dispatcher step `owed_sources` (owed.py sync-sources) and of the homes that do its work
now: one test per promise on design/specs/2026-11-23-owed-sources-retired/boundary.md
(RIMMANDRAKE_RETIRE_OR_REPAIR_OWED_SOURCES_KILLED_EVERY_TICK: killed on 210 of 210 passes on 2026-11-22 UTC).

    python3 src/RimMandrake/rimflow/selftest_owed_sources.py      # exit 0 and "PASS n/n"
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import dispatcher as D  # noqa: E402
import detached_helper as DH  # noqa: E402
import maturation_autonomy as AUT  # noqa: E402
import maturation_now as MN  # noqa: E402
import seat_restart as SR  # noqa: E402

RESULTS = []
OLD_QUEUE = "untracked_" + "promises"       # spelled apart: this file is under src, which must not name it


def check(ok, what):
    RESULTS.append((bool(ok), what))


class It:
    def __init__(self, state):
        self.state = state
        self.open = state not in ("done", "dropped", "superseded")


def t_no_step_in_the_dispatcher():
    sch = json.load(open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8"))
    check("owed_sources_every_s" not in sch, "dispatcher_schedule.json does not hold owed_sources_every_s")
    for key in (300, None):
        started, journalled = [], []
        saved = D.subprocess.Popen, D.subprocess.run, D.journal

        def spy(argv, *a, **k):
            started.append(" ".join(map(str, argv)) if isinstance(argv, (list, tuple)) else str(argv))
            raise OSError("the test starts no child")

        old = {"ledger_notes": False, "publish": True}       # the note and publish path on, as in a live pass
        if key:
            old["owed_sources_every_s"] = key
        fx = {"lock": lambda: open(os.devnull, "w"), "paused": lambda: None, "publish": lambda n: None,
              "owed_sources": lambda *a: started.append("owed_sources ran") or "ran"}
        D.subprocess.Popen, D.subprocess.run = spy, spy
        D.journal = lambda root, rec: journalled.append(rec)
        try:
            D.execute([], old, {"alarms": {}}, tempfile.mkdtemp(prefix="owed_disp_"), True, 1000.0, fx=fx,
                      deadline=10 ** 12)
            err = None
        except Exception as e:  # noqa: BLE001 - said in the check
            err = "%s: %s" % (type(e).__name__, e)
        finally:
            D.subprocess.Popen, D.subprocess.run, D.journal = saved
        check(err is None, "an applied pass ends (old key %s): %s" % (key, err))
        check(not [s for s in started if "owed" in s] and not [r for r in journalled if r.get("do") == "owed_sources"],
              "an applied pass starts no owed.py and journals no owed_sources (old key %s): %s" % (key, started))
    check(not hasattr(D, "owed_sources"), "dispatcher.py has no owed_sources")


def t_old_command_is_refused():
    tmp = tempfile.mkdtemp(prefix="owed_old_cmd_")            # a throwaway ledger: a regressed copy never files for real
    env = dict(os.environ, RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"), RIMFLOW_ITEMS=tmp, RIMFLOW_SEAT="BENCH")
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "owed.py"), "sync-sources"], cwd=REPO, env=env,
                           capture_output=True, text=True, timeout=60)     # hang guard: the old read ran past 110 s
        rc, out = r.returncode, r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        rc, out = "still running at 60 s", ""
    check(rc == 2 and "check-pointers" in out and "OWED " not in out,
          "owed.py sync-sources exits 2 naming the commands that exist (rc %s: %s)" % (rc, out[-160:].strip()))


def t_a_size_kill_writes_no_queue():
    tmp = tempfile.mkdtemp(prefix="owed_kill_")
    tx = os.path.join(tmp, "t.jsonl")
    with open(tx, "w") as f:
        f.write(json.dumps({"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "text", "text": "When the slot frees I will launch it."}]}}) + "\n")
    sch = {"seat_restart": {"enabled": True, "seats": {"BENCH": {"kind": "conductor", "backstop": True}}}}
    st = {"seat_restart": {"BENCH": {"state": "claimed", "source": "backstop", "start": 77, "ts": 1.0, "tx_path": tx}}}
    a = {"do": "restart_kill", "seat": "BENCH", "pid": 4242, "session_id": "S", "session_name": "CONDUCTOR",
         "argv": ["claude"]}
    queued = []
    fx = {"session_file": lambda pid: {"sessionId": "S", "name": "CONDUCTOR", "status": "idle"},
          "recheck": lambda *x: [], "start": lambda pid: 77, "write_killed": lambda *x: None,
          "final": lambda *x: [], "kill": lambda pid, start=None: "SIGTERM, exited",
          "promises": lambda seat, rs: queued.append(seat) or "queued 1"}
    res = SR.execute(a, sch, st, True, 100.0, fx)
    check(str(res).startswith("killed"), "a backstop kill still kills the window (%s)" % str(res)[:80])
    check(not queued and "promises" not in st["seat_restart"]["BENCH"], "a backstop kill queues no promise (%s)" % queued)
    named, looked = [], 0
    for top in ("src", ".claude"):
        for d, dirs, files in os.walk(os.path.join(REPO, top)):
            dirs[:] = [x for x in dirs if x not in ("__pycache__", "bin", "obj", "Textures")]
            for n in files:
                if n.endswith((".py", ".sh", ".json", ".md")):
                    looked += 1
                    with open(os.path.join(d, n), encoding="utf-8", errors="replace") as f:
                        if OLD_QUEUE in f.read():
                            named.append(os.path.join(top, n))
    check(looked > 100 and not named, "no code file names the old queue (%d read): %s" % (looked, named))


def t_cycle_limit_is_paused():
    row = {"mod": "Pyrelands", "decision": "cycle_limit", "why": "three blind cycles in this visit ended not met"}
    AUT._klass({}, {}, row, 1000.0, {})
    rd = AUT.annotate({"mods": {}}, [row])
    check(row.get("klass") == "paused" and len(rd["paused"]) == 1 and rd["paused"][0].startswith("Pyrelands: "),
          "a cycle_limit row is paused and listed (%s, %s)" % (row.get("klass"), rd["paused"]))


def t_his_card_is_in_the_log():
    wrote, st = [], {}
    rows = [{"mod": "FlowWorks", "klass": "owner", "card": "FlowWorks 0.1.0 stands at his walk."},
            {"mod": "Other", "klass": "wait", "card": "not his"}]
    for _ in range(2):
        AUT.post_cards(rows, st, 1000.0, {"card": wrote.append})
    check(len(wrote) == 1 and "FlowWorks 0.1.0 stands at his walk." in wrote[0],
          "an owner card is written to the Conductor log once (%d)" % len(wrote))


def t_run_left_open_is_a_need():
    rec = {"unit": "rm-detached-x-1", "item": "RIMMANDRAKE_X_LEFT_OPEN", "result": "success (exited 0)", "at": 1.0,
           "owed_close": "open"}
    for state, want in (("doing", 1), ("done", 0)):
        lines = DH.owed_lines([rec], {"RIMMANDRAKE_X_LEFT_OPEN": It(state)}, [])
        got = MN.conductor_needs([], {}, 1000.0, owed=lines)["conductor"]
        check(len(got) == want and all("rm-detached-x-1" in g for g in got),
              "a run left open with its item %s is %d need(s): %s" % (state, want, got))


def main():
    t_no_step_in_the_dispatcher()
    t_old_command_is_refused()
    t_a_size_kill_writes_no_queue()
    t_cycle_limit_is_paused()
    t_his_card_is_in_the_log()
    t_run_left_open_is_a_need()
    passed = sum(ok for ok, _ in RESULTS)
    for ok, what in RESULTS:
        print("%s  %s" % ("ok  " if ok else "FAIL", what))
    print("%s %d/%d" % ("PASS" if passed == len(RESULTS) else "FAIL", passed, len(RESULTS)))
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
