#!/usr/bin/env python3
"""Selftest for fauna_drive.py: test runs never supply a decision, run-name classification, install sha gate (pure)."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fauna_drive as FD  # noqa: E402
import round_series as RS  # noqa: E402

FAILS = []


def check(name, ok, detail=None):
    print(("ok   " if ok else "FAIL ") + name + ("" if ok or detail is None else f"  -> {detail}"))
    if not ok:
        FAILS.append(name)


def main():
    # (3 of FAUNA_DRIVE_FIX_TEST_RUNS_COUNTED / 2) candidate vs first-pass run names
    check("_r1_ is a candidate run", bool(FD.CAND_RUN.search("t_r1_00")))
    check("series tag s1r1 is a candidate run", bool(FD.CAND_RUN.search("t_s1r1_00")))
    check("biome glass_reef is first pass", not FD.CAND_RUN.search("glass_reef_00"))
    check("plain first pass", not FD.CAND_RUN.search("t_00"))

    # 1: a --test run is invisible to production(); latest() on production data ignores its newer ACCEPT
    with tempfile.TemporaryDirectory() as td:
        runs = Path(td)
        for name, test, dec, at in (("fauna_t_r1_00", False, "REGEN", "2026-10-23T10:00:00+00:00"),
                                    ("fauna_t_r1_01", True, "ACCEPT", "2026-10-24T10:00:00+00:00")):
            d = runs / name
            d.mkdir()
            (d / "run.json").write_text(json.dumps({"test": test}))
            (d / "decisions.jsonl").write_text(json.dumps({"subject": "D", "decision": dec, "at": at}) + "\n")
        orig = RS.production_decisions
        RS.production_decisions = lambda: orig(runs)
        try:
            recs = FD.production()
            check("test run excluded from production()", [r for r, _ in recs] == ["fauna_t_r1_00"])
            check("latest ignores the newer test ACCEPT", (FD.latest("D", True) or {}).get("decision") == "REGEN")
        finally:
            RS.production_decisions = orig

    # ARTEVAL_FILE_REGENS_JOBID_FIX_SERIES_TAG: a candidate judged under an adopted non-fauna run counts; an
    # unadopted audit run does not; a HOLD_ERROR (transport failure, no verdict) is not "judged"
    with tempfile.TemporaryDirectory() as td:
        runs, ad = Path(td) / "runs", Path(td) / "adopt.jsonl"
        for name, cand, dec, at in (("fauna_t_00", None, "REGEN", "2026-10-27T10:00:00+00:00"),
                                    ("judgestall_t", "s2r1", "REGEN", "2026-10-28T10:00:00+00:00"),
                                    ("audit_t", "r1", "ACCEPT", "2026-10-28T11:00:00+00:00")):
            (runs / name).mkdir(parents=True)
            (runs / name / "run.json").write_text(json.dumps({"test": False}))
            (runs / name / "decisions.jsonl").write_text(json.dumps({"subject": "D", "decision": dec, "candidate": cand,
                                                                     "at": at}) + "\n")
        ad.write_text(json.dumps({"run": "judgestall_t", "why": "t"}) + "\n")
        orig, orig_ad = RS.production_decisions, RS.ADOPTIONS
        RS.production_decisions, RS.ADOPTIONS = (lambda: orig(runs)), ad
        try:
            got = sorted(r for r, _ in FD.production())
            check("production() = fauna_* + adopted, not audit", got == ["fauna_t_00", "judgestall_t"], got)
            check("latest candidate comes from the adopted run", (FD.latest("D", True) or {}).get("candidate") == "s2r1")
            check("first pass latest stays the fauna_ run", (FD.latest("D", False) or {}).get("candidate") is None
                  and (FD.latest("D", False) or {}).get("decision") == "REGEN")
        finally:
            RS.production_decisions, RS.ADOPTIONS = orig, orig_ad
    js = FD.judged_set([("r", {"subject": "D", "candidate": "r1", "decision": "HOLD_ERROR"}),
                        ("r", {"subject": "E", "candidate": "r1", "decision": "HOLD_INPUT"}),
                        ("r", {"subject": "F", "candidate": "r2", "decision": "REGEN"})])
    check("HOLD_ERROR is not judged; other decisions are", js == {("E", "r1"), ("F", "r2")}, js)

    # FAUNA_INSTALL_CHECK_RENDER_IS_JUDGED: the render sha must equal the judged source sha
    j = {"south": "a" * 64}
    check("matching sha passes", FD.render_is_judged(j, "south", "a" * 64))
    check("re-rendered (different) sha refused", not FD.render_is_judged(j, "south", "b" * 64))
    check("record without that facing's sha refused", not FD.render_is_judged(j, "east", "a" * 64))
    check("record with no shas refused", not FD.render_is_judged(None, "south", "a" * 64))
    print("FAILED: " + ", ".join(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
