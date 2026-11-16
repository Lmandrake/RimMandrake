#!/usr/bin/env python3
"""Plant each fault of planted_faults.json in turn, run its suites, restore the file byte for byte, prove the tree clean.
    WINBUILD_ROOT=/mnt/d/ClaudeWork/rimmandrake/scratch/gimmesomeslack_blind_c4_mut/ \\
    python3 plant_faults.py [--baseline] [--only F1,F2] [--append] [--finish]
Suites: a test id of version/test_table.json (its recorded command) or LANE1 (lane1/run_lane1.py to a temp file).
CAUGHT means a NEW failing row against the baseline (a FAIL line, an "N/M checks passed" with N < M, or a lane-1 FAIL row
id the baseline did not have); a non-zero rc alone (a compile break) is never a catch.
Restores on SIGTERM, SIGINT and SIGHUP. --finish writes {"tree_clean_after": ...} from `git diff --quiet` of the mod."""
import argparse, json, os, re, signal, subprocess, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TT = os.path.join(REPO, "design/concepts/GimmeSomeSlack/version/test_table.json")
LANE1 = os.path.join(HERE, "..", "lane1", "run_lane1.py")
OUT = os.path.join(HERE, "planted_results.jsonl")
MOD = "src/RimMandrake/GimmeSomeSlack"
tests = json.load(open(TT))["tests"]
_restore = {}


def restore_all(*_):
    for path, data in list(_restore.items()):
        with open(path, "wb") as f: f.write(data)
        del _restore[path]


def on_signal(sig, frame):
    restore_all(); sys.exit(128 + sig)


for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP): signal.signal(s, on_signal)


def failing(suite, out, lane1_rows):
    if suite == "LANE1":
        return sorted(r["id"] for r in lane1_rows if r.get("verdict") == "FAIL")
    bad = set()
    for l in out.splitlines():
        l = l.strip()
        m = re.search(r"(\d+)/(\d+) checks passed", l)
        if m and int(m.group(1)) < int(m.group(2)): bad.add(re.sub(r"\d+\.\d+s", "", l)[:200])
        elif re.search(r"\bFAIL(ED)?\b|\bfailures=[1-9]|\b[1-9]\d* failed\b", l) and not re.search(r"\b0 failed\b", l):
            bad.add(re.sub(r"\d+\.\d+s", "", l)[:200])
    return sorted(bad)


def run_suite(suite):
    t0 = time.time()
    if suite == "LANE1":
        tmp = tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False).name
        p = subprocess.run([sys.executable, LANE1, "--out", tmp], cwd=REPO, capture_output=True, text=True, timeout=400)
        rows = [json.loads(l) for l in open(tmp) if l.strip()] if os.path.getsize(tmp) else []
        os.remove(tmp)
    else:
        p = subprocess.run(tests[suite]["command"], shell=True, cwd=REPO, capture_output=True, text=True, timeout=400)
        rows = []
    return {"rc": p.returncode, "seconds": round(time.time() - t0, 1), "fails": failing(suite, p.stdout + "\n" + p.stderr, rows),
            "last": ([l for l in (p.stdout or p.stderr).splitlines() if l.strip()] or [""])[-1][:200]}


def baseline_of():
    for l in open(OUT):
        r = json.loads(l)
        if r.get("baseline"): return r["suites"]
    sys.exit("no baseline row in " + OUT)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--baseline", action="store_true"); ap.add_argument("--only", default="")
    ap.add_argument("--append", action="store_true"); ap.add_argument("--finish", action="store_true")
    a = ap.parse_args()
    faults = json.load(open(os.path.join(HERE, "planted_faults.json")))
    if a.finish:
        clean = subprocess.run(["git", "diff", "--quiet", "--", MOD], cwd=REPO).returncode == 0
        with open(OUT, "a") as f: f.write(json.dumps({"tree_clean_after": clean}) + "\n")
        print("tree_clean_after", clean); sys.exit(0 if clean else 1)
    if a.baseline:
        suites = sorted({s for f in faults for s in f["suites"]})
        res = {s: run_suite(s) for s in suites}
        with open(OUT, "a" if a.append else "w") as f: f.write(json.dumps({"baseline": True, "suites": res}) + "\n")
        print("BASELINE", {s: (r["rc"], len(r["fails"])) for s, r in res.items()}); return
    base = baseline_of(); only = set(filter(None, a.only.split(",")))
    for fl in faults:
        if only and fl["id"] not in only: continue
        path = os.path.join(REPO, fl["file"]); data = open(path, "rb").read(); text = data.decode("utf-8")
        row = {"id": fl["id"], "file": fl["file"], "bars": fl["bars"]}
        if text.count(fl["old"]) != 1:
            row.update(applied=False, caught=False, why="old text occurs %d times" % text.count(fl["old"]))
        else:
            _restore[path] = data
            try:
                with open(path, "w", encoding="utf-8", newline="") as f: f.write(text.replace(fl["old"], fl["new"]))
                res = {}
                for s in fl["suites"]:
                    r = run_suite(s); new = sorted(set(r["fails"]) - set(base[s]["fails"]))
                    res[s] = {"rc": r["rc"], "new_fails": new[:6], "caught": bool(new), "last": r["last"], "seconds": r["seconds"]}
            finally:
                restore_all()
            assert open(path, "rb").read() == data, "restore failed: " + path
            row.update(applied=True, suites=res, caught_by=[s for s, r in res.items() if r["caught"]], caught=any(r["caught"] for r in res.values()))
        with open(OUT, "a") as f: f.write(json.dumps(row) + "\n")
        print(("CAUGHT " if row["caught"] else "SURVIVED ") + fl["id"], row.get("caught_by", row.get("why")))


main()
