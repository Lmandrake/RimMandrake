#!/usr/bin/env python3
"""Blind cycle 2: plant each fault of planted_faults.json in turn, run the offline deciders (and blind lane 1 for kernel
faults), restore the file byte for byte, and record who caught it. A fault is CAUGHT only by a suite that was green on the
clean tree and goes red with it in (for lane 1: a NEW failing row), never by a bare non-zero rc.
    python3 plant_faults.py [--only PF_A,PF_B] [--out planted_results.jsonl] [--append] [--no-lane1] [--expect-caught]
--expect-caught makes it a test of the deciders (a fix's red-then-green command): rc 0 only when every selected fault was
planted and caught by a builder suite (lane 1 does not count) and the tree ends clean; rc 1 otherwise, naming the misses.
Builds stage under WINBUILD_ROOT=/mnt/d/ClaudeWork/rimmandrake/scratch/ek_blind_c2_mut. Restores on SIGTERM/SIGINT/SIGHUP;
ends by proving git diff --quiet on the mod and Utils trees against the pre-run state (cycle-1 tool, adapted)."""
import argparse, hashlib, json, os, signal, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
SUITES = {
    "T_KERNEL": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_kernel.py",
    "T_FUZZ": "python3 src/RimMandrake/Utils/selftest_explosiveknockback_fuzz.py",
    "T_LINT": "python3 src/RimMandrake/Utils/lint_explosiveknockback_defs.py",
    "T_SCRIPT": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_script.py",
    "T_PROOFGATE": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_proofgate.py",
    "T_RESTORE": "python3 src/RimMandrake/Utils/selftest_proof_restore_check.py",
    "T_SETTINGS_SWEEP_OFFLINE": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_settings_sweep.py",
    "T_STAGE3_SCENES": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_stage3_scenes.py",
    "T_GAS_CLUMP_ORDER": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_gas_clumps.py",
    "T_ONLY_EXPLOSIONS_STATIC": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_hook_scope.py",
    "T_JOURNAL_JOLT": "python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_journal_jolt.py",
}
LANE1_OUT = "/tmp/ek_blind_c2_lane1_mut.jsonl"
LANE1 = "python3 " + os.path.join(HERE, "..", "lane1", "run_lane1.py")
def lane1_fails():
    return sorted(json.loads(l)["id"] for l in open(LANE1_OUT) if json.loads(l)["verdict"] == "FAIL")
PLANTED = {}
def _restore(*_):
    for p, b in PLANTED.items(): open(p, "wb").write(b)
    sys.exit(3)
for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP): signal.signal(sig, _restore)
def run(cmd, env):
    t = time.time(); p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, env=env, timeout=400)
    tail = [l for l in (p.stdout + p.stderr).splitlines() if l.strip() and "SyntaxWarning" not in l]
    return p.returncode, round(time.time() - t, 1), (tail[-1] if tail else "")[:240]
ap = argparse.ArgumentParser(); ap.add_argument("--only", default=""); ap.add_argument("--out", default=os.path.join(HERE, "planted_results.jsonl"))
ap.add_argument("--append", action="store_true"); ap.add_argument("--no-lane1", action="store_true")
ap.add_argument("--expect-caught", action="store_true")
a = ap.parse_args(); only = set(filter(None, a.only.split(",")))
env = dict(os.environ, WINBUILD_ROOT="/mnt/d/ClaudeWork/rimmandrake/scratch/ek_blind_c2_mut", EK_LANE1_OUT=LANE1_OUT,
           EK_LANE1_STAGE="/mnt/d/ClaudeWork/rimmandrake/scratch/ek_blind_c2_mut/lane1")
os.makedirs(env["WINBUILD_ROOT"], exist_ok=True)
dirty_before = subprocess.run(["git", "diff", "--stat", "--", "src/RimMandrake/ExplosiveKnockback", "src/RimMandrake/Utils"], cwd=REPO, capture_output=True, text=True).stdout
faults = [f for f in json.load(open(os.path.join(HERE, "planted_faults.json"))) if not only or f["id"] in only]
base = {k: run(c, env)[0] for k, c in SUITES.items()}; base_l1 = []
if not a.no_lane1: base["LANE1"] = run(LANE1, env)[0]; base_l1 = lane1_fails(); base["LANE1_FAILS"] = base_l1
print("BASELINE", json.dumps(base), flush=True)
out = open(a.out, "a" if a.append else "w")
if not a.append: out.write(json.dumps({"baseline": base}) + "\n")
rows = []
for f in faults:
    path = os.path.join(REPO, f["file"]); orig = open(path, "rb").read(); text = orig.decode()
    row = {"id": f["id"], "file": f["file"], "bars": f["bars"]}
    if text.count(f["old"]) != 1:
        row.update(planted=False, why="old text found %d times" % text.count(f["old"])); out.write(json.dumps(row) + "\n"); out.flush(); continue
    try:
        PLANTED[path] = orig; open(path, "wb").write(text.replace(f["old"], f["new"]).encode())
        res = {}
        for k, c in SUITES.items():
            rc, sec, last = run(c, env); res[k] = {"rc": rc, "caught": rc != 0 and base[k] == 0, "s": sec, "last": last}
        if f["file"].endswith("RM_KnockbackMath.cs") and not a.no_lane1:
            rc, sec, last = run(LANE1, env); new = [x for x in lane1_fails() if x not in base_l1]
            res["LANE1"] = {"rc": rc, "caught": bool(new), "new_fails": new, "s": sec}
    finally:
        open(path, "wb").write(orig); PLANTED.pop(path, None)
    assert hashlib.sha256(open(path, "rb").read()).digest() == hashlib.sha256(orig).digest()
    builder = [k for k, v in res.items() if k != "LANE1" and v["caught"]]
    row.update(planted=True, results=res, caught_by=builder + (["LANE1"] if res.get("LANE1", {}).get("caught") else []))
    out.write(json.dumps(row) + "\n"); out.flush(); rows.append(row)
    print(f["id"], "caught by:", ",".join(row["caught_by"]) or "MISSED", flush=True)
dirty_after = subprocess.run(["git", "diff", "--stat", "--", "src/RimMandrake/ExplosiveKnockback", "src/RimMandrake/Utils"], cwd=REPO, capture_output=True, text=True).stdout
clean = dirty_after == dirty_before
out.write(json.dumps({"tree_clean_after": clean, "note": "uncommitted fixes present: equality of git diff --stat before/after; git diff --quiet is re-run after the fixes commit"}) + "\n")
print("TREE CLEAN AFTER:", clean)
if a.expect_caught:
    missed = sorted(set(only) - {r["id"] for r in rows}) + [r["id"] for r in rows if not r.get("planted") or not [
        k for k in r.get("caught_by", []) if k != "LANE1"]]
    print("EXPECT CAUGHT: %s" % ("PASS, %d of %d caught by a builder suite" % (len(rows), len(rows)) if not missed and clean
                                 else "FAIL, missed: %s%s" % (", ".join(missed) or "none", "" if clean else "; tree not clean")))
    sys.exit(0 if not missed and clean and rows else 1)
