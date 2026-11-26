#!/usr/bin/env python3
"""Plant each fault of planted_faults.json in turn, run the offline deciders and blind lane 1, restore byte for byte.
    WINBUILD_ROOT=<private> python3 plant_faults.py [--only ID,ID] [--baseline]
Results go to planted_results.jsonl, kept in order: the baseline first, one row per fault, `tree_clean_after` last (a run with
--only merges into the rows already there, so the record can be built in chunks under a 540 s command limit). "Caught" = a
suite red that is green on the baseline, or a lane-1 row FAIL that is not FAIL on the baseline; never an rc alone.
Restores on SIGTERM, SIGINT and SIGHUP, and ends by proving `git diff --quiet` on the planted files' trees."""
import argparse, json, os, re, signal, subprocess, sys, threading

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
FAULTS = os.path.join(HERE, "planted_faults.json")
OUT = os.path.join(HERE, "planted_results.jsonl")
LANE1 = os.path.join(HERE, "..", "lane1", "run_lane1.py")
TABLE = os.path.join(REPO, "design/concepts/Pyrelands/version/test_table.json")
DECIDERS = ["T_ASH_PROBE_OFFLINE", "T_DEFS_OFFLINE", "T_CUT_STAYS_CUT", "T_SETTINGS_SWEEP_OFFLINE", "T_SETTINGS_SCREENS", "T_SITE", "T_FUZZ"]
TREES = ["src/RimMandrake/Pyrelands", "src/RimUtinni/UtinniPatches"]
_orig = {}


def restore(*_):
    for p, b in _orig.items():
        with open(p, "wb") as f:
            f.write(b)
    _orig.clear()


def on_signal(sig, _):
    restore()
    sys.exit(128 + sig)


def verdict(tid, rc, out):
    if tid == "T_SETTINGS_SCREENS":
        mine = [l for l in out.splitlines() if re.match(r"^\S+\s+Pyrelands:", l)]
        return "PASS" if mine and all(l.startswith("ok ") for l in mine) else "FAIL"
    return "PASS" if rc == 0 else "FAIL"


def deciders(cmds, res):
    for tid in DECIDERS:
        try:
            p = subprocess.run(cmds[tid], shell=True, cwd=REPO, capture_output=True, text=True, timeout=300)
            res[tid] = verdict(tid, p.returncode, p.stdout + p.stderr)
        except subprocess.TimeoutExpired:
            res[tid] = "FAIL"


def lane1(res):
    tmp = "/tmp/pyre_plant_lane1.jsonl"
    subprocess.run(["python3", LANE1, "--out", tmp], cwd=REPO, capture_output=True, text=True, timeout=400)
    try:
        res["lane1_fail"] = sorted(json.loads(l)["id"] for l in open(tmp) if json.loads(l)["verdict"] == "FAIL")
    except OSError:
        res["lane1_fail"] = ["<no rows>"]


def run_all(cmds):
    res = {}
    t = threading.Thread(target=lane1, args=(res,))
    t.start()
    deciders(cmds, res)
    t.join()
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--baseline", action="store_true")
    a = ap.parse_args()
    for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(s, on_signal)
    cmds = {k: v["command"] for k, v in json.load(open(TABLE))["tests"].items() if "command" in v}
    faults = json.load(open(FAULTS))
    only = set(filter(None, a.only.split(",")))
    rows = {}
    if os.path.exists(OUT):
        for l in open(OUT):
            r = json.loads(l)
            rows[r["id"]] = r
    if a.baseline or "baseline" not in rows:
        b = run_all(cmds)
        rows["baseline"] = {"id": "baseline", "suites": {k: v for k, v in b.items() if k != "lane1_fail"}, "lane1_fail": b["lane1_fail"]}
    base = rows["baseline"]
    for f in faults:
        if only and f["id"] not in only:
            continue
        p = os.path.join(REPO, f["file"])
        raw = open(p, "rb").read()
        txt = raw.decode("utf-8")
        if txt.count(f["old"]) != 1:
            rows[f["id"]] = {"id": f["id"], "bars": f["bars"], "error": "old text occurs %d times" % txt.count(f["old"])}
            continue
        _orig[p] = raw
        try:
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write(txt.replace(f["old"], f["new"]))
            r = run_all(cmds)
        finally:
            restore()
        red = [k for k in DECIDERS if r.get(k) == "FAIL" and base["suites"].get(k) == "PASS"]
        new1 = [x for x in r["lane1_fail"] if x not in base["lane1_fail"]]
        rows[f["id"]] = {"id": f["id"], "file": f["file"], "bars": f["bars"], "suites_red": red, "lane1_new_fail": new1,
                         "caught": bool(red or new1), "caught_by_deciders": bool(red), "caught_by_lane1": bool(new1)}
    clean = subprocess.run(["git", "diff", "--quiet", "--"] + TREES, cwd=REPO).returncode == 0
    rows["tree_clean_after"] = {"id": "tree_clean_after", "tree_clean_after": clean}
    order = ["baseline"] + [f["id"] for f in faults if f["id"] in rows] + ["tree_clean_after"]
    with open(OUT, "w") as fh:
        for k in order:
            fh.write(json.dumps(rows[k]) + "\n")
    done = [rows[f["id"]] for f in faults if f["id"] in rows and "caught" in rows[f["id"]]]
    print("PLANTED %d/%d caught (deciders %d, lane1 %d); tree clean: %s" % (sum(r["caught"] for r in done), len(done),
          sum(r["caught_by_deciders"] for r in done), sum(r["caught_by_lane1"] for r in done), clean))
    for r in done:
        if not r["caught"]:
            print("MISSED", r["id"])
    sys.exit(0 if clean else 2)


main()
