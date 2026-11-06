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
# GAMEENV_FIX_HARNESS_09849AF1_ITEMS_WAIT: the instance. relentless_live's health read (a one-shot python.exe
# jawa/running_mods client, pid 42468) ended 6 s before live_site.py (pid 33880) asked for go_to_main_menu: one driver
# running a sequence of processes, refused as a concurrent client. A shared lineage token makes them one driver.
os.environ.pop(G.LINEAGE_ENV, None)
rm = lambda lin: dict(st("i", 42468, 6, "jawa/running_mods"), script="rimbridge_client.py", **({"lineage": lin} if lin else {}))
write([rm(None), en("i")]); check("instance: no lineage, health read 6 s before refuses (the old behaviour)", G.foreign_activity(p, now, 33880, alive=lambda r: False) is not None)
write([rm("L1"), en("i")]); check("instance: same lineage proceeds", G.foreign_activity(p, now, 33880, alive=lambda r: False, lineage="L1") is None)
write([rm("L1"), en("i")]); check("other lineage still refuses", G.foreign_activity(p, now, 33880, alive=LIVE, lineage="L2") is not None)
write([rm("L1"), en("i")]); check("caller with no lineage still refuses a lineage row", G.foreign_activity(p, now, 33880, alive=LIVE, lineage="") is not None)
write([rm(None), en("i")]); check("empty lineages never match", G.foreign_activity(p, now, 33880, alive=LIVE, lineage="") is not None)
write([dict(rm("L1"), cid="j"), rm("L1"), en("i")]); check("same-lineage unended call is own too", G.foreign_activity(p, now, 33880, alive=LIVE, lineage="L1") is None)
e = {"WSLENV": "A/p"}; tok = G.export_lineage(env=e)
check("export_lineage sets a token and carries it to python.exe via WSLENV", tok and e[G.LINEAGE_ENV] == tok and e["WSLENV"] == "A/p:" + G.LINEAGE_ENV)
check("export_lineage keeps an existing token (nested driver stays in its parent's lineage)", G.export_lineage(env=e) == tok and e["WSLENV"].count(G.LINEAGE_ENV) == 1)
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "rimbridge_client.py"), encoding="utf-8").read()
check("rimbridge_client writes the lineage on each start row", '"lineage": os.environ.get("%s")' % G.LINEAGE_ENV in src)
import subprocess as _sp
rl = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rimflow")
out = _sp.run([sys.executable, "-c", "import sys, os; sys.path.insert(0, %r); os.environ.pop(%r, None); import relentless_live as L; "
               "L.Fx(); print(os.environ.get(%r, ''), os.environ.get('WSLENV', ''))" % (rl, G.LINEAGE_ENV, G.LINEAGE_ENV)],
              capture_output=True, text=True, timeout=120)
w = (out.stdout.strip().split("\n") or [""])[-1].split(" ")
check("relentless_live.Fx exports a lineage for its children (%s)" % (out.stderr.strip()[-200:] or "ok"),
      out.returncode == 0 and len(w) == 2 and w[0] and G.LINEAGE_ENV in w[1].split(":"))
# LIVETIER_PREFLIGHT_FIX_TRIPS_OWN_GUARD: the instance's two shapes. Log PROOF_HARNESS_BUILD_SAVELOAD_TRIPLET-A1-20261106T142756Z:
# the supervisor's own ping (pid 39752) ended 1 s before validation.py's go_to_main_menu; a sibling tick's one-shot
# jawa/running_mods (lineage ca88009edf7e, 2026-11-06T21:00:29Z) landed inside round f9bfdc62032a, under another lineage.
ping = lambda lin, **kw: dict(st("i", 39752, 1, "rimbridge/ping"), script="rimbridge_client.py", mutating=False, lineage=lin, **kw)
write([ping("f9bf"), en("i")]); check("own supervisor's ping 1 s before setup proceeds", G.foreign_activity(p, now, 33880, alive=LIVE, lineage="f9bf") is None)
write([ping("ca88"), en("i")]); check("another lineage's finished one-shot read proceeds", G.foreign_activity(p, now, 33880, alive=lambda r: False, lineage="f9bf") is None)
write([ping("ca88"), en("i")]); check("another lineage's read from a LIVE writer refuses (a driver between calls)", G.foreign_activity(p, now, 33880, alive=LIVE, lineage="f9bf") is not None)
write([dict(ping("ca88"), mutating=True), en("i")]); check("another lineage's finished MUTATING call refuses", G.foreign_activity(p, now, 33880, alive=lambda r: False, lineage="f9bf") is not None)
write([ping("ca88")]); check("an unended read from a live writer refuses", G.foreign_activity(p, now, 33880, alive=LIVE, lineage="f9bf") is not None)
child = subprocess.Popen([sys.executable, "-c", "pass"]); child.wait()
write([dict(ping("ca88"), pid=child.pid, os=os.name), en("i")]); check("real exited one-shot read proceeds (writer_alive)", G.foreign_activity(p, now, 33880, lineage="f9bf") is None)
os.environ["RM_ALLOW_CONCURRENT_BRIDGE"] = "1"
G.refuse_if_foreign_activity("go_to_main_menu", log=p, now=now, own_pid=222, alive=LIVE); check("env override allows", True)
print("FAIL" if F else "PASS", len(F), "failure(s)")
sys.exit(1 if F else 0)
