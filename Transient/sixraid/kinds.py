# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
KINDS = []
for pre in ("Hutt", "TradeMoot", "Junkers", "Helix", "Wildsteam", "Geonosian",
            "Droid", "Deepwater", "Empire", "DeepDesert", "Homestead"):
    for role in ("Grunt", "Heavy", "Specialist", "Leader"):
        KINDS.append("Jawa_%s_%s" % (pre, role))
KINDS += ["Jawa_Tribal_Scavenger", "Jawa_Tribal_Slinger", "Jawa_Tribal_Elder",
          "Mercenary_Gunner", "Town_Guard"]
DEFS = ";".join("PawnKindDef/" + k for k in KINDS)
with RimBridge(host, port, token, timeout=300) as rb:
    r = rb.call("jawa/get_defs", {"defs": DEFS,
                "fields": "isFighter,combatPower,useFactionXenotypes,factionLeader,maxPerGroup,defaultFactionDef,race",
                "limit": 300})
print("found:", r.get("foundCount"), "notFound:", json.dumps(r.get("notFound"))[:900])
bad = []
for row in r.get("defs", []):
    if not row.get("found"):
        bad.append(row.get("requested")); continue
    f = row["fields"]
    print("%-30s isFighter=%s cp=%s useFacXeno=%s leader=%s race=%s" % (
        row["defName"], f.get("isFighter"), f.get("combatPower"),
        f.get("useFactionXenotypes"), f.get("factionLeader"), f.get("race")))
print("MISSING:", bad)
