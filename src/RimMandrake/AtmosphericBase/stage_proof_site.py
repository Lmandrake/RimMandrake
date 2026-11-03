#!/usr/bin/env python3
"""stage_proof_site.py -- build proof_atmosphere.py's MIN_LIT site on the CURRENT quicktest map and save it as
rm_proof_atmosphere, the save `live_site.py --save rm_proof_atmosphere` loads before a live run.

    python.exe src/RimMandrake/AtmosphericBase/stage_proof_site.py [--save rm_proof_atmosphere] [--dry-run]

ATMOSBASE_PROOF_FIX_UNLIT_LEAVES_DARK_LAMP: its live clause A1 ran on a quicktest map with no lamps (R2.left_as_found
UNMEASURED SITE, "only 0 lit fixtures over 0 cells (need 10 over 8)"), and the save its site line names did not exist.
This makes one: LAMPS player-owned StandingLamps (flickable, CompPowerTrader, CompGlower: what RM_EmitterDiscovery
calls Eligible) in a row, one cell apart so they spread over LAMPS distinct cells, a conduit under each, joined to two
fuelled chemfuel generators, then reads back that every lamp is powered and glowing before it saves. Exit 0 saved,
2 the site could not be made (never 1: a site is not a verdict). Refuses a game past --max-ticks: a test map only.
Runs under Windows Python: RimBridge binds Windows loopback.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
import rimbridge_client as C  # noqa: E402

LAMPS = 14                 # > proof_atmosphere.MIN_LIT (10) so one dark lamp still leaves the site usable
X0, Z0 = 110, 120          # the row starts here, inside a 250x250 quicktest map (clear_area empties the strip first)
GEN = "ChemfuelPoweredGenerator"


def ops():
    """-> (generator ops, conduit ops, lamp ops) for build_batch. Pure."""
    gens = "%s:%d,%d,0;%s:%d,%d,0" % (GEN, X0 - 6, Z0 + 3, GEN, X0 - 3, Z0 + 3)   # off the conduit row, in wire reach
    conduits = ";".join(["PowerConduit:%d,%d" % (x, Z0) for x in range(X0 - 7, X0 + 2 * LAMPS)]
                        # a generator is its own transmitter: without a link its 2x2 (z Z0+3..Z0+4) is a net of one
                        + ["PowerConduit:%d,%d" % (x, z) for x in (X0 - 6, X0 - 3) for z in (Z0 + 1, Z0 + 2)])
    lamps = ";".join("StandingLamp:%d,%d" % (X0 + 2 * i, Z0) for i in range(LAMPS))
    return gens, conduits, lamps


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--save", default="rm_proof_atmosphere")
    ap.add_argument("--max-ticks", type=int, default=120000)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    gens, conduits, lamps = ops()
    if a.dry_run:
        print("\n".join((gens, conduits, lamps)))
        return 0
    h, p, t = C.resolve_endpoint()
    rb = C.RimBridge(h, p, t)
    rb.connect()
    mi = rb.call("jawa/map_info", {})
    if int(mi.get("ticksGame") or 0) > a.max_ticks:
        print("refused: the game is %s ticks old, past --max-ticks %d: a colony, not a test map" % (mi.get("ticksGame"), a.max_ticks))
        return 2
    rb.call("jawa/clear_area", {"rect": "%d,%d,%d,%d" % (X0 - 8, Z0 - 2, 2 * LAMPS + 10, 8), "dryRun": False}, check=False)
    for o, over in ((conduits, False), (gens, True), (lamps, True)):   # conduits first; nothing built later eats one
        r = rb.call("jawa/build_batch", {"ops": o, "faction": "player", "refuseIfDisplaces": over})
        print("build_batch: survived %s, displaced %s" % (r.get("survived"), len(r.get("displaced") or [])))
    for g in (rb.call("jawa/list_things", {"defName": GEN}).get("things") or []):
        rb.call("jawa/thing_refuel", {"thingId": g.get("thingId") or g.get("id"), "amount": 1000})
    rb.call("jawa/map_commit", {})
    lit = 0
    found = rb.call("jawa/list_things", {"defName": "StandingLamp"}).get("things") or []
    for l in found:
        tid = l.get("thingId") or l.get("id")
        # a paused game never ticks the net, so a fresh lamp waits on a restart that never comes: switch it on through
        # the comp (the setter no-ops, read back, when the net cannot carry it), then read the net's source
        pn = rb.call("jawa/power_net", {"thing": tid, "forcePowerOn": True})
        on = pn.get("powerOnAfter") and (pn.get("net") or {}).get("hasPowerSource")
        print("%s powerOn=%s net=%s" % (tid, pn.get("powerOnAfter"), pn.get("net")))
        lit += bool(on)
    if lit < LAMPS:
        print("site not made: %d of %d lamps powered (%d StandingLamps found)" % (lit, LAMPS, len(found)))
        return 2
    rb.call("rimworld/save_game", {"saveName": a.save})
    print("saved %s: %d powered StandingLamps over %d cells" % (a.save, lit, LAMPS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
