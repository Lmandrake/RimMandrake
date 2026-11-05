#!/usr/bin/env python3
"""selftest_metronome: metronome.py's beat against planted faults (OPS_METRONOME_PROVE_IN_SHADOW; strategy §2, §6 last
row: "Shadow must also pass planted crashes, overruns and a duplicate run of the same phase"). Every phase is a planted
child (kid.py, written to a temp dir) run through the real beat path: real subprocesses, real process groups, real
signals, real flocks. Cases: a crashing phase, an overrun that ignores SIGTERM, one that cleans up on SIGTERM, a
straggler left in the group, a child that escapes the group and tries to publish late, a superseded generation, a
duplicate beat, the beat itself SIGKILLed mid-phase, the total budget with ring/raise reserved and a deferred phase
that cannot starve, operation ids through a crash between act and record, wall-clock slots across a restart,
round-robin persistence, a stale reading refused, health from useful work, and the shipped table."""
import ast
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import metronome as m  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="metronome_selftest_"))
FAILS = []

KID = r'''
import json, os, signal, subprocess, sys, time
mode = sys.argv[1]
arg = float(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else 0.0
out = os.environ["METRONOME_OUT"]
def stage(obs=None):
    with open(out, "w") as f:
        json.dump({"payload": {"mode": mode, "gen": os.environ["METRONOME_GEN"]},
                   "observed_at": obs if obs is not None else time.time()}, f)
if mode == "ok":
    stage()
elif mode == "old":
    stage(time.time() - 10000)
elif mode == "crash":
    sys.exit(3)
elif mode == "sleep":
    time.sleep(arg); stage()
elif mode == "ignore_term":
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    open(os.environ["KID_MARK"], "w").write(str(os.getpid()))
    time.sleep(arg)
elif mode == "term_cleanup":
    def bye(*a):
        open(os.environ["KID_MARK"], "w").write("cleaned")
        sys.exit(0)
    signal.signal(signal.SIGTERM, bye)
    time.sleep(arg)
elif mode == "straggler":
    p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    open(os.environ["KID_MARK"], "w").write(str(p.pid))
    stage()
elif mode == "escape":
    if os.fork() == 0:
        os.setsid()
        if os.fork() == 0:
            open(os.environ["KID_MARK"] + ".pid", "w").write(str(os.getpid()))
            time.sleep(2.5)
            with open(out, "w") as f:
                json.dump({"payload": "late", "observed_at": time.time()}, f)
            r = subprocess.run([sys.executable, os.environ["MET"], "publish", "--phase",
                                os.environ["METRONOME_PHASE"], "--gen", os.environ["METRONOME_GEN"], "--file", out,
                                "--dir", os.environ["METRONOME_DIR"]], capture_output=True, text=True)
            open(os.environ["KID_MARK"], "w").write("%d %s" % (r.returncode, r.stdout.strip()))
        os._exit(0)
    time.sleep(arg)
'''
KIDP = TMP / "kid.py"
KIDP.write_text(KID)
os.environ["MET"] = str(HERE / "metronome.py")


def ok(cond, what):
    if not cond:
        FAILS.append(what)
    print(("PASS " if cond else "FAIL ") + what)


def table(budget=45, **ph):
    """Every phase ok and quick unless overridden: ph[name] = (mode, arg) or a dict merged in."""
    t = {"budget_s": budget, "phases": {}}
    for n in m.ORDER:
        t["phases"][n] = {"every": 1, "limit_s": 1, "cleanup_s": 0.5,
                          "argv": ["{python}", str(KIDP), "ok"]}
    for n, v in ph.items():
        if isinstance(v, tuple):
            t["phases"][n]["argv"] = ["{python}", str(KIDP)] + [str(x) for x in v]
        else:
            t["phases"][n].update(v)
    return t


def fresh(name):
    d = TMP / name
    d.mkdir()
    return d


def lines(d):
    p = d / "beats.jsonl"
    return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []


def by(d, beat, phase):
    r = [x for x in lines(d) if x.get("beat") == beat and x["phase"] == phase]
    return r[-1] if r else None


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    try:                                   # a zombie is dead
        return Path("/proc/%d/stat" % pid).read_text().split(")")[1].split()[0] != "Z"
    except FileNotFoundError:
        return False


def wait_for(cond, timeout):
    end = time.time() + timeout
    while time.time() < end:
        if cond():
            return True
        time.sleep(0.05)
    return False


def write_table(path, t):
    path.write_text(json.dumps(t))
    return path


# 1. the shipped table, and a table whose reserve cannot fit
t = m.load_table()
ok(t["budget_s"] == 45, "shipped table: the beat's total budget is 45 s")
res = sum(t["phases"][n]["limit_s"] + t["phases"][n]["cleanup_s"] for n in m.RESERVED)
ok(m.RESERVED == ("raise", "ring") and res <= 45, "shipped table: raise and ring are reserved and fit (%.0f s)" % res)
src = (HERE / "ops_watch.py").read_text()
fams = None
for node in ast.parse(src).body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "FAMILIES":
        fams = list(ast.literal_eval(node.value))
sense = t["phases"]["sense"]
ok(fams is not None and sorted(sense["families"]) == sorted(fams),
   "shipped table: sense's round robin covers exactly ops_watch.FAMILIES")
ok(len(fams or []) / sense["per_beat"] <= 15, "shipped table: every family within 15 beats")
ok(all(p.get("argv") is None or p.get("owns") or "--apply" not in p["argv"] and "--file-alarms" not in p["argv"]
       for p in t["phases"].values()), "shipped table: no shadow command acts (no --apply, no --file-alarms)")
ok(sense.get("owns") == ["rm-ops-watch.timer"] and "--file-alarms" in sense["argv"] and "{gen}" in sense["argv"]
   and "RM_OPS_WATCH_DIR" not in (sense.get("env") or {}),
   "shipped table: sense owns rm-ops-watch.timer and files alarms into the real store, fenced by {gen}")
ok("{state}" not in " ".join(t["phases"]["remember"]["argv"]), "shipped table: remember writes the real memory")
for bad, why in ((table(budget=2), "reserve over budget"),
                 (table(dispatch={"limit_s": 44}), "a phase that can never fit beside the reserve")):
    try:
        m.load_table(write_table(TMP / "bad.json", bad))
        ok(False, "a table with %s is refused" % why)
    except ValueError as e:
        ok(True, "a table with %s is refused (%s)" % (why, e))
# 1b. cutover (OPS_METRONOME_MIGRATE_CLOCKS_FENCED): ownership lives in the table, fenced by generation
ok(t["phases"]["raise"].get("owns") == ["rm-restart-reconcile.timer"]
   and "--metronome-gen" in t["phases"]["raise"]["argv"] and "{gen}" in t["phases"]["raise"]["argv"]
   and "--no-file" not in t["phases"]["raise"]["argv"],
   "shipped table: raise owns rm-restart-reconcile.timer and runs the real pass with its generation")
ok(m.owner_of("rm-restart-reconcile.timer") == "raise" and m.owner_of("rm-ops-watch.timer") == "sense" and m.owner_of("rm-dispatcher.timer") is None,
   "owner_of names the phase owning a cut-over timer, and none for a clock not cut over")
for bad, why in (({"owns": "rm-x.timer"}, "owns not a list"),
                 ({"owns": ["rm-x.service"]}, "owns naming a non-timer"),
                 ({"owns": ["rm-x.timer"]}, "an owning phase without {gen}"),
                 ({"owns": ["rm-x.timer"], "argv": ["{python}", "x.py", "--no-file", "{gen}"]}, "an owning dry run")):
    try:
        m.load_table(write_table(TMP / "bad.json", table(**{"raise": bad})))
        ok(False, "a table with %s is refused" % why)
    except ValueError as e:
        ok(True, "a table with %s is refused (%s)" % (why, e))
d = fresh("owned")
to = table(**{"raise": {"owns": ["rm-x.timer"], "argv": ["{python}", str(KIDP), "ok", "{gen}"]}})
ok(m.beat(d, to, shadow=False) == 0, "beat without --shadow runs (ownership is the table's)")
ok(by(d, 1, "raise")["shadow"] is False and by(d, 1, "ring")["shadow"] is True,
   "the beat line marks an owning phase not shadow, the others shadow")
ok(m.may_act(d, "raise", 1)[0], "may_act: the live generation may act")
m.beat(d, to)
ok(not m.may_act(d, "raise", 1)[0] and "not the live" in m.may_act(d, "raise", 1)[1],
   "may_act: a superseded generation may not act (a child of beat 1 still running in beat 2)")
m.set_fence(d, "raise", 2)
ok(not m.may_act(d, "raise", 2)[0] and "fenced" in m.may_act(d, "raise", 2)[1],
   "may_act: a fenced (killed) live generation may not act")

# 2. a clean beat: order, one line per phase, outputs carry the generation, health from useful work
d = fresh("clean")
ok(m.beat(d, table()) == 0, "clean beat exits 0")
ls = lines(d)
ok([x["phase"] for x in ls] == list(m.ORDER), "phases run in the fixed order, one line each")
ok(all(set(x) >= {"beat", "phase", "start", "seconds", "exit", "read_hash"} and x["exit"] == 0 for x in ls),
   "each line carries beat, phase, start, seconds, exit and the hash of what it read")
rec, _ = m.read_output(d, "ring")
ok(rec and rec["gen"] == 1 and rec["payload"]["gen"] == "1", "ring's output is published with generation 1")
tc = table()
tc["phases"]["raise"].update(critical=True, max_ok_age_s=60)
good, hl = m.health(d, tc)
ok(good, "health: raise did useful work just now (%s)" % hl)
good, hl = m.health(d, tc, now=time.time() + 120)
ok(not good and "DEAD" in hl[0], "health: a raise whose last SUCCESS is too old is dead, beat or no beat")

# 3. planted crash: the phase's exit is logged, later phases still run, nothing published, the reader refuses
d = fresh("crash")
tt = table(sense=("crash",))
tt["phases"]["remember"]["reads"] = {"sense": 900}
tt["phases"]["sense"].update(critical=True, max_ok_age_s=900)
m.beat(d, tt)
ok(by(d, 1, "sense")["exit"] == 3, "planted crash: sense's exit 3 is logged")
ok(by(d, 1, "remember")["exit"] == "stale_input", "planted crash: remember refuses to decide on no reading")
ok(all(by(d, 1, p)["exit"] == 0 for p in ("raise", "ring", "dispatch", "chores")),
   "planted crash: every later phase still runs")
ok(not m.health(d, tt)[0], "planted crash: health says sense never did useful work (UNMEASURED)")

# 4. planted overrun ignoring SIGTERM: killed, group dead, fenced; raise and ring still run inside the budget
d = fresh("overrun")
mark = TMP / "overrun.mark"
os.environ["KID_MARK"] = str(mark)
t0 = time.time()
m.beat(d, table(budget=8, sense=("ignore_term", 30), remember={"limit_s": 3}))
el = time.time() - t0
s = by(d, 1, "sense")
ok(s["exit"] == "overrun" and s["killed"] == "killed_kill", "planted overrun: ignoring SIGTERM ends in SIGKILL")
ok(s["seconds"] < 1 + 0.5 + 1.0, "planted overrun: killed by limit + cleanup (%.2f s)" % s["seconds"])
ok(mark.exists() and not alive(int(mark.read_text())), "planted overrun: the child is dead, not orphaned")
ok(m.fenced(d, "sense") == {1} and m.read_output(d, "sense")[0] is None,
   "planted overrun: generation 1 of sense is fenced and nothing of it is readable")
ok(all(by(d, 1, p)["exit"] == 0 for p in ("raise", "ring")), "planted overrun: raise and ring still run")
ok(el <= 8 + 0.5, "planted overrun: the whole beat stays inside its 8 s budget (%.2f s)" % el)

m.beat(d, table())
m.beat(d, table(budget=8, sense=("ignore_term", 30), remember={"limit_s": 3}))
ok(m.fenced(d, "sense") == {1, 3} and (m.read_output(d, "sense")[0] or {}).get("gen") == 2,
   "a killed generation 3 leaves the good generation 2 readable (real shadow beat, 2026-11-04)")

# 5. SIGTERM honoured: cleanup inside its deadline
d = fresh("term")
mark.unlink(missing_ok=True)
m.beat(d, table(sense=("term_cleanup", 30)))
ok(by(d, 1, "sense")["killed"] == "killed_term" and mark.read_text() == "cleaned",
   "a phase that cleans up on SIGTERM ends inside cleanup_s")

# 6. a straggler left in the group after a normal exit is killed
d = fresh("straggler")
mark.unlink(missing_ok=True)
m.beat(d, table(sense=("straggler",)))
gp = int(mark.read_text())
ok(by(d, 1, "sense")["exit"] == 0 and by(d, 1, "sense").get("stragglers") in ("killed_term", "killed_kill"),
   "a grandchild left in the phase's group is killed")
ok(wait_for(lambda: not alive(gp), 3), "the straggler is dead")

# 7. a child that escapes the group cannot publish late; 8. a superseded generation cannot either
d = fresh("escape")
mark.unlink(missing_ok=True)
m.beat(d, table(sense=("escape", 30)))
ok(by(d, 1, "sense")["exit"] == "overrun", "escapee's phase overran and was killed")
ok(wait_for(lambda: mark.exists() and " " in mark.read_text(), 8), "the escapee tried to publish")
ok(mark.read_text().startswith("1 ") and "fenced" in mark.read_text(),
   "the escapee's late publish is refused: %s" % mark.read_text())
ok(m.read_output(d, "sense")[0] is None, "nothing of the escapee is readable")
m.beat(d, table())
okp, why = m.publish(d, "ring", 1, "late", time.time())
ok(not okp and "superseded" in why, "a generation-1 publish after beat 2 started is refused (%s)" % why)
ok(m.read_output(d, "ring")[0]["gen"] == 2, "readers see generation 2")
ep = Path(str(mark) + ".pid")
if ep.exists():
    try:
        os.kill(int(ep.read_text()), signal.SIGKILL)
    except ProcessLookupError:
        pass

# 9. duplicate run: a second beat while one runs exits 75, logs, and runs no phase
d = fresh("dup")
td = table(sense=("sleep", 2))
td["phases"]["sense"]["limit_s"] = 3
tp = write_table(TMP / "dup.json", td)
pa = subprocess.Popen([sys.executable, str(HERE / "metronome.py"), "beat", "--shadow", "--table", str(tp),
                       "--dir", str(d)])
ok(wait_for(lambda: (m.read_json(d / "state.json") or {}).get("inflight"), 5), "beat A is mid-phase")
rc = m.beat(d, table())
pa.wait(20)
ok(rc == m.EXIT_DUPLICATE, "the duplicate beat exits 75")
ls = lines(d)
ok([x["exit"] for x in ls if x["phase"] == "*"] == ["duplicate"], "the duplicate is logged once")
ok(len([x for x in ls if x["phase"] == "sense"]) == 1 and m.load_state(d)["beat"] == 1,
   "the same phase ran once and the beat count did not move")

# 10. the beat itself SIGKILLed mid-phase: the next beat kills the orphan, fences it, runs the phase overdue
d = fresh("beatdies")
mark.unlink(missing_ok=True)
tk = table(budget=120, sense=("ignore_term", 60))
tk["phases"]["sense"]["limit_s"] = 50
tp = write_table(TMP / "die.json", tk)
tp_args = [sys.executable, str(HERE / "metronome.py"), "beat", "--shadow", "--table", str(tp), "--dir", str(d)]
pa = subprocess.Popen(tp_args)
ok(wait_for(lambda: mark.exists() and mark.read_text(), 5), "beat 1 is inside sense")
orphan = int(mark.read_text())
pa.send_signal(signal.SIGKILL)
pa.wait(5)
ok(alive(orphan), "after the beat's SIGKILL its phase child lives on (own session)")
m.beat(d, table())
died = [x for x in lines(d) if x["exit"] == "beat_died"]
ok(len(died) == 1 and died[0]["beat"] == 1 and died[0]["phase"] == "sense", "beat 2 logs beat 1 died in sense")
ok(wait_for(lambda: not alive(orphan), 3), "beat 2 killed the orphaned phase group")
ok(m.fenced(d, "sense") == {1}, "beat 1's sense generation is fenced")
ok(by(d, 2, "sense")["exit"] == 0 and m.load_state(d)["overdue"] == [] and m.load_state(d)["beat"] == 2,
   "sense runs in beat 2; the count carries on from state")

# 11. total budget: a phase that would not fit is deferred, logged, and held in the reserve next beat
d = fresh("budget")
tb = table(budget=8, sense=("sleep", 2.8), remember=("sleep", 0.9))
tb["phases"]["sense"].update(limit_s=3)
tb["phases"]["dispatch"].update(limit_s=4)
for b in (1, 2, 3):
    t0 = time.time()
    m.beat(d, tb)
    el = time.time() - t0
    ok(el <= 8 + 0.5, "budget: beat %d took %.2f s of 8" % (b, el))
dz = by(d, 1, "dispatch")
ok(dz["exit"] == "deferred" and "reserved" in dz["why"], "budget: dispatch is deferred, not squeezed (%s)" % dz["why"])
ok(all(by(d, b, p)["exit"] == 0 for b in (1, 2, 3) for p in ("raise", "ring")), "budget: raise and ring run every beat")
ok(by(d, 2, "dispatch")["exit"] == 0, "budget: the deferred dispatch runs next beat from the reserve")
ok(by(d, 2, "sense")["exit"] == "deferred" and by(d, 3, "sense")["exit"] == 0,
   "budget: what that pushed out runs the beat after; nothing starves")

# 11b. the reserve is held at run time: phases ahead of raise/ring (sense, remember) that would eat the
# budget must leave raise and ring their room; remember is deferred, never raise or ring
d = fresh("reserve")
tq = table(budget=8, sense=("ignore_term", 30), remember=("ignore_term", 30))
tq["phases"]["sense"].update(limit_s=4)
tq["phases"]["remember"].update(limit_s=2)
os.environ["KID_MARK"] = str(TMP / "reserve.mark")
t0 = time.time()
m.beat(d, tq)
el = time.time() - t0
ok(el <= 8 + 0.5, "reserve: beat took %.2f s of 8" % el)
ok(all(by(d, 1, p) and by(d, 1, p)["exit"] == 0 for p in ("raise", "ring")),
   "reserve: raise and ring exit 0 though sense and remember would eat the budget (%s)"
   % [(p, (by(d, 1, p) or {}).get("exit")) for p in ("raise", "ring")])
rm_ = by(d, 1, "remember")
ok(rm_ and rm_["exit"] == "deferred", "reserve: remember is deferred to keep the reserve (%s)" % (rm_ or {}).get("exit"))

# 12. operation ids: a crash between the act and its record is found by id, never done twice
d = fresh("ops")
st1, oid = m.op_begin(d, "ring", "INC-7:rung2")
st2, oid2 = m.op_begin(d, "ring", "INC-7:rung2")
ok(st1 == "do" and st2 == "unresolved" and oid == oid2, "op: the same act begun twice is unresolved, not 'do'")
m.op_reconcile(d, oid, found=True)
ok(m.op_begin(d, "ring", "INC-7:rung2")[0] == "done", "op: found in the world -> done, never repeated")
sa, oa = m.op_begin(d, "raise", "seat:BENCH:life3")
m.op_reconcile(d, oa, found=False)
ok(m.op_begin(d, "raise", "seat:BENCH:life3")[0] == "do", "op: absent from the world -> may act once more")
m.op_end(d, oa)
cli = lambda *a: subprocess.run([sys.executable, str(HERE / "metronome.py"), "op"] + list(a) + ["--dir", str(d)],
                                capture_output=True, text=True).returncode
ok(cli("begin", "--kind", "raise", "--key", "seat:BENCH:life3") == 3, "op CLI: a done act exits 3")
ok(cli("begin", "--kind", "ring", "--key", "new") == 0 and cli("begin", "--kind", "ring", "--key", "new") == 4,
   "op CLI: do exits 0, unresolved exits 4")

# 13. wall-clock slots: due once, kept across a restart, a late one is reported missed
base = datetime(2026, 11, 3, 7, 31).timestamp()
ok(m.slot_due(["07:30"], 120, base, set())[0] == "2026-11-03T07:30", "slot: 07:30 is due at 07:31")
ok(m.slot_due(["07:30"], 120, base, {"2026-11-03T07:30"})[0] is None, "slot: a done slot is not repeated")
ok(m.slot_due(["07:30"], 120, base + 3 * 3600, {"2026-11-02T07:30"}) == (None, ["2026-11-03T07:30"]),
   "slot: one 3 h late with max_late 120 min is reported missed, not run and not silently dropped")
ok(m.slot_due(["23:50"], 120, datetime(2026, 11, 4, 0, 10).timestamp(), set())[0] == "2026-11-03T23:50",
   "slot: yesterday's 23:50 is still due at 00:10")
d = fresh("slots")
hm = (datetime.now() - timedelta(minutes=1)).strftime("%H:%M")
ts = table()
ts["phases"]["chores"].update(every=1000, offset=999, slots=[hm])
m.beat(d, ts)
m.beat(d, ts)
ok(by(d, 1, "chores") and by(d, 1, "chores").get("slot") and by(d, 2, "chores") is None,
   "slot: the beat runs a due slot once; the next beat (as after a restart) does not repeat it")

# 14. round robin is persisted
d = fresh("rr")
tr = table(sense={"families": ["a", "b", "c"], "per_beat": 2})
m.beat(d, tr)
m.beat(d, tr)
ok(by(d, 1, "sense")["families"] == ["a", "b"] and by(d, 2, "sense")["families"] == ["c", "a"],
   "round robin: beat 2 carries on where beat 1 stopped")

# 15. a reading older than the phase allows is refused, and the line names the oldest reading used
d = fresh("stale")
tf = table(sense=("old",))
tf["phases"]["remember"]["reads"] = {"sense": 60}
tf["phases"]["ring"]["reads"] = {"sense": 20000}
m.beat(d, tf)
ok(by(d, 1, "remember")["exit"] == "stale_input" and "older than" in by(d, 1, "remember")["why"],
   "freshness: a 10000 s old reading is refused by a phase allowing 60 s")
rg = by(d, 1, "ring")
ok(rg["exit"] == 0 and rg["oldest_reading"]["phase"] == "sense", "freshness: the line names the oldest reading used")

print("selftest_metronome: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
