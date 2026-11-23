#!/usr/bin/env python3
"""Plant each fault of planted_faults.json, run its deciders and blind lane 1's no-hose scan, restore byte for byte.
    python3 plant_faults.py [--only A,B]       (writes planted_results.jsonl; a fault is caught only by a NEW failing row)"""
import argparse, json, os, re, signal, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7)); MOD = os.path.join(REPO, "src/RimMandrake/GimmeSomeSlack")
SEL = "python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py --no-export "
SUITES = {"T_NO_HOSE": "python3 src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_hose.py", "T_LOOKS": SEL + "--looks-only", "T_RESTYLE": SEL + "--reach-only",
          "T_PERDIG": SEL + "--perdig-only",
          "LANE1": "python3 " + os.path.join(HERE, "../lane1/blind_no_hose.py")}
HOSEPIC = None
for d, _, fs in os.walk(os.path.join(REPO, "src/RimMandrake/FlowWorks/Textures")):
    for f in sorted(fs):
        if "hose" in (d + f).lower() and f.endswith(".png") and HOSEPIC is None: HOSEPIC = os.path.join(d, f)
PLANTED = {}
def restore_all():
    for p, b in list(PLANTED.items()):
        if b is None: os.path.exists(p) and os.remove(p)
        else: open(p, "wb").write(b)
        PLANTED.pop(p)
def bail(*_): restore_all(); sys.exit(3)
for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP): signal.signal(s, bail)
env = dict(os.environ, WINBUILD_ROOT="/mnt/d/ClaudeWork/rimmandrake/scratch/gimmesomeslack_blind_c1_mut/"); os.makedirs(env["WINBUILD_ROOT"], exist_ok=True)
def run(k):
    p = subprocess.run(SUITES[k], shell=True, cwd=REPO, capture_output=True, text=True, env=env, timeout=500); txt = p.stdout + p.stderr
    if k == "LANE1": fails = sorted(json.loads(l)["id"] for l in txt.splitlines() if l.startswith("{") and json.loads(l)["verdict"] == "FAIL")
    else: fails = sorted({l.strip()[:200] for l in txt.splitlines() if re.match(r"\s*FAIL\b", l) or l.startswith("UNMEASURED")})
    built = "build FAILED" not in txt
    last = [l for l in txt.splitlines() if l.strip()]
    return {"rc": p.returncode, "fails": fails, "built": built, "last": (last[-1] if last else "")[:160]}
ap = argparse.ArgumentParser(); ap.add_argument("--check", default=""); ap.add_argument("--only", default=""); ap.add_argument("--out", default=os.path.join(HERE, "planted_results.jsonl")); a = ap.parse_args()
only = set(filter(None, a.only.split(","))); faults = [f for f in json.load(open(os.path.join(HERE, "planted_faults.json"))) if not only or f["id"] in only]
if a.check:  # plant one fault, run its first decider, restore, exit with the decider's own rc (non-zero = caught)
    f = next(x for x in json.load(open(os.path.join(HERE, "planted_faults.json"))) if x["id"] == a.check); p = os.path.join(MOD, f["file"])
    if f.get("copy_from"): PLANTED[p] = None; open(p, "wb").write(open(HOSEPIC, "rb").read())
    else:
        b = open(p, "rb").read(); assert b.decode().count(f["old"]) == 1; PLANTED[p] = b; open(p, "wb").write(b.decode().replace(f["old"], f["new"]).encode())
    try: r = run(f["suites"][0])
    finally: restore_all()
    print(f["id"], f["suites"][0], "rc", r["rc"], (r["fails"] or ["no failing row"])[0]); sys.exit(r["rc"])
base = {k: run(k) for k in SUITES}; out = open(a.out, "w"); out.write(json.dumps({"baseline": base}) + "\n"); print("BASE", {k: (v["rc"], v["last"]) for k, v in base.items()}, flush=True)
try:
    for f in faults:
        p = os.path.join(MOD, f["file"]); row = {"id": f["id"], "file": f["file"], "bars": f["bars"]}
        if f.get("copy_from"):
            PLANTED[p] = None; open(p, "wb").write(open(HOSEPIC, "rb").read()); row["copied"] = os.path.relpath(HOSEPIC, REPO)
        else:
            b = open(p, "rb").read(); t = b.decode(); old = f["old"].replace("\n", "\r\n") if b"\r\n" in b else f["old"]; new = f["new"].replace("\n", "\r\n") if b"\r\n" in b else f["new"]
            if t.count(old) != 1: row.update(planted=False, why="old text found %d times" % t.count(old)); out.write(json.dumps(row) + "\n"); print("SKIP", f["id"], t.count(old)); continue
            PLANTED[p] = b; open(p, "wb").write(t.replace(old, new).encode())
        try: res = {k: run(k) for k in f["suites"] + (["LANE1"] if "T_NO_HOSE" in f["suites"] else [])}
        finally: restore_all()
        for k, v in res.items(): v["new_fails"] = [x for x in v["fails"] if x not in base[k]["fails"]]; v["caught"] = bool(v["new_fails"])
        by = [k for k, v in res.items() if v["caught"] and k != "LANE1"]
        row.update(planted=True, results=res, caught=bool(by), caught_by=by, caught_by_lane1=res.get("LANE1", {}).get("caught")); out.write(json.dumps(row) + "\n"); out.flush()
        print(f["id"], by or "MISSED", "lane1", row["caught_by_lane1"], {k: (v["rc"], v["built"], v["new_fails"][:1]) for k, v in res.items()}, flush=True)
finally:
    restore_all()
clean = subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/GimmeSomeSlack"], cwd=REPO).returncode == 0 and not subprocess.run(["git", "status", "--porcelain", "--", "src/RimMandrake/GimmeSomeSlack/Textures"], cwd=REPO, capture_output=True, text=True).stdout
out.write(json.dumps({"tree_clean_after": clean}) + "\n"); print("TREE CLEAN AFTER:", clean)
