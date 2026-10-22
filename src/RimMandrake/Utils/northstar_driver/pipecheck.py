#!/usr/bin/env python3
"""pipecheck -- prove or reject pipelined call_many against the live bridge (NORTHSTAR_FAST_DRIVER_1).

    python.exe src/RimMandrake/Utils/northstar_driver/pipecheck.py [--reps 10] [--tool T ...] [--out f.json]

Only READ-ONLY tools are used (TimedTransport never pipelines a mutating batch). The same batch runs
serially twice (S1, S2) and pipelined once (P). A reply FIELD (leaf path) is STABLE when S1 and S2
agree on it; P must agree on every stable field (volatile ones -- a clock, ticks -- drop out). Verdict:
  PASS        every pipelined call answered without error and every stable field matches
  FAIL        a missing/errored pipelined reply, or a stable field where P differs
  UNMEASURED  the batch could not run serially, or no field was stable (nothing to compare)
`speedup` is reported beside the verdict: correctness and worth are separate questions.
MEASURED 2026-10-21 (full list, game up): 16.66 ms/call serial AND pipelined, speedup 1.00 -- the bridge
answers one request per frame (~60 fps), so pipelining is correct-or-not but buys nothing; keep it off.
Exit 0 PASS, 1 FAIL, 2 UNMEASURED. Never takes the bridge lock -- hold it first (`rimflow bridge take`).
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

DEFAULT_TOOLS = ("rimworld/get_game_info", "rimworld/get_ui_state")


def _leaves(x, pre=""):
    """{path: json value} for every leaf; an Exception is one leaf."""
    if isinstance(x, Exception):
        return {pre: "EXC:%s" % type(x).__name__}
    if isinstance(x, dict):
        out = {}
        for k, v in x.items():
            out.update(_leaves(v, "%s/%s" % (pre, k)))
        return out or {pre: "{}"}
    if isinstance(x, list):
        out = {pre + "#len": len(x)}
        for i, v in enumerate(x):
            out.update(_leaves(v, "%s[%d]" % (pre, i)))
        return out
    return {pre: json.dumps(x, default=str)}


# Per-call envelope metadata, never game state. MEASURED 2026-10-21: /operation/DurationMs agreed across two
# serial reads by chance and then differed pipelined (13 -> 16), a false FAIL. Named, so it is not a guess.
# A millisecond suffix is matched case-sensitively (fooMs, foo_ms, FOO_MS): a bare (?i)ms$ also swallowed game-state
# keys such as /items, /rooms, /alarms and silently stopped comparing them.
VOLATILE = re.compile(r"(?i)(duration|elapsed|(?-i:Ms|_ms|MS)$|utc|timestamp|(^|/)(started|ended|finished)|"
                      r"/operation/.*id$|operationid|correlationid)")


def _stable_fields(a, b):
    """Leaves on which two serial reads agree -- volatile ones (clock, ticks while running) drop out."""
    la, lb = _leaves(a), _leaves(b)
    return {k: v for k, v in la.items() if lb.get(k) == v and not VOLATILE.search(k)}


def _timed(tx, calls):
    t0 = time.perf_counter()
    out = tx.call_many(calls)
    return out, (time.perf_counter() - t0) * 1000.0


def check(serial_tx, pipe_tx, calls):
    """serial_tx / pipe_tx: TimedTransport-like (pipeline off / on). Returns a JSON-able verdict dict."""
    bad = [t for t, _ in calls if not serial_tx.rb.looks_read_only(t)]
    if bad:
        raise ValueError("pipecheck uses read-only tools only; refused: %s" % ", ".join(sorted(set(bad))))
    s1, ms_s1 = _timed(serial_tx, calls)
    s2, ms_s2 = _timed(serial_tx, calls)
    p, ms_p = _timed(pipe_tx, calls)
    n = len(calls)
    serial_err = sum(isinstance(r, Exception) for r in s1)
    pipe_err = [i for i, r in enumerate(p) if isinstance(r, Exception)]
    fields = {i: _stable_fields(s1[i], s2[i]) for i in range(n) if not isinstance(s1[i], Exception)}
    stable = [i for i, f in fields.items() if f]
    mismatch = [i for i in stable if any(_leaves(p[i]).get(k) != v for k, v in fields[i].items())]
    if serial_err == n:
        status, why = "UNMEASURED", "serial batch did not run (%d/%d errors)" % (serial_err, n)
    elif pipe_err or len(p) != n:
        status, why = "FAIL", "pipelined replies missing/errored at %s: %s" % (
            pipe_err[:5], "; ".join(str(p[i])[:120] for i in pipe_err[:3]))
    elif mismatch:
        i0 = mismatch[0]
        lp = _leaves(p[i0])
        diff = sorted("%s: %s -> %s" % (k, v[:40], str(lp.get(k))[:40])
                      for k, v in fields[i0].items() if lp.get(k) != v)
        status, why = "FAIL", "pipelined result differs from serial at stable positions %s (%s; %s)" % (
            mismatch[:5], calls[i0][0], "; ".join(diff[:4]))
    elif not stable:
        status, why = "UNMEASURED", "no position returned the same answer twice serially; nothing to compare"
    else:
        status, why = "PASS", "%d/%d pipelined replies answered; %d positions match serial on %d stable fields" % (
            n, n, len(stable), sum(len(fields[i]) for i in stable))
    ms_serial = min(ms_s1, ms_s2)
    return {"status": status, "evidence": why, "n_calls": n, "stable": len(stable),
            "serial_ms": round(ms_serial, 2), "pipelined_ms": round(ms_p, 2),
            "serial_ms_per_call": round(ms_serial / max(1, n), 3),
            "pipelined_ms_per_call": round(ms_p / max(1, n), 3),
            "speedup": round(ms_serial / ms_p, 2) if ms_p > 0 else None,
            "tools": sorted({t for t, _ in calls})}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reps", type=int, default=10, help="batch = reps x tools (default 10)")
    ap.add_argument("--tool", action="append", help="read-only tool, no args (repeat); default %s" %
                    ", ".join(DEFAULT_TOOLS))
    ap.add_argument("--out", help="write the verdict JSON here as well")
    a = ap.parse_args(argv)
    from rimbridge_client import RimBridge, resolve_endpoint
    from transport import TimedTransport
    host, port, token = resolve_endpoint(None, None, None)
    if not token:
        print(json.dumps({"status": "UNMEASURED", "evidence": "no bridge token -- is RimWorld up?"}))
        return 2
    calls = [(t, {}) for _ in range(a.reps) for t in (a.tool or DEFAULT_TOOLS)]
    rb = RimBridge(host, port, token, timeout=60.0)
    with TimedTransport(rb, pipeline=False) as serial:
        pipe = TimedTransport(rb, pipeline=True)      # same socket: pipelining is per call_many
        res = check(serial, pipe, calls)
    text = json.dumps(res, indent=1, sort_keys=True)
    print(text)
    if a.out:
        with open(a.out, "w", newline="\n") as f:
            f.write(text + "\n")
    return {"PASS": 0, "FAIL": 1}.get(res["status"], 2)


if __name__ == "__main__":
    sys.exit(main())
