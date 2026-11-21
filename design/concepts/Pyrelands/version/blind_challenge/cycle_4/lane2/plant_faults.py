#!/usr/bin/env python3
"""Plant each fault of planted_faults.json in turn, run the suites that decide or support its bars plus blind lane 1,
restore the file byte for byte, and record which suites went red.
    python3 plant_faults.py --baseline                 # fresh planted_results.jsonl, the clean run of every suite first
    python3 plant_faults.py --ids A,B,C                # append one row per fault
    python3 plant_faults.py --finish                   # append {"tree_clean_after": ...} from git diff --quiet
A fault is CAUGHT by a suite only when it makes a new failing row: a selftest that was green on the baseline exits
non-zero with no build error or traceback in its output (those are BROKE, not caught); lane 1 shows a FAIL row id the
baseline did not have. Restores on SIGTERM, SIGINT and SIGHUP. Set WINBUILD_ROOT to a private folder (default below)."""
import argparse, json, os, signal, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
CYCLE = os.path.dirname(HERE)
FAULTS = os.path.join(HERE, "planted_faults.json")
OUT = os.path.join(HERE, "planted_results.jsonl")
TABLE = os.path.join(REPO, "design/concepts/Pyrelands/version/test_table.json")
EXTRA = {"T_WIND_BURN_ROWS": "python3 src/RimMandrake/Pyrelands/selftest_pyrelands_wind_burn_rows.py"}
BY_BAR = {
    "ash_fertility_probe": ["T_ASH_PROBE_OFFLINE", "T_FUZZ"],
    "fresh_burn_compounds_with_black_rain": ["T_ASH_PROBE_OFFLINE", "T_FUZZ"],
    "biome_text_says_engineered": ["T_DEFS_OFFLINE"],
    "inv_art_and_text": ["T_DEFS_OFFLINE", "T_SELF_CONTAINED_OFFLINE"],
    "inv_firebreak_firefoam": ["T_CUT_STAYS_CUT"],
    "inv_lightning_breaker": ["T_CUT_STAYS_CUT"],
    "inv_settings_gate": ["T_SETTINGS_SWEEP_OFFLINE", "T_SETTINGS_SCREENS", "T_SITE"],
    "fire_walks_with_wind": ["T_FUZZ", "T_BURN_ECOLOGY", "T_WIND_BURN_ROWS"],
    "burn_line_walks": ["T_FUZZ", "T_BURN_ECOLOGY", "T_WIND_BURN_ROWS"],
    "three_skies": ["T_FUZZ"],
}
_restore = {}


def restore(*_):
    for p, b in list(_restore.items()):
        with open(p, "wb") as f:
            f.write(b)
        _restore.pop(p, None)
    if _:
        sys.exit(3)


for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, restore)


def commands():
    t = json.load(open(TABLE))["tests"]
    c = {k: v.get("command") or (v.get("runs_today") or {}).get("command") for k, v in t.items()}
    c.update(EXTRA)
    return c


def env():
    e = dict(os.environ)
    e.setdefault("WINBUILD_ROOT", "/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c4_mut/")
    e["LANE1_STAGE"] = "/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c4_mut_lane1"
    return e


def run_suite(name, cmds):
    t0 = time.time()
    if name == "LANE1":
        out = tempfile.mktemp(suffix=".jsonl")
        r = subprocess.run([sys.executable, os.path.join(CYCLE, "lane1", "run_lane1.py"), "--out", out], cwd=REPO,
                           capture_output=True, text=True, timeout=500, env=env())
        fails = []
        if os.path.exists(out):
            fails = sorted(json.loads(l)["id"] for l in open(out) if json.loads(l)["verdict"] == "FAIL")
            os.remove(out)
        return {"rc": r.returncode, "fails": fails, "last": (r.stdout.strip().splitlines() or [""])[0][:200], "s": round(time.time() - t0, 1)}
    r = subprocess.run(cmds[name], shell=True, cwd=REPO, capture_output=True, text=True, timeout=500, env=env())
    txt = r.stdout + "\n" + r.stderr
    broke = "error CS" in txt or "BUILD FAILED" in txt or "Traceback (most recent call last)" in txt
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    red = [l for l in lines if any(w in l for w in ("FAIL", "MISS", "RED", "not ok", "differs", "missing"))][:3]
    return {"rc": r.returncode, "broke": broke, "red": [x[:200] for x in red], "last": (lines[-1] if lines else "")[:200], "s": round(time.time() - t0, 1)}


def suites_for(f):
    s = ["LANE1"]
    for b in f["bars"]:
        for x in BY_BAR.get(b, []):
            if x not in s:
                s.append(x)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--ids", default="")
    ap.add_argument("--finish", action="store_true")
    a = ap.parse_args()
    faults = {f["id"]: f for f in json.load(open(FAULTS))["faults"]}
    cmds = commands()
    if a.baseline:
        allsuites = ["LANE1"] + sorted({x for v in BY_BAR.values() for x in v})
        res = {s: run_suite(s, cmds) for s in allsuites}
        with open(OUT, "w") as fo:
            fo.write(json.dumps({"baseline": True, "suites": res}) + "\n")
        print("BASELINE", {s: r["rc"] for s, r in res.items()})
        return
    if a.finish:
        clean = subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/Pyrelands"], cwd=REPO).returncode == 0
        with open(OUT, "a") as fo:
            fo.write(json.dumps({"tree_clean_after": clean}) + "\n")
        print("tree_clean_after", clean)
        sys.exit(0 if clean else 1)
    base = json.loads(open(OUT).readline())["suites"]
    for fid in [x for x in a.ids.split(",") if x]:
        f = faults[fid]
        p = os.path.join(REPO, f["file"])
        orig = open(p, "rb").read()
        text = orig.decode("utf-8")
        if text.count(f["old"]) != 1:
            row = {"id": fid, "error": "old text found %d times" % text.count(f["old"])}
        else:
            _restore[p] = orig
            with open(p, "wb") as fo:
                fo.write(text.replace(f["old"], f["new"]).encode("utf-8"))
            try:
                res = {s: run_suite(s, cmds) for s in suites_for(f)}
            finally:
                restore()
            assert open(p, "rb").read() == orig, "restore failed for " + p
            caught, broke = [], []
            for s, r in res.items():
                if s == "LANE1":
                    if r["rc"] == 2:
                        broke.append(s)
                    elif set(r["fails"]) - set(base[s]["fails"]):
                        caught.append(s)
                elif base.get(s, {}).get("rc") == 0 and r["rc"] != 0:
                    (broke if r["broke"] else caught).append(s)
            row = {"id": fid, "file": f["file"], "bars": f["bars"], "where": f["where"], "caught_by": caught, "broke": broke,
                   "caught": bool(caught), "suites": res}
        with open(OUT, "a") as fo:
            fo.write(json.dumps(row) + "\n")
        print(fid, "CAUGHT" if row.get("caught") else "MISSED", row.get("caught_by"), "broke", row.get("broke"), row.get("error", ""))


if __name__ == "__main__":
    main()
