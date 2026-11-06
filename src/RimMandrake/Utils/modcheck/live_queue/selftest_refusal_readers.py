#!/usr/bin/env python3
"""MODCHECK_READERS_FIX_REFUSAL_READ_AS_FAIL: every reader of a modcheck results JSON scores a REFUSED run
(summary.refused, unmeasured=stale_load, chains []) as UNMEASURED exit 2, never FAIL; a PASS row still 0, a FAIL 1.

Readers covered: modcheck/live_queue/row_verdict.py check(), Stillsand/prove_roof_cover.py judge_path(),
Bones/prove_bones.py judge_path(). (Scarlands/chatrak_live_proof.py carries its own selftest, 427693afa4.)
"""
import importlib.util
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", "..", ".."))       # src/RimMandrake


def load(rel, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(SRC, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


REFUSED = {"chains": [], "all_green": False, "findings": [], "unmeasured": "stale_load",
           "refused": "UNMEASURED: the running load is not the composed list (stale_load)"}


def sheet(mod, row, verdict):
    return {"mod": mod, "summary": {"chains": [{"name": "c", "components": [
        {"name": row, "verdict": verdict, "detail": "d"}]}], "refused": ""}}


def main():
    rv = load("Utils/modcheck/live_queue/row_verdict.py", "row_verdict")
    st = load("Stillsand/prove_roof_cover.py", "prove_roof_cover")
    bo = load("Bones/prove_bones.py", "prove_bones")
    bad, n = [], 0
    with tempfile.TemporaryDirectory() as td:
        def put(mod, data):
            for old in os.listdir(td):
                os.remove(os.path.join(td, old))
            p = os.path.join(td, "%s_20261105T234400Z.json" % mod)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(data, f)
            return p

        for label, data, want in [("refused", {"mod": "M", "summary": REFUSED}, 2),
                                  ("pass", sheet("M", "r", "PASS"), 0),
                                  ("fail", sheet("M", "r", "FAIL"), 1)]:
            put("M", data)
            n += 1
            got = rv.check(td, "M", ["r"], 60)[0]
            if got != want:
                bad.append("row_verdict %s: want %d got %d" % (label, want, got))

        row = st.ROW
        for label, data, want in [("refused", {"mod": "Stillsand", "summary": REFUSED}, 2),
                                  ("pass", sheet("Stillsand", row, "PASS"), 0),
                                  ("fail", sheet("Stillsand", row, "FAIL"), 1),
                                  ("missing", sheet("Stillsand", "other", "PASS"), 1)]:
            n += 1
            got, line = st.judge_path(put("Stillsand", data))
            if got != want:
                bad.append("prove_roof_cover %s: want %d got %d (%s)" % (label, want, got, line))

        row = bo.CLAUSES["G1"]
        for label, data, want in [("refused", {"mod": "Bones", "summary": REFUSED}, 2),
                                  ("pass", sheet("Bones", row, "PASS"), 0),
                                  ("fail", sheet("Bones", row, "FAIL"), 1),
                                  ("missing", sheet("Bones", "other", "PASS"), 1)]:
            n += 1
            got, line = bo.judge_path(put("Bones", data), "G1", row)
            if got != want:
                bad.append("prove_bones %s: want %d got %d (%s)" % (label, want, got, line))

    for b in bad:
        print("  " + b)
    print("selftest_refusal_readers: %s (%d cases)" % ("FAIL" if bad else "PASS", n))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
