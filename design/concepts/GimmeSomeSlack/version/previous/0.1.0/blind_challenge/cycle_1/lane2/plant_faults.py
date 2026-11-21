#!/usr/bin/env python3
"""Plant each fault of planted_faults.json in turn, run its suites, restore the file byte for byte, and prove the tree clean.
    python3 plant_faults.py [--ids A,B] [--baseline] [--finish] [--out planted_results.jsonl]
Suites: core = selftest_gimmesomeslack.py --geometry (T_CORE's checks plus T_CORD_GEOMETRY_OFFLINE's), lane1 = this cycle's
blind lane 1, binding = the three shock binding tests, settings = T_SETTINGS_SWEEP_OFFLINE, nohose = T_NO_HOSE.
WINBUILD_ROOT is a private folder (never the shared build staging); lane 1 stages in its own folder too. A fault is CAUGHT
only when a suite shows a NEW failing row against the baseline (a FAIL line, a lane-1 FAIL row, or a short 'N/M checks
passed'), never on a bare non-zero rc. Results append to the out file, so a run can be split across calls; --baseline
writes the baseline row first, --finish appends tree_clean_after. Restores on SIGTERM, SIGINT and SIGHUP."""
import argparse, json, os, re, signal, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MUT = "/mnt/d/ClaudeWork/rimmandrake/scratch/gss_blind_mut"
SUITES = {
    "core": ["python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py --geometry"],
    "lane1": ["python3 %s --stage %s/lane1 --out %s/lane1_rows.jsonl" % (os.path.join(HERE, "..", "lane1", "run_lane1.py"), MUT, MUT)],
    "binding": ["python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_shock_outlives_wire.py",
                "python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_shock_outlives_wire_binding.py",
                "python3 src/RimMandrake/Utils/selftest_gss_shock_still_bites_binding.py"],
    "settings": ["python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_settings_sweep.py"],
    "nohose": ["python3 src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_hose.py"],
    "dropcord": ["python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_dropped_cords_ignore_aerial_master.py"],
}
planted = {}   # path -> original bytes (None = the file did not exist)

def restore(*_):
    for p, b in list(planted.items()):
        if b is None:
            if os.path.exists(p): os.remove(p)
            d = os.path.dirname(p)
            while d.startswith(os.path.join(REPO, "src")) and os.path.isdir(d) and not os.listdir(d): os.rmdir(d); d = os.path.dirname(d)
        else:
            open(p, "wb").write(b)
        planted.pop(p, None)
    if _: sys.exit(3)
for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP): signal.signal(s, restore)

def fails_of(suite, out):
    """The failing rows a suite printed, as a set of strings."""
    if suite == "lane1":
        p = os.path.join(MUT, "lane1_rows.jsonl")
        rows = [json.loads(l) for l in open(p)] if os.path.exists(p) else []
        return {r["id"] for r in rows if r["verdict"] == "FAIL"} | ({"lane1:BUILD_OR_RUN_FAILED"} if "BUILD FAILED" in out or "RUN FAILED" in out else set())
    s = set()
    for l in out.splitlines():
        t = re.sub(r"\d+(\.\d+)?\s?(ms|s)\b", "<t>", l.strip())
        if re.search(r"\bFAIL|\bFAILED\b|error CS\d+|Build FAILED|Traceback", t): s.add(t[:200])
        m = re.search(r"(\d+)/(\d+) checks passed", t)
        if m and m.group(1) != m.group(2): s.add("short: " + t[:120])
    return s

def run_suites(names):
    env = dict(os.environ, WINBUILD_ROOT=MUT)
    res = {}
    for n in names:
        outs, rcs = "", []
        for cmd in SUITES[n]:
            os.makedirs(MUT, exist_ok=True)
            if n == "lane1" and os.path.exists(os.path.join(MUT, "lane1_rows.jsonl")): os.remove(os.path.join(MUT, "lane1_rows.jsonl"))
            try: p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, timeout=400, env=env); rc, o = p.returncode, p.stdout + "\n" + p.stderr
            except subprocess.TimeoutExpired as e: rc, o = 124, "TIMEOUT " + cmd
            rcs.append(rc); outs += o
        res[n] = {"rc": max(rcs), "fails": sorted(fails_of(n, outs))}
    return res

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ids", default=""); ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--finish", action="store_true"); ap.add_argument("--suites", default=""); ap.add_argument("--out", default=os.path.join(HERE, "planted_results.jsonl"))
    a = ap.parse_args()
    faults = json.load(open(os.path.join(HERE, "planted_faults.json")))
    base_p = os.path.join(HERE, ".baseline.json")
    if a.baseline:
        b = run_suites([s for s in SUITES if not a.suites or s in a.suites.split(",")]); json.dump(b, open(base_p, "w"))
        with open(a.out, "w") as f: f.write(json.dumps({"id": "baseline", "suites": b}) + "\n")
        print("BASELINE", {k: (v["rc"], len(v["fails"])) for k, v in b.items()})
    base = json.load(open(base_p))
    ids = [i for i in a.ids.split(",") if i]
    for ft in faults:
        if ids and ft["id"] not in ids: continue
        p = os.path.join(REPO, ft["file"]); t0 = time.time()
        orig = open(p, "rb").read() if os.path.exists(p) else None
        planted[p] = orig
        if ft["old"] is None:
            os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "wb").write(b"\x89PNG\r\n\x1a\n" if ft["new"] == "PNG" else ft["new"].encode())
            applied = True
        else:
            txt = orig.decode("utf-8"); applied = txt.count(ft["old"]) == 1
            if applied: open(p, "wb").write(txt.replace(ft["old"], ft["new"]).encode("utf-8"))
        try:
            r = run_suites(ft["suites"]) if applied else {}
        finally:
            restore()
        assert (open(p, "rb").read() if os.path.exists(p) else None) == orig, "restore failed for " + p
        new = {n: sorted(set(v["fails"]) - set(base[n]["fails"])) for n, v in r.items()}
        caught_by = [n for n, v in new.items() if v]
        row = {"id": ft["id"], "file": ft["file"], "bars": ft["bars"], "applied": applied, "suites": {n: {"rc": r[n]["rc"], "new_fails": new[n][:6]} for n in r},
               "caught": bool(caught_by), "caught_by": caught_by, "rc_only": [n for n in r if r[n]["rc"] != base[n]["rc"] and not new[n]], "seconds": round(time.time() - t0, 1)}
        with open(a.out, "a") as f: f.write(json.dumps(row) + "\n")
        print(("CAUGHT " if row["caught"] else "MISSED ") + ft["id"], caught_by, row["rc_only"], row["seconds"], "s", flush=True)
    if a.finish:
        clean = subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/GimmeSomeSlack", "src/RimMandrake/_Shared"], cwd=REPO).returncode == 0
        untracked = subprocess.run(["git", "status", "--porcelain", "--", "src/RimMandrake/GimmeSomeSlack", "src/RimMandrake/_Shared"], cwd=REPO, capture_output=True, text=True).stdout.strip()
        with open(a.out, "a") as f: f.write(json.dumps({"id": "tree_clean_after", "tree_clean_after": clean and not untracked, "git_diff_quiet": clean, "untracked": untracked}) + "\n")
        print("TREE CLEAN", clean and not untracked, untracked)
main()
