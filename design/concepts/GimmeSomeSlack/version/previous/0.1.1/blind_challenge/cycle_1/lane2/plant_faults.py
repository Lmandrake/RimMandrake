#!/usr/bin/env python3
"""Plant each fault of planted_faults.json in turn, run the deciders, restore the file byte for byte, record who caught it.
    python3 plant_faults.py --baseline                       clean-tree run of every suite (written first)
    python3 plant_faults.py --only PF_A[,PF_B]               plant, run, restore (rows appended)
    python3 plant_faults.py --finish                         prove src/RimMandrake/GimmeSomeSlack equals HEAD, write the last row
Suites: the fast offline deciders (FAST), blind lane 1 (always) and, for a fault marked slow, T_CORE (the C# SelfTest, about
310 s, which also decides T_SHOCK_RULE_OFFLINE and T_SWITCH_OFF_NODE_OFFLINE). One fault per call keeps each call under 540 s.
A fault is CAUGHT by a suite only when that suite goes from green on the baseline to red (a builder test), or when lane 1
shows a FAIL row the baseline did not have; a non-zero rc alone never counts for lane 1.
Builds stage under WINBUILD_ROOT=/mnt/d/ClaudeWork/rimmandrake/scratch/gimmesomeslack_blind_c1_mut/ (never the shared
staging). SIGTERM, SIGINT and SIGHUP restore the planted file before exiting."""
import argparse, hashlib, json, os, signal, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/GimmeSomeSlack")
TT = json.load(open(os.path.join(REPO, "design/concepts/GimmeSomeSlack/version/test_table.json")))["tests"]
FAST = ["T_NO_HOSE", "T_SHOCK_OUTLIVES", "T_SHOCK_OUTLIVES_BINDING", "T_SHOCK_BITES_BINDING", "T_SETTINGS_SWEEP_OFFLINE",
        "T_DROPPED_CORDS_AERIAL_MASTER_OFFLINE", "T_STATICS_CENSUS", "T_TEXPATH_OFFLINE", "T_H_AERIAL_PROBE_BATCH",
        "T_MAIN_THREAD_TEXTURES_OFFLINE", "T_STUB_ART_CENSUS", "T_FLIP_FRESH_OFFLINE", "T_H_PROOF_ALL"]
SLOW = ["T_CORE"]
LANE1_OUT = "/tmp/gss_blind_c1_lane1_mut.jsonl"
LANE1 = "python3 " + os.path.join(HERE, "..", "lane1", "run_lane1.py") + " --out " + LANE1_OUT
RESULTS = os.path.join(HERE, "planted_results.jsonl")
ENV = dict(os.environ, WINBUILD_ROOT="/mnt/d/ClaudeWork/rimmandrake/scratch/gimmesomeslack_blind_c1_mut/",
           GSS_LANE1_STAGE="/mnt/d/ClaudeWork/rimmandrake/scratch/gimmesomeslack_blind_c1_mut/lane1")
PLANTED = {}


def _restore(*_):
    for p, b in PLANTED.items(): open(p, "wb").write(b)
    sys.exit(3)


for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP): signal.signal(s, _restore)


def run(cmd, timeout=520):
    t = time.time()
    try:
        p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, env=ENV, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, round(time.time() - t, 1), "TIMEOUT"
    tail = [l for l in (p.stdout + p.stderr).splitlines() if l.strip()]
    return p.returncode, round(time.time() - t, 1), (tail[-1] if tail else "")[:240]


def lane1_fails():
    return sorted(json.loads(l)["id"] for l in open(LANE1_OUT) if json.loads(l)["verdict"] == "FAIL")


def suites(slow):
    return FAST + (SLOW if slow else [])


def baseline():
    for k in [r for r in open(RESULTS)] if os.path.exists(RESULTS) else []:
        if '"baseline"' in k: return json.loads(k)["baseline"]
    raise SystemExit("no baseline row: run --baseline first")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--only", default=""); ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--with-slow", action="store_true", help="baseline: also run T_CORE"); ap.add_argument("--finish", action="store_true")
    a = ap.parse_args()
    os.makedirs(ENV["WINBUILD_ROOT"], exist_ok=True)
    if a.finish:
        clean = subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/GimmeSomeSlack"], cwd=REPO).returncode == 0
        open(RESULTS, "a").write(json.dumps({"tree_clean_after": clean}) + "\n"); print("TREE CLEAN AFTER:", clean); return
    if a.baseline:
        base = {}
        for k in suites(a.with_slow): base[k] = run(TT[k]["command"])[0]
        base["LANE1"] = run(LANE1)[0]; base["LANE1_FAILS"] = lane1_fails()
        open(RESULTS, "w").write(json.dumps({"baseline": base, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}) + "\n")
        print("BASELINE", json.dumps(base)); return
    base = baseline()
    faults = {f["id"]: f for f in json.load(open(os.path.join(HERE, "planted_faults.json")))}
    for fid in [x for x in a.only.split(",") if x]:
        f = faults[fid]
        path = os.path.join(MOD, f["file"]); orig = open(path, "rb").read(); text = orig.decode()
        n = text.count(f["old"]); row = {"id": fid, "file": os.path.relpath(path, REPO), "bars": f["bars"]}
        if n != 1:
            row.update(planted=False, why="old text found %d times" % n)
            open(RESULTS, "a").write(json.dumps(row) + "\n"); print("SKIP", fid, n); continue
        res = {}
        try:
            PLANTED[path] = orig; open(path, "wb").write(text.replace(f["old"], f["new"]).encode())
            for k in suites(f.get("slow")):
                rc, sec, last = run(TT[k]["command"])
                b = base.get(k, 0)   # T_CORE's baseline: the rerun in reruns.jsonl (PASS) when not in the baseline row
                res[k] = {"rc": rc, "caught": rc not in (0, None) and b == 0, "s": sec, "last": last}
            rc, sec, last = run(LANE1)
            new = [x for x in lane1_fails() if x not in base["LANE1_FAILS"]]
            det = {json.loads(l)["id"]: json.loads(l)["detail"][:300] for l in open(LANE1_OUT)}
            res["LANE1"] = {"rc": rc, "caught": bool(new), "new_fails": new, "new_detail": [det[x] for x in new], "s": sec}
        finally:
            open(path, "wb").write(orig); PLANTED.pop(path, None)
        assert hashlib.sha256(open(path, "rb").read()).digest() == hashlib.sha256(orig).digest()
        builder = [k for k, v in res.items() if k != "LANE1" and v["caught"]]
        row.update(planted=True, results=res, caught_by_builder=builder, caught_by_lane1=res["LANE1"]["caught"],
                   caught=bool(builder) or res["LANE1"]["caught"])
        open(RESULTS, "a").write(json.dumps(row) + "\n")
        print(fid, "builder:", ",".join(builder) or "MISSED", "| lane1:", res["LANE1"]["caught"], res["LANE1"]["new_fails"])


main()
