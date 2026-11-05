#!/usr/bin/env python3
"""The sense beat's two read caches (OPS_METRONOME_MIGRATE_CLOCKS_FENCED): csuite_codex_limits.readings(cache=) and
ops_watch.newest_progress_mtime. Each must read what the uncached read reads (the codex family took 24 s and queues 16 s
on drvfs, over the metronome's 15 s sense limit). Fixture-only: temp dirs, no real queue or rollout is read."""
import json
import os
import sys
import tempfile as _tf
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "sim"))
_TMP = Path(_tf.mkdtemp(prefix="selftest_ops_watch_sense_caches_"))
os.environ["RM_OPS_WATCH_DIR"] = str(_TMP / "ops")
import ops_watch as OW  # noqa: E402
import csuite_codex_limits as CX  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  %s" % (detail,)))
    if not cond:
        FAILS.append(name)


# --- codex readings cache -------------------------------------------------------------------------------------------
def rl(ts, used):
    return json.dumps({"timestamp": ts, "payload": {"rate_limits": {
        "primary": {"used_percent": used, "window_minutes": 300, "resets_at": 1},
        "secondary": {"used_percent": used, "window_minutes": 10080, "resets_at": 2}, "plan_type": "pro"}}}) + "\n"


cd = _TMP / "codex" / "2026" / "11"
cd.mkdir(parents=True)
a, b = cd / "rollout-a.jsonl", cd / "rollout-b.jsonl"
a.write_text(rl("2026-11-04T01:00:00Z", 10) + '{"other": 1}\n' + rl("2026-11-04T02:00:00Z", 11))
b.write_text(rl("2026-11-04T03:00:00Z", 12))
cache = str(_TMP / "cx.json")
dirs = [str(_TMP / "codex")]


def same(label):
    plain, cached = CX.readings(dirs), CX.readings(dirs, cache=cache)
    check("codex cache: %s reads what the plain read reads" % label, plain == cached, (plain, cached))
    return cached


same("cold")
check("codex cache: the cache file is written", os.path.exists(cache))
same("warm")
with open(a, "a") as fh:            # an appended reading, then a half-written line still being flushed
    fh.write(rl("2026-11-04T04:00:00Z", 13))
    fh.write(rl("2026-11-04T05:00:00Z", 14)[:30])
got = same("after an append with a half line")
check("codex cache: the half-written line is not a reading", len(got[0]) == 4, got)
with open(a, "a") as fh:
    fh.write(rl("2026-11-04T05:00:00Z", 14)[30:])
got = same("once the half line completes")
check("codex cache: the completed line is read once", [r[1] for r in got[0]] == [10, 11, 12, 13, 14], got)
b.write_text(rl("2026-11-04T03:30:00Z", 20))   # rewritten shorter: read whole again
same("after a rewrite")
os.unlink(b)
got = same("after a file is deleted")
check("codex cache: a deleted file's readings go", 20 not in [r[1] for r in got[0]], got)
Path(cache).write_text("not json")
same("over a corrupt cache file")
for bad in ({"x": 1}, {"v": CX.CACHE_V, "files": {str(a): 5}}, {"v": CX.CACHE_V, "files": {str(a): {"recs": 3}}},
            {"v": CX.CACHE_V, "files": {str(a): {"mt": 1, "sz": 1, "off": 1, "head": "", "recs": [5], "tail": []}}}):
    Path(cache).write_text(json.dumps(bad))
    try:
        same("over a malformed cache %s" % json.dumps(bad)[:40])
    except Exception as e:  # noqa: BLE001
        check("codex cache: a malformed cache %s reads afresh" % json.dumps(bad)[:40], False, repr(e))
nl = cd / "rollout-nl.jsonl"
nl.write_text(rl("2026-11-04T06:00:00Z", 30).rstrip("\n"))     # a whole reading with no newline yet
got = same("with a last line that has no newline")
got = same("with that line, warm")
check("codex cache: the unterminated whole line is a reading, once", [r[1] for r in got[0]].count(30) == 1, got)
with open(nl, "a") as fh:
    fh.write("\n" + rl("2026-11-04T07:00:00Z", 31))
got = same("once that line gains its newline and another")
check("codex cache: it is still read once", [r[1] for r in got[0]].count(30) == 1 and 31 in [r[1] for r in got[0]], got)
os.utime(a, (time.time() - 30 * 86400,) * 2)
check("codex cache: newer_than still skips an old file",
      CX.readings(dirs, newer_than=time.time() - 86400, cache=cache) == CX.readings(dirs, newer_than=time.time() - 86400))

# --- queue progress-dir cache ---------------------------------------------------------------------------------------
qd = _TMP / "done"
qd.mkdir()
now = time.time()
for i in range(5):
    f = qd / ("j%d.json" % i)
    f.write_text("{}")
    os.utime(f, (now - 1000 + i, now - 1000 + i))
pc = {}


def progress(label, at=None):
    want = OW.newest_mtime(qd)
    got = OW.newest_progress_mtime(qd, pc, now if at is None else at)
    check("queue cache: %s matches newest_mtime" % label, want == got, (want, got))


progress("cold")
progress("warm")
f = qd / "j9.json"
f.write_text("{}")
os.utime(f, (now - 10, now - 10))
progress("after a finish moves a newer job in")
(qd / "x.worker_last_message.json").write_text("{}")
os.utime(qd / "x.worker_last_message.json", (now, now))
progress("with a worker message file (skipped)")
os.unlink(f)
progress("after the newest job vanishes")
os.utime(qd / "j0.json", (now - 5, now - 5))   # rewritten in place: seen at the hourly full pass
OW.PROGRESS_RESTAT = 2
os.utime(qd / "j0.json", (now - 5, now - 5))   # rewritten in place under an old name: seen once the cursor reaches it
for _ in range(4):
    OW.newest_progress_mtime(qd, pc, now)
progress("after an in-place rewrite, once the rolling re-stat has gone round")
OW.PROGRESS_RESTAT = 4000
for bad in ({"names": "x"}, {"names": [1], "cur": 0}, {"names": [], "cur": 0, "newest": "soon"}, [], None):
    try:
        got = OW.newest_progress_mtime(qd, {str(qd): bad}, now)
        check("queue cache: a malformed entry %r reads afresh" % (bad,), got == OW.newest_mtime(qd), got)
    except Exception as e:  # noqa: BLE001
        check("queue cache: a malformed entry %r reads afresh" % (bad,), False, repr(e))
pc2, saves = {}, []
for i in range(4100):
    (qd / ("k%04d.json" % i)).write_text("")
OW.newest_progress_mtime(qd, pc2, now, checkpoint=lambda: saves.append(len(pc2[str(qd)]["names"])))
check("queue cache: a long cold pass checkpoints its progress", len(saves) == 2 and saves[0] >= 2000, saves)
check("queue cache: an absent dir reads None", OW.newest_progress_mtime(_TMP / "nope", {}, now) is None)
cpath = _TMP / "ops" / "queue_progress_cache.json"
cpath.parent.mkdir(parents=True, exist_ok=True)
OW._save_json(cpath, pc)
check("queue cache: saves and loads", OW._load_json_dict(cpath) == json.loads(json.dumps(pc)))
_qr2 = {"queues": [{"name": "q", "pending": str(_TMP / "pq"), "active": str(_TMP / "aq"), "progress": [str(qd)]}]}
(_TMP / "pq").mkdir(); (_TMP / "aq").mkdir()
OW._save_json(cpath, {"/gone/done": {"names": ["a"], "cur": 0, "newest": None, "top": None}})
OW.c_queues(now, _qr2, {})
check("queue cache: a dir no queue names any more is pruned", list(OW._load_json_dict(cpath)) == [str(qd)],
      list(OW._load_json_dict(cpath)))
cpath.write_text("[]")
check("queue cache: a non-dict cache file loads as empty", OW._load_json_dict(cpath) == {})

print("selftest_ops_watch_sense_caches: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
sys.exit(1 if FAILS else 0)
