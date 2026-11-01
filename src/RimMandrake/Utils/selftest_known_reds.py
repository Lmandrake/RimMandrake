#!/usr/bin/env python3
"""selftest_known_reds.py -- TE1's own test: plant a new red, alarm; plant a listed red, silence; an entry past its age
alarms; an entry with no open item is refused and covers nothing; a new red on an open alarm is said, not swallowed."""
import json
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
check("metric: listed reds are counted, the unlisted ones are the news", pts["testing.nightly_news"]["v"] == 2
      and pts["testing.nightly_known_reds"]["v"] == 1, pts)
check("metric: no ledger is UNMEASURED, not 0", OW.nightly_news(NOW, {})["testing.nightly_news"]["m"] == "UNMEASURED")
check("metric: a stale newest night is UNMEASURED", OW.nightly_news(NOW + 2 * K.DAY, {"open_ids": OPEN})["testing.nightly_news"]["m"] == "UNMEASURED")
Path(os.environ["RM_KNOWN_REDS"]).write_text("{", encoding="utf-8")
check("metric: an unreadable list is UNMEASURED, not 0", OW.nightly_news(NOW, {"open_ids": OPEN})["testing.nightly_news"]["m"] == "UNMEASURED")
K.save([dict(entry(), item="")])
check("a malformed entry is refused: it covers nothing and is news", any("bad list entry" in n for n in K.measure(OPEN, NOW)["news"]))

# ---- TE1 end to end, through the real rules and the real alarm step
RULES = OW.load_rules(HERE / "ops_watch_rules.json")
KEY = "testing.nightly_news"
AID = "NIGHTLY_NEWS:" + KEY
calls = []


def filer(todo, conf):
    calls.extend(todo)
    return {a["name"]: None for a in todo}


K.save([entry()])
write_log(night("2026-11-04T10:00:00Z", [A]))
st = OW.run_alarms(OW.nightly_news(NOW, {"open_ids": OPEN}), RULES, NOW, set(OPEN), filer, OPEN)
check("TE1 end to end: a listed red files nothing", calls == [] and not st, (calls, st))
write_log(night("2026-11-04T10:00:00Z", [A, B]))
st = OW.run_alarms(OW.nightly_news(NOW, {"open_ids": OPEN}), RULES, NOW, set(OPEN), filer, OPEN)
filed = [a for a in calls if not a.get("note_only")]
check("TE1 end to end: a new red files one item naming the test", len(filed) == 1 and B in filed[0]["title"]
      and filed[0]["name"].startswith("OPS_NIGHTLY_RED_DIAGNOSE_"), calls)
item = st[AID]["item"]
calls.clear()
write_log(night("2026-11-05T10:00:00Z", [A, B]))
live = {item, "OPEN_ITEM"}
OW.run_alarms(OW.nightly_news(NOW + K.DAY, {"open_ids": OPEN}), RULES, NOW + K.DAY, live, filer, live)
check("the same red next night is said once", calls == [], calls)
write_log(night("2026-11-06T10:00:00Z", [A, B, C]))
st = OW.run_alarms(OW.nightly_news(NOW + 2 * K.DAY, {"open_ids": OPEN}), RULES, NOW + 2 * K.DAY, live, filer, live)
check("a second new red on the open alarm is a note on its item", [(a.get("note_only"), a.get("item")) for a in calls] == [(True, item)]
      and C in calls[0]["text"] and B not in calls[0]["text"], calls)
calls.clear()
OW.run_alarms(OW.nightly_news(NOW + 2 * K.DAY, {"open_ids": OPEN}), RULES, NOW + 2 * K.DAY + 900, live, filer, live)
check("and is said once", calls == [], calls)
write_log(night("2026-11-07T10:00:00Z", [A, B, C], ["src/x/selftest_d.py"]))
st = OW.run_alarms(OW.nightly_news(NOW + 3 * K.DAY, {"open_ids": OPEN}), RULES, NOW + 3 * K.DAY, live, filer, set(OPEN))
check("a new red after the alarm's item closed reopens that item, it does not note a closed one",
      [(bool(a.get("reopen")), a["name"]) for a in calls] == [(True, item)] and st[AID]["state"] == "OPEN", calls)

print("known_reds: " + ("FAIL %d" % len(FAILS) if FAILS else "ok"))
sys.exit(1 if FAILS else 0)
