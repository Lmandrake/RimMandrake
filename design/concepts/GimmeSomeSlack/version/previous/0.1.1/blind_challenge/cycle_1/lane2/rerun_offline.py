#!/usr/bin/env python3
"""Rerun offline tests of GimmeSomeSlack version/test_table.json with their recorded commands, and compare with runs_today.
    python3 rerun_offline.py --only T_A,T_B [--out reruns.jsonl] [--timeout 530]
Rows are APPENDED (a later row for the same test replaces an earlier one when read), so the suite can be run in batches,
each under the 540 s command bound. Tests that share one recorded command are run once; each row names the shared run.
A rerun MATCHES when its verdict (rc 0 = PASS) equals the recorded result and its last non-empty line equals the
recorded `last`, or one is a prefix of the other (the recorded line may be cut short), timings masked.
A run killed by the timeout is result UNMEASURED, never FAIL."""
import argparse, json, os, re, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TT = os.path.join(REPO, "design/concepts/GimmeSomeSlack/version/test_table.json")
# timings: "12.3 s", "40ms", ISO stamps, and JSON timing fields ("wall_s": 315.4, "seconds": 2.1)
mask = lambda s: re.sub(r'("(?:wall_s|seconds|secs|elapsed_s|ms)":\s*)[\d.]+', r"\1<t>",
                        re.sub(r"\d+(\.\d+)? ?(ms|s)\b|\d{4}-\d\d-\d\dT[\d:.]+Z?", "<t>", s or "")).strip()


def last_line(txt):
    lines = [l for l in (txt or "").splitlines() if l.strip()]
    return lines[-1].strip() if lines else ""


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=os.path.join(HERE, "reruns.jsonl"))
    ap.add_argument("--only", default=""); ap.add_argument("--timeout", type=int, default=530)
    ap.add_argument("--recheck", action="store_true", help="re-derive last_matches/match of the stored rows (no rerun)")
    a = ap.parse_args(); only = [x for x in a.only.split(",") if x]
    if a.recheck:
        rows = [json.loads(l) for l in open(a.out) if l.strip()]
        for r in rows:
            ml, mr = mask(r["last"]), mask(r["recorded_last"])
            r["last_matches"] = bool(ml) and (ml == mr or ml.startswith(mr) or mr.startswith(ml))
            r["match"] = r["result_matches"] and r["last_matches"]
        with open(a.out, "w") as f:
            for r in rows: f.write(json.dumps(r) + "\n")
        print("RECHECK", sum(r["match"] for r in rows), "of", len(rows), "match"); return
    if not only: raise SystemExit("--only T_A,T_B required")
    tests = json.load(open(TT))["tests"]
    env = dict(os.environ)
    env.setdefault("WINBUILD_ROOT", "/mnt/d/ClaudeWork/rimmandrake/scratch/gimmesomeslack_blind_c1_mut/")
    done = {}
    with open(a.out, "a") as f:
        for k in only:
            v = tests[k]
            if v.get("kind") != "offline": raise SystemExit("not an offline test: " + k)
            rec = v.get("runs_today") or {}
            cmd = v["command"]
            if cmd not in done:
                t0 = time.time()
                try:
                    p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, timeout=a.timeout, env=env)
                    done[cmd] = (p.returncode, last_line(p.stdout) or last_line(p.stderr), round(time.time() - t0, 2), k)
                except subprocess.TimeoutExpired:
                    done[cmd] = (None, "TIMEOUT after %d s" % a.timeout, round(time.time() - t0, 2), k)
            rc, ll, secs, first = done[cmd]
            got = "UNMEASURED" if rc is None else ("PASS" if rc == 0 else "FAIL")
            want = rec.get("result")
            ml, mr = mask(ll), mask(rec.get("last"))
            row = {"test": k, "command": cmd, "rc": rc, "seconds": secs, "result": got, "recorded_result": want,
                   "recorded_rc": rec.get("rc"), "last": ll[:400], "recorded_last": (rec.get("last") or "")[:400],
                   "result_matches": got == want, "last_matches": bool(ml) and (ml == mr or ml.startswith(mr) or mr.startswith(ml)),
                   "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            if first != k: row["shared_run_with"] = first
            row["match"] = row["result_matches"] and row["last_matches"]
            f.write(json.dumps(row) + "\n"); f.flush()
            print(("MATCH" if row["match"] else "DIFF "), k, got, "vs", want, "|", ll[:160], "| was:", (rec.get("last") or "")[:120])


main()
