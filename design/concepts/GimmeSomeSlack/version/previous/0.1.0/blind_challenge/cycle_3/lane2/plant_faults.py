#!/usr/bin/env python3
"""Plant each fault of planted_faults.json in turn, run its suites, restore byte for byte, prove the tree clean.
    python3 plant_faults.py --baseline [--suites A,B]   run the suites on the clean tree (the failing rows to subtract)
    python3 plant_faults.py --only ID[,ID...]           plant and run those faults (each call stays under 540 s)
Results go to planted_results.jsonl: the baseline first, one row per fault (a later run replaces an earlier one), and
{"tree_clean_after": ...} last, rewritten on every call. A fault is CAUGHT by a suite only when it makes a failing row the
baseline does not have; a non-zero rc alone is never a catch. Restores on SIGTERM, SIGINT and SIGHUP. C# suites build under
the private WINBUILD_ROOT /mnt/d/ClaudeWork/rimmandrake/scratch/gimmesomeslack_blind_c3_mut/."""
import argparse, json, os, re, signal, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
OUT = os.path.join(HERE, "planted_results.jsonl")
WROOT = "/mnt/d/ClaudeWork/rimmandrake/scratch/gimmesomeslack_blind_c3_mut/"
L1 = os.path.join(HERE, "..", "lane1", "run_lane1.py")
TMP = "/tmp/gssc3"
SUITES = {
    "NOHOSE": ["python3", "src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_hose.py"],
    "LANE1": ["python3", L1, "--out", os.path.join(TMP, "lane1_planted.jsonl")],
    "CORE": ["python3", "src/RimMandrake/Utils/selftest_gimmesomeslack.py"],
    "GEOM": ["python3", "src/RimMandrake/Utils/selftest_gimmesomeslack.py", "--geometry-only"],
    "CENSUS": ["python3", "src/RimMandrake/GimmeSomeSlack/selftest_gss_statics_census.py"],
}
norm = lambda s: re.sub(r"-?\d+(\.\d+)?", "#", s.strip())[:200]

def failing(suite, out):
    if suite == "LANE1":
        p = os.path.join(TMP, "lane1_planted.jsonl")
        return sorted({json.loads(l)["id"] for l in open(p) if l.strip() and json.loads(l)["verdict"] == "FAIL"}) if os.path.exists(p) else ["<no rows>"]
    rows = set()
    for l in out.splitlines():
        t = l.strip()
        if suite == "NOHOSE" and (t.startswith("FAIL") or t.startswith("UNMEASURED")): rows.add(" ".join(t.split()[:2]))
        elif suite != "NOHOSE" and (t.startswith("FAIL") or " FAIL" in t[:60] or t.startswith("REFUS") or "BUILD FAILED" in t or "error CS" in t):
            rows.add(norm(t))
    return sorted(rows)

def run(suite):
    os.makedirs(TMP, exist_ok=True)
    if suite == "LANE1" and os.path.exists(os.path.join(TMP, "lane1_planted.jsonl")): os.remove(os.path.join(TMP, "lane1_planted.jsonl"))
    t0 = time.time()
    try:
        p = subprocess.run(SUITES[suite], cwd=REPO, capture_output=True, text=True, timeout=500, env=dict(os.environ, WINBUILD_ROOT=WROOT))
        rc, out = p.returncode, p.stdout + "\n" + p.stderr
    except subprocess.TimeoutExpired as e:
        rc, out = 124, "TIMEOUT"
    return {"rc": rc, "seconds": round(time.time() - t0, 1), "failing": failing(suite, out)}

saved = {}
def restore(*_):
    for path, data in saved.items():
        if data is None:
            if os.path.exists(path): os.remove(path)
        else:
            open(path, "wb").write(data)
    saved.clear()
for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, lambda *a: (restore(), sys.exit(130)))

def load():
    rows = {}
    if os.path.exists(OUT):
        for l in open(OUT):
            if l.strip():
                r = json.loads(l)
                if "tree_clean_after" in r: continue
                rows[r.get("id", "baseline")] = r
    return rows

def write(rows, clean):
    order = ["baseline"] + [f["id"] for f in json.load(open(os.path.join(HERE, "planted_faults.json")))["faults"]]
    with open(OUT, "w") as f:
        for k in order:
            if k in rows: f.write(json.dumps(rows[k]) + "\n")
        f.write(json.dumps({"tree_clean_after": clean}) + "\n")

def tree_clean():
    d = subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/GimmeSomeSlack"], cwd=REPO).returncode == 0
    u = subprocess.run(["git", "ls-files", "--others", "--exclude-standard", "--", "src/RimMandrake/GimmeSomeSlack"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    return d and not u

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--baseline", action="store_true"); ap.add_argument("--only", default=""); ap.add_argument("--suites", default=",".join(SUITES))
    a = ap.parse_args()
    if not tree_clean(): sys.exit("tree not clean before planting: refusing")
    faults = {f["id"]: f for f in json.load(open(os.path.join(HERE, "planted_faults.json")))["faults"]}
    rows = load()
    if a.baseline:
        b = rows.get("baseline", {"id": "baseline", "suites": {}})
        for s in a.suites.split(","): b["suites"][s] = run(s)
        rows["baseline"] = b
    base = rows.get("baseline", {}).get("suites")
    if a.only and not base: sys.exit("run --baseline first")
    for fid in [x for x in a.only.split(",") if x]:
        f = faults[fid]; path = os.path.join(REPO, f["file"])
        try:
            if f["old"] is None:
                saved[path] = None; os.makedirs(os.path.dirname(path), exist_ok=True); open(path, "w").write(f["new"])
            else:
                data = open(path, "rb").read(); saved[path] = data
                txt = data.decode("utf-8")
                assert txt.count(f["old"]) == 1, (fid, "old text not unique")
                open(path, "wb").write(txt.replace(f["old"], f["new"]).encode("utf-8"))
            res = {}
            for s in f["suites"]:
                r = run(s); r["new_failing"] = sorted(set(r["failing"]) - set(base[s]["failing"])); r["caught"] = bool(r["new_failing"])
                r["failing"] = r["failing"][:12]; r["new_failing"] = r["new_failing"][:12]; res[s] = r
        finally:
            restore()
        rows[fid] = {"id": fid, "file": f["file"], "bars": f["bars"], "suites": res, "caught_by": [s for s in res if res[s]["caught"]],
                     "caught": any(res[s]["caught"] for s in res)}
        print(fid, "caught by", rows[fid]["caught_by"] or "NOTHING", {s: res[s]["new_failing"][:2] for s in res})
    clean = tree_clean()
    write(rows, clean)
    print("tree_clean_after", clean)
    sys.exit(0 if clean else 3)

main()
