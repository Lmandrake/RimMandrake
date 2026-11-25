#!/usr/bin/env python3
"""Time K whole-tree check runs (publish.tree_checks: full checkout + the checks) started at once, K in argv."""
import json, os, subprocess, sys, time
top = os.getcwd()
ONE = r'''
import os, sys, time
sys.path.insert(0, "src/RimMandrake/Utils")
os.environ.pop("RM_TREECHECK_SLOTS", None)
import publish
t = time.monotonic()
try:
    publish.tree_checks(os.getcwd(), ["src/RimMandrake/Utils/publish.py"])
    v = "GREEN"
except publish.Refuse as e:
    v = "RED " + str(e).splitlines()[0]
print("RESULT %.1f %s" % (time.monotonic() - t, v), flush=True)
'''
def disk():
    busy = 0
    for ln in open("/proc/diskstats"):
        f = ln.split()
        if f[2] == "sdd":
            busy = int(f[12])
    io = open("/proc/pressure/io").read().split("\n")[1].split()[-1].split("=")[1]
    return busy, int(io)
out = []
for k in [int(x) for x in sys.argv[1:]]:
    b0, p0 = disk(); l0 = os.getloadavg()[0]; t0 = time.monotonic()
    ps = [subprocess.Popen([sys.executable, "-c", ONE], cwd=top, env=dict(os.environ, RM_TREECHECK_SLOTS="99"), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) for _ in range(k)]
    res = []
    for p in ps:
        o = p.communicate()[0]
        r = [l for l in o.splitlines() if l.startswith("RESULT")]
        res.append(r[-1] if r else "NO RESULT: " + o.strip().splitlines()[-1] if o.strip() else "NO OUTPUT")
    wall = time.monotonic() - t0; b1, p1 = disk()
    row = dict(k=k, wall_s=round(wall, 1), runs=res, disk_busy_pct=round(100 * (b1 - b0) / 1000 / wall, 1),
               io_full_pct=round(100 * (p1 - p0) / 1e6 / wall, 1), load_before=l0, load_after=os.getloadavg()[0],
               at=time.strftime("%Y-%m-%d %H:%M:%S %Z"))
    print(json.dumps(row), flush=True); out.append(row)
