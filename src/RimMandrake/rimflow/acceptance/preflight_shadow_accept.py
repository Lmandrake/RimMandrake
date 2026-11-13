#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_BACKTEST_PREFLIGHT_OVER_REAL_PAST_TICKETS (spec:
design/specs/2026-11-12-ticket-preflight-before-any-token.md, section 7 ticket 3, section 8). Written by the filing
seat; the builder does not edit it (a wrong clause goes to the Conductor).

    python3 src/RimMandrake/rimflow/acceptance/preflight_shadow_accept.py     # exit 0 and "PASS 21/21" when built

It runs real `rimflow file / claim / start` in a sandbox ledger (RIMFLOW_LEDGER, RIMFLOW_ITEMS), never the real one.
THE CONTRACT:
  * file, claim and start run the preflight in SHADOW: they print its lines, record them, and refuse nothing. Each
    run appends a timing line (RIMFLOW_PREFLIGHT_RUNS) with "door" set to file / claim / start; the claim and start
    events carry "preflight_run" (that line's run_id) and "preflight_ms". The claim line lists the existing gates it
    observed (at least I2 focus cap and E1 sections); the filing line lists A1 (name grammar).
  * RIMFLOW_PREFLIGHT_BREAK=1 (test hook) makes the runner raise at entry: the door still works and prints
    "preflight did not run". A timing file that cannot be written is reported ("timing") and stops nothing.
  * detached_helper.launch calls it; no relentless*.py file does (owner, by card 2026-11-13: out of Relentless
    entirely until the 2026-11-06 freeze ends).
  * The backtest writes infrastructure/state/evidence/preflight_backtest/<date>.json with: "corpora" (open,
    closed_60d, measured_week, labelled, each with "n"), "checks" (rows with id, fires, incremental, audited, false),
    "planted" (at least 10 known-bad tickets covering at least 8 of the 9 groups A to I, each "caught": true),
    "joint_false_block", and "timing" per door (p50, p95, max).
  What it cannot check: the person's audit of each would-be refusal (spec section 8 "False refusal"). That is read by
  the Conductor at close; this test only proves the table has the columns to hold it.
"""
import ast
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(RIMFLOW, "..", "..", ".."))
CLI = os.path.join(RIMFLOW, "cli.py")
TOTAL = 21
RESULTS = []
A = "RIMMANDRAKE_PLANT_SHADOW_TICKET_FOR_ACCEPTANCE_RUN"
B = "RIMMANDRAKE_PLANT_BROKEN_RUNNER_FOR_ACCEPTANCE_RUN"


def check(ok, what):
    RESULTS.append((bool(ok), what))
    print(("ok    " if ok else "FAIL  ") + what)


def lines(path):
    return [json.loads(l) for l in open(path)] if os.path.isfile(path) else []


def main():
    tmp = tempfile.mkdtemp(prefix="preflight_shadow_")
    items = os.path.join(tmp, "items")
    os.makedirs(items)
    runs = os.path.join(tmp, "runs.jsonl")
    for i in (A, B):
        open(os.path.join(items, i + ".md"), "w").write(
            "## spec\nA planted ticket.\n\n## refs\nfile: src/A/missing_on_purpose.py\n\n## verify\ntrue\n")
    base = {k: v for k, v in os.environ.items() if not k.startswith("RIMFLOW_")}
    base.update(RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"), RIMFLOW_ITEMS=items, RIMFLOW_SEAT="BENCH",
                RIMFLOW_PROBE="no-reading", RIMFLOW_PREFLIGHT_RUNS=runs, PYTHONDONTWRITEBYTECODE="1")

    def cli(*a, **env):
        e = dict(base, **env)
        return subprocess.run([sys.executable, CLI] + list(a) + ["--why", "acceptance sandbox"], cwd=REPO, env=e,
                              capture_output=True, text=True, timeout=120)

    def events():
        out = []
        for f in glob.glob(os.path.join(tmp, "events", "*.jsonl")) + [base["RIMFLOW_LEDGER"]]:
            out += lines(f)
        return out

    try:
        f = cli("file", A, "--for", "BENCH", "--title", "planted", "--kind", "build")
        check(f.returncode == 0, "file never refuses: a declared missing path still files")
        check("B1" in f.stdout + f.stderr, "file prints the preflight line for the missing path (B1)")
        by = {l.get("door"): l for l in lines(runs)}
        check("file" in by and "A1" in {c.get("id") for c in by["file"].get("checks", [])},
              "filing writes a timing line, door=file, observing A1")
        c = cli("claim", A)
        check(c.returncode == 0, "claim is shadow: a FAIL refuses nothing")
        by = {l.get("door"): l for l in lines(runs)}
        cl = by.get("claim", {})
        check(cl and {"I2", "E1"} <= {x.get("id") for x in cl.get("checks", [])},
              "the claim line observes the existing gates I2 and E1")
        check(cl and cl.get("total_ms", 1e9) < 3000, "the claim run is inside the 3 s PICKUP hard stop (%s ms)"
              % cl.get("total_ms"))
        ev = [e for e in events() if e.get("event") == "claim" and e.get("id") == A]
        check(ev and ev[-1].get("preflight_run") and ev[-1]["preflight_run"] == cl.get("run_id") and isinstance(ev[-1].get("preflight_ms"), (int, float)),
              "the claim event carries preflight_run (= the timing line's run_id) and preflight_ms")
        s = cli("start", A)
        by = {l.get("door"): l for l in lines(runs)}
        sv = [e for e in events() if e.get("event") == "start" and e.get("id") == A]
        check(s.returncode == 0 and "start" in by, "start is shadow and writes door=start")
        check(sv and sv[-1].get("preflight_run") and sv[-1]["preflight_run"] == by.get("start", {}).get("run_id"),
              "the start event carries preflight_run")

        f2 = cli("file", B, "--for", "BENCH", "--title", "planted", "--kind", "build", RIMFLOW_PREFLIGHT_BREAK="1")
        c2 = cli("claim", B, RIMFLOW_PREFLIGHT_BREAK="1")
        check(f2.returncode == 0 and c2.returncode == 0, "a broken runner leaves file and claim working")
        check("preflight did not run" in c2.stdout + c2.stderr, "a broken runner says 'preflight did not run'")
        os.makedirs(os.path.join(tmp, "runs_is_a_dir"))
        s2 = cli("start", B, RIMFLOW_PREFLIGHT_RUNS=os.path.join(tmp, "runs_is_a_dir"))
        check(s2.returncode == 0 and "timing" in (s2.stdout + s2.stderr).lower(),
              "an unwritable timing file is reported and stops nothing")
    except Exception as e:
        check(False, "sandbox doors crashed: %s: %s" % (type(e).__name__, e))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rel = [p for p in glob.glob(os.path.join(RIMFLOW, "relentless*.py")) if "ticket_preflight" in open(p).read()]
    check(not rel, "no relentless*.py file calls ticket_preflight (%s)" % ", ".join(os.path.basename(p) for p in rel))
    try:
        src = open(os.path.join(RIMFLOW, "detached_helper.py")).read()
        fn = [ast.get_source_segment(src, n) for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "launch"]
        check(fn and "ticket_preflight" in fn[0], "detached_helper.launch runs the preflight")
    except Exception as e:
        check(False, "detached_helper.launch unreadable: %s" % e)

    files = sorted(glob.glob(os.path.join(REPO, "infrastructure", "state", "evidence", "preflight_backtest", "*.json")))
    bt = {}
    if files:
        try:
            bt = json.load(open(files[-1]))
        except ValueError:
            bt = {}
    check(bt, "a backtest table exists (%s)" % (files[-1] if files else "none"))
    cor = bt.get("corpora", {})
    check(all(isinstance(cor.get(k, {}).get("n"), int) for k in ("open", "closed_60d", "measured_week", "labelled")),
          "the four corpora of spec section 8 are each counted")
    rows = bt.get("checks", [])
    check(rows and all({"id", "fires", "incremental", "audited", "false"} <= set(r) for r in rows),
          "every check row has fires, incremental, audited, false")
    pl = bt.get("planted", [])
    check(len(pl) >= 10 and all(p.get("caught") is True for p in pl) and len({p.get("group") for p in pl}) >= 8,
          "at least 10 planted known-bad tickets over at least 8 groups, all caught (%d)" % len(pl))
    check("joint_false_block" in bt and all({"p50", "p95", "max"} <= set(v) for v in bt.get("timing", {}).values())
          and bt.get("timing"), "joint false block and per-door timing are reported")
    for t in ("preflight_spine_accept.py", "preflight_core_accept.py"):
        p = subprocess.run([sys.executable, os.path.join(HERE, t)], cwd=REPO, capture_output=True, text=True, timeout=600)
        check(p.returncode == 0, "%s still passes" % t)
    passed = sum(1 for ok, _ in RESULTS if ok)
    print("PASS %d/%d" % (passed, TOTAL))
    return 0 if passed == TOTAL and len(RESULTS) == TOTAL else 1


if __name__ == "__main__":
    sys.exit(main())
