#!/usr/bin/env python3
"""Plant each fault of planted_faults.json, run the offline tests it names (recorded commands, version/test_table.json),
and record whether a test turned red with a new failing line. A non-zero rc alone is not a catch (a crash is recorded as
such). The tree is restored after each plant and on SIGTERM, SIGINT and SIGHUP.
    WINBUILD_ROOT=/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c2_mut/ python3 plant_faults.py [--only ID,..]
Writes planted_results.jsonl: the baseline row first, one row per plant, {"tree_clean_after": true|false} last.
Exit 0 = ran to the end with the tree clean; 2 = a plant could not be applied or the tree was not clean after."""
import argparse, json, os, re, signal, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
TABLE = os.path.join(REPO, "design/concepts/ExplosiveKnockback/version/test_table.json")
SAVED = {}   # path -> original bytes, while planted


def restore_all(*_):
    for p, b in list(SAVED.items()):
        with open(p, "wb") as f:
            f.write(b)
        SAVED.pop(p, None)


def on_signal(sig, frame):
    restore_all()
    sys.exit(128 + sig)


def fail_lines(out):
    return {l.strip() for l in out.splitlines() if re.search(r"\bFAIL|NOT CAUGHT|\bFAILED\b|AssertionError", l)}


def run(cmd, env):
    t0 = time.time()
    try:
        # hang guard: the slowest test named here took 54 s as recorded (T_LINT_PLANTED); a plant can make a loop endless
        p = subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True, text=True, timeout=900, env=env)
        return p.returncode, p.stdout + "\n" + p.stderr, round(time.time() - t0, 1)
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT 900 s", 900.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default=os.path.join(HERE, "planted_results.jsonl"))
    a = ap.parse_args()
    for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(s, on_signal)
    env = dict(os.environ)
    env.setdefault("WINBUILD_ROOT", "/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c2_mut/")
    tests = json.load(open(TABLE))["tests"]
    plants = json.load(open(os.path.join(HERE, "planted_faults.json")))
    only = set(x for x in a.only.split(",") if x)
    if only:
        plants = [p for p in plants if p["id"] in only]
    if subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/ExplosiveKnockback"], cwd=REPO).returncode:
        print("REFUSED: src/RimMandrake/ExplosiveKnockback is not clean before planting")
        return 2
    cmds = sorted({tests[t]["command"] for p in plants for t in p["tests"]})
    base = {}
    for c in cmds:
        rc, out, secs = run(c, env)
        base[c] = (rc, fail_lines(out))
        print("baseline rc=%d %.1fs %s" % (rc, secs, c), flush=True)
    rows = [{"baseline": {c: {"rc": rc, "fail_lines": sorted(fl)[:5]} for c, (rc, fl) in base.items()},
             "all_green": all(rc == 0 for rc, _ in base.values())}]
    bad_apply = []
    for p in plants:
        path = os.path.join(REPO, p["file"])
        orig = open(path, "rb").read()
        text = orig.decode("utf-8")
        if p["old"] not in text:
            bad_apply.append(p["id"])
            rows.append({"id": p["id"], "applied": False, "caught": False, "why": "old text not found"})
            continue
        SAVED[path] = orig
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.replace(p["old"], p["new"], 1))
        per = []
        for c in sorted({tests[t]["command"] for t in p["tests"]}):
            rc, out, secs = run(c, env)
            new = sorted(fail_lines(out) - base[c][1])
            per.append({"command": c, "rc": rc, "seconds": secs, "new_fail_lines": new[:4],
                        "red": rc != 0 and base[c][0] == 0 and bool(new), "crash": rc != 0 and not new})
        restore_all()
        caught = any(x["red"] for x in per)
        rows.append({"id": p["id"], "file": p["file"], "bars": p["bars"], "applied": True, "caught": caught,
                     "caught_by": [x["command"] for x in per if x["red"]], "runs": per})
        print("%-44s %s %s" % (p["id"], "CAUGHT" if caught else "SURVIVED", [x["command"].split("/")[-1] for x in per if x["red"]]), flush=True)
    clean = subprocess.run(["git", "diff", "--quiet", "--", "src/RimMandrake/ExplosiveKnockback"], cwd=REPO).returncode == 0
    rows.append({"tree_clean_after": clean})
    with open(a.out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    n = [r for r in rows if "caught" in r]
    print("PLANTED %d, caught %d, survived %s, tree_clean_after %s" % (len(n), sum(r["caught"] for r in n),
          [r["id"] for r in n if not r["caught"]], clean))
    return 0 if clean and not bad_apply else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        restore_all()
