#!/usr/bin/env python3
"""Rerun ExplosiveKnockback's offline tests (test_table.json kind=offline) with their recorded commands and compare with
runs_today: verdict first, then the last line (a recorded prefix is accepted: it may be cut short or come from stderr).
    python3 rerun_offline.py [--only T_KERNEL,T_FUZZ] [--out reruns.jsonl]
WINBUILD_ROOT defaults to a private scratch folder so the builder's kernel selftest never shares the machine-wide stage."""
import argparse, json, os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TABLE = os.path.join(REPO, "design/concepts/ExplosiveKnockback/version/test_table.json")
DECIDERS_FIRST = ["T_KERNEL", "T_FUZZ", "T_SCRIPT", "T_PROOFGATE", "T_RESTORE"]


def last_line(text):
    lines = [l for l in text.splitlines() if l.strip()]
    return lines[-1].strip() if lines else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default=os.path.join(HERE, "reruns.jsonl"))
    ap.add_argument("--timeout", type=int, default=300)
    a = ap.parse_args()
    t = json.load(open(TABLE))
    tests = t["tests"]
    off = [k for k, v in tests.items() if v.get("kind") == "offline"]
    order = [k for k in DECIDERS_FIRST if k in off] + [k for k in off if k not in DECIDERS_FIRST]
    if a.only:
        want = a.only.split(",")
        order = [k for k in order if k in want]
    env = dict(os.environ)
    env.setdefault("WINBUILD_ROOT", "/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c5_mut/")
    rows = []
    for k in order:
        v = tests[k]
        rt = v.get("runs_today") or {}
        cmd = v["command"]
        t0 = time.time()
        try:
            p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, timeout=a.timeout, env=env)
            rc, out, err = p.returncode, p.stdout, p.stderr
        except subprocess.TimeoutExpired as e:
            rc, out, err = 124, (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""), "TIMEOUT"
        result = "PASS" if rc == 0 else "FAIL"
        last = last_line(out) or last_line(err)
        rlast = (rt.get("last") or "").strip()
        norm = lambda x: re.sub(r"\d+(\.\d+)?s\b", "<t>s", x)
        lastm = bool(rlast) and (norm(last).startswith(norm(rlast)) or norm(rlast).startswith(norm(last)) or rlast in out or rlast in err)
        row = {"test": k, "command": cmd, "rc": rc, "result": result, "recorded_result": rt.get("result"), "last": last,
               "recorded_last": rlast, "verdict_match": result == rt.get("result"), "last_match": lastm,
               "match": result == rt.get("result") and lastm, "seconds": round(time.time() - t0, 2)}
        rows.append(row)
        print(json.dumps(row)[:400], flush=True)
    mode = "a" if a.only and os.path.exists(a.out) else "w"
    with open(a.out, mode) as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print("RERUNS", sum(r["match"] for r in rows), "of", len(rows), "match;", sum(r["result"] == "PASS" for r in rows), "PASS")


main()
