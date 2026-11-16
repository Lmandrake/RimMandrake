#!/usr/bin/env python3
"""Plant each fault of planted_faults.json in turn, run its suites, restore the file byte for byte.
    python3 plant_faults.py --baseline                 every suite the faults name, on the clean tree
    python3 plant_faults.py --only ID[,ID...]          those faults (rows MERGE into --out by id)
    python3 plant_faults.py --finish                   write the closing {"tree_clean_after": ...} row
    --out <file> writes elsewhere (a red/green run); --require-caught exits 1 unless every --only fault is caught;
--no-lane1 leaves lane 1 out (a decider's own red/green run)
Suites per fault: lane 1 (run_lane1.py) when the file is one of its kernels; one selftest_flowworks_stock.py run over
the fault's `stock` globs; each `py` command. A fault is CAUGHT only when a suite shows a failing row (a FAIL case name, a
failing law, a lane-1 FAIL id) that the baseline row does not show; a build failure of the C# selftest counts as no row.
WINBUILD_ROOT defaults to <agent storage>/rimmandrake/scratch/flowworks_blind_c3_mut/ (private; never the shared stage).
Restores on SIGTERM, SIGINT and SIGHUP; every fault ends with `git diff --quiet -- src/RimMandrake/FlowWorks`."""
import argparse, json, os, re, signal, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
FAULTS = os.path.join(HERE, "planted_faults.json"); OUT = os.path.join(HERE, "planted_results.jsonl")
LANE1 = os.path.join(HERE, "..", "lane1", "run_lane1.py")
LANE1_KERNELS = {"RM_SheetMath.cs", "RM_FloodReleaseMath.cs", "RM_ConversionMath.cs", "RM_DrillSurveyMath.cs", "RM_SprinklerKernel.cs", "RM_ThirstMath.cs"}
MUT = "/mnt/d/ClaudeWork/rimmandrake/scratch/flowworks_blind_c3_mut/"
os.environ.setdefault("WINBUILD_ROOT", MUT)
os.environ.setdefault("LANE1_STAGE", MUT.rstrip("/") + "_lane1")
_restore = {}

def restore_all(*_):
    for path, data in list(_restore.items()):
        with open(path, "wb") as f: f.write(data)
        _restore.pop(path, None)
    if _:
        print("RESTORED on signal", _[0]); sys.exit(130)

for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP): signal.signal(s, restore_all)

def run(cmd, timeout=520):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout + "\n" + p.stderr, round(time.time() - t0, 1)
    except subprocess.TimeoutExpired:
        return -9, "TIMEOUT", round(time.time() - t0, 1)

def suite_rows(name, rc, out):
    if name == "lane1":
        rows = []
        for l in out.splitlines():
            if l.startswith("FAIL "): rows.append(l.split()[1])
        return rows, rc == 2
    if name.startswith("stock"):
        rows = [l[6:].strip() for l in out.splitlines() if l.startswith("FAIL  ")]
        build_failed = rc != 0 and not rows and "case(s)" not in out
        return rows, build_failed
    rows = [l.strip()[:160] for l in out.splitlines() if re.match(r"\s*(FAIL|RED)\b", l)]
    rows += [m.group(1) + " FAIL" for m in (re.match(r"^(\S+)\s+FAIL\b", l) for l in out.splitlines()) if m]   # validation_v2 rows
    return rows, False

NO_LANE1 = "--no-lane1" in sys.argv

def suites_for(f):
    s = []
    if os.path.basename(f["file"]) in LANE1_KERNELS and not NO_LANE1: s.append(("lane1", "python3 %s --out /tmp/fw_c3_planted_lane1.jsonl" % os.path.relpath(LANE1, REPO)))
    if f.get("stock"): s.append(("stock:" + f["stock"], "python3 src/RimMandrake/Utils/selftest_flowworks_stock.py --only '%s'" % f["stock"]))
    for c in f.get("py", []): s.append(("py:" + c.split("FlowWorks/")[-1], c))
    return s

def load_out():
    rows = {}
    if os.path.exists(OUT):
        for l in open(OUT):
            if l.strip():
                r = json.loads(l); rows[r.get("id", "tree_clean_after" if "tree_clean_after" in r else "?")] = r
    return rows

def save_out(rows):
    order = ["baseline"] + [f["id"] for f in json.load(open(FAULTS))["faults"]] + ["tree_clean_after"]
    with open(OUT, "w") as fh:
        for k in order:
            if k in rows: fh.write(json.dumps(rows[k]) + "\n")

def tree_clean():
    return subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/FlowWorks"], cwd=REPO).returncode == 0

def main():
    global OUT
    ap = argparse.ArgumentParser(); ap.add_argument("--only", default=""); ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--finish", action="store_true"); ap.add_argument("--out", default=OUT)
    ap.add_argument("--baseline-extra", action="store_true", help="add to the baseline row any py suite it does not hold yet")
    ap.add_argument("--no-lane1", action="store_true", help="run only the builder's suites (a red/green run of a decider fix)")
    ap.add_argument("--require-caught", action="store_true", help="exit 1 unless every --only fault is caught (a fix's red/green run)")
    a = ap.parse_args()
    OUT = a.out
    missed = []
    faults = json.load(open(FAULTS))["faults"]; rows = load_out()
    if not tree_clean(): sys.exit("REFUSED: src/RimMandrake/FlowWorks is not clean before planting")
    if a.baseline:
        seen = {}
        for f in faults:
            for name, cmd in suites_for(f): seen.setdefault(name, cmd)
        # one stock run over the union of every glob (one build)
        globs = sorted({g for n in seen if n.startswith("stock:") for g in n[6:].split(",")})
        res = {}
        rc, out, sec = run("python3 src/RimMandrake/Utils/selftest_flowworks_stock.py --only '%s'" % ",".join(globs))
        r, bf = suite_rows("stock", rc, out); res["stock:*"] = {"rc": rc, "failing": r, "build_failed": bf, "seconds": sec, "globs": ",".join(globs)}
        for name, cmd in seen.items():
            if name.startswith("stock:"): continue
            rc, out, sec = run(cmd); r, bf = suite_rows(name, rc, out)
            res[name] = {"rc": rc, "failing": r, "build_failed": bf, "seconds": sec}
        rows["baseline"] = {"id": "baseline", "suites": res, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        save_out(rows); print("BASELINE", json.dumps({k: (v["rc"], len(v["failing"])) for k, v in res.items()})); return
    if a.baseline_extra:
        res = rows["baseline"]["suites"]
        for f in faults:
            for name, cmd in suites_for(f):
                if name.startswith("py:") and name not in res:
                    rc, out, sec = run(cmd); r, bf = suite_rows(name, rc, out)
                    res[name] = {"rc": rc, "failing": r, "build_failed": bf, "seconds": sec}
                    print("BASELINE+", name, rc, len(r))
        save_out(rows); return
    if a.finish:
        rows["tree_clean_after"] = {"tree_clean_after": tree_clean()}; save_out(rows)
        print("tree_clean_after", rows["tree_clean_after"]["tree_clean_after"]); return
    base = rows.get("baseline", {}).get("suites", {})
    base_fail = set()
    for v in base.values(): base_fail.update(v["failing"])
    for fid in [x for x in a.only.split(",") if x]:
        f = next(x for x in faults if x["id"] == fid)
        path = os.path.join(REPO, f["file"]); data = open(path, "rb").read(); text = data.decode("utf-8")
        if text.count(f["old"]) != 1:
            rows[fid] = {"id": fid, "error": "old text found %d times" % text.count(f["old"])}; save_out(rows); continue
        _restore[path] = data
        try:
            with open(path, "w", encoding="utf-8", newline="") as fh: fh.write(text.replace(f["old"], f["new"], 1))
            res = {}; new = []
            for name, cmd in suites_for(f):
                rc, out, sec = run(cmd); r, bf = suite_rows(name, rc, out)
                fresh = [x for x in r if x not in base_fail]
                res[name] = {"rc": rc, "failing": r[:12], "new_failing": fresh[:12], "build_failed": bf, "seconds": sec}
                new += fresh
        finally:
            restore_all()
        clean = tree_clean()
        rows[fid] = {"id": fid, "file": f["file"], "bars": f["bars"], "suites": res, "caught": bool(new),
                     "build_failed": any(v["build_failed"] for v in res.values()), "tree_clean": clean,
                     "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        save_out(rows)
        print(("CAUGHT " if new else "MISSED ") + fid, "|", "; ".join("%s rc%s %s%s" % (k, v["rc"], (v["new_failing"][:1] or [""])[0][:70], " BUILD-FAILED" if v["build_failed"] else "") for k, v in res.items()))
        if not clean: sys.exit("TREE NOT CLEAN after " + fid)
        if not new: missed.append(fid)
    if a.require_caught and missed:
        print("MISSED", ",".join(missed)); sys.exit(1)

main()
