#!/usr/bin/env python3
"""Plant each fault of planted_faults.json in turn, run the offline suites and lane 1, restore byte for byte.
    python3 plant_faults.py --baseline                 fresh planted_results.jsonl with the unplanted baseline row
    python3 plant_faults.py --ids A,B,...|--from N --to M   append one row per fault (index range into the list)
    python3 plant_faults.py --finish                   append {"tree_clean_after": ...} (git diff --quiet -- src/RimMandrake/Graffiti)
A fault is CAUGHT only when it makes a new failing row: a suite red that is green on the baseline, or a lane-1 row FAIL that is
not FAIL on the baseline. A non-zero rc alone never counts. Builds go to WINBUILD_ROOT (default the private
/mnt/d/ClaudeWork/rimmandrake/scratch/graffiti_blind_c2_mut/). The original bytes are restored on SIGTERM, SIGINT and SIGHUP."""
import argparse, json, os, signal, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
OUT = os.path.join(HERE, "planted_results.jsonl")
LANE1 = os.path.join(HERE, "..", "lane1", "run_lane1.py")
SUITES = [
    ("T_FUZZ", "python3 src/RimMandrake/Utils/selftest_graffiti_fuzz.py"),
    ("T_UGLINESS_OFFLINE", "python3 src/RimMandrake/Utils/selftest_graffiti_ugliness.py"),
    ("T_WEATHER_OFFLINE", "python3 src/RimMandrake/Utils/selftest_graffiti_weather.py"),
    ("T_SETTINGS_SCREENS", "python3 src/RimMandrake/Utils/selftest_settings_screens.py"),
    ("T_RAID_TAG_BUILT_WALL_ONLY", "python3 src/RimMandrake/Utils/selftest_graffiti_raid_tag_wall.py"),
    ("T_V1_LIVE_VERDICTS", "python3 src/RimMandrake/Graffiti/selftest_graffiti_v1_live.py"),
    ("T_PLAY_ZOOM", "python3 src/RimMandrake/Graffiti/selftest_graffiti_play_zoom.py"),
    ("T_SPREE_SURPRISE", "python3 src/RimMandrake/Graffiti/selftest_graffiti_spree_surprise.py"),
    ("T_FULL_LIST_MODE", "python3 src/RimMandrake/Graffiti/selftest_full_list_mode.py"),
    ("T_FRESH_QT", "python3 src/RimMandrake/Graffiti/selftest_graffiti_fresh_quicktest.py"),
]
LINT = ("T_LINT", "python3 src/RimMandrake/Utils/selftest_graffiti_lint.py")
LINT_FILES = ("RM_GraffitiMod.cs", "northstar_site.py", "validation.py")
ENV = dict(os.environ); ENV.setdefault("WINBUILD_ROOT", "/mnt/d/ClaudeWork/rimmandrake/scratch/graffiti_blind_c2_mut/")
ENV["LANE1_STAGE"] = "/mnt/d/ClaudeWork/rimmandrake/scratch/graffiti_blind_c2_mut_lane1"
_restore = {}


def restore(*_):
    for path, data in _restore.items():
        with open(path, "wb") as f:
            f.write(data)
    _restore.clear()


def on_signal(sig, _frame):
    restore()
    sys.exit(128 + sig)


for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, on_signal)


def last(txt):
    ls = [l for l in (txt or "").splitlines() if l.strip()]
    return ls[-1].strip()[:240] if ls else ""


def run_suites(lint):
    res = {}
    for name, cmd in SUITES + ([LINT] if lint else []):
        try:
            p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, timeout=300, env=ENV)
            res[name] = {"rc": p.returncode, "last": last(p.stdout) or last(p.stderr)}
        except subprocess.TimeoutExpired:
            res[name] = {"rc": -9, "last": "TIMEOUT 300 s"}
    rows_path = os.path.join("/tmp", "graffiti_c2_mut_lane1_%d.jsonl" % os.getpid())
    p = subprocess.run([sys.executable, LANE1, "--out", rows_path], cwd=REPO, capture_output=True, text=True, timeout=400, env=ENV)
    fails = []
    if os.path.exists(rows_path):
        fails = [json.loads(l)["id"] for l in open(rows_path) if l.strip() and json.loads(l)["verdict"] == "FAIL"]
        os.remove(rows_path)
    res["LANE1"] = {"rc": p.returncode, "fail_rows": fails, "last": last(p.stdout) or last(p.stderr)}
    return res


def baseline():
    rows = [json.loads(l) for l in open(OUT)] if os.path.exists(OUT) else []
    return next(r for r in rows if r.get("baseline"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", action="store_true"); ap.add_argument("--finish", action="store_true")
    ap.add_argument("--ids", default=""); ap.add_argument("--from", dest="lo", type=int, default=None); ap.add_argument("--to", dest="hi", type=int, default=None)
    a = ap.parse_args()
    faults = json.load(open(os.path.join(HERE, "planted_faults.json")))["faults"]
    if a.baseline:
        res = run_suites(lint=True)
        with open(OUT, "w") as f:
            f.write(json.dumps({"baseline": True, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "suites": res}) + "\n")
        print("BASELINE", {k: v["rc"] for k, v in res.items()}, "lane1 FAIL rows", res["LANE1"]["fail_rows"])
        return
    if a.finish:
        clean = subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/Graffiti"], cwd=REPO).returncode == 0
        with open(OUT, "a") as f:
            f.write(json.dumps({"tree_clean_after": clean}) + "\n")
        print("tree_clean_after", clean)
        sys.exit(0 if clean else 1)
    base = baseline()["suites"]
    pick = [f for i, f in enumerate(faults) if (a.ids and f["id"] in a.ids.split(",")) or
            (a.lo is not None and a.lo <= i <= (a.hi if a.hi is not None else len(faults)))]
    for fault in pick:
        path = os.path.join(REPO, fault["file"])
        data = open(path, "rb").read(); text = data.decode("utf-8")
        n = text.count(fault["old"])
        if n != 1:
            row = {"fault": fault["id"], "planted": False, "why": "anchor occurs %d times" % n}
        else:
            _restore[path] = data
            try:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(text.replace(fault["old"], fault["new"]))
                res = run_suites(lint=fault["file"].endswith(LINT_FILES))
            finally:
                restore()
            red = [k for k, v in res.items() if k != "LANE1" and v["rc"] != 0 and base.get(k, {}).get("rc") == 0]
            new_rows = [r for r in res["LANE1"]["fail_rows"] if r not in base["LANE1"]["fail_rows"]]
            row = {"fault": fault["id"], "file": fault["file"], "bars": fault["bars"], "planted": True,
                   "caught": bool(red or new_rows), "red_suites": red, "lane1_new_fail_rows": new_rows,
                   "lasts": {k: res[k]["last"] for k in red}}
        with open(OUT, "a") as f:
            f.write(json.dumps(row) + "\n")
        print(row["fault"], "CAUGHT" if row.get("caught") else ("SURVIVED" if row.get("planted") else "NOT PLANTED"),
              row.get("red_suites", ""), row.get("lane1_new_fail_rows", ""), flush=True)
    sys.exit(0 if subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/Graffiti"], cwd=REPO).returncode == 0 else 3)


main()
