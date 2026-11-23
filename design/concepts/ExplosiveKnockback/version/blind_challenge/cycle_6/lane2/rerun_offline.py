#!/usr/bin/env python3
"""Rerun ExplosiveKnockback offline tests with their recorded commands and compare with test_table.json runs_today.
    python3 rerun_offline.py [--only T_A,T_B] [--out reruns.jsonl] [--append]
Verdicts first; a recorded `last` may be a prefix (cut short, or from stderr). The per-test timeout is a hang guard
(set far above a real run: the slowest recorded run is about 15 s), never a speed bar."""
import argparse, json, os, subprocess, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TABLE = os.path.join(REPO, "design/concepts/ExplosiveKnockback/version/test_table.json")
HANG_GUARD_S = 480


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default=os.path.join(HERE, "reruns.jsonl"))
    ap.add_argument("--append", action="store_true")
    a = ap.parse_args()
    d = json.load(open(TABLE))
    tests = d["tests"] if isinstance(d["tests"], dict) else {t["id"]: t for t in d["tests"]}
    ids = [i.strip() for i in a.only.split(",") if i.strip()] or [k for k, v in tests.items() if v.get("kind") == "offline"]
    rows = []
    env = dict(os.environ)
    env.setdefault("WINBUILD_ROOT", "/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c6_rerun/")
    os.makedirs(env["WINBUILD_ROOT"], exist_ok=True)  # the kernel selftest reads a missing root as UNMEASURED
    for tid in ids:
        t = tests[tid]
        rt = t.get("runs_today") or {}
        cmd = t.get("command") or rt.get("command")
        t0 = time.time()
        try:
            p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, timeout=HANG_GUARD_S, env=env)
            rc, out = p.returncode, (p.stdout + "\n" + p.stderr)
        except subprocess.TimeoutExpired:
            rc, out = 124, "HANG GUARD: no answer in %d s" % HANG_GUARD_S
        lines = [l for l in out.splitlines() if l.strip()]
        so = [l for l in p.stdout.splitlines() if l.strip()] if rc != 124 else []
        last = (so or lines or [""])[-1].strip()
        result = "PASS" if rc == 0 else "FAIL"
        rec_last = (rt.get("last") or "").strip()
        rec_res = rt.get("result")
        lmatch = bool(rec_last) and (last.startswith(rec_last[:60]) or rec_last.startswith(last[:60]) or any(l.strip().startswith(rec_last[:60]) for l in lines))
        rows.append({"test": tid, "command": cmd, "rc": rc, "result": result, "recorded_result": rec_res, "last": last[:400],
                     "recorded_last": rec_last[:400], "match": result == rec_res, "last_match": lmatch,
                     "seconds": round(time.time() - t0, 2), "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        print("%-34s %s (recorded %s) %s" % (tid, result, rec_res, last[:120]), flush=True)
    with open(a.out, "a" if a.append else "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


main()
