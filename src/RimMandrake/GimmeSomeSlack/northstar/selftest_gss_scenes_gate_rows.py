#!/usr/bin/env python3
"""selftest_gss_scenes_gate_rows.py -- a scene that names an offline gate row (O1..O8) can read PASS from a proof result.

RIMMANDRAKE_CARRY_GSS_GATE_ROWS_SCENES_NEVER_SAW (Stage 6 visit 1, 2026-11-16): validation.py --scenes-from read only
the result's live "rows", but six scenes (sc_conduit_invisible, sc_cords_slack, sc_true_to_grid, sc_spans,
sc_four_looks, sc_settings) also want offline gate rows, which proof_all kept only as a not_pass id list. Those scenes
read UNMEASURED (O*=MISSING) on every proof, green or not. The fix: the gate records each row's status, and
scenes_from reads them beside the live rows.

Checks (exit 0 all pass, 1 any fail):
  G1 a result whose gate recorded O1=PASS gives a scene needing O1 + one live row PASS
  G2 a gate row recorded FAIL turns that scene FAIL (the gate's verdict is not upgraded)
  G3 a result with the gate skipped (--skip-offline) still reads O1 MISSING, so the scene is UNMEASURED, never PASS
  G4 a live row of the same id is not shadowed by the gate (the live FAIL stands)
"""
import contextlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import validation as V  # noqa: E402


def verdict(res, sid):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(res, f)
        p = f.name
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            V.scenes_from(p)
    finally:
        os.unlink(p)
    for ln in buf.getvalue().splitlines():
        parts = ln.split()
        if parts and parts[0] == sid:
            return parts[1]
    return "ABSENT"


def gate(statuses):
    return {"red": [], "steps": {"validation_offline": {"rows": len(statuses),
            "not_pass": [k for k, v in statuses.items() if v != "PASS"], "statuses": statuses}}}


def main():
    want = V.scene_rows_for("sc_conduit_invisible")
    live = [{"id": w, "status": "PASS"} for w in want if not w.startswith("O")]
    offl = {w: "PASS" for w in want if w.startswith("O")}
    if not offl:
        print("FAIL G0 sc_conduit_invisible names no offline row any more; this test needs a new scene")
        return 1
    o = sorted(offl)[0]
    checks = [
        ("G1 gate PASS + live PASS -> PASS", verdict({"rows": live, "offline": gate(offl)}, "sc_conduit_invisible"), "PASS"),
        ("G2 gate FAIL -> FAIL", verdict({"rows": live, "offline": gate(dict(offl, **{o: "FAIL"}))}, "sc_conduit_invisible"), "FAIL"),
        ("G3 gate skipped -> UNMEASURED", verdict({"rows": live, "offline": {"skipped": "--skip-offline"}}, "sc_conduit_invisible"), "UNMEASURED"),
        ("G4 live FAIL not shadowed", verdict({"rows": live[:-1] + [dict(live[-1], status="FAIL")], "offline": gate(offl)}, "sc_conduit_invisible"), "FAIL"),
    ]
    bad = 0
    for name, got, exp in checks:
        ok = got == exp
        bad += not ok
        print("%s %s  want=%s got=%s" % ("PASS" if ok else "FAIL", name, exp, got))
    print("%d/%d checks passed" % (len(checks) - bad, len(checks)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
