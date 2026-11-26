#!/usr/bin/env python3
"""selftest_crystallize_instruments.py - the two Crystallize criterion instruments read what they claim to read.

    python3 src/RimMandrake/Utils/selftest_crystallize_instruments.py

lesson_dup_rate.py: a planted twin is counted, a distinct lesson is not, dashed and plain dates agree, an empty folder
is could-not-look (exit 2). refused_spawn_slot_holds.py: a slots_full with a reserved- slot within 180 s of a type
refusal is one event; one past 180 s is none; no records is could-not-look (exit 2).
"""
import json, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
FAILS = []
def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  " + str(detail)[:300]))
    cond or FAILS.append(name)
def run(script, *args):
    p = subprocess.run([sys.executable, os.path.join(HERE, script)] + [str(a) for a in args], capture_output=True, text=True, timeout=600)
    return p.returncode, p.stdout + p.stderr
t = tempfile.mkdtemp()
les = os.path.join(t, "lessons"); os.makedirs(les)
A = "Publish refuses a staged deletion unless the pathspec names the deleted file; give the path to publish explicitly.\n"
filler = ["Bridge %d call returns before the map tick; poll the reading instead of the call result.\n" % i for i in range(8)]
for i, x in enumerate(filler):
    open(os.path.join(les, "202611%02dT000000Z-BENCH-filler-%d.md" % (1 + i, i)), "w").write(x + "word%d unique%d\n" % (i, i))
open(os.path.join(les, "20261110T000000Z-BENCH-a.md"), "w").write(A)
open(os.path.join(les, "20261121T000000Z-BENCH-a-again.md"), "w").write("Publish refuses to land a staged deletion when the pathspec omits the deleted file; name each deleted path on the publish line.\n")
open(os.path.join(les, "20261122T000000Z-BENCH-other.md"), "w").write("Steam overlay steals focus from the art window; close it before capture.\n")
rc, out = run("lesson_dup_rate.py", les, "2026-11-20", "2026-11-26", "0.35")
check("a planted twin is counted and a distinct lesson is not: 1 of 2", rc == 0 and "2 lessons, 1 with" in out, out)
rc2, out2 = run("lesson_dup_rate.py", les, "20261120", "20261126", "0.35")
check("dashed and plain dates read the same window", out2 == out, (out, out2))
empty = os.path.join(t, "none"); os.makedirs(empty)
rc, out = run("lesson_dup_rate.py", empty, "2026-11-20", "2026-11-26", "0.35")
check("an empty lessons folder is could-not-look, exit 2", rc == 2 and "COULD NOT LOOK" in out, (rc, out))
root = os.path.join(t, "projects", "p"); os.makedirs(root)
def rec(ts, text):
    return json.dumps({"type": "user", "timestamp": ts, "message": {"content": [{"type": "tool_result", "content": text}]}}) + "\n"
REF = "Blocked: `(no subagent_type)` runs on an unbounded context (1M window)"
FULL = "slots_full: this role run already has 5 helper(s) running. Running: a1, reserved-1, reserved-1"
open(os.path.join(root, "s1.jsonl"), "w").write(rec("2026-11-27T03:00:00Z", REF) + rec("2026-11-27T03:01:00Z", FULL))
open(os.path.join(root, "s2.jsonl"), "w").write(rec("2026-11-27T03:00:00Z", REF) + rec("2026-11-27T03:05:00Z", FULL))
import datetime as DT
when = DT.datetime(2026, 11, 27, 3, 10, tzinfo=DT.timezone.utc).timestamp()
for n in ("s1.jsonl", "s2.jsonl"):
    os.utime(os.path.join(root, n), (when, when))      # the instrument skips a transcript last written before the window
rc, out = run("refused_spawn_slot_holds.py", "2026-11-27", "2026-11-27", "--root", os.path.join(t, "projects"))
check("a slots_full 60 s after a type refusal is one event; one 300 s after is none", rc == 0 and "2 unbounded-type refusals, 1 slots_full" in out, out)
rc, out = run("refused_spawn_slot_holds.py", "2026-12-20", "2026-12-21", "--root", os.path.join(t, "projects"))
check("a window with no records is could-not-look, exit 2", rc == 2 and "COULD NOT LOOK" in out, (rc, out))
print("\n%s: %d failed" % ("GREEN" if not FAILS else "RED", len(FAILS)))
sys.exit(1 if FAILS else 0)
