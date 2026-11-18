#!/usr/bin/env python3
"""Plant each fault of planted_faults.json in turn, run the offline suites and blind lane 1, restore the file byte for byte.
    WINBUILD_ROOT=/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c5_mut/ python3 plant_faults.py [--ids A,B] [--baseline] [--finish]
--baseline writes the baseline row (a fresh results file); --ids runs those faults and appends; --finish appends the
tree-clean row (git diff --quiet -- src/RimMandrake/ExplosiveKnockback). --faults and --out name another fault list and
results file (default planted_faults.json, planted_results.jsonl), so a re-planted list never overwrites this cycle's record. A fault is CAUGHT only when it makes a new failing
row: a suite that was PASS at baseline goes FAIL, or a lane-1 row id that was not FAIL at baseline goes FAIL. Restores on
SIGTERM, SIGINT and SIGHUP."""
import argparse, json, os, signal, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
OUT = os.path.join(HERE, "planted_results.jsonl")
LANE1 = os.path.join(HERE, "..", "lane1", "run_lane1.py")
SUITES = {
    "T_KERNEL": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_kernel.py",
    "T_FUZZ": "python3 src/RimMandrake/Utils/selftest_explosiveknockback_fuzz.py",
    "T_SCRIPT": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_script.py",
    "T_PROOFGATE": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_proofgate.py",
    "T_RESTORE": "python3 src/RimMandrake/Utils/selftest_proof_restore_check.py",
    "T_SETTINGS_SCREEN": "python3 src/RimMandrake/Utils/selftest_settings_screens.py",
    "T_SETTINGS_SWEEP_OFFLINE": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_settings_sweep.py",
    "T_STAGE3_SCENES": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_stage3_scenes.py",
    "T_GAS_CLUMP_ORDER": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_gas_clumps.py",
    "T_GAS_TAG_CENSUS": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_gas_census.py",
    "T_ONLY_EXPLOSIONS_STATIC": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_hook_scope.py",
    "T_CENSUS": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_storage_census.py",
    "T_LINT": "python3 src/RimMandrake/Utils/lint_explosiveknockback_defs.py",
}


def discover_suites(repo, listed):
    """The concept's selftests on disk (src/**/selftest_explosiveknockback*.py) that the hand list above does not name,
    as {T_AUTO_<stem>: command}. 'Survived every offline suite' must mean every suite that exists, not every suite
    someone remembered to list (RIMMANDRAKE_LIST_WALK_SUITE_IN_HARNESS_MUTANTS_SURVIVED)."""
    named = {c.split()[-1] for c in listed.values()}
    found = {}
    for root, _dirs, files in os.walk(os.path.join(repo, "src")):
        for fn in files:
            if fn.startswith("selftest_explosiveknockback") and fn.endswith(".py"):
                rel = os.path.relpath(os.path.join(root, fn), repo).replace(os.sep, "/")
                if rel not in named:
                    found["T_AUTO_" + fn[len("selftest_"):-3].upper()] = "python3 " + rel
    return dict(sorted(found.items()))


def verdict_of(returncode):
    """PASS (0), UNMEASURED (rc 2: a suite that could not run here, e.g. a Windows-only def dump: never 'ran and missed'),
    else FAIL."""
    return "PASS" if returncode == 0 else "UNMEASURED" if returncode == 2 else "FAIL"


current = {}


def restore(*_):
    for path, data in list(current.items()):
        with open(path, "wb") as f:
            f.write(data)
        current.pop(path, None)
    if _:
        sys.exit(130)


for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, restore)


def run_all(env):
    res = {}
    for k, cmd in {**SUITES, **discover_suites(REPO, SUITES)}.items():
        try:
            p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, timeout=200, env=env)
            res[k] = verdict_of(p.returncode)
        except subprocess.TimeoutExpired:
            res[k] = "FAIL"
    tmp = "/tmp/ek_c5_lane1_planted.jsonl"
    p = subprocess.run([sys.executable, LANE1, "--out", tmp], cwd=REPO, capture_output=True, text=True, timeout=300, env=env)
    fails = []
    try:
        fails = sorted(json.loads(l)["id"] for l in open(tmp) if json.loads(l)["verdict"] == "FAIL")
    except OSError:
        fails = ["LANE1_NO_OUTPUT"]
    return res, fails


def baseline():
    for l in open(OUT):
        r = json.loads(l)
        if r.get("baseline"):
            return r
    sys.exit("no baseline row in " + OUT)


def main():
    global OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default="")
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--finish", action="store_true")
    ap.add_argument("--faults", default=os.path.join(HERE, "planted_faults.json"))
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    OUT = os.path.abspath(a.out)
    env = dict(os.environ)
    env.setdefault("WINBUILD_ROOT", "/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c5_mut/")
    if a.baseline:
        res, fails = run_all(env)
        with open(OUT, "w") as f:
            f.write(json.dumps({"baseline": True, "suites": res, "lane1_fail": fails}) + "\n")
        print("BASELINE", res, fails)
    faults = json.load(open(a.faults))
    want = [x for x in a.ids.split(",") if x]
    for fl in faults:
        if fl["id"] not in want:
            continue
        b = baseline()
        path = os.path.join(REPO, fl["file"])
        data = open(path, "rb").read()
        crlf = b"\r\n" in data
        old, new = fl["old"].encode(), fl["new"].encode()
        if crlf:
            old, new = old.replace(b"\n", b"\r\n"), new.replace(b"\n", b"\r\n")
        if data.count(old) != 1:
            row = {"id": fl["id"], "error": "old text occurs %d times" % data.count(old)}
        else:
            current[path] = data
            with open(path, "wb") as f:
                f.write(data.replace(old, new, 1))
            t0 = time.time()
            try:
                res, fails = run_all(env)
            finally:
                restore()
            new_suite = sorted(k for k, v in res.items() if v == "FAIL" and b["suites"].get(k) == "PASS")
            new_lane1 = sorted(set(fails) - set(b["lane1_fail"]))
            row = {"id": fl["id"], "file": fl["file"], "bars": fl["bars"], "suites_red": new_suite, "lane1_new_fail": new_lane1,
                   "caught": bool(new_suite or new_lane1), "caught_by_builder": bool(new_suite), "caught_by_lane1": bool(new_lane1),
                   "unconsulted": sorted(k for k in res if k not in b["suites"]),     # ran now, absent from the baseline: re-run --baseline
                   "unmeasured": sorted(k for k, v in res.items() if v == "UNMEASURED"),
                   "seconds": round(time.time() - t0, 1)}
            if row["unconsulted"] and not row["caught"]:
                row["survived_every_suite"] = False      # never "survived every offline suite" while a suite was not in the baseline
        with open(OUT, "a") as f:
            f.write(json.dumps(row) + "\n")
        print(json.dumps(row), flush=True)
    if a.finish:
        clean = subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/ExplosiveKnockback"], cwd=REPO).returncode == 0
        with open(OUT, "a") as f:
            f.write(json.dumps({"tree_clean_after": clean}) + "\n")
        print("tree_clean_after", clean)


if __name__ == "__main__":
    main()
