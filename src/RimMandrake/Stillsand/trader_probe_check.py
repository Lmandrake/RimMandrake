#!/usr/bin/env python3
"""trader_probe_check.py -- can a vanilla trade caravan arrive on the RUNNING Stillsand map? One read-only call.

    python.exe src/RimMandrake/Stillsand/trader_probe_check.py < /dev/null

Item HORIZON_CARAVAN_VANILLA_REFUSES_1, criterion A1. It calls jawa/static_call on
RimMandrake.Stillsand.RM_StillsandTraderProbe.Report("-"), which runs the engine's own predicates
(IncidentWorker_TraderCaravanArrival.FactionCanBeGroupSource, PawnGroupMaker.CanGenerateFrom against the tile
biome's allowedPackAnimals, RCellFinder.TryFindRandomPawnEntryCell) on Find.CurrentMap and changes nothing.

Exit 0: the current map is RM_Stillsand, an entry cell exists and generable >= 1 (a faction is a group source with a
Trader group the engine would generate here). Exit 1: the game answered for an RM_Stillsand map and one of those is
false (a real FAIL). Exit 2 UNMEASURED: no bridge, no answer, no current map, or the map is not RM_Stillsand.

The type and method are fixed: this script can run that one read-only probe and nothing else, which is why it calls the
bridge library directly instead of the CLI (whose read-only heuristic does not know static_call targets).
RimBridge binds Windows loopback, so it runs under Windows Python (python.exe), as rimbridge_client.py says.
"""
import os
import re
import sys

PASS, FAIL, UNMEASURED = 0, 1, 2
TYPE = "RimMandrake.Stillsand.RM_StillsandTraderProbe"
METHOD = "Report"
LINE = re.compile(r"^TRADERS biome=(?P<biome>\S+) entryCell=(?P<entry>True|False) source=(?P<source>\d+) "
                  r"desperate=(?P<desp>\d+) generable=(?P<gen>\d+)\b")


def verdict(reply):
    """bridge reply -> (exit code, one line). Pure: the selftest drives it with canned replies."""
    if not isinstance(reply, dict) or reply.get("success") is False:
        return UNMEASURED, "UNMEASURED: the probe did not answer: %s" % str(reply)[:200]
    res = str(reply.get("result", "")).strip()
    m = LINE.match(res)
    if not m:
        return UNMEASURED, "UNMEASURED: not a TRADERS line: %s" % res[:200]
    if m.group("biome") != "RM_Stillsand":
        return UNMEASURED, "UNMEASURED: the current map is %s, not RM_Stillsand" % m.group("biome")
    if m.group("entry") != "True":
        return FAIL, "FAIL: no pawn entry cell on the Stillsand map: %s" % res[:400]
    if int(m.group("gen")) < 1:
        return FAIL, "FAIL: no faction can send a trade caravan here (generable=0): %s" % res[:400]
    return PASS, "PASS: %s" % res[:400]


def main():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
    try:
        import rimbridge_client as rc
        host, port, token = rc.resolve_endpoint(None, None, None, None)
        if not token:
            print("UNMEASURED: no bridge token found")
            return UNMEASURED
        with rc.RimBridge(host, port, token, timeout=60) as rb:
            reply = rb.call("jawa/static_call", {"type": TYPE, "method": METHOD, "args": "-"})
    except Exception as e:      # any bridge or import failure is ignorance, never a FAIL
        print("UNMEASURED: bridge call failed: %s" % str(e)[:200])
        return UNMEASURED
    code, line = verdict(reply)
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
