#!/usr/bin/env python3
"""Plant each fault of planted_faults.json in turn, run lane 1 and the offline deciders of the fault's bars, restore byte for
byte, and prove the tree clean.

    WINBUILD_ROOT=/mnt/d/ClaudeWork/rimmandrake/scratch/flowworks_blind_c5_mut/ python3 plant_faults.py [--ids A,B] [--append]
    python3 plant_faults.py --baseline      # one baseline row from an unplanted run of every suite (lane 1 + all deciders)

A fault is CAUGHT only by a NEW failing row against the baseline: a lane-1 row whose verdict turns FAIL, a C# case printed
"FAIL  <name>" by selftest_flowworks_stock.py, or a Python decider that prints FAIL. A non-zero rc alone (a compile error, a
crash) is recorded as such and is not a catch (FORMAT_NOTES trap b). The original bytes are restored after every fault and
on SIGTERM, SIGINT and SIGHUP; the run ends with `git diff --quiet -- src/RimMandrake/FlowWorks` and writes
{"tree_clean_after": ...} last. Output: planted_results.jsonl beside this file."""
import argparse, json, os, re, signal, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
LANE1 = os.path.join(HERE, "..", "lane1", "run_lane1.py")
TABLE = os.path.join(REPO, "design/concepts/FlowWorks/version/test_table.json")
OUT = os.path.join(HERE, "planted_results.jsonl")
WROOT = os.environ.get("WINBUILD_ROOT", "/mnt/d/ClaudeWork/rimmandrake/scratch/flowworks_blind_c5_mut/")
LANE1_KERNELS = {"RM_SheetMath.cs", "RM_ConversionMath.cs", "RM_DrillSurveyMath.cs", "RM_SprinklerKernel.cs", "RM_ContainerStyleMath.cs",
                 "RM_ThirstMath.cs", "RM_Volume.cs", "RM_FireMath.cs", "RM_StockMath.cs"}
OFFLINE = ["inv_overflow_sheet", "inv_converters", "inv_bottles_thirst", "inv_drilling", "inv_sprinklers"]

_saved = {}  # path -> original bytes


def restore_all(*_):
    for p, b in list(_saved.items()):
        with open(p, "wb") as f:
            f.write(b)
        _saved.pop(p, None)


def on_signal(sig, _frame):
    restore_all()
    sys.stderr.write("plant_faults: signal %d, tree restored\n" % sig)
    sys.exit(128 + sig)


for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, on_signal)


def deciders():
    t = json.load(open(TABLE))
    bars = t["bars"] if isinstance(t["bars"], dict) else {b["id"]: b for b in t["bars"]}
    tests = t["tests"] if isinstance(t["tests"], dict) else {x["id"]: x for x in t["tests"]}
    return {b: [(d, tests[d].get("command")) for d in bars[b].get("offline_decides", []) if tests[d].get("command")] for b in OFFLINE}


def run_suite(tid, cmd):
    env = dict(os.environ, WINBUILD_ROOT=WROOT)
    t0 = time.time()
    try:
        p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
                           timeout=1500)  # a hang guard: the slowest decider recorded 395 s
        rc, out = p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return {"suite": tid, "rc": None, "fails": [], "note": "timed out at 1500 s (hang guard): UNMEASURED", "seconds": 1500}
    fails = sorted(set(re.findall(r"^FAIL\s+(\S+)", out, re.M)))
    if not fails and rc and re.search(r"\bFAIL\b", out) and "selftest_flowworks_stock" not in cmd:
        fails = ["%s:FAIL" % tid]
    summary = re.findall(r"^(\d+/\d+ passed)", out, re.M)
    errs = re.findall(r"error CS\d+[^\n]*", out)[:3]
    return {"suite": tid, "rc": rc, "fails": fails, "passed": summary[-1] if summary else None,
            "note": ("; ".join(errs) if errs else (out.strip().splitlines() or [""])[-1][:300]), "seconds": round(time.time() - t0, 1)}


def run_lane1():
    tmp = os.path.join(WROOT, "lane1_rows_planted.jsonl")
    env = dict(os.environ, FW_LANE1_STAGE=os.path.join(WROOT, "lane1_stage"))
    t0 = time.time()
    p = subprocess.run(["python3", LANE1, "--out", tmp], cwd=REPO, capture_output=True, text=True, env=env, timeout=900)  # hang guard: ~10 s measured
    rows = [json.loads(l) for l in open(tmp)] if p.returncode in (0, 1) and os.path.exists(tmp) else []
    return {"suite": "lane1", "rc": p.returncode, "fails": sorted(r["id"] for r in rows if r["verdict"] == "FAIL"),
            "note": (p.stdout.strip().splitlines() or [""])[0][:200], "seconds": round(time.time() - t0, 1)}


def baseline_fails():
    if not os.path.exists(OUT):
        return {}
    for l in open(OUT):
        r = json.loads(l)
        if r.get("id") == "baseline":
            return {s["suite"]: set(s["fails"]) for s in r["suites"]}
    return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default=None)
    ap.add_argument("--append", action="store_true")
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--baseline-from-reruns", action="store_true",
                    help="write the baseline row from reruns.jsonl and lane1_rows.jsonl of this cycle (same tree, unplanted)")
    ap.add_argument("--finish", action="store_true", help="prove the tree clean and append the last row")
    ap.add_argument("--run-planted", default=None, metavar="ID",
                    help="plant fault ID, run the command after --, restore, exit with the command's rc (a repaired check's red run)")
    ap.add_argument("--patch-of", default=None, metavar="ID", help="print fault ID as a unified diff (for maturation.py red-seen)")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    if a.run_planted or a.patch_of:
        fid = a.run_planted or a.patch_of
        fl = next(x for x in json.load(open(os.path.join(HERE, "planted_faults.json")))["faults"] if x["id"] == fid)
        path = os.path.join(REPO, fl["file"])
        orig = open(path, "rb").read()
        text = orig.decode("utf-8")
        if text.count(fl["old"]) != 1:
            sys.exit("fault %s: old text occurs %d times" % (fid, text.count(fl["old"])))
        _saved[path] = orig
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text.replace(fl["old"], fl["new"], 1))
        try:
            if a.patch_of:
                d = subprocess.run(["git", "-C", REPO, "diff", "--", fl["file"]], capture_output=True, text=True)
                sys.stdout.write(d.stdout)
                rc = 0 if d.stdout else 1
            else:
                cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
                rc = subprocess.run(cmd, cwd=REPO, env=dict(os.environ, WINBUILD_ROOT=WROOT)).returncode
        finally:
            restore_all()
        sys.exit(rc)
    if a.finish:
        restore_all()
        clean = subprocess.run(["git", "-C", REPO, "diff", "--quiet", "--", "src/RimMandrake/FlowWorks"]).returncode == 0
        with open(OUT, "a") as f:
            f.write(json.dumps({"tree_clean_after": clean}) + "\n")
        print("tree_clean_after", clean)
        sys.exit(0 if clean else 1)
    if a.baseline_from_reruns:
        rr = [json.loads(l) for l in open(os.path.join(HERE, "reruns.jsonl"))]
        l1 = [json.loads(l) for l in open(os.path.join(HERE, "..", "lane1", "lane1_rows.jsonl"))]
        suites = [{"suite": "lane1", "rc": 0, "fails": sorted(r["id"] for r in l1 if r["verdict"] == "FAIL"), "note": "lane1/lane1_rows.jsonl"}]
        suites += [{"suite": r["test"], "rc": r["rc"], "fails": [] if r["result"] == "PASS" else ["%s:%s" % (r["test"], r["result"])],
                    "note": r.get("last")} for r in rr if r.get("rc") is not None]
        with open(OUT, "w") as f:
            f.write(json.dumps({"id": "baseline", "source": "reruns.jsonl + lane1_rows.jsonl, this cycle, unplanted tree", "suites": suites}) + "\n")
        print("baseline", [(s["suite"], s["fails"]) for s in suites])
        return
    os.makedirs(WROOT, exist_ok=True)
    dec = deciders()
    mode = "a" if a.append else "w"
    if a.baseline:
        suites = [run_lane1()] + [run_suite(d, c) for b in OFFLINE for d, c in dec[b]]
        with open(OUT, mode) as f:
            f.write(json.dumps({"id": "baseline", "suites": suites, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}) + "\n")
        print(json.dumps({"baseline": [(s["suite"], s["rc"], s["fails"]) for s in suites]}))
        return
    base = baseline_fails()
    faults = json.load(open(os.path.join(HERE, "planted_faults.json")))["faults"]
    if a.ids:
        want = set(a.ids.split(","))
        faults = [x for x in faults if x["id"] in want]
    for fl in faults:
        path = os.path.join(REPO, fl["file"])
        orig = open(path, "rb").read()
        text = orig.decode("utf-8")
        if text.count(fl["old"]) != 1:
            row = {"id": fl["id"], "caught": False, "note": "old text occurs %d times: not planted" % text.count(fl["old"])}
        else:
            _saved[path] = orig
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(text.replace(fl["old"], fl["new"], 1))
            suites = []
            try:
                if os.path.basename(path) in LANE1_KERNELS:
                    suites.append(run_lane1())
                seen = set()
                for b in fl["bars"]:
                    for d, c in dec.get(b, []):
                        if d not in seen:
                            seen.add(d)
                            suites.append(run_suite(d, c))
            finally:
                restore_all()
            new = {s["suite"]: sorted(set(s["fails"]) - base.get(s["suite"], set())) for s in suites}
            caught_by = sorted(k for k, v in new.items() if v)
            row = {"id": fl["id"], "file": fl["file"], "bars": fl["bars"], "where": fl.get("where"), "caught": bool(caught_by),
                   "caught_by": caught_by, "new_failing_rows": {k: v for k, v in new.items() if v}, "suites": suites,
                   "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        with open(OUT, "a") as f:
            f.write(json.dumps(row) + "\n")
        print(json.dumps({"id": row["id"], "caught": row["caught"], "by": row.get("caught_by"), "rcs": [(s["suite"], s["rc"]) for s in row.get("suites", [])]}), flush=True)
    clean = subprocess.run(["git", "-C", REPO, "diff", "--quiet", "--", "src/RimMandrake/FlowWorks"]).returncode == 0
    print("tree_clean_after", clean)


if __name__ == "__main__":
    main()
