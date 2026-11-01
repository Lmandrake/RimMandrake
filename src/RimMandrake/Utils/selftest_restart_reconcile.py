#!/usr/bin/env python3
"""selftest_restart_reconcile: RESTART_JOIN_BUILD_EVERY_GOODBYE_ENDS (CK3). Runs on the real program with real files.

testdata/restart_goodbyes_2026-11-01.jsonl is the real record, cut from the Dispatcher's journal: the peer-message cancels
of 05:47 to 06:52Z and the verified restarts around them, replayed pass by pass. The planted faults use the real
seat_restart.decide and dispatcher.journal, so a renamed journal field fails here: a goodbye cancelled by its window
going away, then cancelled with the Dispatcher never reading it; and a verified restart that must stay silent.
"""
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
TMP = Path(tempfile.mkdtemp(prefix="selftest_restart_reconcile_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["RM_DISPATCHER_STATE"] = str(TMP / "disp")
os.environ["CLAUDE_CONFIG_DIR"] = str(TMP / "claude")
import dispatcher as D  # noqa: E402
import doorbell  # noqa: E402
import ops_watch as OW  # noqa: E402
import restart_reconcile as RR  # noqa: E402
import seat_restart as SR  # noqa: E402

FAILS = []
SHIPPED = json.loads((HERE.parent / "rimflow/dispatcher_schedule.json").read_text(encoding="utf-8"))
LIM = RR.limits(SHIPPED)
RECORD = [json.loads(x) for x in (HERE / "testdata/restart_goodbyes_2026-11-01.jsonl").read_text(encoding="utf-8").splitlines()]
PASS = LIM["restart_reconcile_pass_s"]


def check(ok, name):
    print("  %s %s" % ("ok  " if ok else "FAIL", name))
    if not ok:
        FAILS.append(name)


def fresh(name):
    root = TMP / name
    (root / "restart" / "done").mkdir(parents=True)
    log = TMP / (name + "_log.md")
    sch = json.loads(json.dumps(SHIPPED))
    sch["seat_restart"]["seats"]["BENCH"]["seat_log"] = str(log)
    return str(root), sch, log


class Filer:
    def __init__(self, fail=False):
        self.todo, self.fail = [], fail

    def __call__(self, todo, conf):
        self.todo.extend(todo)
        if self.fail:
            raise OSError("ledger down")
        return {a["name"]: None for a in todo}


def write_journal(root, rows):
    with open(os.path.join(root, "journal.jsonl"), "w", encoding="utf-8") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)


def request_file(root, seat, ts, reason="goodbye", where="."):
    p = Path(root) / "restart" / where / ("%s%s.request.json" % (seat, "" if where == "." else "-%d" % ts))
    p.write_text(json.dumps({"seat": seat, "ts": ts, "reason": reason, "session_id": "s1"}), encoding="utf-8")
    return p


# ---- the shipped numbers keep the promise
check(LIM["restart_reconcile_s"] == 600, "restart_reconcile_s is 600 in dispatcher_schedule.json")
check(LIM["restart_reconcile_s"] - LIM["restart_reconcile_slack_s"] >= LIM["restart_reconcile_s"] - LIM["restart_reconcile_pass_s"] - LIM["restart_reconcile_slack_s"]
      and LIM["restart_reconcile_pass_s"] + LIM["restart_reconcile_slack_s"] < 600, "a pass and a filing fit inside the bound")
unit = (HERE / "systemd/rm-restart-reconcile.timer").read_text(encoding="utf-8")
check("OnUnitInactiveSec=%ds" % PASS in unit, "the timer's period is restart_reconcile_pass_s")
try:
    RR.limits({})
    check(False, "a missing threshold fails by name")
except ValueError as e:
    check("restart_reconcile_s" in str(e), "a missing threshold fails by name")

# ---- replay of the real record
root, sch, log = fresh("replay")
first = OW.epoch(RECORD[0]["at"]) - 60
last = OW.epoch(RECORD[-1]["at"]) + 1200
filer, st, opened, closed = Filer(), {"armed_at": first}, {}, {}
t = first
while t < last:
    write_journal(root, [r for r in RECORD if OW.epoch(r["at"]) <= t])
    rep = RR.run_pass(t, root, sch, st, filer, TMP / "replay_out")
    for s in rep["open"]:
        opened.setdefault(s, t)
    for s in opened:
        if s not in rep["open"] and s not in closed:
            closed[s] = t
    t += PASS
goodbye = next(r for r in RECORD if r["seat"] == "BENCH" and r["do"] == "restart_request")
check(set(opened) == {"BENCH"}, "replay: the cancelled goodbyes are the only incident; every FOUNDRY restart silent: %s" % sorted(opened))
late = opened.get("BENCH", 1e12) - goodbye["req_ts"]
check(0 < late <= 600, "replay: the 05:38Z goodbye is told %d s after it was asked" % late)
check(len([a for a in filer.todo if not a.get("note_only")]) == 1, "replay: one outage, one alarm")
check(OW.iso(closed.get("BENCH", 0)) > "2026-11-01T12:31:00Z", "replay: the 12:31Z verified closes the incident")
check(any(a.get("note_only") for a in filer.todo), "replay: the item is told it closed")
check("restart_reconcile" in log.read_text(encoding="utf-8"), "replay: the Conductor log has the line")

# ---- planted on the real path: real seat_restart.decide writes the journal; a goodbye is cancelled in the window's life
root, sch, log = fresh("planted")
T0 = time.time() - 1000
cfgs = SR.config(sch)
sch["seat_restart"]["seats"]["BENCH"]["enabled"] = True
req = {"seat": "BENCH", "ts": T0, "pid": 7, "start": 9, "session_id": "old", "reason": "goodbye", "ticket": "gone"}
Path(SR.request_path("BENCH", root)).write_text(json.dumps(req), encoding="utf-8")
state = {"seat_restart": {}}
ro = {"request": lambda seat: SR._read_json(SR.request_path(seat, root)) if seat == "BENCH" else None,
      "start": lambda pid: 9, "tx": lambda *a: None, "helpers": lambda *a: [], "armed": lambda s: {}, "intile": lambda *a: None}
named = [{"pid": 8, "sessionId": "new", "status": "idle", "name": "CONDUCTOR", "cwd": "/x"}]


def act(**k):
    D.journal(root, dict(k, at=OW.iso(T0 + 60), result=None if k.get("do") != "restart_request" else "request taken"))


SR._one("BENCH", cfgs["BENCH"], state["seat_restart"], state, {"seat_restart": ro}, named, T0 + 60, True, act)
kinds = [r["do"] for r in RR.read_journal(root)[0]]
check(kinds == ["restart_request", "restart_cancel"], "planted: the real code path wrote a request and a cancel: %s" % kinds)
filer, st = Filer(), {"armed_at": T0 - 5}
early = RR.run_pass(T0 + 300, root, sch, st, filer, TMP / "o1")
check(not early["open"], "planted: not called before it is due")
doorbell.arm("BENCH", "new", root)
rep = RR.run_pass(T0 + LIM["restart_reconcile_s"] - PASS - LIM["restart_reconcile_slack_s"], root, sch, st, filer, TMP / "o1")
check("BENCH" in rep["open"], "planted: incident opens inside restart_reconcile_s of the goodbye")
check(rep["open"]["BENCH"]["told"]["doorbell"] is True and os.path.exists(doorbell.inbox_path("BENCH", root)), "planted: the seat is rung")
check("OPS_RESTART_UNSTICK_BENCH" in filer.todo[0]["name"], "planted: the fixed item is filed")
check(OW.iso(0) and json.loads((TMP / "o1/restart_reconcile.json").read_text())["open"], "planted: the reading names it")
RR.run_pass(T0 + 500, root, sch, st, filer, TMP / "o1")
check(len(filer.todo) == 1, "planted: a repeat pass files nothing")
D.journal(root, {"at": OW.iso(T0 + 550), "do": "restart_verified", "seat": "BENCH"})
rep = RR.run_pass(time.time(), root, sch, st, filer, TMP / "o1")
check(not rep["open"], "planted: restart_verified closes it")

# ---- a verified restart stays silent through the real journal
root, sch, log = fresh("silent")
T0 = time.time() - 900
request_file(root, "FOUNDRY", T0, "ticket ended", "done")
write_journal(root, [{"at": OW.iso(T0 + 1), "do": "restart_request", "seat": "FOUNDRY", "req_ts": T0, "result": "request taken", "why": "requested by FOUNDRY: closed"},
                     {"at": OW.iso(T0 + 250), "do": "restart_verified", "seat": "FOUNDRY"}])
f = Filer()
rep = RR.run_pass(T0 + 800, root, sch, {"armed_at": T0 - 5}, f, TMP / "o2")
check(not rep["open"] and not f.todo and not log.exists(), "silent: a verified restart tells nobody")

# ---- the Dispatcher never read it (dead tick): only the request file exists
root, sch, log = fresh("deadtick")
T0 = time.time() - 500
request_file(root, "BENCH", T0)
write_journal(root, [])
f = Filer()
rep = RR.run_pass(T0 + 420, root, sch, {"armed_at": T0 - 5}, f, TMP / "o3")
check("BENCH" in rep["open"] and f.todo, "dead Dispatcher: a request file no tick took alarms")

# ---- the window never asked: his goodbye is only in the transcript
root, sch, log = fresh("nowindow")
T0 = time.time() - 500
d = TMP / "claude" / "projects" / SR.re.sub(r"[^A-Za-z0-9]", "-", sch["seats"]["BENCH"]["clone"])
d.mkdir(parents=True)
rec = {"type": "user", "timestamp": OW.iso(T0), "uuid": "u", "message": {"role": "user", "content": "Goodbye!"}}
peer = {"type": "user", "timestamp": OW.iso(T0), "uuid": "p", "origin": {"kind": "peer", "name": "AGENT FOUNDRY"},
        "message": {"role": "user", "content": "goodbye"}}
(d / "s.jsonl").write_text(json.dumps(rec) + "\n", encoding="utf-8")
(d / "peer.jsonl").write_text(json.dumps(peer) + "\n", encoding="utf-8")
write_journal(root, [])
f, st = Filer(), {"armed_at": T0 - 5}
rep = RR.run_pass(T0 + 100, root, sch, st, f, TMP / "o4")
check(not rep["open"] and len(st["goodbyes"]) == 1, "goodbye in the transcript: read once, a peer's is not his, not due yet")
rep = RR.run_pass(T0 + 420, root, sch, st, f, TMP / "o4")
check("BENCH" in rep["open"], "goodbye in the transcript: remembered past the cursor, alarms with no request anywhere")

# ---- held: bounded, and a cancel ends the patience; a goodbye gets none
root, sch, log = fresh("held")
T0 = time.time() - 4000
hold = {"at": OW.iso(T0 + 3000), "do": "restart_hold", "seat": "FOUNDRY"}
rq = {"at": OW.iso(T0), "do": "restart_request", "seat": "FOUNDRY", "req_ts": T0, "result": "request taken", "why": "DEFERRED (only the kill waits) by FOUNDRY: ticket ended"}
J = lambda *r: list(r)  # noqa: E731
L = LIM
check(not RR.join([], J(rq, hold), T0 + 3000, L, T0 - 1), "held: a deferred ticket restart waits")
check(RR.join([], J(rq), T0 + L["restart_reconcile_held_s"], L, T0 - 1), "held: the bound still ends")
cx = {"at": OW.iso(T0 + 500), "do": "restart_cancel", "seat": "FOUNDRY"}
check(RR.join([], J(rq, cx), T0 + 500, L, T0 - 1), "held: a cancel ends the patience")
rg = dict(rq, why="DEFERRED (only the kill waits) by BENCH: goodbye", seat="BENCH")
check(RR.join([], J(rg, dict(hold, seat="BENCH")), T0 + 420, L, T0 - 1), "held: a goodbye never waits")
sy = {"at": OW.iso(T0), "do": "restart_request", "seat": "FOUNDRY", "result": "started by the Dispatcher", "why": "hard context limit"}
check(not RR.join([], J(sy, cx), T0 + 500, L, T0 - 1), "held: the Dispatcher withdrawing its own is no fault")
check(not RR.join([], [dict(rq, result="would take the request")], T0 + 5000, L, T0 - 1), "dry: a would-be request asked nothing")
check(not RR.join([], J(rq), T0 + 5000, L, T0 + 1), "history before the first pass is not alarmed")

told = {RR.row_key("FOUNDRY", T0)}
check(RR.join([], J(rq, dict(hold, at=OW.iso(T0 + 3900))), T0 + 3900, L, T0 - 1, told), "held: a later hold never un-alarms a told request")
# ---- a transcript that stays unreadable is an incident; one bad pass is not
root, sch, log = fresh("torn")
(d / "s.jsonl").write_text('{"type": "user", "bad line\n', encoding="utf-8")
(d / "peer.jsonl").unlink()
write_journal(root, [])
st = {"armed_at": time.time()}
now = time.time()
reps = [sorted(RR.run_pass(now + i, root, sch, st, Filer(), TMP / "o7")["open"]) for i in range(RR.STUCK_PASSES)]
check(not reps[0] and RR.TRANSCRIPT_SEAT in reps[-1], "transcript: one bad pass is quiet, a stuck file alarms")
(d / "s.jsonl").unlink()

# ---- told even when the filer is down, then retried; blind journal is an incident
root, sch, log = fresh("filerdown")
T0 = time.time() - 500
request_file(root, "BENCH", T0)
write_journal(root, [])
st = {"armed_at": T0 - 5}
rep = RR.run_pass(T0 + 420, root, sch, st, Filer(fail=True), TMP / "o5")
check("BENCH" in rep["open"] and not rep["open"]["BENCH"]["filed"] and "restart_reconcile" in log.read_text(encoding="utf-8"), "filer down: the log still hears")
f = Filer()
st["open"]["BENCH"]["told"]["log"] = "disk full"
rep = RR.run_pass(T0 + 480, root, sch, st, f, TMP / "o5")
check(rep["open"]["BENCH"]["told"]["log"] == "ok", "log failed: the Conductor's line is retried")
check(rep["open"]["BENCH"]["filed"] and f.todo[0]["reopen"], "filer down: the next pass retries, reopening if the spawn landed")
root, sch, log = fresh("blind")
rep = RR.run_pass(time.time(), root, sch, {}, Filer(), TMP / "o6")
check(RR.JOURNAL_SEAT in rep["open"], "blind: no journal is an incident, never silence")

# ---- the CLI end to end, with the deadman's reading
T0 = time.time() - 500
root = str(TMP / "disp")
Path(root, "restart").mkdir(parents=True)
request_file(root, "BENCH", T0)
write_journal(root, [])
sp = OW.ops_dir()
sp.mkdir(parents=True)
(sp / "restart_reconcile_state.json").write_text(json.dumps({"armed_at": T0 - 5}), encoding="utf-8")
sf = TMP / "sch.json"
cli = json.loads(json.dumps(SHIPPED))
cli["seat_restart"]["seats"]["BENCH"]["seat_log"] = str(TMP / "cli_log.md")
sf.write_text(json.dumps(cli), encoding="utf-8")
os.environ["RM_RESTART_RECONCILE_SCHEDULE"] = str(sf)
f = Filer()
rc = RR.main(["run"], filer=f)
check(rc == 0 and json.loads((sp / "restart_reconcile.json").read_text())["open"].get("BENCH") and f.todo, "cli: a run files and writes the deadman's reading")

shutil.rmtree(TMP, ignore_errors=True)
print("selftest_restart_reconcile: %s" % ("FAIL " + "; ".join(FAILS) if FAILS else "OK"))
sys.exit(1 if FAILS else 0)
