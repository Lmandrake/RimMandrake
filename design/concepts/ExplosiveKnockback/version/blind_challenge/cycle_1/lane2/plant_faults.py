#!/usr/bin/env python3
"""Plant each fault of planted_faults.json in turn, run the builder's offline deciders (and blind lane 1 for kernel
faults), restore the file byte for byte, and record who caught it.
    python3 plant_faults.py [--only PF_A,PF_B] [--out planted_results.jsonl]
Builds stage under WINBUILD_ROOT=<agent storage>/scratch/ek_blind_mut so a planted fault never reaches the shared
D:\\ClaudeWork\\rimmandrake\\build staging other clones use. Ends by proving the mod tree equals HEAD (git diff --quiet)."""
import argparse, hashlib, json, os, signal, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
SRC = os.path.join(REPO, "src/RimMandrake/ExplosiveKnockback/Source")
SUITES = {
    "T_KERNEL": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_kernel.py",
    "T_FUZZ": "python3 src/RimMandrake/Utils/selftest_explosiveknockback_fuzz.py",
    "T_SETTINGS_SWEEP_OFFLINE": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_settings_sweep.py",
    "T_GAS_CLUMP_ORDER": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_gas_clumps.py",
    "T_CENSUS": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_storage_census.py",
    "T_ONLY_EXPLOSIONS_STATIC": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_hook_scope.py",
    "T_LINT": "python3 src/RimMandrake/Utils/lint_explosiveknockback_defs.py",
    "T_GAS_TAG_CENSUS": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_gas_census.py",
}
LANE1_OUT = "/tmp/ek_blind_lane1_mut.jsonl"
LANE1 = "python3 " + os.path.join(HERE, "..", "lane1", "run_lane1.py") + " --out " + LANE1_OUT
def lane1_fails():
    return sorted(json.loads(l)["id"] for l in open(LANE1_OUT) if json.loads(l)["verdict"] == "FAIL")
PLANTED = {}  # path -> original bytes while a fault is in; restored on SIGTERM/SIGINT too
def _restore(*_):
    for p, b in PLANTED.items(): open(p, "wb").write(b)
    sys.exit(3)
signal.signal(signal.SIGTERM, _restore); signal.signal(signal.SIGINT, _restore); signal.signal(signal.SIGHUP, _restore)
def run(cmd, env):
    t = time.time(); p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, env=env, timeout=900)
    tail = [l for l in (p.stdout + p.stderr).splitlines() if l.strip()]
    return p.returncode, round(time.time() - t, 1), (tail[-1] if tail else "")[:240]
ap = argparse.ArgumentParser(); ap.add_argument("--only", default=""); ap.add_argument("--out", default=os.path.join(HERE, "planted_results.jsonl"))
a = ap.parse_args(); only = set(filter(None, a.only.split(",")))
root = subprocess.run(["python3", os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")], capture_output=True, text=True, check=True).stdout.strip()
env = dict(os.environ, WINBUILD_ROOT=os.path.join(root, "scratch", "ek_blind_mut")); os.makedirs(env["WINBUILD_ROOT"], exist_ok=True)
faults = [f for f in json.load(open(os.path.join(HERE, "planted_faults.json"))) if not only or f["id"] in only]
# baseline: every suite must be green (or its known red state) on the clean tree, or a "caught" means nothing
base = {k: run(c, env)[0] for k, c in SUITES.items()}; base["LANE1"] = run(LANE1, env)[0]; base_l1 = lane1_fails(); base["LANE1_FAILS"] = base_l1
print("BASELINE", json.dumps(base), flush=True)
out = open(a.out, "w"); out.write(json.dumps({"baseline": base}) + "\n")
for f in faults:
    path = os.path.normpath(os.path.join(SRC, f["file"])); orig = open(path, "rb").read(); text = orig.decode()
    n = text.count(f["old"])
    row = {"id": f["id"], "file": os.path.relpath(path, REPO), "bars": f["bars"]}
    if n != 1:
        row.update(planted=False, why="old text found %d times" % n); out.write(json.dumps(row) + "\n"); out.flush(); print("SKIP", f["id"], n, flush=True); continue
    try:
        PLANTED[path] = orig; open(path, "wb").write(text.replace(f["old"], f["new"]).encode())
        res = {}
        for k, c in SUITES.items():
            rc, sec, last = run(c, env); res[k] = {"rc": rc, "caught": rc != 0 and base[k] == 0, "s": sec, "last": last}
        if f["file"] == "RM_KnockbackMath.cs":
            rc, sec, last = run(LANE1, env); new = [x for x in lane1_fails() if x not in base_l1]; det = {json.loads(l)["id"]: json.loads(l)["detail"][:400] for l in open(LANE1_OUT)}
            res["LANE1"] = {"rc": rc, "caught": bool(new), "new_fails": new, "new_detail": [det[x] for x in new], "s": sec, "last": last}
    finally:
        open(path, "wb").write(orig); PLANTED.pop(path, None)
    assert hashlib.sha256(open(path, "rb").read()).digest() == hashlib.sha256(orig).digest()
    builder = [k for k, v in res.items() if k != "LANE1" and v["caught"]]
    row.update(planted=True, results=res, caught_by_builder=builder, caught_by_lane1=res.get("LANE1", {}).get("caught"))
    out.write(json.dumps(row) + "\n"); out.flush()
    print(f["id"], "builder:", ",".join(builder) or "MISSED", "| lane1:", row["caught_by_lane1"], flush=True)
clean = subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/ExplosiveKnockback"], cwd=REPO).returncode == 0
out.write(json.dumps({"tree_clean_after": clean}) + "\n"); print("TREE CLEAN AFTER:", clean)
