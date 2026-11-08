"""bars2_probe.py -- sanity probe: can the hediff reader see a known-hurt pawn? Prints the health shape of list_pawns
and pawn_health for the first downed/injured player pawn, and for a named pawn id if given."""
import sys
from bars2_common import bridge, log, j

B = bridge()
r = B.call("jawa/list_pawns", includeHealth=True) or {}
ps = r.get("pawns") or []
log("list_pawns n", len(ps), "keys0", sorted((ps[0] if ps else {}).keys()))
want = sys.argv[1:] or []
for p in ps:
    h = p.get("health")
    if p.get("downed") or (p.get("id") in want) or (h and (h.get("hediffs") or h.get("injuries"))):
        log("pawn", p.get("id"), p.get("name"), "downed", p.get("downed"), "health", j(h, 900))
        hh = B.call("jawa/pawn_health", pawn=p.get("id")) or {}
        log("pawn_health", j(hh, 1200))
        break
for w in want:
    hh = B.call("jawa/pawn_health", pawn=w) or {}
    log("pawn_health", w, j(hh, 1500))
