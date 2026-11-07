#!/usr/bin/env python3
"""Sum the shape audit over a lab output folder: strands, sharp corners, rods (2.2+ cells within 7 degrees), and the longest rods. python3 ralph/live/lab_audit_sum.py OUTDIR"""
import glob, json, os, sys
tot = dict(strands=0, sharpStrands=0, corners=0, rods=0)
rods = []
for f in sorted(glob.glob(os.path.join(sys.argv[1], "*.out.json"))):
    a = json.load(open(f))["audit"]
    for k in tot:
        tot[k] += a.get(k, 0)
    rods += [(r["rod"], os.path.basename(f)[:-9], r["at"]) for r in a.get("rows", []) if "rod" in r]
print(json.dumps(tot), "rod lengths: median %.1f max %.1f" % (sorted(r[0] for r in rods)[len(rods) // 2], max(r[0] for r in rods)) if rods else "")
for r in sorted(rods, reverse=True)[:5]:
    print("  %.1f %s %s" % r)
