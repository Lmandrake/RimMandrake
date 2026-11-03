#!/usr/bin/env python3
"""BRIDGE_STALL_DIAGNOSTIC_1, client half: a bridge call that blocked >= STALL_DUMP_SECONDS names on its evidence
`end` row the stall dumps the companion's watchdog wrote while it waited (JawaBenchStallDump.cs writes them; its own
proof is the C# units StallDumpDecision / StallDumpAt60s in selftest_tps_record.py).

Offline: a temp stall dir, a temp evidence log, the transport replaced, the clock moved by hand. No game, no socket.
"""
import json
import os
import re
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rimbridge_client as rc  # noqa: E402

FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)


def parity():
    cs = os.path.join(HERE, "..", "bridgetools", "JawaBench.BridgeTools", "JawaBenchStallDump.cs")
    m = re.search(r"internal const double DumpSeconds = ([0-9.]+);", open(cs, encoding="utf-8").read())
    check(m is not None, "DumpSeconds not found in JawaBenchStallDump.cs")
    if m:
        check(float(m.group(1)) == rc.STALL_DUMP_SECONDS,
              "client STALL_DUMP_SECONDS %r != companion DumpSeconds %s" % (rc.STALL_DUMP_SECONDS, m.group(1)))


def fields(d):
    os.environ["RIMBRIDGE_STALL_DIR"] = d
    t0 = 1_000_000.0
    old, new = os.path.join(d, "stall_aaaa_01.json"), os.path.join(d, "stall_bbbb_01.json")
    for p, mt in ((old, t0 - 600), (new, t0 + 61)):
        open(p, "w").write("{}")
        os.utime(p, (mt, mt))
    open(os.path.join(d, "hb_bbbb.json"), "w").write("{}")
    check(rc._stall_fields(t0, now=t0 + 59.9) == {}, "a call under 60 s carries no stall fields")
    f = rc._stall_fields(t0, now=t0 + 61)
    check(f.get("stall_dumps") == ["stall_bbbb_01.json"], "only the dump written during the call is named: %r" % f)
    check(f.get("stall_dir") == d and "stall_note" not in f, "dir named, no note when a dump exists: %r" % f)
    os.utime(new, (t0 - 10, t0 - 10))
    f = rc._stall_fields(t0, now=t0 + 61)
    check(f.get("stall_dumps") == [] and "no stall dump" in f.get("stall_note", ""), "none -> an empty list and why: %r" % f)
    os.environ["RIMBRIDGE_STALL_DIR"] = os.path.join(d, "missing")
    f = rc._stall_fields(t0, now=t0 + 61)
    check("unreadable" in f.get("stall_note", ""), "a missing dir is said, not raised: %r" % f)


def end_to_end(d):
    """Through RimBridge.call: the real end-row composition, a reply that took 61 s by the module's clock."""
    sd = os.path.join(d, "tps")
    os.makedirs(sd)
    os.environ["RIMBRIDGE_STALL_DIR"] = sd
    rc.EVIDENCE_LOG = os.path.join(d, "bridge_calls.jsonl")
    real = time.time
    clock = [real()]
    rc.time.time = lambda: clock[0]
    try:
        b = rc.RimBridge()

        def slow_ok(method, params=None):
            clock[0] += 61.0
            p = os.path.join(sd, "stall_cccc_01.json")
            open(p, "w").write("{}")
            os.utime(p, (clock[0] - 5, clock[0] - 5))
            return {"success": True}

        def slow_timeout(method, params=None):
            clock[0] += 300.0
            p = os.path.join(sd, "stall_cccc_02.json")
            open(p, "w").write("{}")
            os.utime(p, (clock[0] - 200, clock[0] - 200))
            raise rc.RimBridgeError("read timed out after 300 s")

        def fast(method, params=None):
            clock[0] += 0.2
            return {"success": True}

        b._request = slow_ok
        b.call("jawa/get_map_info", {}, check=False)
        b._request = slow_timeout
        try:
            b.call("jawa/get_map_info", {}, check=False)
        except rc.RimBridgeError:
            pass
        b._request = fast
        b.call("jawa/get_map_info", {}, check=False)
    finally:
        rc.time.time = real
    rows = [json.loads(x) for x in open(rc.EVIDENCE_LOG, encoding="utf-8")]
    ends = [r for r in rows if r.get("ev") == "end"]
    check(len(ends) == 3, "three end rows: %d" % len(ends))
    if len(ends) == 3:
        check(ends[0].get("stall_dumps") == ["stall_cccc_01.json"], "a 61 s ok call names its dump: %r" % ends[0])
        check(ends[1].get("outcome") == "timeout" and ends[1].get("stall_dumps") == ["stall_cccc_02.json"],
              "a 300 s timeout names the dump written during it: %r" % ends[1])
        check("stall_dumps" not in ends[2], "a fast call carries no stall fields: %r" % ends[2])


def main():
    parity()
    with tempfile.TemporaryDirectory() as d:
        fields(d)
    with tempfile.TemporaryDirectory() as d:
        end_to_end(d)
    for f in FAILS:
        print("FAIL", f)
    print("selftest_bridge_stall_client: %s (%d failures)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
