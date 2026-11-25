"""ExplosiveKnockback 0.2.0, blind cycle 1 (copied from Pyrelands cycle 2). Plant each fault of planted_faults.json in turn, run the deciders and lane 1, restore byte for byte.
    python3 plant_faults.py --baseline                  write the clean baseline row (truncates planted_results.jsonl)
    python3 plant_faults.py --ids A,B,C | --from N --to M  plant those faults, append one row each
    python3 plant_faults.py --finish                    prove the tree clean and append {"tree_clean_after": ...}
WINBUILD_ROOT and the lane-1 stage default to /mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c1_mut/ (private, so the
builder's machine-wide staging is never touched). A fault is CAUGHT only by a NEW failing row (a decider PASS in the baseline
that fails, or a lane-1 row id that was not FAIL in the baseline), never by a non-zero rc alone. The planted file is restored
on SIGTERM, SIGINT and SIGHUP too."""
import argparse, json, os, shlex, signal, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
OUT = os.path.join(HERE, "planted_results.jsonl")
MUT = "/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c1_mut"
LANE1 = os.path.join(HERE, "..", "lane1", "run_lane1.py")
TABLE = os.path.join(REPO, "design/concepts/ExplosiveKnockback/version/test_table.json")
# the deciders of both offline bars (inv_kernel: T_KERNEL T_FUZZ; inv_proof_scenes: T_SCRIPT T_PROOFGATE T_RESTORE), then the
# fast offline supports that read the planted files; the 315 s situation map only for a fault marked slow (planner, flyer)
ALWAYS = ["T_KERNEL", "T_FUZZ", "T_SCRIPT", "T_PROOFGATE", "T_RESTORE", "T_LINT", "T_SETTINGS_SWEEP_OFFLINE", "T_SETTINGS_SCREEN",
          "T_CARRY_STATIC", "T_STAGE3_SCENES", "T_GAS_CLUMP_ORDER", "T_LANDING_JOB_SEARCH_OFFLINE", "T_BLAST_SHOW_OFFLINE",
          "T_SETTINGS_SWEEP_SHOW", "T_SAVE_IN_AIR_OFFLINE", "T_ONLY_EXPLOSIONS_STATIC"]
SLOW = ["T_SITUATION_MAP_OFFLINE"]
ENV = dict(os.environ, WINBUILD_ROOT=MUT, EK_LANE1_STAGE=os.path.join(MUT, "lane1"))
ENV["WSLENV"] = ":".join(filter(None, [os.environ.get("WSLENV", ""), "WINBUILD_ROOT/p"]))
_restore = {}


def restore(*_):
    for path, data in list(_restore.items()):
        with open(path, "wb") as f:
            f.write(data)
        _restore.pop(path, None)
    if _:
        sys.exit(130)


for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, restore)


def run(cmd):
    try:
        r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=530, env=ENV)  # a hang guard: the slowest suite measured 315 s
        rc, txt = r.returncode, (r.stdout + r.stderr)
    except subprocess.TimeoutExpired:
        rc, txt = 124, "TIMEOUT"
    lines = [l for l in txt.splitlines() if l.strip()]
    return rc, (lines[-1] if lines else "")[:200]


def suites(slow):
    tests = json.load(open(TABLE))["tests"]
    return {n: tests[n]["command"] for n in ALWAYS + (SLOW if slow else [])}


def run_all(slow):
    res = {}
    for name, cmd in suites(slow).items():
        rc, last = run(shlex.split(cmd))
        res[name] = {"rc": rc, "last": last}
    tmp = os.path.join(MUT, "lane1_rows_%d.jsonl" % os.getpid())
    rc, last = run(["python3", LANE1, "--out", tmp])
    rows = [json.loads(l) for l in open(tmp)] if os.path.exists(tmp) else []
    res["LANE1"] = {"rc": rc, "last": last, "fail_ids": sorted(r["id"] for r in rows if r["verdict"] == "FAIL"), "rows": len(rows)}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--finish", action="store_true")
    ap.add_argument("--ids", default="")
    ap.add_argument("--from", dest="lo", type=int, default=0)
    ap.add_argument("--to", dest="hi", type=int, default=0)
    a = ap.parse_args()
    os.makedirs(MUT, exist_ok=True)
    if a.baseline:
        t0 = time.time()
        res = run_all(True)
        with open(OUT, "w") as f:
            f.write(json.dumps({"baseline": True, "suites": res, "seconds": round(time.time() - t0, 1)}) + "\n")
        print("BASELINE", {k: v["rc"] for k, v in res.items()}, res["LANE1"]["fail_ids"])
        return
    if a.finish:
        clean = subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/ExplosiveKnockback"], cwd=REPO).returncode == 0
        with open(OUT, "a") as f:
            f.write(json.dumps({"tree_clean_after": clean}) + "\n")
        print("tree_clean_after", clean)
        sys.exit(0 if clean else 1)
    base = json.loads(open(OUT).readline())["suites"]
    faults = json.load(open(os.path.join(HERE, "planted_faults.json")))
    pick = set(filter(None, a.ids.split(",")))
    todo = [f for i, f in enumerate(faults) if (f["id"] in pick) or (not pick and a.lo <= i < (a.hi or len(faults)))]
    for f in todo:
        path = os.path.join(REPO, f["file"])
        data = open(path, "rb").read()
        text = data.decode("utf-8")
        if text.count(f["old"]) != 1:
            row = {"id": f["id"], "error": "old text found %d times" % text.count(f["old"])}
        else:
            _restore[path] = data
            t0 = time.time()
            try:
                with open(path, "w", encoding="utf-8", newline="") as g:
                    g.write(text.replace(f["old"], f["new"], 1))
                res = run_all(bool(f.get("slow")))
            finally:
                restore()
            red = [n for n, v in res.items() if n != "LANE1" and v["rc"] != 0 and base.get(n, {}).get("rc") == 0]
            deciders = {"inv_kernel": ["T_KERNEL", "T_FUZZ"], "inv_proof_scenes": ["T_SCRIPT", "T_PROOFGATE", "T_RESTORE"]}
            new_l1 = [i for i in res["LANE1"]["fail_ids"] if i not in base["LANE1"]["fail_ids"]]
            row = {"id": f["id"], "file": f["file"], "bars": f["bars"], "deciders_red": red, "lane1_new_fail": new_l1,
                   "caught": bool(red or new_l1), "offline_deciders_red": sorted(n for b in f["bars"] for n in deciders.get(b, []) if n in red), "lasts": {n: res[n]["last"] for n in red}, "seconds": round(time.time() - t0, 1)}
        with open(OUT, "a") as g:
            g.write(json.dumps(row) + "\n")
        print(("CAUGHT " if row.get("caught") else "MISSED ") + f["id"], row.get("deciders_red"), row.get("lane1_new_fail"), row.get("error", ""), flush=True)
    clean = subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/ExplosiveKnockback"], cwd=REPO).returncode == 0
    print("tree clean:", clean)


main()
