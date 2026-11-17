#!/usr/bin/env python3
"""Plant each fault of planted_faults.json in turn, run the suites that should see it, restore byte for byte.
    WINBUILD_ROOT=/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c3_mut/ python3 plant_faults.py --baseline
    ... python3 plant_faults.py --from 0 --to 10        (appends to planted_results.jsonl; resumable in chunks)
    ... python3 plant_faults.py --finish                (writes {"tree_clean_after": ...} last)
Suites per fault: the offline/record deciders of its bars, every offline test whose `reads` covers the file, and lane 1
(run_lane1.py). Caught = a NEW failing row: a suite that passed at baseline fails, or a lane-1 row id FAILs that did not.
Restores on SIGTERM, SIGINT and SIGHUP; ends by proving `git diff --quiet -- src/RimMandrake/Pyrelands`."""
import argparse, json, os, signal, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TABLE = json.load(open(os.path.join(REPO, "design/concepts/Pyrelands/version/test_table.json")))
TESTS = TABLE["tests"]
BARS = {b["id"]: b for b in TABLE["bars"]}
FAULTS = json.load(open(os.path.join(HERE, "planted_faults.json")))["faults"]
OUT = os.path.join(HERE, "planted_results.jsonl")
LANE1 = os.path.join(HERE, "..", "lane1", "run_lane1.py")
os.environ.setdefault("WINBUILD_ROOT", "/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c3_mut/")
os.environ.setdefault("LANE1_STAGE", "/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c3_mut/lane1")

state = {"path": None, "orig": None}


def restore(*_):
    if state["path"]:
        with open(state["path"], "wb") as f:
            f.write(state["orig"])
        state["path"] = None
    if _:
        sys.exit(130)


for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, restore)


def suites_for(fault):
    s = set()
    for b in fault["bars"]:
        for t in BARS.get(b, {}).get("decides", []) + BARS.get(b, {}).get("supports", []):
            if TESTS.get(t, {}).get("kind") in ("offline", "record"):
                s.add(t)
    for k, v in TESTS.items():
        if v.get("kind") in ("offline", "record") and any(fault["file"].startswith(r.rstrip("/")) for r in v.get("reads", [])):
            s.add(k)
    return sorted(s) + ["LANE1"]


def run(suite):
    t0 = time.time()
    if suite == "LANE1":
        out = "/tmp/pyre_c3_mut_lane1.jsonl"
        try:
            subprocess.run([sys.executable, LANE1, "--out", out], cwd=REPO, capture_output=True, text=True, timeout=500)
            rows = [json.loads(l) for l in open(out)]
        except Exception as e:
            return {"fails": ["lane1_crash:" + str(e)[:80]], "s": round(time.time() - t0, 1)}
        os.remove(out)
        return {"fails": sorted(r["id"] for r in rows if r["verdict"] == "FAIL"), "s": round(time.time() - t0, 1)}
    try:
        p = subprocess.run(TESTS[suite]["command"], shell=True, cwd=REPO, capture_output=True, text=True, timeout=500)
        rc, last = p.returncode, ((p.stdout.strip().splitlines() or p.stderr.strip().splitlines() or [""])[-1])[:200]
    except subprocess.TimeoutExpired:
        rc, last = -9, "TIMEOUT"
    return {"fails": [suite] if rc else [], "rc": rc, "last": last, "s": round(time.time() - t0, 1)}


def baseline_fails():
    for l in open(OUT):
        r = json.loads(l)
        if r.get("baseline"):
            return r["fails"]
    sys.exit("no baseline row in " + OUT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--from", dest="lo", type=int, default=0)
    ap.add_argument("--to", dest="hi", type=int, default=len(FAULTS))
    ap.add_argument("--finish", action="store_true")
    a = ap.parse_args()
    if a.baseline:
        suites = sorted(set(s for f in FAULTS for s in suites_for(f)))
        fails = {}
        for s in suites:
            r = run(s)
            fails[s] = r["fails"]
            print("baseline", s, r["fails"], r["s"], flush=True)
        with open(OUT, "w") as f:
            f.write(json.dumps({"baseline": True, "suites": suites, "fails": fails}) + "\n")
        return
    if a.finish:
        clean = subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/Pyrelands"], cwd=REPO).returncode == 0
        with open(OUT, "a") as f:
            f.write(json.dumps({"tree_clean_after": clean}) + "\n")
        print("tree_clean_after", clean)
        sys.exit(0 if clean else 1)
    base = baseline_fails()
    for i in range(a.lo, min(a.hi, len(FAULTS))):
        fault = FAULTS[i]
        path = os.path.join(REPO, fault["file"])
        orig = open(path, "rb").read()
        text = orig.decode("utf-8")
        if text.count(fault["old"]) != 1:
            row = {"id": fault["id"], "error": "old text occurs %d times" % text.count(fault["old"])}
        else:
            state["path"], state["orig"] = path, orig
            with open(path, "wb") as f:
                f.write(text.replace(fault["old"], fault["new"]).encode("utf-8"))
            res = {}
            try:
                for s in suites_for(fault):
                    res[s] = run(s)
            finally:
                restore()
            new = {s: sorted(set(r["fails"]) - set(base.get(s, []))) for s, r in res.items()}
            caught_by = sorted(s for s, n in new.items() if n)
            row = {"id": fault["id"], "file": fault["file"], "bars": fault["bars"], "caught": bool(caught_by), "caught_by": caught_by,
                   "new_failing_rows": {s: n for s, n in new.items() if n}, "suites": {s: {k: v for k, v in r.items() if k != "fails"} for s, r in res.items()}}
        with open(OUT, "a") as f:
            f.write(json.dumps(row) + "\n")
        print(i, fault["id"], "CAUGHT by " + ",".join(row.get("caught_by", [])) if row.get("caught") else "SURVIVED", flush=True)
    if subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/Pyrelands"], cwd=REPO).returncode != 0:
        sys.exit("TREE NOT CLEAN after the chunk")


main()
