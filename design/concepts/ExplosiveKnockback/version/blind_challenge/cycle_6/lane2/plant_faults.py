#!/usr/bin/env python3
"""Plant each fault of planted_faults.json in turn, run the suites that can see it, restore byte for byte, prove the tree clean.
    WINBUILD_ROOT=/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c6_mut/ python3 plant_faults.py [--only PF_A,PF_B]
Suites per fault: lane 1 (when the file is a kernel lane 1 compiles or reads), and every offline test of test_table.json whose
`reads` names the file or whose own script names its basename (the situation map runs --map-only). Caught = a NEW failing row:
a lane-1 FAIL row id absent from the baseline, or a suite that passed on the baseline now failing with a failing verdict line
(a build error is not a catch). Restores on SIGTERM, SIGINT and SIGHUP. Writes planted_results.jsonl: baseline first,
{"tree_clean_after": ...} last. The per-suite timeout is a hang guard, far above a real run."""
import argparse, json, os, re, signal, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TABLE = os.path.join(REPO, "design/concepts/ExplosiveKnockback/version/test_table.json")
LANE1 = os.path.join(HERE, "..", "lane1", "run_lane1.py")
LANE1_FILES = ("RM_KnockbackMath.cs", "RM_KnockbackPlan.cs", "RM_KnockbackMod.cs", "proof_build_gate.py")
HANG_GUARD_S = 600
FAILWORD = re.compile(r"FAIL|BREAKS|NOT CAUGHT|red|mismatch|missing|wrong", re.I)
BUILDFAIL = re.compile(r"error CS\d+|BUILD FAILED|SyntaxError|Traceback", re.I)

state = {"file": None, "bytes": None}


def restore(*_):
    if state["file"] is not None:
        open(state["file"], "wb").write(state["bytes"])
        state["file"] = None
    if _:
        sys.exit(130)


for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, restore)


def run(cmd, env):
    try:
        p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, timeout=HANG_GUARD_S, env=env)
        return p.returncode, p.stdout + "\n" + p.stderr
    except subprocess.TimeoutExpired:
        return 124, "HANG GUARD"


def lane1(env):
    out = "/tmp/ek_c6_plant_lane1.jsonl"
    if os.path.exists(out):
        os.remove(out)
    rc, text = run("python3 %s --out %s" % (LANE1, out), env)
    rows = [json.loads(l) for l in open(out)] if os.path.exists(out) and rc in (0, 1) else []
    return rc, {r["id"] for r in rows if r["verdict"] == "FAIL"}, text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default=os.path.join(HERE, "planted_results.jsonl"))
    a = ap.parse_args()
    env = dict(os.environ)
    env.setdefault("WINBUILD_ROOT", "/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c6_mut/")
    os.makedirs(env["WINBUILD_ROOT"], exist_ok=True)
    faults = json.load(open(os.path.join(HERE, "planted_faults.json")))
    if a.only:
        keep = set(a.only.split(","))
        faults = [f for f in faults if f["id"] in keep]
    tests = json.load(open(TABLE))["tests"]
    offline = {k: v for k, v in tests.items() if v.get("kind") == "offline"}

    def cmd_of(tid):
        c = offline[tid]["command"]
        return c + " --map-only" if tid == "T_SITUATION_MAP_OFFLINE" else c

    def suites_for(path):
        # the tests whose `reads` name the file; only when none does, the tests whose own script names its basename.
        # One run per distinct command (T_HEAVY_KNOCK_RULE is T_KERNEL's command); the map runs --map-only.
        base = os.path.basename(path)
        by_reads = [tid for tid, t in offline.items() if any(r == path or r.endswith("/" + base) for r in (t.get("reads") or []))]
        s = by_reads
        if not s:
            for tid, t in offline.items():
                fp = os.path.join(REPO, t.get("file") or "")
                if t.get("file") and os.path.exists(fp) and base in open(fp).read():
                    s.append(tid)
        out, seen = [], set()
        for tid in sorted(s):
            if cmd_of(tid) not in seen:
                seen.add(cmd_of(tid))
                out.append(tid)
        return out

    plan = {f["id"]: suites_for(f["file"]) for f in faults}
    needed = sorted({t for v in plan.values() for t in v})
    rows = []
    fh = open(a.out, "w")

    def emit(r):
        rows.append(r)
        fh.write(json.dumps(r) + "\n")
        fh.flush()
    base = {}
    for tid in needed:
        rc, text = run(cmd_of(tid), env)
        base[tid] = rc
    l1rc, l1base, _ = lane1(env)
    emit({"baseline": True, "suites": base, "lane1_rc": l1rc, "lane1_fail_rows": sorted(l1base),
                 "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    print("BASELINE", json.dumps(base), "lane1", l1rc, sorted(l1base), flush=True)
    for f in faults:
        path = os.path.join(REPO, f["file"])
        raw = open(path, "rb").read()
        text = raw.decode("utf-8")
        if text.count(f["old"]) != 1:
            emit({"id": f["id"], "planted": False, "why": "old text occurs %d times" % text.count(f["old"])})
            continue
        state["file"], state["bytes"] = path, raw
        open(path, "w").write(text.replace(f["old"], f["new"], 1))
        try:
            red, notes = [], {}
            for tid in plan[f["id"]]:
                rc, out = run(cmd_of(tid), env)
                last = [l for l in out.splitlines() if l.strip()][-1:] or [""]
                if rc != 0 and base.get(tid) == 0:
                    if BUILDFAIL.search(out) and not FAILWORD.search(last[0]):
                        notes[tid] = "build or crash, not a catch: " + last[0][:160]
                    else:
                        red.append(tid)
                        notes[tid] = last[0][:160]
            l1new = []
            if os.path.basename(path) in LANE1_FILES:
                l1rc, l1fail, _ = lane1(env)
                l1new = sorted(l1fail - l1base)
                if l1rc == 2:
                    notes["lane1"] = "build failed (not a catch)"
        finally:
            restore()
        caught = bool(red or l1new)
        emit({"id": f["id"], "file": f["file"], "bars": f["bars"], "suites": plan[f["id"]], "red_suites": red,
                     "lane1_new_fail_rows": l1new, "caught": caught, "notes": notes})
        print("%-40s %s  red=%s lane1=%s" % (f["id"], "CAUGHT" if caught else "SURVIVED", red, l1new), flush=True)
    clean = subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/ExplosiveKnockback"], cwd=REPO).returncode == 0
    emit({"tree_clean_after": clean})
    fh.close()
    n = sum(1 for r in rows if r.get("caught"))
    print("PLANTED %d caught of %d; tree_clean_after %s" % (n, len(faults), clean))


main()
