#!/usr/bin/env python3
"""ops_watch.c_queues checks, standalone (OPS_QUEUES_READING_RESTORE_HQXV): a crash elsewhere in
selftest_ops_watch.py must not hide them. Fixture-only: temp dirs, no real queue is read."""
import json
import os
import shutil
import sys
import tempfile as _tf
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
_TMP = Path(_tf.mkdtemp(prefix="selftest_ops_watch_queues_"))
os.environ["RM_OPS_WATCH_DIR"] = str(_TMP / "ops")
import ops_watch as OW  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  %s" % (detail,)))
    if not cond:
        FAILS.append(name)


# queues stalled (QUEUE_ORPHAN_WEDGE_1): pending > 0 with only a stale orphan in active/ is a stall, calm idle or not
_qd = Path(_tf.mkdtemp(prefix="qs_")); _qn = time.time()
for _x in ("pending", "active", "done", "failed"):
    (_qd / _x).mkdir()
_qr = {"queues": [{"name": "q", "pending": str(_qd / "pending"), "active": str(_qd / "active"),
                   "progress": [str(_qd / "done"), str(_qd / "failed")], "paused_file": str(_qd / "paused.json")}]}
def _qs(): return OW.c_queues(_qn, _qr, {})["queues.q.stalled_min"]
check("queues: nothing pending reads 0", _qs()["v"] == 0.0 and _qs()["m"] == "MEASURED")
(_qd / "pending" / "a.json").write_text("{}"); (_qd / "active" / "orph.json").write_text("{}")
for _f in (_qd / "pending" / "a.json", _qd / "active" / "orph.json"):
    os.utime(_f, (_qn - 3600, _qn - 3600))
check("queues: pending plus a 1 h stale orphan reads ~60 min stalled", 59 <= _qs()["v"] <= 61, _qs())
os.utime(_qd / "active" / "orph.json", (_qn - 60, _qn - 60))
check("queues: a heartbeating active job is movement", _qs()["v"] <= 1.1, _qs())
os.utime(_qd / "active" / "orph.json", (_qn - 3600, _qn - 3600))
(_qd / "paused.json").write_text("{}")
check("queues: a paused queue reads 0", _qs()["v"] == 0.0, _qs())
(_qd / "paused.json").unlink()
_qglob = Path.glob  # OPS_QUEUES_READING_RESTORE_HQXV: a pending job claimed between glob and stat is movement
def _ghost_glob(self, pat):
    yield from _qglob(self, pat)
    if self == _qd / "pending":
        yield self / "claimed_meanwhile.json"
Path.glob = _ghost_glob
try:
    _qv = OW.c_queues(_qn, _qr, {})
finally:
    Path.glob = _qglob
check("queues: a job claimed between glob and stat is not a blind queue", _qv["queues.blind"]["v"] == 0
      and _qv["queues.q.pending"]["v"] == 1 and _qv["queues.q.stalled_min"]["m"] == "MEASURED", _qv)
_qr["queues"][0]["pending"] = str(_qd / "nope")
check("queues: an unlistable queue is blind, not 0", OW.c_queues(_qn, _qr, {})["queues.blind"]["v"] == 1
      and OW.c_queues(_qn, _qr, {})["queues.q.stalled_min"]["m"] == "UNMEASURED")
_rl = OW.load_rules()
check("queues: artpipe is wired with one fixed alarm id", any(t["key"] == "queues.artpipe.stalled_min" and t["alarm"]
      and t["name"] == "OPS_ARTPIPE_UNSTICK" for t in _rl["targets"]))

# every class of every queues.* metric in the real ranges block has its fixture (selftest_ops_ranges excludes queues.*
# from its count and delegates here; OPS_RANGES_FIXTURE_REPAIR_FOUR_CLASSES_SHORT). The real rules, the queue dirs
# swapped for fixtures under the same names, so a new queue or class in the rules without a fixture here goes red.
import copy  # noqa: E402
_cr = copy.deepcopy(_rl)
_cd = Path(_tf.mkdtemp(prefix="qc_"))
_cr["queues"] = []
for _q in _rl["queues"]:
    _b = _cd / _q["name"]
    for _x in ("pending", "active", "done"):
        (_b / _x).mkdir(parents=True)
    _cr["queues"].append({"name": _q["name"], "pending": str(_b / "pending"), "active": str(_b / "active"),
                          "progress": [str(_b / "done")], "paused_file": str(_b / "paused.json")})
_cms = {k: m for k, m in OW.ranges_of(_cr).items() if k.startswith("queues.")}


def _classes():
    pts = OW.c_queues(_qn, _cr, {})
    OW.stamp_ranges(pts, _cr)
    return {k: pts.get(k, {}).get("class") for k in _cms}


_seen = set()
_calm = _classes()
check("queues classes: every queue idle and listable reads sane on every queues.* metric",
      all(c == "sane" for c in _calm.values()), _calm)
_seen |= {(k, c) for k, c in _calm.items()}
for _q in _cr["queues"]:
    _p = Path(_q["pending"]) / "stuck.json"; _p.write_text("{}")
    os.utime(_p, (_qn - 3600, _qn - 3600))
_stuck = _classes()
_sk = ["queues.%s.stalled_min" % q["name"] for q in _cr["queues"]]
check("queues classes: a pending job stalled 1 h reads distressed on its queue's stalled_min",
      all(_stuck.get(k) == "distressed" for k in _sk) and _stuck.get("queues.blind") == "sane", _stuck)
_seen |= {(k, c) for k, c in _stuck.items()}
_cr["queues"][0]["pending"] = str(_cd / "nope")
_blind = _classes()
check("queues classes: an unlistable queue reads distressed on queues.blind", _blind.get("queues.blind") == "distressed",
      _blind)
_seen |= {(k, c) for k, c in _blind.items()}
_every = {(k, c) for k, m in _cms.items() for c in m["classes"]}
check("queues classes: every class of every queues.* metric had its fixture", _every <= _seen and len(_every) > 0,
      sorted(_every - _seen))
_rlq = OW.load_rules()
# the stragglers (QUEUE_STALL_ALARM_FINISH_THE_STRAGGLERS): every claim/lease queue is a rules entry read by a named reader
_ar = Path(_tf.mkdtemp(prefix="qrc_")); _rc = _ar / "ralph_c"
for _x in ("claims", "logs", "results"):
    (_rc / _x).mkdir(parents=True)
_qr2 = {"queues": [{"name": "rc", "reader": "ralph_c", "root": str(_ar), "armed_file": str(_ar / "arm.toml")}]}
def _rcs(): return OW.c_queues(_qn, _qr2, {})["queues.rc.stalled_min"]
check("queues/ralph_c: an empty runner queue reads 0", _rcs()["v"] == 0.0 and _rcs()["m"] == "MEASURED", _rcs())
(_rc / "candidates.jsonl").write_text(json.dumps({"builder": "B", "cand": "c1", "item": "I1", "sha": "s",
    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(_qn - 7200))}) + "\n")
check("queues/ralph_c: unarmed (no arm.toml) reads 0 though a candidate waits",
      _rcs()["v"] == 0.0 and OW.c_queues(_qn, _qr2, {})["queues.rc.pending"]["v"] == 1, _rcs())
(_ar / "arm.toml").write_text("")
check("queues/ralph_c: armed, a candidate pending 2 h with no claim or run reads ~120 min", 119 <= _rcs()["v"] <= 121, _rcs())
(_rc / "claims" / "c1").write_text("run1"); os.utime(_rc / "claims" / "c1", (_qn - 5400, _qn - 5400))
(_rc / "logs" / "run1.log").write_text("x"); os.utime(_rc / "logs" / "run1.log", (_qn - 120, _qn - 120))
check("queues/ralph_c: a claimed run whose log moves is movement", _rcs()["v"] <= 2.1, _rcs())
os.utime(_rc / "logs" / "run1.log", (_qn - 5400, _qn - 5400))
check("queues/ralph_c: an orphan claim with a dead log is a stall", 89 <= _rcs()["v"] <= 91, _rcs())
(_ar / "events").mkdir(); (_ar / "events" / "ralph_c.jsonl").write_text("{}\n")
os.utime(_ar / "events" / "ralph_c.jsonl", (_qn - 300, _qn - 300))
check("queues/ralph_c: a long run whose lane events move is movement (its log lands only at the end)",
      _rcs()["v"] <= 5.1, _rcs())
os.utime(_ar / "events" / "ralph_c.jsonl", (_qn - 5400, _qn - 5400))
(_rc / "results" / "run1.json").write_text(json.dumps({"item": "I1", "cand": "c1", "verdict": "pass"}))
check("queues/ralph_c: a counted result empties the queue", _rcs()["v"] == 0.0
      and OW.c_queues(_qn, _qr2, {})["queues.rc.pending"]["v"] == 0, _rcs())
(_rc / "results" / "bad.json").write_text("{not json")
check("queues/ralph_c: an unreadable result is blind, not 0", _rcs()["m"] == "UNMEASURED"
      and OW.c_queues(_qn, _qr2, {})["queues.blind"]["v"] == 1, _rcs())
(_ar / "arm.toml").unlink()
check("queues/ralph_c: a switched-off arena with an unreadable queue reads 0, not blind", _rcs()["v"] == 0.0
      and _rcs()["m"] == "MEASURED" and OW.c_queues(_qn, _qr2, {})["queues.blind"]["v"] == 0, _rcs())
_rp = Path(_tf.mkdtemp(prefix="qrp_")); (_rp / "logs").mkdir(); _tk = _rp / "ticks.jsonl"
_qr3 = {"queues": [{"name": "rp", "reader": "replay_arms", "replay": str(_rp), "ticks": str(_tk), "arms": ["a1", "a2"],
                    "stop_line": _qn + 86400}]}
def _rps(): return OW.c_queues(_qn, _qr3, {})["queues.rp.stalled_min"]
check("queues/replay: no tick and no arm log reads 0", _rps()["v"] == 0.0 and _rps()["m"] == "MEASURED", _rps())
_tk.write_text(json.dumps({"rows": [{"arm": "a1", "state": "PAGED"}, {"arm": "a2", "state": "WAITING"}]}) + "\n")
os.utime(_tk, (_qn - 7200, _qn - 7200))
(_rp / "logs" / "a1.log").write_text("x"); os.utime(_rp / "logs" / "a1.log", (_qn - 9000, _qn - 9000))
check("queues/replay: paged and waiting arms with a stale tick are not in flight", _rps()["v"] == 0.0, _rps())
os.utime(_rp / "logs" / "a1.log", (_qn - 60, _qn - 60))
check("queues/replay: an arm logging after the last tick with no tick since reads ~120 min", 119 <= _rps()["v"] <= 121, _rps())
(_rp / "logs" / "a1.log").write_text("2026-10-31T22:10:19-0700 a1: task T DONE closed verdict accept\n"
                                     "2026-10-31T22:10:19-0700 a1: runner ends: ran 11, skipped 14, stopped None\n")
os.utime(_rp / "logs" / "a1.log", (_qn - 60, _qn - 60))
check("queues/replay: an arm that finished after the last tick is not in flight", _rps()["v"] == 0.0, _rps())
(_rp / "logs" / "a1.log").write_text("2026-10-31T22:10:19-0700 a1: task T START\n")
os.utime(_rp / "logs" / "a1.log", (_qn - 60, _qn - 60))
_tk.rename(_rp / "ticks.off")
check("queues/replay: an arm in flight and no watcher tick ever is blind, not a calm 0", _rps()["m"] == "UNMEASURED", _rps())
(_rp / "ticks.off").rename(_tk)
os.utime(_rp / "logs" / "a1.log", (_qn - 9000, _qn - 9000))
_tk.write_text(json.dumps({"rows": [{"arm": "a1", "state": "RUNNING"}]}) + "\n"); os.utime(_tk, (_qn - 300, _qn - 300))
check("queues/replay: a RUNNING arm with a fresh tick is watched", _rps()["v"] <= 5.1, _rps())
os.utime(_tk, (_qn - 3600, _qn - 3600))
check("queues/replay: a RUNNING arm and a dead watcher is a stall", 59 <= _rps()["v"] <= 61, _rps())
_qr3["queues"][0]["stop_line"] = _qn - 1
check("queues/replay: past the stop line nothing is in flight", _rps()["v"] == 0.0, _rps())
_qr3["queues"][0]["replay"] = str(_rp / "nope")
check("queues/replay: past the stop line even a cleaned-up replay dir reads 0", _rps()["v"] == 0.0 and _rps()["m"] == "MEASURED")
_qr3["queues"][0]["stop_line"] = _qn + 86400
check("queues/replay: a missing replay dir is blind", _rps()["m"] == "UNMEASURED")
check("queues: an unknown reader is blind, not 0", OW.c_queues(_qn, {"queues": [{"name": "z", "reader": "nope"}]}, {})
      ["queues.blind"]["v"] == 1)
_ids = {t["key"]: t["name"] for t in _rlq["targets"] if t["key"].startswith("queues.") and t.get("alarm")}
_qnames = [q["name"] for q in _rlq["queues"]]
check("queues: every wired queue has exactly one fixed-id alarm target and a range",
      all(_ids.get("queues.%s.stalled_min" % n) for n in _qnames)
      and all(("queues.%s.stalled_min" % n) in _rlq["ranges"] for n in _qnames)
      and len(set(_ids.values())) == len(_ids) and "queues.blind" in _ids, (_qnames, _ids))
check("queues: the stragglers are wired (arena runner claims, replay watcher)",
      {"arena_ralph_c", "replay_watch"} <= set(_qnames)
      and all(q.get("reader", "dirs") in OW.QUEUE_READERS for q in _rlq["queues"]), _qnames)
# census (QUEUE_STALL_ALARM_FINISH_THE_STRAGGLERS): the claim/lease queues are exactly these; a new one joins the census here
_CENSUS = {"artpipe", "testq", "arena_ralph_c", "replay_watch"}
check("queues: the wired set is exactly the claim/lease census (none dropped, none unaccounted)",
      set(_qnames) == _CENSUS and len(_qnames) == len(_CENSUS), sorted(set(_qnames) ^ _CENSUS))
check("queues: the stragglers read through their own readers, not the dir reader",
      {q["name"]: q.get("reader", "dirs") for q in _rlq["queues"] if q["name"] in ("arena_ralph_c", "replay_watch")}
      == {"arena_ralph_c": "ralph_c", "replay_watch": "replay_arms"}, _rlq["queues"])
check("queues: each straggler's alarm target carries its fixed id",
      _ids.get("queues.arena_ralph_c.stalled_min") == "OPS_ARENA_CLAIMS_UNSTICK_NOBODY_HOME"
      and _ids.get("queues.replay_watch.stalled_min") == "OPS_REPLAY_UNSTICK_WATCHMAN_NAPPING", _ids)
# Fleet Watch is not a queue: the owner retired it 2026-11-04, so no queue or alarm target may name it
_own = HERE.parents[2] / "infrastructure" / "state" / "ledger" / "events" / "OWNER.jsonl"
_ret = [json.loads(_l) for _l in _own.read_text(encoding="utf-8").splitlines()
        if "FLEETWATCH_CODE_RETIRE_NOBODY_WAS_WATCHING" in _l] if _own.exists() else []
check("queues/fleet: the owner's retirement of Fleet Watch is on the ledger",
      any(e.get("id") == "FLEETWATCH_CODE_RETIRE_NOBODY_WAS_WATCHING" and e.get("seat") == "OWNER"
          and "Retire FleetWatch" in (e.get("ownerSaid") or "") for e in _ret), (str(_own), len(_ret)))
check("queues/fleet: no queue entry or queues.* target names the retired Fleet Watch",
      not any("fleet" in json.dumps(q).lower() for q in _rlq["queues"])
      and not any("fleet" in t["key"].lower() for t in _rlq["targets"] if t["key"].startswith("queues.")), _qnames)
for _d in (_TMP, _qd, _cd, _ar, _rp):
    shutil.rmtree(_d, ignore_errors=True)
print("GREEN" if not FAILS else "RED: %d failed: %s" % (len(FAILS), ", ".join(FAILS)))
sys.exit(1 if FAILS else 0)
