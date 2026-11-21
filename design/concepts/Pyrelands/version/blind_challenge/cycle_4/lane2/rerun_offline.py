#!/usr/bin/env python3
"""Rerun Pyrelands' offline and record tests from version/test_table.json with their recorded commands and compare with
runs_today. One row per test: test, result, recorded_result, last, recorded_last, match, rc, seconds, cmd.
    python3 rerun_offline.py [--only T_A,T_B] [--deciders | --others] [--out reruns.jsonl] [--append]
A test is PASS on rc 0, FAIL on rc non-zero, NOT_RUN when it has no command, TIMEOUT past --timeout. match compares the
verdict first, then accepts the recorded last line as a prefix of (or contained in) the new one.
Exit 0 always when every row was written; 2 when the table cannot be read."""
import argparse, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TABLE = os.path.join(REPO, "design/concepts/Pyrelands/version/test_table.json")


def last_line(out, err):
    for s in (out, err):
        lines = [l.strip() for l in (s or "").splitlines() if l.strip()]
        if lines:
            return lines[-1]
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--deciders", action="store_true")
    ap.add_argument("--others", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "reruns.jsonl"))
    ap.add_argument("--append", action="store_true")
    ap.add_argument("--timeout", type=int, default=480)
    a = ap.parse_args()
    try:
        t = json.load(open(TABLE))
    except Exception as e:
        print("RERUN COULD NOT READ the test table:", e)
        sys.exit(2)
    offline_bars = [b for b in t["bars"] if str(b.get("proves_at")) in ("2", "4-5")]
    deciders = []
    for b in offline_bars:
        for d in b["decides"]:
            if d not in deciders:
                deciders.append(d)
    cands = [k for k, v in t["tests"].items() if v.get("kind") in ("offline", "record")]
    if a.only:
        pick = a.only.split(",")
    elif a.deciders:
        pick = deciders
    elif a.others:
        pick = [k for k in cands if k not in deciders]
    else:
        pick = deciders + [k for k in cands if k not in deciders]
    env = dict(os.environ)
    env.setdefault("WINBUILD_ROOT", "/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c4_rerun/")
    mode = "a" if a.append else "w"
    with open(a.out, mode) as f:
        for k in pick:
            v = t["tests"].get(k, {})
            rt = v.get("runs_today") or {}
            cmd = v.get("command") or rt.get("command")
            row = {"test": k, "recorded_result": rt.get("result"), "recorded_last": rt.get("last"), "recorded_at": rt.get("at"),
                   "decider_of_offline_bar": k in deciders, "cmd": cmd}
            if not cmd:
                row.update(result="NOT_RUN", last="no command in the table", match=False, rc=None, seconds=0)
            else:
                t0 = time.time()
                try:
                    r = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, timeout=a.timeout, env=env)
                    rc, last = r.returncode, last_line(r.stdout, r.stderr)
                    res = "PASS" if rc == 0 else "FAIL"
                except subprocess.TimeoutExpired:
                    rc, last, res = None, "timed out after %d s" % a.timeout, "TIMEOUT"
                rl = (rt.get("last") or "").strip()
                same_line = bool(rl) and (last.startswith(rl[:60]) or rl[:60] in last or last[:60] in rl)
                row.update(result=res, last=last, rc=rc, seconds=round(time.time() - t0, 2),
                           match=(res == rt.get("result")), last_line_match=same_line)
            f.write(json.dumps(row) + "\n")
            f.flush()
            print(row["test"], row["result"], "recorded", row["recorded_result"], "match", row["match"], "|", row["last"][:120])


if __name__ == "__main__":
    main()
