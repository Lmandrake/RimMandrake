#!/usr/bin/env python3
"""DESIGNER_STALL_MONITOR_READY_AND_FORGOTTEN: a Designer concept at status=ready with no run for over 60 min raises
the ops_watch alarm for Operations; so does one at status=waiting_owner whose owner has answered
(DESIGNER_ANSWERED_MONITOR_WAITING_ON_NOBODY), pending since his answer. Fixture-only: stage.json files in temp dirs fed through c_queues and run_alarms
with the real rules; no real concept is read and nothing is filed."""
import json
import os
import shutil
import sys
import tempfile as _tf
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
_TMP = Path(_tf.mkdtemp(prefix="selftest_designer_stall_"))
os.environ["RM_OPS_WATCH_DIR"] = str(_TMP / "ops")
import ops_watch as OW  # noqa: E402

FAILS = []
KEY = "queues.designer.stalled_min"


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  %s" % (detail,)))
    if not cond:
        FAILS.append(name)


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


NOW = time.time()
ROOT = _TMP / "concepts"
ROOT.mkdir()


def concept(name, status, last_min, running_min=None):
    d = ROOT / name
    d.mkdir(exist_ok=True)
    st = {"schema": 1, "mod": name, "stage": 2, "status": status,
          "running": {"run": "r", "at": iso(NOW - running_min * 60)} if running_min is not None else None,
          "history": [{"at": iso(NOW - 900 * 60), "what": "init", "why": "", "stage": 0},
                      {"at": iso(NOW - last_min * 60), "what": "close", "why": "", "stage": 2}]}
    (d / "stage.json").write_text(json.dumps(st))


RULES = OW.load_rules()
Q = [q for q in RULES["queues"] if q.get("name") == "designer"]
check("rules: a designer queue is wired through the designer_stage reader, paused by the Designer's off switch",
      len(Q) == 1 and Q[0].get("reader") == "designer_stage" and Q[0].get("paused_file", "").endswith("DESIGNER_OFF"), Q)
TG = [t for t in RULES["targets"] if t.get("key") == KEY]
check("rules: one alarm target over 60 min with a fixed id", len(TG) == 1 and TG[0].get("alarm") is True
      and TG[0].get("op") == ">" and TG[0].get("value") == 60 and TG[0].get("name") == "OPS_DESIGNER_UNSTICK_READY_AND_WAITING", TG)
RG = OW.ranges_of(RULES).get(KEY) or {}
check("ranges: owned by Operations, distressed from 60 min", RG.get("owner") == "Operations"
      and RG.get("classes", {}).get("distressed") == {"at_least": 60}, RG)
OFF = _TMP / "DESIGNER_OFF"
QR = {"queues": [dict(Q[0] if Q else {}, root=str(ROOT), paused_file=str(OFF))]}


def read():
    return OW.c_queues(NOW, QR, {})


def stalled():
    return read()[KEY]


check("an empty concepts dir reads 0, measured", stalled()["v"] == 0.0 and stalled()["m"] == "MEASURED", stalled())
concept("Waiting", "waiting_owner", 600)
concept("Locked", "locked", 600)
concept("Blocked", "blocked", 600)
check("concepts waiting on him, locked or blocked are not pending", stalled()["v"] == 0.0
      and read()["queues.designer.pending"]["v"] == 0, read())
concept("Fresh", "ready", 59)
check("a concept ready 59 min reads ~59, under the alarm", 58.5 <= stalled()["v"] <= 59.5, stalled())
concept("FlowWorks", "ready", 61)
check("a concept ready 61 min with no run reads ~61 (the oldest ready concept wins)", 60.5 <= stalled()["v"] <= 61.5, stalled())
concept("Busy", "ready", 3, running_min=3)
check("a run on another concept does not hide the forgotten one", 60.5 <= stalled()["v"] <= 61.5
      and read()["queues.designer.active"]["v"] == 1, read())
concept("FlowWorks", "ready", 120, running_min=5)
check("a run open on the forgotten concept is movement", stalled()["v"] <= 59.5, stalled())
concept("FlowWorks", "ready", 120, running_min=90)
check("a run open 90 min with no close is a stall again", 89.5 <= stalled()["v"] <= 90.5, stalled())
concept("FlowWorks", "ready", 120)
check("FlowWorks' 2026-11-04 shape (ready 120 min, no run) reads ~120", 119.5 <= stalled()["v"] <= 120.5, stalled())
OFF.write_text("")
check("the Designer's off switch reads 0", stalled()["v"] == 0.0, stalled())
OFF.unlink()
(ROOT / "Torn").mkdir()
(ROOT / "Torn" / "stage.json").write_text("{not json")
_r = read()
check("a stage.json that does not parse is blind, never a calm 0", _r[KEY]["m"] == "UNMEASURED"
      and _r["queues.blind"]["v"] == 1, _r)
shutil.rmtree(ROOT / "Torn")
(ROOT / "NoTime").mkdir()
(ROOT / "NoTime" / "stage.json").write_text(json.dumps({"status": "ready", "history": [{"at": "garbled"}]}))
check("a ready concept with no readable time is blind, never a guess", read()[KEY]["m"] == "UNMEASURED", read()[KEY])
shutil.rmtree(ROOT / "NoTime")
# DESIGNER_ANSWERED_MONITOR_WAITING_ON_NOBODY: waiting_owner with his answer in, and nobody opens the run
sys.path.insert(0, str(HERE.parent / "rimflow"))
import designer_stage as DS  # noqa: E402
CL = _TMP / "clone"
SHARD = CL / "infrastructure/state/ledger/events/OWNER.jsonl"
SHARD.parent.mkdir(parents=True)
SHARD.write_text("")
ITEM = "SELFTEST_FIXTURE_CONCEPT_ZZQ"
QR = {"queues": [dict(QR["queues"][0], repo=str(CL))]}
# RELAPSE_QUEUES_FIX_DIED_TWICE: a ready concept whose rejected last result is PARKED (designer_stage.rejection_parked,
# the rule the orphan sweep retries by) is not pending; once its cause is gone (the cited file landed) it is, so the
# stall alarm counts exactly what the sweep should have moved (incident queues-20261105210826).
_GSV = "design/concepts/Gss/coverage_verdict.json"
concept("Gss", "ready", 300)
_g = json.loads((ROOT / "Gss" / "stage.json").read_text())
_g["results"] = [{"at": iso(NOW - 300 * 60), "outcome": "rejected", "run": "rm-role-designer-1", "stage": 2,
                  "why": ["asks[a]: source path %s does not exist" % _GSV]}]
(ROOT / "Gss" / "stage.json").write_text(json.dumps(_g))
check("a rejected concept whose cited file is still missing is parked, not a stall", 119.5 <= stalled()["v"] <= 120.5,
      stalled())
(CL / _GSV).parent.mkdir(parents=True, exist_ok=True)
(CL / _GSV).write_text("{}")
check("the cited file lands after the rejection: the concept is pending again (~300 min)",
      299.5 <= stalled()["v"] <= 300.5, stalled())
shutil.rmtree(ROOT / "Gss")


def owner_event(min_ago, ident):
    with open(SHARD, "a") as fh:
        fh.write(json.dumps({"seat": "OWNER", "event": "note", "id": ITEM, "note": ident,
                             "tsn": int((NOW - min_ago * 60) * 1e9)}) + "\n")


def waiting(name, last_min, feed_now=True):
    d = ROOT / name
    d.mkdir(exist_ok=True)
    st = {"schema": 1, "mod": name, "item": ITEM, "stage": 1, "status": "waiting_owner", "running": None,
          "history": [{"at": iso(NOW - 900 * 60), "what": "init", "why": "", "stage": 0},
                      {"at": iso(NOW - last_min * 60), "what": "close", "why": "", "stage": 1}]}
    if feed_now:
        st["waiting_owner_feed"] = DS.owner_feed(str(CL), ITEM, str(d))
    (d / "stage.json").write_text(json.dumps(st))


for _n in ("Fresh", "FlowWorks", "Busy", "Waiting", "Locked", "Blocked"):
    shutil.rmtree(ROOT / _n, ignore_errors=True)
owner_event(1000, "an older reply, already there when the asks went out")
waiting("GSS", 300)
check("waiting_owner, he has not answered (feed unchanged) for 300 min: not pending", stalled()["v"] == 0.0
      and read()["queues.designer.pending"]["v"] == 0, read())
owner_event(45, "his answer")
check("his answer 45 min ago, no run: pending ~45 min, under the alarm (pending since his answer, not the wait)",
      44.5 <= stalled()["v"] <= 45.5 and read()["queues.designer.pending"]["v"] == 1, read())
owner_event(30, "a second reply")
check("a second reply does not restart the clock: the earliest answer wins", 44.5 <= stalled()["v"] <= 45.5, stalled())
SHARD.write_text("")
owner_event(1000, "an older reply, already there when the asks went out")
owner_event(61, "his answer")
check("his answer 61 min ago, no run: ~61, the alarm's side", 60.5 <= stalled()["v"] <= 61.5, stalled())
_pts = read()
OW.stamp_ranges(_pts, RULES)
check("the alarm target is crossed by an answered, forgotten waiting_owner concept",
      OW.target_state(_pts, RULES).get("QUEUE_STALLED:" + KEY) is True, _pts[KEY])
waiting("GSS", 300, feed_now=False)
check("waiting_owner with no feed recorded is not answered (owner_moved's rule): 0", stalled()["v"] == 0.0, stalled())
SHARD.write_text("")
owner_event(1000, "an older reply, already there when the asks went out")
waiting("GSS", 300)
owner_event(400, "a reply older than the wait, newly visible (a clone that had not pulled it)")
# the feed moved, but by no event newer than the wait: the clock is the wait's start
_st = json.loads((ROOT / "GSS" / "stage.json").read_text())
_st["waiting_owner_feed"] = "a-feed-that-no-longer-matches"
(ROOT / "GSS" / "stage.json").write_text(json.dumps(_st))
check("feed moved with no event newer than the wait: pending since the wait began (~300)",
      299.5 <= stalled()["v"] <= 300.5, stalled())
_orig = DS.owner_uncited
DS.owner_uncited = lambda *a, **k: None
_r = read()
check("a waiting concept whose OWNER shard is unreadable is blind, never a calm 0", _r[KEY]["m"] == "UNMEASURED"
      and _r["queues.blind"]["v"] == 1, _r)
DS.owner_uncited = _orig
shutil.rmtree(ROOT / "GSS")
concept("FlowWorks", "ready", 120)
QR_MISSING = {"queues": [dict(QR["queues"][0], root=str(_TMP / "nope"))]}
_r = OW.c_queues(NOW, QR_MISSING, {})
check("a missing concepts dir is blind", _r[KEY]["m"] == "UNMEASURED" and _r["queues.blind"]["v"] == 1, _r)

# class and alarm: the real ranges and target over the fixture's points
_pts = read()
OW.stamp_ranges(_pts, RULES)
check("120 min ready reads distressed", _pts[KEY].get("class") == "distressed", _pts[KEY])
AID = "QUEUE_STALLED:" + KEY
check("the alarm target is crossed on a 120 min stall", OW.target_state(_pts, RULES).get(AID) is True,
      OW.target_state(_pts, RULES).get(AID))
_nm = OW.alarm_prefix(TG[0], "QUEUE_STALLED", KEY, {}, AID, _pts[KEY]) if TG else ""
import pulse_core as _pc  # noqa: E402
check("its fixed item name is this rule's own, the same on every pass, and passes the namecheck",
      _nm.startswith("OPS_DESIGNER_UNSTICK_READY_AND_WAITING_") and _nm == OW.alarm_prefix(TG[0], "QUEUE_STALLED", KEY,
      {}, AID, _pts[KEY]) and not _pc._model().mint_problems(_nm, set()), _nm)
concept("FlowWorks", "ready", 59)
_ok = read()
check("the alarm is clear at 59 min", OW.target_state(_ok, RULES).get(AID) is False, _ok[KEY])
# routing: Operations reads it (alarm_routes.json, first match wins)
_routes = json.loads((HERE.parent / "rimflow" / "alarm_routes.json").read_text(encoding="utf-8"))["routes"]
import fnmatch  # noqa: E402
_hit = next((r for r in _routes if fnmatch.fnmatch(KEY, r["match"])), None)
check("the alarm routes to Operations", bool(_hit) and _hit.get("reader") == "Operations", _hit)
shutil.rmtree(_TMP, ignore_errors=True)
print("GREEN" if not FAILS else "RED: %d failed: %s" % (len(FAILS), ", ".join(FAILS)))
sys.exit(1 if FAILS else 0)
