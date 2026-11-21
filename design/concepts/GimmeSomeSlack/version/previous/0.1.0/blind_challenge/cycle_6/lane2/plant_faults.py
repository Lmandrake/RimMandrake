#!/usr/bin/env python3
"""Plant each fault of planted_faults.json in turn, run its suites, restore byte for byte, prove the tree clean.
    python3 plant_faults.py --baseline                 every suite on the clean tree; starts planted_results.jsonl afresh
    python3 plant_faults.py --only ID[,ID...]          those faults; appends one row each
    python3 plant_faults.py --finish                   appends {"tree_clean_after": ...} (git diff --quiet over the planted paths)
A fault is CAUGHT by a suite only when the suite prints a failing line (FAIL / UNMEASURED / REFUSED / MISSING / error CS)
that its baseline did not; a non-zero rc alone is recorded as rc_only, never as caught. A fault whose old text is no longer
found is NOT_APPLIED. A fault with "encoding": "latin-1" or "utf-16-le" is planted in a binary file (the DLL), its old and
new texts encoded so and of equal length. Restores on SIGTERM, SIGINT and SIGHUP. Set WINBUILD_ROOT to a private folder before running."""
import argparse, json, os, re, shutil, signal, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
FAULTS = json.load(open(os.path.join(HERE, "planted_faults.json")))
OUT = os.path.join(HERE, "planted_results.jsonl")
LANE1_OUT = "/tmp/gss_c6_lane1_planted.jsonl"
SUITES = {
    "NOHOSE": "python3 src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_hose.py",
    "LANE1": "python3 design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_6/lane1/run_lane1.py --out " + LANE1_OUT,
    "CORE": "python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py",
    "BITES": "python3 src/RimMandrake/Utils/selftest_gss_shock_still_bites_binding.py",
    "SETTINGS": "python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_settings_sweep.py",
}
BAD = re.compile(r"\b(FAIL|FAILED|UNMEASURED|REFUSED|REFUSE|MISSING)\b|error CS\d+")
TIMINGS = re.compile(r"\d+(\.\d+)?\s?(ms|s)\b|\d+\.\d+")
state = {"fault": None, "orig": None}


def restore(*_):
    f = state["fault"]
    if f is not None:
        p = os.path.join(REPO, f["file"])
        if state["orig"] is None:
            if os.path.exists(p):
                os.remove(p)
            d = os.path.dirname(p)
            while d != REPO and os.path.isdir(d) and not os.listdir(d):
                os.rmdir(d); d = os.path.dirname(d)
        else:
            open(p, "wb").write(state["orig"])
        state["fault"] = None
    if _:
        sys.exit(130)


for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, restore)


def run_suite(name):
    try:
        p = subprocess.run(SUITES[name], shell=True, cwd=REPO, capture_output=True, text=True, timeout=500, errors="replace")
        rc, txt = p.returncode, p.stdout + "\n" + p.stderr
    except subprocess.TimeoutExpired:
        rc, txt = -9, "TIMEOUT"
    if name == "LANE1":
        bad = set()
        if os.path.exists(LANE1_OUT):
            for l in open(LANE1_OUT):
                r = json.loads(l)
                if r["verdict"] == "FAIL":
                    bad.add("FAIL " + r["id"])
            os.remove(LANE1_OUT)
        if "BUILD FAILED" in txt:
            bad.add("BUILD FAILED")
    else:
        bad = set(TIMINGS.sub("#", l.strip())[:240] for l in txt.splitlines() if BAD.search(l) and not l.lstrip().startswith("WARN"))
    return rc, bad


def baseline_of():
    b = {}
    for l in open(OUT):
        r = json.loads(l)
        if r.get("baseline"):
            for k, v in r["suites"].items():
                b[k] = (v["rc"], set(v["failing"]))
    return b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", action="store_true"); ap.add_argument("--only", default=""); ap.add_argument("--finish", action="store_true")
    a = ap.parse_args()
    if a.baseline:
        res = {}
        for name in SUITES:
            rc, bad = run_suite(name)
            res[name] = {"rc": rc, "failing": sorted(bad)}
            print("BASE", name, rc, len(bad), flush=True)
        with open(OUT, "w") as f:
            f.write(json.dumps({"baseline": True, "suites": res}) + "\n")
        return
    if a.finish:
        paths = sorted(set(f["file"] for f in FAULTS))
        left = [f["file"] for f in FAULTS if f["old"] is None and os.path.exists(os.path.join(REPO, f["file"]))]
        q = subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/GimmeSomeSlack"] + [p for p in paths if not p.startswith("src/RimMandrake/GimmeSomeSlack")], cwd=REPO)
        clean = q.returncode == 0 and not left
        with open(OUT, "a") as f:
            f.write(json.dumps({"tree_clean_after": clean}) + "\n")
        print("tree_clean_after", clean, left)
        sys.exit(0 if clean else 1)
    base = baseline_of()
    only = set(filter(None, a.only.split(",")))
    for f in FAULTS:
        if f["id"] not in only:
            continue
        p = os.path.join(REPO, f["file"])
        row = {"id": f["id"], "file": f["file"], "bars": f["bars"], "suites": {}}
        if f["old"] is None:
            if os.path.exists(p):
                row["status"] = "NOT_APPLIED (file exists)"
            else:
                state["fault"], state["orig"] = f, None
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, "w", encoding="utf-8").write(f["new"])
        else:
            orig = open(p, "rb").read()
            enc = f.get("encoding", "utf-8")
            if enc == "utf-8":
                t = orig.decode("utf-8")
                n = t.count(f["old"])
                planted = t.replace(f["old"], f["new"]).encode("utf-8") if n == 1 else None
            else:
                ob, nb = f["old"].encode(enc), f["new"].encode(enc)
                n = orig.count(ob) if len(ob) == len(nb) else -1
                planted = orig.replace(ob, nb) if n == 1 else None
            if planted is None:
                row["status"] = "NOT_APPLIED (old text found %d times)" % n
            else:
                state["fault"], state["orig"] = f, orig
                open(p, "wb").write(planted)
        if "status" not in row:
            try:
                for name in f["suites"]:
                    rc, bad = run_suite(name)
                    brc, bbad = base.get(name, (0, set()))
                    new = sorted(bad - bbad)
                    row["suites"][name] = {"rc": rc, "new_failing": new[:8],
                                           "verdict": "caught" if new else ("rc_only" if rc != brc else "missed")}
            finally:
                restore()
            row["caught_by"] = [n for n, v in row["suites"].items() if v["verdict"] == "caught"]
            row["status"] = "CAUGHT" if row["caught_by"] else "MISSED"
        row["caught"] = row.get("status") == "CAUGHT"   # the top-level flag maturation.py next reads
        with open(OUT, "a") as o:
            o.write(json.dumps(row) + "\n")
        print(row["id"], row["status"], row.get("caught_by"), {k: v["verdict"] for k, v in row["suites"].items()}, flush=True)


main()
