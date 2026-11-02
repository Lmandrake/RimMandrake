#!/usr/bin/env python3
"""Live-proof wrapper for PLANET_ATMOSPHERE_CLOUD_COST_1 (A1, A2, A3).

    python3 infrastructure/state/live_proofs/PLANET_ATMOSPHERE_CLOUD_COST_1_live.py A1|A2|A3

Exit codes follow relentless_live: 0 PASS, 1 FAIL, 2 UNMEASURED (retried on a later load).

Why it exists: A1 needs a launch WITH rwnodetree.rwplanetatmosphere, A2 one WITHOUT it. Any one staged launch is
only one of the two, and a FAIL stands until a new build, so `record --require` straight on the live line made the
other clause a standing FAIL. Here a launch that is the wrong condition (or not up, or whose ModsConfig moved since
launch, or lacks a DLC: staging facts, not the clause) is UNMEASURED and rides the next load on that list. A broken
instrument (no GPU counter, no load timing) stays FAIL. A3 is UNMEASURED until both sides exist, and FAIL when both
exist but no with/without pair differs by this mod alone.
"""
import contextlib
import io
import json
import os
import sys
import types

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
import planet_atmosphere_cost as pac  # noqa: E402

PASS, FAIL, UNMEASURED = 0, 1, 2
# record()'s reasons that describe the staged launch, not the clause (prefixes of its own messages)
STAGING = ("RimWorldWin64 is not running", "powershell gave no JSON", "ModsConfig.xml written",
           "DLC missing from the list", "this launch is the ")


def classify_record(rc, out):
    """Pure: record()'s exit code and stdout -> PASS / FAIL / UNMEASURED."""
    if rc == 0:
        return PASS
    line = [l for l in out.splitlines() if l.startswith("UNMEASURED: ")]
    if rc != 1 or not line:
        return FAIL
    reasons = [r.strip() for r in line[-1][len("UNMEASURED: "):].split("; ") if r.strip()]
    if reasons and all(r.startswith(STAGING) for r in reasons):
        return UNMEASURED
    return FAIL


def classify_verdict(rc, rows):
    """Pure: verdict()'s exit code and the sample rows -> PASS / FAIL / UNMEASURED."""
    if rc == 0:
        return PASS
    if not any(r.get("with") is True for r in rows) or not any(r.get("with") is False for r in rows):
        return UNMEASURED
    return FAIL


def run(fn, **kw):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(types.SimpleNamespace(**kw))
    return rc, buf.getvalue()


def main(argv):
    if len(argv) != 1 or argv[0] not in ("A1", "A2", "A3"):
        print("usage: %s A1|A2|A3" % os.path.basename(__file__))
        return 3
    clause = argv[0]
    if clause in ("A1", "A2"):
        rc, out = run(pac.record, require="with" if clause == "A1" else "without")
        code = classify_record(rc, out)
    else:
        rc, out = run(pac.verdict)
        path = pac.samples_path()
        rows = []
        if os.path.exists(path):
            with open(path) as fh:
                rows = [json.loads(l) for l in fh if l.strip()]
        code = classify_verdict(rc, rows)
    sys.stdout.write(out)
    print("%s: %s" % (clause, {PASS: "PASS", FAIL: "FAIL", UNMEASURED: "UNMEASURED (rides a later load)"}[code]))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
