#!/usr/bin/env python3
"""The sense phase runs apart from the beat, under a hang guard (RIMMANDRAKE_SIZE_SENSE_STEP_LIMIT_FIFTEEN_SECONDS_NOBODY_
CAN_SOURCE). Page: design/specs/2026-11-23-sense-apart-from-beat/boundary.md; each test is named for its promise.
Real subprocesses, process groups and flocks in temp dirs, as selftest_metronome.py; no live store, no live unit."""
import json
import math
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import metronome as m  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="metronome_apart_selftest_"))
FAILS = []
KID = r'''
import json, os, sys, time
mode, arg = sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
with open(os.environ["KID_LOG"], "a") as f:
    f.write(json.dumps({"mode": mode, "phase": os.environ["METRONOME_PHASE"], "dir": os.environ["METRONOME_DIR"],
                        "gen": os.environ["METRONOME_GEN"], "t": time.time()}) + "\n")
time.sleep(arg)
with open(os.environ["METRONOME_OUT"], "w") as f:
    json.dump({"payload": {"mode": mode}, "observed_at": time.time()}, f)
'''
KIDP = TMP / "kid.py"
KIDP.write_text(KID)
os.environ["KID_LOG"] = str(TMP / "kid.jsonl")


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  %s" % (detail,)))
    if not cond:
        FAILS.append(name)


def table(sense_arg=0.0, sense_limit=120, apart=True, mode="sleep"):
    t = {"budget_s": 45, "phases": {}}
    for n in m.ORDER:
        t["phases"][n] = {"every": 1, "limit_s": 2, "cleanup_s": 0.5, "argv": ["{python}", str(KIDP), "quick", "0"]}
    t["phases"]["sense"].update({"limit_s": sense_limit, "cleanup_s": 1,
                                 "argv": ["{python}", str(KIDP), mode, str(sense_arg)]})
    if apart:
        t["phases"]["sense"]["apart"] = True
    t["phases"]["remember"]["reads"] = {"sense": 900}
    return t


_N = [0]


def lt(t):
    """The table through the real loader (a file, as the units read it)."""
    _N[0] += 1
    p = TMP / ("table_%d.json" % _N[0])
    p.write_text(json.dumps(t))
    return m.load_table(str(p))


def run_sense(d, t):
    """The sense phase as the shipped units run it: apart when the code has it, else inside a beat (the parent)."""
    if hasattr(m, "apart"):
        return m.apart(d, t, "sense")
    return m.beat(d, t)


SHIPPED = json.loads((HERE / "systemd" / "metronome_phases.json").read_text())["phases"]["sense"]


def kid_lines():
    p = TMP / "kid.jsonl"
    return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []


def lines(d):
    p = d / "beats.jsonl"
    return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []


def fresh(name):
    d = TMP / name
    d.mkdir()
    (TMP / "kid.jsonl").unlink(missing_ok=True)
    return d


def t_the_beat_never_runs_an_apart_phase():
    d = fresh("beat_skips")
    t = lt(table(sense_arg=30))
    t0 = time.time()
    m.beat(d, t)
    took = time.time() - t0
    ran = [k["phase"] for k in kid_lines()]
    check("the-beat-never-runs-an-apart-phase: the beat runs every phase but the apart one", "sense" not in ran
          and "dispatch" in ran and not [x for x in lines(d) if x.get("phase") == "sense"], (ran, lines(d)))
    disp = [k for k in kid_lines() if k["phase"] == "dispatch"]
    check("the-beat-never-runs-an-apart-phase: dispatch starts within seconds although sense would take 30 s",
          disp and disp[0]["t"] - t0 < 10 and took < 15, (took, disp))
    bad = table(sense_limit=120, apart=False)
    try:
        lt(bad)
        refused = False
    except ValueError:
        refused = True
    ok_apart = True
    try:
        lt(table(sense_limit=120, apart=True))
    except ValueError:
        ok_apart = False
    check("the-beat-never-runs-an-apart-phase: a 120 s sense fits only apart (the beat's budget does not count it)",
          refused and ok_apart, (refused, ok_apart))


def t_an_apart_phase_runs_in_its_own_dir():
    d = fresh("own_dir")
    t = lt(table(sense_arg=0))
    m.beat(d, t)
    rc = m.apart(d, t, "sense")
    sd = d / "apart" / "sense"
    k = [x for x in kid_lines() if x["phase"] == "sense"]
    ls = [x for x in lines(d) if x.get("phase") == "sense"]
    check("an-apart-phase-runs-in-its-own-dir: its state, generation and output live under apart/sense",
          rc == 0 and (sd / "state.json").exists() and (sd / "out" / "sense.json").exists()
          and m.load_state(sd)["generation"] == 1 and m.load_state(d)["generation"] == 1, (rc, os.listdir(d)))
    check("an-apart-phase-runs-in-its-own-dir: the child's METRONOME_DIR is the apart dir, and it may act there",
          k and k[0]["dir"] == str(sd) and m.may_act(sd, "sense", int(k[0]["gen"]))[0], k)
    check("an-apart-phase-runs-in-its-own-dir: its line is in the shared beats.jsonl, marked apart",
          len(ls) == 1 and ls[0].get("apart") is True and ls[0].get("exit") == 0, ls)
    m.beat(d, t)
    check("an-apart-phase-runs-in-its-own-dir: a beat does not supersede the apart generation",
          m.may_act(sd, "sense", 1)[0], m.may_act(sd, "sense", 1))


def t_a_slow_collector_completes():
    d = fresh("slow")
    tb = table(sense_arg=20, sense_limit=SHIPPED["limit_s"], apart=bool(SHIPPED.get("apart")))
    tb["phases"]["sense"]["cleanup_s"] = SHIPPED["cleanup_s"]
    t = lt(tb)
    t0 = time.time()
    rc = run_sense(d, t)
    ls = [x for x in lines(d) if x.get("phase") == "sense"]
    check("a-slow-collector-completes: a 20 s sense pass under the shipped limit (%s s) exits 0 and publishes"
          % SHIPPED["limit_s"],
          rc == 0 and ls and ls[-1].get("exit") == 0 and ls[-1].get("published") is True and time.time() - t0 >= 19,
          ls)


def t_a_hung_collector_is_stopped():
    d = fresh("hung")
    t = lt(table(sense_arg=3600, sense_limit=3))
    t0 = time.time()
    m.apart(d, t, "sense")
    took = time.time() - t0
    ls = [x for x in lines(d) if x.get("phase") == "sense"]
    sd = d / "apart" / "sense"
    check("a-hung-collector-is-stopped: a pass that never returns is killed at limit_s and fenced",
          took < 10 and ls and ls[-1].get("exit") == "overrun" and 1 in m.fenced(sd, "sense"), (took, ls))
    t2 = lt(table(sense_arg=0))
    rc = m.apart(d, t2, "sense")
    check("a-hung-collector-is-stopped: the next apart run is not blocked", rc == 0
          and lines(d)[-1].get("exit") == 0, lines(d)[-1:])


def t_a_reader_finds_an_apart_output():
    d = fresh("reader")
    t = lt(table(sense_arg=0))
    m.apart(d, t, "sense")
    m.beat(d, t)
    rem = [x for x in lines(d) if x.get("phase") == "remember"]
    check("a-reader-finds-an-apart-output: a phase that reads sense finds it in the apart dir",
          rem and rem[-1].get("exit") == 0, rem)
    rec, why = m.read_output(m.phase_dir(d, t, "sense"), "sense")
    check("a-reader-finds-an-apart-output: read_output in phase_dir finds it", rec is not None, why)
    p = TMP / "reader_table.json"
    p.write_text(json.dumps(table(sense_arg=0)))
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = m.main(["read", "--phase", "sense", "--dir", str(d)])
    check("a-reader-finds-an-apart-output: `metronome.py read --phase sense` finds it", rc == 0, buf.getvalue())


def t_the_round_bound_reads_the_sense_unit():
    import ops_watch as OW
    p = TMP / "bound_table.json"
    tb = table(sense_limit=120)
    tb["phases"]["sense"]["per_beat"] = 2
    p.write_text(json.dumps(tb))
    tm = TMP / "rm-metronome-sense.timer"
    tm.write_text("[Timer]\nOnUnitInactiveSec=60s\nAccuracySec=5s\n")
    b, why = OW.compose_round_bound_s(phases=p, sense_timer=tm, n_families=21)
    want = math.ceil(21 / 2) * (60 + 5 + 120 + 1)
    check("the-round-bound-reads-the-sense-unit: gap from the sense timer, pass length limit+cleanup, no retry beats",
          b == want, (b, want, why))
    tb = json.loads(p.read_text())
    tb["phases"]["sense"].update(limit_s=1300, pass_s=120)
    p.write_text(json.dumps(tb))
    b, why = OW.compose_round_bound_s(phases=p, sense_timer=tm, n_families=21)
    check("the-round-bound-reads-the-real-pass: pass_s, not the hang guard, is a healthy pass", b == want, (b, want, why))


def main():
    for t in (t_the_beat_never_runs_an_apart_phase, t_an_apart_phase_runs_in_its_own_dir, t_a_slow_collector_completes,
              t_a_hung_collector_is_stopped, t_a_reader_finds_an_apart_output, t_the_round_bound_reads_the_sense_unit):
        try:
            t()
        except (Exception, SystemExit) as e:  # noqa: BLE001  a test that raises is a red, named
            check("%s raised %s: %s" % (t.__name__, type(e).__name__, e), False)
    print("selftest_metronome_apart: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
