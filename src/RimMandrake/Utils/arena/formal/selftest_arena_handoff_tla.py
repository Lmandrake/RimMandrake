#!/usr/bin/env python3
"""selftest_arena_handoff_tla.py — Handoff.tla under TLC: the known goodbye race is found, the fixed protocol passes.

ARENA_HANDOFF_PROVE_MODEL_FINDS_KNOWN_RACE criteria, each by forced failure:
  parser      run_tlc.parse reads a canned TLC pass, an invariant violation and a temporal violation correctly, and
              calls a run that never finished (no "0 states left on queue") an error, never a pass
  race        the unfixed goodbye (Bugs {dead_session_drop}) violates S5, and the trace is the known interleaving:
              a message sent while phase = killed is lost; is_known_goodbye_race refuses a trace without that step
  fixed       Bugs {} in goodbye, testpilot and arena: S1-S6 and L1, L2 hold
  mutants     each of S1..S6, L1, L2 is violated by its own planted defect (a property that cannot fail proves nothing)
Exit 2 (UNMEASURED) when java or tla2tools.jar is absent. Evidence goes to a temp dir, deleted on success.
"""
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_tlc as R  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


PASS_LOG = """Model checking completed. No error has been found.
1118121 states generated, 259,664 distinct states found, 0 states left on queue.
"""
INV_LOG = """Error: Invariant S5 is violated.
Error: The behavior up to this point is:
State 1: <Initial predicate>
/\\ phase = "killed"
/\\ msg = (m1 :> "unsent" @@ m2 :> "unsent")

State 2: <Send line 1, col 1 to line 2, col 2 of module Handoff>
/\\ phase = "killed"
/\\ msg = (m1 :> "lost" @@ m2 :> "unsent")

49 states generated, 49 distinct states found, 3 states left on queue.
"""
TEMP_LOG = "Error: Temporal properties L1 and L2 were violated.\n12 distinct states found, 0 states left on queue.\n"
HALF_LOG = "Model checking completed. No error has been found.\n99 distinct states found, 7 states left on queue.\n"


def t_parser():
    r = R.parse(PASS_LOG, [])
    check(r["result"] == "pass" and r["states"] == 259664, "parser: a finished clean run is a pass with the final count")
    r = R.parse(INV_LOG, [])
    check(r["result"] == "violated" and r["prop"] == "S5" and len(r["trace"]) == 2, "parser: invariant violation + trace")
    ok, _ = R.is_known_goodbye_race(r["trace"])
    check(ok, "parser: the canned killed-phase loss is recognised as the known race")
    calm = [s.replace('"killed"', '"pending"') for s in r["trace"]]
    ok, _ = R.is_known_goodbye_race(calm)
    check(not ok, "parser: the same loss outside phase killed is NOT the known race (forced failure)")
    r = R.parse(TEMP_LOG, ["L1", "L2"])
    check(r["result"] == "violated" and r["prop"] == "L1,L2", "parser: temporal violation names its properties")
    check(R.parse(HALF_LOG, [])["result"] == "error", "parser: an unfinished search is an error, never a pass")
    check(R.parse("", [])["result"] == "error", "parser: empty output is an error")


def t_model():
    java, jar = R.find_java(), R.find_jar()
    if not java or not jar:
        print("UNMEASURED: java=%s tla2tools=%s" % (java, jar))
        sys.exit(2)
    out = Path(tempfile.mkdtemp(prefix="handoff_tla_"))
    rows = {}
    for name in R.MATRIX:
        rows[name] = r = R.run_row(name, java, jar, out)
        check(r["ok"], "%s: expect %s, got %s%s (%s states) %s" % (name, r["expect"], r["result"],
              "(%s)" % r["violated"] if r["violated"] else "", r["states"], r["why"]))
    fixed = [r for n, r in rows.items() if n.startswith("fixed_")]
    check(len(fixed) == 3 and all(r["states"] and r["states"] > 40 for r in fixed),
          "fixed rows explored a real state space (not a vacuous init-only model)")
    covered = {r["expect"] for n, r in rows.items() if n.startswith("m_")}
    check(covered == set(R.INVS + R.PROPS), "every S1-S6, L1, L2 has its own mutant: %s" % sorted(covered))
    if FAILS:
        print("evidence kept: %s" % out)
    else:
        shutil.rmtree(out, ignore_errors=True)


if __name__ == "__main__":
    t_parser()
    t_model()
    print("%d failure(s)" % len(FAILS))
    sys.exit(1 if FAILS else 0)
