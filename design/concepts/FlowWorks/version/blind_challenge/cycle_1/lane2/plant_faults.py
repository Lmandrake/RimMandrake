#!/usr/bin/env python3
"""Plant FlowWorks faults one at a time, run the bar's offline deciders and blind lane 1, restore byte for byte.
    python3 plant_faults.py --baseline            # unplanted: record the failing cases each suite already shows
    python3 plant_faults.py --fault ID [--fault ID ...]
    python3 plant_faults.py --final               # prove git diff --quiet -- src/RimMandrake/FlowWorks, rebuild clean
One fault per call fits the 540 s foreground limit when it needs a C# rebuild (~3.5 min). Every fault restages and rebuilds once
(the first decider), then the other deciders run --no-build on that stage: a source-text check reads the STAGED copy,
so a --no-build run without a restage never sees a planted caller. "Caught" = a NEW failing case / row versus the baseline, never a bare non-zero rc.
Restores on SIGTERM, SIGINT and SIGHUP. WINBUILD_ROOT defaults to <agent storage>/scratch/fw_blind_mut/."""
import argparse, json, os, re, signal, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TABLE = os.path.join(REPO, "design/concepts/FlowWorks/version/test_table.json")
FAULTS = os.path.join(HERE, "planted_faults.json")
OUT = os.path.join(HERE, "planted_results.jsonl")
LANE1 = os.path.join(HERE, "..", "lane1", "run_lane1.py")
STOCK = "selftest_flowworks_stock.py"
SELFTEST_CSPROJ = os.path.join(REPO, "src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj")
_restore = []


def restore(*_):
    for path, data in _restore:
        with open(path, "wb") as f:
            f.write(data)
    _restore.clear()


def on_signal(sig, frm):
    restore()
    sys.exit(128 + sig)


for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, on_signal)


def compiled_by_selftest(rel):
    txt = open(SELFTEST_CSPROJ, encoding="utf-8").read()
    return os.path.basename(rel) in txt


def deciders(bars):
    t = json.load(open(TABLE))
    byid = {b["id"]: b for b in t["bars"]}
    ids = []
    for b in bars:
        for d in byid[b].get("offline_decides", []):
            if d not in ids:
                ids.append(d)
    return [(i, t["tests"][i]["command"]) for i in ids]


def run(cmd, env, timeout):
    try:
        p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=timeout)
        return p.returncode, p.stdout + "\n" + p.stderr
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT"


def failing(out):
    return sorted(set(m.group(1) for m in re.finditer(r"^FAIL\s+(\S+)", out, re.M)))


def suites(bars, build, env):
    res = {}
    built = not build
    for tid, cmd in deciders(bars):
        c = cmd
        if STOCK in cmd:
            c = cmd.replace(STOCK, STOCK + " --no-build", 1) if built else cmd
            built = True
        t0 = time.time()
        rc, out = run(c, env, 420)
        build_failed = rc not in (0, 1, None) or "error CS" in out
        fl = failing(out) if STOCK in cmd else ([tid] if rc != 0 else [])   # a python decider is one row: red = rc != 0
        res[tid] = dict(rc=rc, failing=fl, build_failed=build_failed, last=[l for l in out.splitlines() if l.strip()][-1:] , s=round(time.time() - t0, 1))
    rows_out = "/tmp/fw_pf_lane1_rows.jsonl"
    rc, out = run("python3 %s --out %s" % (LANE1, rows_out), env, 200)
    l1 = []
    if os.path.exists(rows_out):
        l1 = sorted(json.loads(l)["id"] for l in open(rows_out) if l.strip() and json.loads(l)["verdict"] == "FAIL")
    res["LANE1"] = dict(rc=rc, failing=l1, build_failed=rc == 2)
    return res


def baseline():
    if not os.path.exists(OUT):
        return None
    for l in open(OUT):
        r = json.loads(l)
        if r.get("id") == "baseline":
            return r
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--fault", action="append", default=[])
    ap.add_argument("--final", action="store_true")
    a = ap.parse_args()
    env = dict(os.environ)
    env.setdefault("WINBUILD_ROOT", "/mnt/d/ClaudeWork/rimmandrake/scratch/fw_blind_mut/")
    env["FW_LANE1_STAGE"] = "fw_blind_lane1_mut"
    faults = {f["id"]: f for f in json.load(open(FAULTS))}
    allbars = sorted({b for f in faults.values() for b in f["bars"]})
    if a.baseline:
        res = suites(allbars, True, env)
        with open(OUT, "w") as f:
            f.write(json.dumps(dict(id="baseline", suites=res)) + "\n")
        print("BASELINE", {k: v["failing"] for k, v in res.items()})
        return
    if a.final:
        rc = subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/FlowWorks"], cwd=REPO).returncode
        rb, _ = run("python3 src/RimMandrake/Utils/selftest_flowworks_stock.py --only Sprinkler*", env, 420)   # leave the stage built clean
        with open(OUT, "a") as f:
            f.write(json.dumps(dict(id="tree_clean_after", tree_clean_after=rc == 0, clean_rebuild_rc=rb)) + "\n")
        print("TREE CLEAN" if rc == 0 else "TREE DIRTY", "rebuild rc", rb)
        sys.exit(rc)
    base = baseline()
    if base is None:
        sys.exit("run --baseline first")
    for fid in a.fault:
        f = faults[fid]
        path = os.path.join(REPO, f["file"])
        data = open(path, "rb").read()
        txt = data.decode("utf-8")
        if txt.count(f["old"]) != 1:
            sys.exit("%s: old text occurs %d times" % (fid, txt.count(f["old"])))
        build = True   # always restage: a --no-build run reads the STAGED copy of every source file, not the planted tree (measured: 9 caller faults "survived" unseen)
        _restore.append((path, data))
        try:
            with open(path, "wb") as fh:
                fh.write(txt.replace(f["old"], f["new"], 1).encode("utf-8"))
            res = suites(f["bars"], build, env)
        finally:
            restore()
        if open(path, "rb").read() != data:
            sys.exit("RESTORE FAILED for " + path)
        newly = {}
        for k, v in res.items():
            b0 = set(base["suites"].get(k, {}).get("failing", []))
            nf = sorted(set(v["failing"]) - b0)
            if nf:
                newly[k] = nf
        bf = [k for k, v in res.items() if v.get("build_failed")]
        caught_by = sorted(newly)
        row = dict(id=fid, file=f["file"], bars=f["bars"], rebuilt=build, caught=bool(newly), caught_by=caught_by,
                   caught_by_builder=[k for k in caught_by if k != "LANE1"], caught_by_lane1="LANE1" in newly, new_failing=newly,
                   build_failed=bf, suites=res)
        with open(OUT, "a") as fh:
            fh.write(json.dumps(row) + "\n")
        print(fid, "CAUGHT by " + ",".join(caught_by) if newly else "SURVIVED", ("BUILD FAILED " + ",".join(bf)) if bf else "")


main()
