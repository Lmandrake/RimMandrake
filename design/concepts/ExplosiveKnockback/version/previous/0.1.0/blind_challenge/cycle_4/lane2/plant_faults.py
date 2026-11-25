#!/usr/bin/env python3
"""Blind cycle 4: plant each fault of planted_faults.json in turn, run every offline builder suite (and blind lane 1 for
kernel, settings and def-patch faults), restore the file byte for byte, and record who caught it. A fault is CAUGHT only by
a suite that was green on the clean tree and goes red with it in (for lane 1: a NEW failing row), never by a bare rc.
    python3 plant_faults.py [--only PF_A,PF_B] [--out planted_results.jsonl] [--append] [--no-lane1] [--expect-caught]
--append reuses the baseline recorded on the first line of --out (batches stay under the 540 s command bound).
--expect-caught makes it a test of the deciders (a fix's red-then-green command): rc 0 only when every selected fault was
planted and caught by a builder suite (lane 1 does not count) and the tree ends clean; rc 1 otherwise, naming the misses.
Builds stage under WINBUILD_ROOT=/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c4_mut/. Restores on
SIGTERM/SIGINT/SIGHUP; each run ends by comparing git diff on the planted trees with the pre-run state (cycle-3 tool, adapted for cycle 4: lane 1 is cycle 4's own run_lane1.py)."""
import argparse, hashlib, json, os, signal, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = "src/RimMandrake/ExplosiveKnockback"
TT = os.path.join(REPO, "design/concepts/ExplosiveKnockback/version/test_table.json")
SLOW = {"T_LINT_PLANTED"}                      # 32 s; run only for def-patch and lint faults
SUITES = {}
for k, v in json.load(open(TT))["tests"].items():
    if v.get("kind") == "offline" and v["command"] not in SUITES.values():
        SUITES[k] = v["command"]
for f in sorted(os.listdir(os.path.join(REPO, MOD))):            # the builder's selftests the table does not list
    cmd = "python3 %s/%s" % (MOD, f)
    if f.startswith("selftest_") and f.endswith(".py") and cmd not in SUITES.values():
        SUITES["S_" + f[len("selftest_explosiveknockback_"):-3].upper()] = cmd
MUT = "/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c4_mut"
LANE1_OUT = "/tmp/ek_blind_c4_lane1_mut.jsonl"
LANE1 = "python3 %s --out %s" % (os.path.join(HERE, "..", "lane1", "run_lane1.py"), LANE1_OUT)
LANE1_FILES = ("RM_KnockbackMath.cs", "RM_KnockbackMod.cs", "proof_build_gate.py", "RM_KnockbackProof.cs")
TREES = [MOD, "src/RimMandrake/Utils"]


def lane1_fails():
    return sorted(json.loads(l)["id"] for l in open(LANE1_OUT) if json.loads(l)["verdict"] == "FAIL")


PLANTED = {}


def _restore(*_):
    for p, b in PLANTED.items():
        open(p, "wb").write(b)
    sys.exit(3)


for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(sig, _restore)


def run(cmd, env):
    t = time.time()
    try:
        p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, env=env, timeout=400)
        rc, txt = p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        rc, txt = 124, "TIMEOUT"
    tail = [l for l in txt.splitlines() if l.strip() and "SyntaxWarning" not in l]
    return rc, round(time.time() - t, 1), (tail[-1] if tail else "")[:240]


def suites_for(f):
    return {k: c for k, c in SUITES.items() if k not in SLOW or f["file"].endswith((".xml", "lint_explosiveknockback_defs.py"))}


ap = argparse.ArgumentParser()
ap.add_argument("--only", default=""); ap.add_argument("--out", default=os.path.join(HERE, "planted_results.jsonl"))
ap.add_argument("--append", action="store_true"); ap.add_argument("--no-lane1", action="store_true")
ap.add_argument("--expect-caught", action="store_true")
a = ap.parse_args(); only = set(filter(None, a.only.split(",")))
env = dict(os.environ, WINBUILD_ROOT=MUT + "/", EK_LANE1_STAGE=MUT + "/lane1", WINBUILD_ROOT_LANE1=MUT + "/lane1_winbuild")
os.makedirs(MUT, exist_ok=True)
diff = lambda: subprocess.run(["git", "diff", "--stat", "--"] + TREES, cwd=REPO, capture_output=True, text=True).stdout
dirty_before = diff()
faults = [f for f in json.load(open(os.path.join(HERE, "planted_faults.json"))) if not only or f["id"] in only]
if a.append and os.path.exists(a.out):
    base = json.loads(open(a.out).readline())["baseline"]
else:
    base = {k: run(c, env)[0] for k, c in SUITES.items()}
    if not a.no_lane1:
        base["LANE1"] = run(LANE1, env)[0]; base["LANE1_FAILS"] = lane1_fails()
print("BASELINE", json.dumps(base), flush=True)
out = open(a.out, "a" if a.append else "w")
if not a.append:
    out.write(json.dumps({"baseline": base, "suites": SUITES}) + "\n")
rows = []
for f in faults:
    path = os.path.join(REPO, f["file"]); orig = open(path, "rb").read(); text = orig.decode()
    row = {"id": f["id"], "file": f["file"], "bars": f["bars"]}
    if text.count(f["old"]) != 1:
        row.update(planted=False, why="old text found %d times" % text.count(f["old"]))
        out.write(json.dumps(row) + "\n"); out.flush(); rows.append(row); print(f["id"], "NOT PLANTED", flush=True); continue
    res = {}
    try:
        PLANTED[path] = orig; open(path, "wb").write(text.replace(f["old"], f["new"]).encode())
        for k, c in suites_for(f).items():
            rc, sec, last = run(c, env)
            res[k] = {"rc": rc, "caught": rc != 0 and base.get(k) == 0, "s": sec, "last": last}
        if f["file"].endswith(LANE1_FILES) and not a.no_lane1 and "LANE1" in base:
            rc, sec, last = run(LANE1, env); new = [x for x in lane1_fails() if x not in base["LANE1_FAILS"]]
            res["LANE1"] = {"rc": rc, "caught": bool(new), "new_fails": new, "s": sec}
    finally:
        open(path, "wb").write(orig); PLANTED.pop(path, None)
    assert hashlib.sha256(open(path, "rb").read()).digest() == hashlib.sha256(orig).digest()
    builder = [k for k, v in res.items() if k != "LANE1" and v["caught"]]
    row.update(planted=True, results=res, caught_by=builder + (["LANE1"] if res.get("LANE1", {}).get("caught") else []))
    out.write(json.dumps(row) + "\n"); out.flush(); rows.append(row)
    print(f["id"], "caught by:", ",".join(row["caught_by"]) or "MISSED", flush=True)
clean = diff() == dirty_before
quiet = subprocess.run(["git", "diff", "--quiet", "--", MOD], cwd=REPO).returncode == 0
out.write(json.dumps({"tree_clean_after": clean and (quiet or bool(dirty_before)), "git_diff_quiet_mod": quiet}) + "\n")
print("TREE CLEAN AFTER:", clean, "git diff --quiet mod:", quiet)
if a.expect_caught:
    missed = sorted(only - {r["id"] for r in rows}) + [r["id"] for r in rows if not r.get("planted") or not [
        k for k in r.get("caught_by", []) if k != "LANE1"]]
    print("EXPECT CAUGHT: %s" % ("PASS, %d of %d caught by a builder suite" % (len(rows), len(rows)) if not missed and clean
                                 else "FAIL, missed: %s%s" % (", ".join(missed) or "none", "" if clean else "; tree not clean")))
    sys.exit(0 if not missed and clean and rows else 1)
