#!/usr/bin/env python3
# selftest temp containment (wave 7, DIRTY_CODE_REVIEW_STANDING_LOOP_1): every mkdtemp/mkstemp below,
# and every child process via TMPDIR, lands in one private dir removed at exit — this
# test used to leave its temp dirs behind in the seat TMPDIR on every run.
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_bridge_concurrency_guard_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import json, os, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bridge_concurrency_guard as G

F = []
def check(n, c):
    print(("PASS " if c else "FAIL ") + n)
    if not c: F.append(n)

def iso(t): return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))
now = 1_800_000_000
d = tempfile.mkdtemp(); p = os.path.join(d, "c.jsonl")
def write(rows):
    with open(p, "w") as fh:
        for r in rows: fh.write(json.dumps(r) + "\n")
st = lambda cid, pid, age, tool="rimworld/step_game_ticks": {"ev": "start", "cid": cid, "pid": pid, "t": iso(now - age), "tool": tool, "script": "x.py"}
LIVE = lambda r: True
en = lambda cid: {"ev": "end", "cid": cid, "t": iso(now)}
write([st("a", 111, 20), en("a")]); check("foreign call just ended refuses", G.foreign_activity(p, now, 222, alive=LIVE) is not None)
write([st("a", 111, 20), {"ev": "end", "cid": "a", "t": iso(now - 20)}]); check("foreign call ended 20s ago proceeds (own sequel)", G.foreign_activity(p, now, 222, alive=LIVE) is None)
write([st("a", 111, 20)]); check("unended foreign start refuses", G.foreign_activity(p, now, 222, alive=LIVE) is not None)
write([st("a", 111, 20)]); check("own pid proceeds", G.foreign_activity(p, now, 111, alive=LIVE) is None)
write([st("a", 111, 300), {"ev": "end", "cid": "a", "t": iso(now - 290)}]); check("old ended foreign proceeds", G.foreign_activity(p, now, 222, alive=LIVE) is None)
write([st("a", 111, 5000)]); check("ancient unended (dead client) proceeds", G.foreign_activity(p, now, 222, alive=LIVE) is None)
write([st("a", 111, 300)]); check("120s+ unended long call refuses", G.foreign_activity(p, now, 222, alive=LIVE) is not None)
# BRIDGEGUARD_FIX_DEAD_PID_STILL_BLOCKS: an unended start whose writer is gone is a crashed client, not a live call
import subprocess
write([st("a", 111, 20)]); check("unended start, dead writer, proceeds", G.foreign_activity(p, now, 222, alive=lambda r: False) is None)
write([st("a", 111, 20), en("a")]); check("just-ended call still refuses even if writer died", G.foreign_activity(p, now, 222, alive=lambda r: False) is not None)
child = subprocess.Popen([sys.executable, "-c", "pass"]); child.wait()        # a pid that certainly existed and is now dead
row = dict(st("a", child.pid, 20), os=os.name); write([row])
check("real dead pid proceeds (writer_alive)", G.foreign_activity(p, now, 222) is None)
check("writer_alive: dead pid is False", G.writer_alive(row) is False)
me = dict(st("b", os.getpid(), 20), os=os.name)
check("writer_alive: live pid is True", G.writer_alive(me) is True)
write([me]); check("real live foreign pid refuses", G.foreign_activity(p, now, -1) is not None)
check("writer_alive: reused pid (pid_start differs) is False", G.writer_alive(dict(me, pid_start=-12345)) is False)
check("writer_alive: other OS pid is presumed alive", G.writer_alive(dict(row, os="nt" if os.name != "nt" else "posix")) is True)
check("writer_alive: no pid is presumed alive", G.writer_alive({"ev": "start"}) is True)
check("missing log allows", G.foreign_activity(os.path.join(d, "nope"), now, 222) is None)
check("empty log path allows", G.foreign_activity("", now, 222) is None)
write([st("a", 111, 20)])
try: G.refuse_if_foreign_activity("go_to_main_menu", log=p, now=now, own_pid=222, alive=LIVE); check("raises", False)
except G.ConcurrentBridgeClient: check("raises ConcurrentBridgeClient", True)
os.environ["RM_ALLOW_CONCURRENT_BRIDGE"] = "1"
G.refuse_if_foreign_activity("go_to_main_menu", log=p, now=now, own_pid=222, alive=LIVE); check("env override allows", True)
print("FAIL" if F else "PASS", len(F), "failure(s)")
sys.exit(1 if F else 0)
