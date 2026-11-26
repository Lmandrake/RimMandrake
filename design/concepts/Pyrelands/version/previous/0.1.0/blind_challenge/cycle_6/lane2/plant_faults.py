#!/usr/bin/env python3
"""Plant each fault of planted_faults.json in turn, run the suites, restore byte for byte.
    WINBUILD_ROOT=/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c6_mut/ python3 plant_faults.py --baseline [--out f]
    ... python3 plant_faults.py --only ID,ID [--append]        ... --finish   (writes {"tree_clean_after": ...})
    ... python3 plant_faults.py --plant ID [--patch out.patch] -- CMD...   plant one fault, run CMD, restore; exit = CMD's rc
                                                                           (a check's red run on that plant)
Suites: the ones each fault names ("suites"); lane 1 (run_lane1.py: caught = a FAIL row id not FAIL in the baseline) and the offline tests below with the test
table's own commands (caught = PASS in the baseline, FAIL now with a verdict line, not a crash). A non-zero rc alone is
never a catch: a suite whose output carries a Traceback or BUILD FAILED and no verdict reads CRASH. Restores on SIGTERM,
SIGINT and SIGHUP and at exit; every run ends checking git diff --quiet -- src/RimMandrake/Pyrelands."""
import argparse, concurrent.futures as cf, json, os, re, signal, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TABLE = os.path.join(REPO, "design/concepts/Pyrelands/version/test_table.json")
LANE1 = os.path.join(HERE, "..", "lane1", "run_lane1.py")
SUITES = ["T_ASH_PROBE_OFFLINE", "T_DEFS_OFFLINE", "T_CUT_STAYS_CUT", "T_SETTINGS_SWEEP_OFFLINE", "T_SETTINGS_SCREENS", "T_SITE", "T_FUZZ",
          "T_LINT", "T_VENOM_DOSE", "T_VENOM_STAGING", "T_FIREFOAM_SCENE", "T_ROUND6_GAPS"]
SLOW = ["T_BURN_LANES", "T_BURN_ECOLOGY"]  # run on a survivor only (--slow)
EXTRA = {"ACCEPT_ROOF": "python3 design/concepts/Pyrelands/version/evidence/accept_furnace_beast_spares_roof.py"}
SAVED = {}


def restore(*_):
    for path, data in SAVED.items():
        with open(path, "wb") as f:
            f.write(data)
    SAVED.clear()
    if _:
        sys.exit(3)


for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, restore)


def commands():
    t = json.load(open(TABLE))["tests"]
    c = {n: t[n]["command"] for n in SUITES + SLOW}
    c.update(EXTRA)
    return c


def run_suite(name, cmd, timeout=420):
    env = dict(os.environ)
    root = os.environ.get("WINBUILD_ROOT", "/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c6_mut/")
    env["WINBUILD_ROOT"] = os.path.join(root, name)
    os.makedirs(env["WINBUILD_ROOT"], exist_ok=True)
    try:
        r = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return {"verdict": "TIMEOUT", "rc": None, "last": ""}
    out = r.stdout + "\n" + r.stderr
    lines = [l for l in r.stdout.splitlines() if l.strip()] or [l for l in out.splitlines() if l.strip()] or [""]
    crash = r.returncode != 0 and (("Traceback" in out or "BUILD FAILED" in out or "error CS" in out)
                                   and not re.search(r"\bFAIL\b|mutant|failed", lines[-1]))
    return {"verdict": "CRASH" if crash else ("PASS" if r.returncode == 0 else "FAIL"), "rc": r.returncode, "last": lines[-1][:240]}


def run_lane1():
    fd, out = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    env = dict(os.environ, PYRE_LANE1_STAGE="/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c6_mut/lane1")
    r = subprocess.run([sys.executable, LANE1, "--out", out], cwd=REPO, capture_output=True, text=True, timeout=480, env=env)
    rows = [json.loads(l) for l in open(out)] if os.path.getsize(out) else []
    os.remove(out)
    if r.returncode == 2 or not rows:
        return {"verdict": "CRASH", "rc": r.returncode, "fail_ids": [], "last": (r.stdout + r.stderr).strip().splitlines()[-1:]}
    return {"verdict": "FAIL" if r.returncode else "PASS", "rc": r.returncode, "fail_ids": sorted(x["id"] for x in rows if x["verdict"] == "FAIL")}


def run_all(only=None, slow=False):
    cmds = {n: c for n, c in commands().items() if (only is None or n in only) and (slow or n not in SLOW)}
    res = {}
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(run_suite, n, c): n for n, c in cmds.items()}
        lane = ex.submit(run_lane1) if only is None or "LANE1" in only else None
        for f in cf.as_completed(futs):
            res[futs[f]] = f.result()
        if lane: res["LANE1"] = lane.result()
    return res


def plant_and_run(fid, cmd, patch):
    flt = next(f for f in json.load(open(os.path.join(HERE, "planted_faults.json")))["faults"] if f["id"] == fid)
    path = os.path.join(REPO, flt["file"])
    data = open(path, "rb").read()
    text = data.decode("utf-8")
    if text.count(flt["old"]) != 1:
        print("REFUSED: %s old text occurs %d times" % (fid, text.count(flt["old"])))
        return 2
    SAVED[path] = data
    try:
        open(path, "w", encoding="utf-8", newline="").write(text.replace(flt["old"], flt["new"], 1))
        if patch:
            open(patch, "w").write(subprocess.run(["git", "diff", "--", flt["file"]], cwd=REPO, capture_output=True, text=True).stdout)
        r = subprocess.run(cmd, cwd=REPO)
    finally:
        restore()
    clean = subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/Pyrelands"], cwd=REPO).returncode == 0
    print("planted %s; command rc %s; restored, tree clean %s" % (fid, r.returncode, clean))
    return r.returncode if clean else 3


def main():
    if "--plant" in sys.argv:
        i = sys.argv.index("--plant")
        fid = sys.argv[i + 1]
        patch = sys.argv[sys.argv.index("--patch") + 1] if "--patch" in sys.argv else None
        cmd = sys.argv[sys.argv.index("--") + 1:]
        sys.exit(plant_and_run(fid, cmd, patch))
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--finish", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "planted_results.jsonl"))
    ap.add_argument("--append", action="store_true")
    ap.add_argument("--slow", action="store_true")
    a = ap.parse_args()
    if a.finish:
        clean = subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/Pyrelands"], cwd=REPO).returncode == 0
        with open(a.out, "a") as f:
            f.write(json.dumps({"tree_clean_after": clean}) + "\n")
        print("tree_clean_after", clean)
        sys.exit(0 if clean else 1)
    if subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/Pyrelands"], cwd=REPO).returncode:
        sys.exit("REFUSED: src/RimMandrake/Pyrelands is dirty before planting")
    mode = "a" if a.append else "w"
    if a.baseline:
        t0 = time.time()
        res = run_all(slow=a.slow)
        row = {"baseline": True, "suites": res, "seconds": round(time.time() - t0, 1)}
        open(a.out, mode).write(json.dumps(row) + "\n")
        print("baseline", {k: v["verdict"] for k, v in res.items()}, "lane1 FAIL", res["LANE1"].get("fail_ids"))
        return
    base = [json.loads(l) for l in open(a.out) if '"baseline": true' in l]
    if not base:
        sys.exit("REFUSED: no baseline row in " + a.out)
    base = base[-1]["suites"]
    faults = json.load(open(os.path.join(HERE, "planted_faults.json")))["faults"]
    want = a.only.split(",") if a.only else [f["id"] for f in faults]
    for flt in [f for f in faults if f["id"] in want]:
        path = os.path.join(REPO, flt["file"])
        data = open(path, "rb").read()
        text = data.decode("utf-8")
        if text.count(flt["old"]) != 1:
            row = {"fault": flt["id"], "error": "old text occurs %d times" % text.count(flt["old"])}
        else:
            SAVED[path] = data
            open(path, "w", encoding="utf-8", newline="").write(text.replace(flt["old"], flt["new"], 1))
            t0 = time.time()
            try:
                res = run_all(flt["suites"], a.slow)
            finally:
                restore()
            caught_by, crashed = [], []
            for n, r in res.items():
                if r["verdict"] in ("CRASH", "TIMEOUT"):
                    crashed.append(n)
                elif n == "LANE1":
                    new = sorted(set(r["fail_ids"]) - set(base["LANE1"].get("fail_ids", [])))
                    if new:
                        caught_by.append("LANE1:" + ",".join(new))
                elif r["verdict"] == "FAIL" and base.get(n, {}).get("verdict") == "PASS":
                    caught_by.append(n)
            row = {"fault": flt["id"], "file": flt["file"], "bars": flt["bars"], "caught": bool(caught_by), "caught_by": caught_by,
                   "crashed": crashed, "seconds": round(time.time() - t0, 1),
                   "suites": {n: {k: v for k, v in r.items() if k != "fail_ids"} | ({"fail_ids": r["fail_ids"]} if "fail_ids" in r else {}) for n, r in res.items()}}
        open(a.out, "a").write(json.dumps(row) + "\n")
        print(flt["id"], "CAUGHT by " + ", ".join(row.get("caught_by", [])) if row.get("caught") else "NOT CAUGHT", "crashed", row.get("crashed"), flush=True)
    clean = subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/Pyrelands"], cwd=REPO).returncode == 0
    print("tree clean", clean)
    sys.exit(0 if clean else 1)


main()
