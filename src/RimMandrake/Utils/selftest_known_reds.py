#!/usr/bin/env python3
"""selftest_known_reds.py -- TE1's own test: plant a new red, alarm; plant a listed red, silence; an entry past its age
alarms; an entry with no open item is refused and covers nothing; a new red on an open alarm is said, not swallowed."""
import json
import re
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TMP = Path(tempfile.mkdtemp())
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
(TMP / "ops").mkdir()
os.environ["RM_STREAMS_BENCH"] = str(TMP)
os.environ["RM_KNOWN_REDS"] = str(TMP / "known.json")
(TMP / "Transient").mkdir()
import known_reds as K  # noqa: E402
import ops_watch as OW  # noqa: E402

FAILS = []
A, B, C = "src/x/selftest_a.py", "src/x/selftest_b.py", "src/x/selftest_c.py"
NOW = K.epoch("2026-11-04T12:00:00Z")


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  -- %s" % (detail,)))
    if not cond:
        FAILS.append(name)


def night(at, fails=(), crashes=(), result=True):
    s = "\n=== %s nightly\nnoise FAIL line\n" % at
    if crashes:
        s += "CRASH (%d/9) — reached no verdict: %s\n" % (len(crashes), ", ".join("%s [uncaught X (rc 1), died]" % c for c in crashes))
    if fails:
        s += "FAIL (%d/9): %s\n" % (len(fails), ", ".join(fails))
    return s + ("RESULT: RED (green = FAIL 0 and CRASH 0)\nexit 1\n" if result else "")


def write_log(*parts):
    K.log_path().write_text("".join(parts), encoding="utf-8")


def entry(test=A, item="OPEN_ITEM", added="2026-11-01T00:00:00Z", expires="2026-11-10T00:00:00Z"):
    return {"test": test, "item": item, "added": added, "expires": expires, "why": "w"}


# ---- the log
log = night("2026-11-01T10:00:00Z", [A]) + night("2026-11-02T10:00:00Z", [A, B]) + night("2026-11-03T10:00:00Z", crashes=[A]) \
    + night("2026-11-04T10:00:00Z", [A, C], [B])
ns = K.nights(log)
check("night: FAIL and CRASH both read, a comma inside a crash's reason is no name",
      ns[-1]["reds"] == {A, B, C} and ns[2]["reds"] == {A}, ns[-1])
check("streak: consecutive nights ending on the newest", (K.streak(ns, A), K.streak(ns, B), K.streak(ns, C)) == (4, 1, 1))
check("a section with no RESULT line is a sweep in progress: the night before stands",
      K.nights(log + night("2026-11-05T10:00:00Z", result=False))[-1]["at"] == "2026-11-04T10:00:00Z")
torn = "\n=== 2026-11-05T10:00:00Z nightly\nFAIL (3/9): a.py\nRESULT: RED\n"
check("a summary shorter than its own count is not a night", K.nights(log + torn)[-1]["at"] == "2026-11-04T10:00:00Z")

# ---- the verdict
OPEN = {"OPEN_ITEM"}
v = K.judge([entry()], [{"at": "n", "t": NOW, "reds": {A}, "total": 9}], OPEN, NOW)
check("TE1: a planted LISTED red is silence", v["news"] == [] and v["listed"] == [A], v)
v = K.judge([entry()], [{"at": "n", "t": NOW, "reds": {A, B}, "total": 9}], OPEN, NOW)
check("TE1: a planted NEW red is news beside a listed one", v["news"] == ["red, not listed: " + B], v)
check("the said line names the test", B in v["said"], v["said"])
v = K.judge([entry(expires="2026-11-03T00:00:00Z")], [{"at": "n", "t": NOW, "reds": {A}, "total": 9}], OPEN, NOW)
check("TE1: an entry past its age is news though listed", v["news"] == ["past its age: " + A], v)
v = K.judge([entry(item="CLOSED_ITEM")], [{"at": "n", "t": NOW, "reds": {A}, "total": 9}], OPEN, NOW)
check("TE1: an entry whose item closed covers nothing", v["news"] == ["red, not listed: " + A] and v["itemless"] == [A], v)
v = K.judge([entry()], [{"at": "n", "t": NOW, "reds": set(), "total": 9}], OPEN, NOW)
check("a listed test gone green is no news, and is said as cured", v["news"] == [] and v["cured"] == [A], v)
check("TE1: add is refused with no open item", "open item" in (K.add_refusal(A, "CLOSED_ITEM", ns, OPEN, 3) or ""))
check("add is refused under the threshold", "1 consecutive" in (K.add_refusal(B, "OPEN_ITEM", ns, OPEN, 3) or ""))
check("add passes at the threshold", K.add_refusal(A, "OPEN_ITEM", ns, OPEN, 3) is None)
pol = K.policy()
check("the threshold and age limit come from testing_policy.json, threshold 3", pol[0] == 3 and pol[1] > 0, pol)

# ---- the CLI's add refuses on the real path, and writes nothing
K.ledger_open = lambda: set(OPEN)
K.save([])
write_log(log)
check("CLI: add with no open item is refused", K.main([ "add", A, "--item", "NOPE", "--why", "w"]) == 2 and K.read_list()[0] == [])
check("CLI: add at the threshold lists it, with an age limit", K.main(["add", A, "--item", "OPEN_ITEM", "--why", "w"]) == 0
      and K.read_list()[0][0]["item"] == "OPEN_ITEM" and K.epoch(K.read_list()[0][0]["expires"]) > K.epoch(K.read_list()[0][0]["added"]))
check("CLI: drop removes it", K.main(["drop", A, "--why", "w"]) == 0 and K.read_list()[0] == [])

# ---- blind is never clean
K.save([entry()])
pts = OW.nightly_news(NOW, {"open_ids": OPEN})
check("metric: listed reds are counted, the unlisted ones are unparked (the list's own news is none)",
      pts["testing.nightly_unparked_reds"]["v"] == 2 and pts["testing.nightly_news"]["v"] == 0
      and pts["testing.nightly_known_reds"]["v"] == 1, pts)
check("metric: no ledger is UNMEASURED, not 0", OW.nightly_news(NOW, {})["testing.nightly_news"]["m"] == "UNMEASURED")
check("metric: a stale newest night is UNMEASURED", OW.nightly_news(NOW + 2 * K.DAY, {"open_ids": OPEN})["testing.nightly_news"]["m"] == "UNMEASURED")
Path(os.environ["RM_KNOWN_REDS"]).write_text("{", encoding="utf-8")
check("metric: an unreadable list is UNMEASURED, not 0", OW.nightly_news(NOW, {"open_ids": OPEN})["testing.nightly_news"]["m"] == "UNMEASURED")
K.save([dict(entry(), item="")])
check("a malformed entry is refused: it covers nothing and is news", any("bad list entry" in n for n in K.measure(OPEN, NOW)["news"]))

# ---- TE1 end to end, through the real rules and the real alarm step: NIGHTLY_NEWS is the list's own faults now
RULES = OW.load_rules(HERE / "ops_watch_rules.json")
CLOG = TMP / "conductor_log.md"     # the real rules name the real Conductor log: a test's fake alarm never reaches it
for _t in RULES["targets"]:
    if _t.get("conductor_log"):
        _t["conductor_log"] = str(CLOG)
AID ="NIGHTLY_NEWS:testing.nightly_news"
calls = []


def filer(todo, conf):
    calls.extend(todo)
    return {a["name"]: None for a in todo}


def filed():
    return [a for a in calls if not a.get("note_only")]


def last(at, rows, result=True, mtime=None):
    """The night's full output: progress rows (ignored), then the sorted listing with each red's detail."""
    s = "[1/9] PASS          0.1s  src/x/selftest_ok.py\n"
    for t, status, lines in rows:
        s += "%-5s        1.0s  %s\n" % (status, t) + "".join("             %s\n" % ln for ln in lines)
    s += "PASS          0.1s  src/x/selftest_ok.py\n" + ("RESULT: RED (green = FAIL 0 and CRASH 0)\n" if result else "")
    K.last_path().write_text(s, encoding="utf-8")
    t = K.epoch(at) + 60 if mtime is None else mtime
    os.utime(K.last_path(), (t, t))


def run(now, known, open_ids):
    return OW.run_alarms(OW.nightly_news(now, {"open_ids": OPEN}), RULES, now, known, filer, open_ids)


def reset():
    calls.clear()
    (TMP / "ops" / "alarms.json").unlink(missing_ok=True)


reset()
K.save([entry()])
write_log(night("2026-11-04T10:00:00Z", [A, B]))
last("2026-11-04T10:00:00Z", [(A, "FAIL", ["rc 1", "FAIL a broke"]), (B, "FAIL", ["rc 1", "FAIL b broke: the widget count is 3"])])
st = run(NOW, set(OPEN), OPEN)
check("TE1 end to end: a new red is no list news (the build cop files it)", AID not in st and
      not any(a["name"].startswith("OPS_NIGHTLY_RED_DIAGNOSE") for a in filed()), (calls, st))
reset()
K.save([entry(expires="2026-11-03T00:00:00Z")])
st = run(NOW, set(OPEN), OPEN)
f = [a for a in filed() if a["name"].startswith("OPS_NIGHTLY_RED_DIAGNOSE_")]
check("TE1 end to end: an entry past its age files the one list item, naming the test", len(f) == 1 and A in f[0]["title"], calls)

# ---- BUILD COP: the first error line, and grouping by it
check("cop: a crash's cause is its last exception line", K.first_error("CRASH", [
    "uncaught OSError (rc 1) - the test died before reaching a verdict", "Traceback (most recent call last):",
    '  File "/x/y.py", line 3, in main', "~~~~^^", "OSError: [Errno 28] No space left on device: 'a.xml'"])
    == "OSError: [Errno 28] No space left on device: 'a.xml'")
check("cop: a fail's cause is its first error-like line, past rc and ok rows",
      K.first_error("FAIL", ["rc 1", "ok    fine thing", "FAIL the count is 3"]) == "FAIL the count is 3")
n1 = K.normalise("OSError: [Errno 28] No space left on device: 'a.xml' -> 'b.xml'", A)
n2 = K.normalise("FAIL s4_scratch crashed: OSError: [Errno 28] No space left on device", B)
check("cop: one OS error on different files reads the same", n1 == n2 == "OSError: [Errno] No space left on device", (n1, n2))
check("cop: numbers, hex and directories are taken out", K.normalise("timeout: exceeded 240s in /a/b/c.py at d378a4b2", A)
      == "timeout: exceeded #s in c.py at #")
check("cop: a bare `uncaught X` names no cause", K.normalise("uncaught OSError (rc 1) - died", A) == "")
det = K.details("[3/9] FAIL   1.0s  src/x/selftest_a.py\nFAIL          1.0s  src/x/selftest_a.py\n             rc 1\n"
                "             FAIL x\nPASS          1.0s  src/x/selftest_b.py\n             noise\n")
check("cop: details are read from the sorted listing, not the progress rows",
      det.get(A) == ("FAIL", ["rc 1", "FAIL x"]) and det.get(B) == ("PASS", ["noise"]), det)
D = "src/x/selftest_d.py"
gs = K.groups([A, B, C, D], {A: ("CRASH", ["OSError: [Errno 28] No space left on device: 'p'"]),
                             B: ("FAIL", ["FAIL q crashed: OSError: [Errno 28] No space left on device"]),
                             C: ("CRASH", ["AssertionError"]), D: ("CRASH", ["AssertionError"])})
check("cop: reds with one cause are one group; a generic line stands alone",
      [len(g["tests"]) for g in gs] == [2, 1, 1] and gs[0]["tests"] == [A, B], gs)
check("cop: a group's key is stable and a valid alarm key", gs[0]["key"] == K.groups([B, A], {
    A: ("CRASH", ["OSError: [Errno 28] No space left on device: 'zz'"]), B: ("FAIL", ["OSError: [Errno 28] No space left on device"])})[0]["key"]
      and re.fullmatch(r"testing\.red_[a-z]{6}", gs[0]["key"]), gs[0]["key"])
H = K.red_deadline_h()
check("cop: the deadline comes from testing_policy.json, at least the nights it takes to park a red",
      H >= 24 * K.policy()[0], H)

# ---- BUILD COP end to end, through the real rules and the real alarm step
reset()
K.save([entry()])
E1 = ["rc 1", "OSError: [Errno 28] No space left on device: 'one.xml'"]
E2 = ["rc 1", "FAIL tmp crashed: OSError: [Errno 28] No space left on device"]
write_log(night("2026-11-04T10:00:00Z", [A, B, C]))
last("2026-11-04T10:00:00Z", [(A, "FAIL", ["rc 1", "FAIL listed"]), (B, "CRASH", E1), (C, "FAIL", E2)])
known = set(OPEN)
st = run(NOW, known, OPEN)
f = filed()
check("BUILD COP: two new reds with one cause file ONE item, its title naming the cause, the tests and the deadline",
      len(f) == 1 and f[0]["name"].startswith("NIGHTLY_COP_FIX_RED_") and "No space left" in f[0]["title"]
      and "due 2026-11-07" in f[0]["title"] and "selftest_b.py" in f[0]["title"] and "selftest_c.py" in f[0]["title"], f)
check("BUILD COP: a listed red files nothing", not any("selftest_a.py" in a["title"] for a in f), f)
import pulse_core as PC  # noqa: E402  (ops_watch put pulse/ on the path)
check("BUILD COP: the minted name passes the ledger's name rules", f and not PC._model().mint_problems(f[0]["name"], set()), f)
item = f[0]["name"]
check("BUILD COP: the real filer raises every item it files (first in relentless pool_order)",
      'ing.rimflow("raise", a["name"]' in Path(OW.__file__).read_text(encoding="utf-8"))
known |= {item}
calls.clear()
write_log(night("2026-11-04T10:00:00Z", [A, B, C]) + night("2026-11-05T10:00:00Z", [A, B, C]))
last("2026-11-05T10:00:00Z", [(A, "FAIL", ["rc 1", "FAIL listed"]), (B, "CRASH", E1), (C, "FAIL", E2)])
st = run(NOW + K.DAY, known, known)
check("BUILD COP: the same group next night files nothing and says nothing", calls == [], calls)
last("2026-11-05T10:00:00Z", [], result=False, mtime=K.epoch("2026-11-05T10:00:00Z") + 60)
pts = OW.nightly_news(NOW + K.DAY, {"open_ids": OPEN})
check("BUILD COP: a night whose output is being rewritten emits no group (absent holds; no guess files)",
      not any(k.startswith("testing.red_") for k in pts) and pts["testing.nightly_unparked_reds"]["v"] == 2, sorted(pts))
check("BUILD COP: ... but the deadline reading stands on the log alone", pts["testing.nightly_reds_overdue"]["m"] == "MEASURED")

# the deadline: owned or not
three = night("2026-11-04T10:00:00Z", [A, B, C]) + night("2026-11-05T10:00:00Z", [A, B, C]) + night("2026-11-06T10:00:00Z", [A, B, C]) \
    + night("2026-11-07T10:00:00Z", [A, B, C])
write_log(three)
last("2026-11-07T10:00:00Z", [(A, "FAIL", ["rc 1", "FAIL listed"]), (B, "CRASH", E1), (C, "FAIL", E2)])
calls.clear()
LATE = K.epoch("2026-11-07T11:00:00Z")
st = run(LATE, known, known)
over = [a for a in filed() if a["name"].startswith("OPS_RED_OVERDUE_CHASE_")]
check("BUILD COP: a red past its deadline alarms though its item is open (owned is not fixed)",
      len(over) == 1 and "selftest_b.py" in over[0]["title"] and not any(n.startswith("NIGHTLY_COP_FIX") for n in (a["name"] for a in filed())), calls)
check("BUILD COP: a parked (listed) red is never overdue", "selftest_a.py" not in json.dumps(over), over)
check("BUILD COP: the overdue alarm owes the Conductor a line", over and over[0].get("conductor_log"), over)
K.save([entry(), entry(test=B), entry(test=C)])
pts = OW.nightly_news(LATE, {"open_ids": OPEN})
check("BUILD COP: parking every red ends the deadline and the groups", pts["testing.nightly_reds_overdue"]["v"] == 0
      and (pts.get(item.replace("NIGHTLY_COP_FIX_RED_", "testing.red_")[:-5].lower()) or {}).get("v") == 0, pts)

# a cured group reads 0 and clears; the cap spreads a flood over passes
reset()
K.save([])
reds = ["src/x/selftest_r%d.py" % i for i in range(12)]
write_log(night("2026-11-04T10:00:00Z", reds))
last("2026-11-04T10:00:00Z", [(t, "FAIL", ["rc 1", "FAIL cause number %s is its own" % chr(65 + i)]) for i, t in enumerate(reds)])
cap = K.new_items_per_pass()
known = set(OPEN)
st = run(NOW, known, OPEN)
check("BUILD COP: a flood files at most the per-pass cap of new items", 0 < len(filed()) == cap < 12, len(filed()))
known |= {a["name"] for a in filed()}
calls.clear()
st = run(NOW + 900, known, known)
check("BUILD COP: and the rest the next pass, none twice", len(filed()) == min(cap, 12 - cap)
      and not (set(a["name"] for a in filed()) & (known - set(OPEN))), filed())
known |= {a["name"] for a in filed()}
write_log(night("2026-11-04T10:00:00Z", reds) + night("2026-11-05T10:00:00Z", reds[1:]))
last("2026-11-05T10:00:00Z", [(t, "FAIL", ["rc 1", "FAIL cause number %s is its own" % chr(65 + i)]) for i, t in enumerate(reds) if i])
gone = [k for k, p in OW.nightly_news(NOW + K.DAY, {"open_ids": OPEN}).items() if k.startswith("testing.red_") and p["v"] == 0]
check("BUILD COP: a group gone green on a read night reads 0 (an absent key would hold its alarm open)", len(gone) == 1, gone)
calls.clear()
for k in range(4):
    st = run(NOW + K.DAY + 900 * k, known, known)
cleared = [a for a in calls if a.get("note_only") and "cleared" in a.get("text", "")]
check("BUILD COP: and clears after clear_passes, with a note on its item", len(cleared) == 1, calls)

import contextlib  # noqa: E402
import io  # noqa: E402
buf = io.StringIO()
real_time = K.time.time
K.time.time = lambda: NOW + K.DAY      # report reads the clock: pin it to the planted nights
try:
    with contextlib.redirect_stdout(buf):
        rc = K.main(["report"])
finally:
    K.time.time = real_time
check("CLI: report lists every group with its due date and each of its tests", rc == 0 and "build cop: 11 unparked red(s) in 11 group(s)"
      in buf.getvalue() and "selftest_r5.py" in buf.getvalue() and " due 2026-11-07" in buf.getvalue(), buf.getvalue()[-600:])

# ---- BUILD COP, the production wiring: the unit's own command line through main, run, the flow and testing collectors,
# the real rules and the real filer. Only what is outside this repo's reach is planted: the ledger events, the night, the
# ops dir, and the rimflow transport the filer spawns through. Every other family's collector is off (they read the machine).
import shlex  # noqa: E402
import time  # noqa: E402

WIRE = TMP / "wire"
(WIRE / "ops").mkdir(parents=True)
(WIRE / "queue").mkdir()
_ing = WIRE / "clone" / "src/RimMandrake/Utils/testq"
_ing.mkdir(parents=True)
(_ing / "ingest.py").write_text("import json, os\ndef rimflow(*a):\n    open(os.environ['KR_STUB_LOG'], 'a').write(json.dumps(a) + '\\n')\n"
                                "    return 0, ''\ndef publish(n, message=''):\n    return 'ok'\n", encoding="utf-8")
STUB = WIRE / "rimflow.log"
WCLOG = WIRE / "conductor_log.md"
_wr = json.loads((HERE / "ops_watch_rules.json").read_text(encoding="utf-8"))
for _t in _wr["targets"]:
    if _t.get("conductor_log"):
        _t["conductor_log"] = str(WCLOG)
(WIRE / "rules.json").write_text(json.dumps(_wr), encoding="utf-8")
os.environ.update(RM_OPS_WATCH_DIR=str(WIRE / "ops"), RM_OPS_WATCH_RULES=str(WIRE / "rules.json"), RM_OPS_ALARM_CLONE=str(WIRE / "clone"),
                  TESTQ_QUEUE=str(WIRE / "queue"), RM_TESTING_METRICS_DIR=str(WIRE / "metrics"), KR_STUB_LOG=str(STUB))


def ledger_file(iid, at):
    return {"event": "file", "id": iid, "ts": at, "seat": "BENCH", "title": "t", "for": "BENCH", "kind": "task", "target": "v1"}


def stamp(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def wire_pass(argv):
    """One pass as the unit runs it; -> (exit code, the rimflow calls this pass spawned)."""
    STUB.unlink(missing_ok=True)
    with contextlib.redirect_stdout(io.StringIO()):
        rc = OW.main(argv)
    return rc, [json.loads(ln) for ln in STUB.read_text(encoding="utf-8").splitlines()] if STUB.exists() else []


m = re.search(r"^ExecStart=\S+ \S*ops_watch\.py (.*)$", OW.UNIT, re.M)
ARGV = shlex.split(m.group(1)) if m else []
check("WIRE: the timer's unit files alarms on every family", ARGV == ["run", "--file-alarms"], ARGV)
WNOW = time.time()
WH = K.red_deadline_h()
OLD_RED, NEW_RED, PARKED = "src/x/selftest_old.py", "src/x/selftest_new.py", "src/x/selftest_parked.py"
NIGHTS = int(WH // 24) + 2                # OLD_RED's first night is past its deadline; NEW_RED went red only last night
_at = [stamp(WNOW - 3600 - (NIGHTS - 1 - i) * K.DAY) for i in range(NIGHTS)]
write_log(*[night(a, [OLD_RED, PARKED] + ([NEW_RED] if a == _at[-1] else [])) for a in _at])
last(_at[-1], [(OLD_RED, "FAIL", ["rc 1", "FAIL the old cause is one thing"]), (NEW_RED, "FAIL", ["rc 1", "FAIL the new cause is another"]),
               (PARKED, "FAIL", ["rc 1", "FAIL parked and still red"])])
K.save([entry(test=PARKED, item="WIRE_OPEN_ITEM", added=stamp(WNOW - K.DAY), expires=stamp(WNOW + 5 * K.DAY))])
_events = [ledger_file("WIRE_OPEN_ITEM", stamp(WNOW - 2 * K.DAY))]
_saved_collectors, _saved_release, _saved_ledger = dict(OW.COLLECTORS), OW.steve_release, PC.read_ledger
for _fam in list(OW.COLLECTORS):
    if _fam not in ("flow", "testing"):
        OW.COLLECTORS[_fam] = lambda now, rules, ctx: {}
OW.steve_release = lambda: []
PC.read_ledger = lambda: list(_events)
try:
    rc, seen = wire_pass(ARGV)
    spawned = {}
    for c in seen:
        if c[0] == "spawn":
            spawned[c[c.index("--name") + 1]] = c[c.index("--title") + 1]
    raised = [c[1] for c in seen if c[0] == "raise"]
    cop = {n: t for n, t in spawned.items() if n.startswith("NIGHTLY_COP_FIX_RED_")}
    late = {n: t for n, t in spawned.items() if n.startswith("OPS_RED_OVERDUE_CHASE_")}
    check("WIRE: a pass exits 0", rc == 0, rc)
    check("WIRE: the pass reads the nightly (the testing collector and the flow ledger reach known_reds)", cop, seen)
    check("WIRE: each new root cause is one item", len(cop) == 2 and any("selftest_new.py" in t for t in cop.values())
          and any("selftest_old.py" in t for t in cop.values()), spawned)
    _due = stamp(K.epoch(_at[-1]) + WH * 3600)[:16]
    check("WIRE: the new red's item carries its deadline, the night it went red plus the policy's hours",
          any("selftest_new.py" in t and "due " + _due in t for t in cop.values()), (_due, cop))
    check("WIRE: a red an entry on an OPEN item parks files nothing (the flow ledger's open items reach the list)",
          not any("selftest_parked.py" in t for t in spawned.values()), spawned)
    check("WIRE: the overdue red alarms, though its own item was filed this very pass; the fresh red is not overdue",
          len(late) == 1 and OLD_RED in list(late.values())[0] and NEW_RED not in list(late.values())[0], spawned)
    check("WIRE: every filing is raised, so it is top priority", spawned and sorted(raised) == sorted(spawned), (raised, sorted(spawned)))
    _rc_args = [c for c in seen if c[0] == "spawn" and c[c.index("--name") + 1] in cop]
    check("WIRE: filed for the pool relentless drains", all(c[c.index("--for") + 1] == _wr["alarm"]["for"] for c in _rc_args) and _rc_args, _rc_args)
    _log = WCLOG.read_text(encoding="utf-8") if WCLOG.exists() else ""
    check("WIRE: the overdue alarm reached the Conductor's log", late and list(late)[0] in _log, _log[-300:])
    _status = json.loads((WIRE / "ops" / "status.json").read_text(encoding="utf-8"))
    check("WIRE: the pass's own status shows the readings MEASURED", _status["points"]["testing.nightly_reds_overdue"].get("m") == "MEASURED"
          and _status["points"]["testing.nightly_reds_overdue"].get("v") == 1, _status["points"].get("testing.nightly_reds_overdue"))

    _events += [ledger_file(n, stamp(WNOW - 60)) for n in spawned]
    rc2, seen2 = wire_pass(ARGV)
    check("WIRE: the next pass, items open, files no second item", rc2 == 0 and not [c for c in seen2 if c[0] == "spawn"], seen2)

    # the flow ledger's open items reach the alarm step too: a newcomer to a group is a note while its item is open, a reopen once closed
    NEWITEM = next(n for n, t in cop.items() if "selftest_new.py" in t)


    def join_group(*tests):
        rows = [(OLD_RED, "FAIL", ["rc 1", "FAIL the old cause is one thing"]), (PARKED, "FAIL", ["rc 1", "FAIL parked and still red"])]
        rows += [(t, "FAIL", ["rc 1", "FAIL the new cause is another"]) for t in (NEW_RED,) + tests]
        write_log(*[night(a, [OLD_RED, PARKED] + ([NEW_RED] + list(tests) if a == _at[-1] else [])) for a in _at])
        last(_at[-1], rows)


    join_group("src/x/selftest_joins.py")
    rc3, seen3 = wire_pass(ARGV)
    check("WIRE: a second test with an open group's cause is a note on its item, no second item",
          any(c[:2] == ["note", NEWITEM] and "selftest_joins.py" in " ".join(c) for c in seen3)
          and not [c for c in seen3 if c[0] in ("spawn", "live")], seen3)
    _events.append({"event": "drop", "id": NEWITEM, "ts": stamp(WNOW - 30), "seat": "BENCH", "reason": "r"})  # replay gates a bare close; any not-open state serves
    join_group("src/x/selftest_joins.py", "src/x/selftest_joins_too.py")
    rc4, seen4 = wire_pass(ARGV)
    check("WIRE: the same news once the ledger says its item is no longer open reopens that item and raises it, no second item",
          any(c[:2] == ["live", NEWITEM] for c in seen4) and ["raise", NEWITEM] in [c[:2] for c in seen4]
          and not [c for c in seen4 if c[0] == "spawn"], seen4)
finally:
    OW.COLLECTORS.clear()
    OW.COLLECTORS.update(_saved_collectors)
    OW.steve_release, PC.read_ledger = _saved_release, _saved_ledger

print("known_reds: " + ("FAIL %d" % len(FAILS) if FAILS else "ok"))
sys.exit(1 if FAILS else 0)
