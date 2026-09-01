# -*- coding: utf-8 -*-
"""Discriminator: vanilla FactionDef + OUR pawnkinds  vs  our FactionDef + our pawnkinds."""
import sys, io, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

CASES = ["Empire", "Pirate", "OutlanderCivil", "TribeCivil",
         "Jawa_IndigenousTribes", "Jawa_HuttCartel"]

def census(rb):
    r = rb.call("jawa/list_pawns", {"limit": 500})
    c = collections.Counter()
    for p in r.get("pawns", []):
        c[p.get("faction")] += 1
    return c, r.get("totalOnMap")

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for F in CASES:
        rb.call("jawa/faction_relations_set", {"faction": F, "other": "Player", "kind": "Hostile"})
        before, nb = census(rb)
        f = rb.call("jawa/fire_raid", {"points": 3000, "faction": F, "dryRun": False,
                                       "strategy": "ImmediateAttack", "arrivalMode": "EdgeWalkIn"})
        after, na = census(rb)
        kinds = collections.Counter()
        r = rb.call("jawa/list_pawns", {"limit": 500, "faction": F})
        for p in r.get("pawns", []):
            kinds[p.get("kindDef")] += 1
        print("%-24s executed=%s substituted=%s arrived=%s  pawns %s->%s kinds=%s" % (
            F, f.get("executed"), f.get("actual", {}).get("substituted"),
            json.dumps(f.get("arrived")), nb, na, dict(kinds)))
        rb.call("jawa/destroy_bulk", {"filter": "nonColonists", "dryRun": False})
        rb.call("jawa/faction_relations_set", {"faction": F, "other": "Player", "kind": "Neutral", "goodwill": 0})
