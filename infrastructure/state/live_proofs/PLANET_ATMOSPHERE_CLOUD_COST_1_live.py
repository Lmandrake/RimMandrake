#!/usr/bin/env python3
"""Live-proof wrapper for PLANET_ATMOSPHERE_CLOUD_COST_1 (A1, A2, A3).

    python3 infrastructure/state/live_proofs/PLANET_ATMOSPHERE_CLOUD_COST_1_live.py A1|A2|A3

Exit codes follow relentless_live: 0 PASS, 1 FAIL, 2 UNMEASURED (retried on a later load).

Why it exists: A1 needs a launch WITH rwnodetree.rwplanetatmosphere, A2 one WITHOUT it. Any one staged launch is
only one of the two, and a FAIL stands until a new build, so `record --require` straight on the live line made the
other clause a standing FAIL. Here a launch that is the wrong condition (or not up, or whose ModsConfig moved since
launch, or lacks a DLC, or has left the main menu for a game: staging facts, not the clause) is UNMEASURED and rides
the next load on that list. A broken instrument (no GPU counter, no load timing) stays FAIL. A3 is UNMEASURED until both sides exist, and FAIL when both
exist but no with/without pair differs by this mod alone.
"""
import contextlib
import io
import json
import os
import re
import sys
import types

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
import planet_atmosphere_cost as pac  # noqa: E402

PASS, FAIL, UNMEASURED = 0, 1, 2
# record()'s reasons that describe the staged launch, not the clause (prefixes of its own messages)
STAGING = ("RimWorldWin64 is not running", "powershell gave no JSON", "ModsConfig.xml written",
           "DLC missing from the list", "this launch is the ",
           "a game was started after the load")


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


FIELDS = ("load_ms", "gpu_dedicated_mb", "gpu_shared_mb", "private_mb")
SAMPLE_LINE = re.compile(r"^SAMPLE (with|without): load (-?\d+\.\d) s, GPU dedicated (-?\d+\.\d) MB, "
                         r"shared (-?\d+\.\d) MB, private (-?\d+\.\d) MB -> ", re.M)
AB_LINE = re.compile(r"^A/B \S+ \(with (\S+), without (\S+)\): load ([+-]\d+\.\d) s \((-?\d+\.\d) vs "
                     r"(-?\d+\.\d)\), GPU dedicated ([+-]\d+\.\d) MB, shared ([+-]\d+\.\d) MB, "
                     r"private ([+-]\d+\.\d) MB$", re.M)


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _close(a, b):
    return abs(a - b) < 0.051


def recorded_ok(out, new_rows, want):
    """Pure: A1/A2 'recorded' = exactly one new row of the wanted condition whose four numbers are real and are
    the ones the SAMPLE line printed. A rc-0 record that wrote nothing, or wrote a row without its numbers, is FAIL."""
    if len(new_rows) != 1:
        return False
    r = new_rows[0]
    if r.get("with") is not (want == "with") or not all(_num(r.get(f)) for f in FIELDS):
        return False
    m = SAMPLE_LINE.findall(out)
    if len(m) != 1 or m[0][0] != want:
        return False
    shown = [float(x) for x in m[0][1:]]
    return all(_close(a, b) for a, b in zip(shown, [r["load_ms"] / 1000.0, r["gpu_dedicated_mb"],
                                                    r["gpu_shared_mb"], r["private_mb"]]))


def deltas_ok(out, rows):
    """Pure: A3 'prints the load-time and VRAM deltas' = an A/B line whose figures are the with-minus-without
    deltas of the pair pac.pair() picks from the rows. A rc-0 verdict that printed nothing, or wrong figures, FAILS."""
    p = pac.pair(rows)
    m = AB_LINE.findall(out)
    if not p or len(m) != 1:
        return False
    w, o = p
    at_w, at_o, d_load, l_w, l_o, d_ded, d_sha, d_priv = m[0]
    if (at_w, at_o) != (w["at"], o["at"]):
        return False
    want = [(w["load_ms"] - o["load_ms"]) / 1000.0, w["load_ms"] / 1000.0, o["load_ms"] / 1000.0,
            w["gpu_dedicated_mb"] - o["gpu_dedicated_mb"], w["gpu_shared_mb"] - o["gpu_shared_mb"],
            w["private_mb"] - o["private_mb"]]
    got = [float(x) for x in (d_load, l_w, l_o, d_ded, d_sha, d_priv)]
    return all(_close(a, b) for a, b in zip(got, want))


def classify_verdict(rc, rows, out=""):
    """Pure: verdict()'s exit code, the sample rows and its stdout -> PASS / FAIL / UNMEASURED."""
    if rc == 0:
        return PASS if deltas_ok(out, rows) else FAIL
    if not any(r.get("with") is True for r in rows) or not any(r.get("with") is False for r in rows):
        return UNMEASURED
    return FAIL


def run(fn, **kw):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(types.SimpleNamespace(**kw))
    return rc, buf.getvalue()


def read_rows():
    path = pac.samples_path()
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        return [json.loads(l) for l in fh if l.strip()]


def main(argv):
    if len(argv) != 1 or argv[0] not in ("A1", "A2", "A3"):
        print("usage: %s A1|A2|A3" % os.path.basename(__file__))
        return 3
    clause = argv[0]
    if clause in ("A1", "A2"):
        want = "with" if clause == "A1" else "without"
        before = read_rows()
        rc, out = run(pac.record, require=want)
        code = classify_record(rc, out)
        if code == PASS and not recorded_ok(out, read_rows()[len(before):], want):
            out += "record exited 0 but did not append one '%s' row with real load/GPU/private numbers " \
                   "matching its SAMPLE line\n" % want
            code = FAIL
    else:
        rc, out = run(pac.verdict)
        rows = read_rows()
        code = classify_verdict(rc, rows, out)
        if rc == 0 and code == FAIL:
            out += "verdict exited 0 but printed no A/B line whose load/GPU deltas match the pair\n"
    sys.stdout.write(out)
    print("%s: %s" % (clause, {PASS: "PASS", FAIL: "FAIL", UNMEASURED: "UNMEASURED (rides a later load)"}[code]))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
