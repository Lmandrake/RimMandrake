#!/usr/bin/env python3
"""ops_watch.c_queues checks, standalone (OPS_QUEUES_READING_RESTORE_HQXV): a crash elsewhere in
selftest_ops_watch.py must not hide them. Fixture-only: temp dirs, no real queue is read."""
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
for _d in (_TMP, _qd, _cd):
    shutil.rmtree(_d, ignore_errors=True)
print("GREEN" if not FAILS else "RED: %d failed: %s" % (len(FAILS), ", ".join(FAILS)))
sys.exit(1 if FAILS else 0)
