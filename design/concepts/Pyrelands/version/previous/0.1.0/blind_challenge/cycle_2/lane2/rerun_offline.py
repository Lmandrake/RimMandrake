"""Rerun every kind offline/record test of Pyrelands' test_table.json with its recorded command; compare with runs_today.
    python3 rerun_offline.py [--only T_A,T_B] [--out reruns.jsonl]
A match compares verdicts first (rc 0 = PASS), then accepts the recorded last line as a prefix of ours or ours of it
(a recorded line may be cut short or taken from stderr). Exit 0 = every rerun PASS."""
import argparse, json, os, shlex, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TABLE = os.path.join(REPO, "design/concepts/Pyrelands/version/test_table.json")


def last_line(out, err):
    for blob in (out, err):
        lines = [l.strip() for l in blob.splitlines() if l.strip()]
        if lines:
            return lines[-1]
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default=os.path.join(HERE, "reruns.jsonl"))
    a = ap.parse_args()
    tests = json.load(open(TABLE))["tests"]
    only = set(filter(None, a.only.split(",")))
    rows = []
    for tid, t in tests.items():
        if t.get("kind") not in ("offline", "record") or (only and tid not in only):
            continue
        cmd = t["command"]
        t0 = time.time()
        try:
            r = subprocess.run(shlex.split(cmd), cwd=REPO, capture_output=True, text=True, timeout=530)
            rc, out, err = r.returncode, r.stdout, r.stderr
        except subprocess.TimeoutExpired:
            rc, out, err = 124, "", "TIMEOUT 530 s"
        rt = t.get("runs_today") or {}
        res = "PASS" if rc == 0 else "FAIL"
        rec = rt.get("result") or ("PASS" if rt.get("rc") == 0 else "FAIL")
        mine, theirs = last_line(out, err), (rt.get("last") or "").strip()
        same_line = bool(theirs) and (mine.startswith(theirs[:60]) or theirs.startswith(mine[:60]))
        rows.append({"test": tid, "command": cmd, "rc": rc, "result": res, "recorded_result": rec, "last": mine[:300],
                     "recorded_last": theirs[:300], "line_match": same_line, "match": res == rec,
                     "seconds": round(time.time() - t0, 2)})
        print(res, tid, mine[:120], flush=True)
    with open(a.out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    bad = [r["test"] for r in rows if r["result"] != "PASS"]
    print("RERUN", len(rows), "tests;", sum(r["match"] for r in rows), "match;", len(bad), "not PASS", bad)
    sys.exit(1 if bad else 0)


main()
