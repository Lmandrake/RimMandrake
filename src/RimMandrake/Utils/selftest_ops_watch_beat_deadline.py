#!/usr/bin/env python3
"""selftest_ops_watch_beat_deadline.py -- OPS_METRONOME_MIGRATE_CLOCKS_FENCED: inside a metronome beat the sense pass is
killed at METRONOME_DEADLINE, so ops_watch's real filer starts a filing only when it and the publish still fit.

Beat 1749 (2026-11-05, the first real sense beat) met 13 pending alarm filings and was killed at 15 s mid-filing.
Real ops_watch.real_filer against a fake ingest module whose spawn takes 0.4 s. Expect: with no deadline every alarm
is filed; with a deadline near, the late ones come back FILING_DEFERRED, the publish still runs, and run_alarms counts
no try and logs no file_failed for a deferred one, leaving it PENDING for the next pass."""
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
TMP = Path(tempfile.mkdtemp(prefix="selftest_ops_beat_deadline_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["RM_DATA_ROOT"] = str(TMP / "data")
os.environ.pop("METRONOME_DEADLINE", None)
(TMP / "ops").mkdir()
ing_dir = TMP / "clone" / "src/RimMandrake/Utils/testq"
ing_dir.mkdir(parents=True)
(ing_dir / "ingest.py").write_text('''
import time
CALLS = []
PUBLISHED = []
def rimflow(*a):
    CALLS.append(a)
    if a[0] == "spawn":
        time.sleep(0.4)
    return 0, "ok"
def publish(n, message=""):
    PUBLISHED.append(n)
    return "published %d" % n
''')
import ops_watch as OW  # noqa: E402

FAILS = []


def ok(c, w):
    print(("  ok    " if c else "  FAIL  ") + w)
    if not c:
        FAILS.append(w)


conf = dict(OW.alarm_conf(OW.load_rules()))
conf["clone"] = str(TMP / "clone")
OW.qhome = lambda: TMP
OW.alarm_receiver_problem = lambda conf: None
todo = [{"name": "OPS_DEADLINE_T%d_X" % i, "title": "t", "aid": "A%d" % i} for i in range(6)]

# 1. outside a beat: every alarm is filed
ok(OW.beat_deadline() is None, "no METRONOME_DEADLINE: no deadline")
res = OW.real_filer([dict(a) for a in todo], conf)
ok(all(res.get(a["name"]) is None for a in todo), "no deadline: all 6 filed (%s)" % {k: v for k, v in res.items() if v})

# 2. inside a beat with room for about two filings: the rest are deferred, the publish runs, the deadline is kept
OW.FILING_FIRST_GUESS_S = 0.5
OW.FILING_PUBLISH_RESERVE_S = 0.5
os.environ["METRONOME_DEADLINE"] = "%.3f" % (time.time() + 1.6)
t0 = time.time()
res = OW.real_filer([dict(a) for a in todo], conf)
took = time.time() - t0
filed = [a["name"] for a in todo if res.get(a["name"]) is None]
deferred = [a["name"] for a in todo if res.get(a["name"]) == OW.FILING_DEFERRED]
ok(1 <= len(filed) <= 3 and len(filed) + len(deferred) == 6, "deadline near: %d filed, %d deferred" % (len(filed), len(deferred)))
ok(filed == [a["name"] for a in todo[:len(filed)]], "the earliest alarms are the ones filed")
ok(took < 1.6, "the filer returned before the deadline (%.2f s)" % took)
ok(str(res.get("_publish", "")).startswith("published"), "the publish still ran (%s)" % res.get("_publish"))

# 3. a deadline already past: nothing is started, nothing to publish
os.environ["METRONOME_DEADLINE"] = "%.3f" % (time.time() - 1)
res = OW.real_filer([dict(a) for a in todo], conf)
ok(all(res.get(a["name"]) == OW.FILING_DEFERRED for a in todo), "deadline past: all deferred")
ok(res.get("_publish") in (None, "nothing to publish"), "deadline past: nothing published")
os.environ["METRONOME_DEADLINE"] = "not a number"
ok(OW.beat_deadline() is None, "an unreadable METRONOME_DEADLINE is no deadline")
os.environ.pop("METRONOME_DEADLINE", None)

# 4. run_alarms (source read): a deferred filing stays PENDING with no try counted and no file_failed logged
src = Path(OW.__file__).read_text()
ok("if filer and err == FILING_DEFERRED:" in src and 'cur["deferred_n"]' in src and '"file_deferred"' in src,
   "run_alarms counts no try for FILING_DEFERRED, keeps last_try and the last error, logs file_deferred")

# 5. a busy ingest.lock inside a beat is a deferral, not a failed try
import fcntl  # noqa: E402
lk = open(TMP / "ingest.lock", "w")
fcntl.flock(lk, fcntl.LOCK_EX)
os.environ["METRONOME_DEADLINE"] = "%.3f" % (time.time() + 1.6)
res = OW.real_filer([dict(a) for a in todo], conf)
ok(all(res.get(a["name"]) == OW.FILING_DEFERRED for a in todo), "lock busy inside a beat: all deferred (%s)" % set(res.values()))
lk.close()

# 6. the brake release is skipped (no flag) when it cannot fit before the kill, and runs outside a beat
os.environ["METRONOME_DEADLINE"] = "%.3f" % (time.time() + 2)
ok(OW.steve_release() == [], "brake release: no room in the beat -> skipped, no flag")
os.environ.pop("METRONOME_DEADLINE", None)

print("FAIL (%d)" % len(FAILS) if FAILS else "PASS")
sys.exit(1 if FAILS else 0)
