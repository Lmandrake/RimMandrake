#!/usr/bin/env python3
"""selftest_brake_release_reads_once.py - one brake_release pass reads each queue record file at most once
(RIMMANDRAKE_SPEED_BRAKE_RELEASE_PASS_MISSES_ITS_BEAT).

2026-11-19 a pass with the lane paused took 11.9 s of a 15 s beat: testq.records() ran 7 times (filler_jobs walks four
states, brake_tail re-reads cancelled and done, lane_proven_after done again), 3,159 json reads over the D: mount at
about 2 ms an open. Here the queue is a temp dir with filler records in every state; read_json is COUNTED per path.
A second pass must read the files again (the memo lives for one pass only), and a record a caller edits must not leak
into the next caller's copy.
"""
import collections
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
tmp = tempfile.mkdtemp(prefix="rf_brake_reads_")
os.environ.update(TESTQ_QUEUE=os.path.join(tmp, "q"), TESTQ_INGEST_PUSH="0", RM_DATA_ROOT=os.path.join(tmp, "data"),
                  TESTQ_READ_CACHE=os.path.join(tmp, "reads_cache.json"))
os.makedirs(os.environ["TESTQ_QUEUE"])
import brake_release as BR  # noqa: E402
import schema as S  # noqa: E402
import testq as T  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


T.ensure_dirs()
for i in range(6):
    job = {"id": "J2026111%dT000000Z-%06d" % (i, i), "mod": "M", "requested_by": T.FILLER, "lane": T.STEVE,
           "submitted": "2026-11-1%dT00:00:00Z" % i}
    st = ("done", "done", "done", "cancelled", "pending", "done")[i]
    rec = job if st == "pending" else {"job": job, "finished": "2026-11-1%dT01:00:00Z" % i,
                                       "result": {"outcome": "INVALID", "cause": "HARNESS",
                                                  "finished": "2026-11-1%dT01:00:00Z" % i}}
    S.dump(rec, T.q(st, job["id"] + ".json"))

reads = collections.Counter()
real_read = T.read_json


def counted(path):
    reads[os.path.abspath(path)] += 1
    return real_read(path)


T.read_json = counted


def counted_open(path, *a, **k):     # brake_release's own reads of queue files (its local text cache's misses)
    if not str(path).endswith(".tmp") and "reads_cache" not in str(path):
        reads[os.path.abspath(path)] += 1
    return open(path, *a, **k)


BR.open = counted_open
T.fill_plan = lambda mod, n, cap, *, now=None: {"verdict": "busy", "text": "stub", "tail": []}

rec = BR.release_pass(now=1000.0, mods=["M"])
qdir = os.path.abspath(T.q())
per_file = {p: n for p, n in reads.items() if p.startswith(qdir) and os.sep + "brake_release.json" not in p}
worst = max(per_file.values()) if per_file else 0
check(bool(per_file), "the pass read the queue at all (%d record file(s))" % len(per_file))
check(worst == 1, "each record file is read once per pass (worst %d: %s)" % (
    worst, sorted((os.path.basename(p), n) for p, n in per_file.items() if n > 1)[:4]))
check(rec.get("state") in ("none", "wait", "escalate", "refused", "unmeasured", "released"),
      "the pass still answers: %s %s" % (rec.get("state"), rec.get("reason", "")[:80]))

check(T.read_json is counted, "testq.read_json is the real one again after the pass")

# the local text cache: an unchanged record is not opened again on the next pass; a rewritten one is, and its new
# content is what the pass sees
reads.clear()
BR.release_pass(now=1001.0, mods=["M"])
again = {p: n for p, n in reads.items() if p.startswith(qdir) and os.sep + "brake_release.json" not in p
         and os.path.exists(p)}     # a file that is not there has nothing to cache
check(not again, "a second pass over unchanged records opens none of them (opened: %s)" % sorted(
    os.path.basename(p) for p in again)[:4])
first = sorted(os.listdir(T.q("done")))[0]
path = T.q("done", first)
r = real_read(path)
r["job"]["mod"] = "CHANGED_MOD_NAME"
S.dump(r, path)
st = os.stat(path)
os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns + 10 ** 9))
reads.clear()
seen = []
real_records = T.records


def spy(state):
    got = real_records(state)
    seen.extend(x for x in got if isinstance(x, dict))
    return got


T.records = spy
BR.release_pass(now=1002.0, mods=["M"])
T.records = real_records
opened = {os.path.basename(p) for p, n in reads.items() if p.startswith(qdir) and os.path.exists(p)} - {
    "brake_release.json"}
check(opened == {first}, "a rewritten record is read again, and only it: %s" % sorted(opened)[:4])
check(any((x.get("job") or {}).get("mod") == "CHANGED_MOD_NAME" for x in seen),
      "and the pass sees its new content, not the cached one")
with open(os.environ["TESTQ_READ_CACHE"], "w") as f:
    f.write("{not json")
reads.clear()
rec = BR.release_pass(now=1003.0, mods=["M"])
check(rec.get("state") and len({p for p in reads if p.startswith(qdir)}) >= 6,
      "a broken cache file only costs the reads: the pass answers (%s) and reads the queue" % rec.get("state"))

with BR.records_once():
    a = T.records("done")
    a[0]["job"]["mod"] = "EDITED"
    a.append({"junk": 1})
    b = T.records("done")
check(b[0]["job"]["mod"] == real_read(sorted(T.q("done", x) for x in os.listdir(T.q("done")))[0])["job"]["mod"]
      and {"junk": 1} not in b, "a caller's edit does not reach the next caller's copy")

print("%d failed" % len(FAILS))
sys.exit(1 if FAILS else 0)
