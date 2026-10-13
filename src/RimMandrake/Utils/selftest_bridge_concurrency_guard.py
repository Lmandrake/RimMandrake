#!/usr/bin/env python3
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
en = lambda cid: {"ev": "end", "cid": cid, "t": iso(now)}
write([st("a", 111, 20), en("a")]); check("recent foreign start refuses", G.foreign_activity(p, now, 222) is not None)
write([st("a", 111, 20)]); check("unended foreign start refuses", G.foreign_activity(p, now, 222) is not None)
write([st("a", 111, 20)]); check("own pid proceeds", G.foreign_activity(p, now, 111) is None)
write([st("a", 111, 300), en("a")]); check("old ended foreign proceeds", G.foreign_activity(p, now, 222) is None)
write([st("a", 111, 5000)]); check("ancient unended (dead client) proceeds", G.foreign_activity(p, now, 222) is None)
write([st("a", 111, 300)]); check("120s+ unended long call refuses", G.foreign_activity(p, now, 222) is not None)
check("missing log allows", G.foreign_activity(os.path.join(d, "nope"), now, 222) is None)
check("empty log path allows", G.foreign_activity("", now, 222) is None)
write([st("a", 111, 20)])
try: G.refuse_if_foreign_activity("go_to_main_menu", log=p, now=now, own_pid=222); check("raises", False)
except G.ConcurrentBridgeClient: check("raises ConcurrentBridgeClient", True)
os.environ["RM_ALLOW_CONCURRENT_BRIDGE"] = "1"
G.refuse_if_foreign_activity("go_to_main_menu", log=p, now=now, own_pid=222); check("env override allows", True)
print("FAIL" if F else "PASS", len(F), "failure(s)")
sys.exit(1 if F else 0)
