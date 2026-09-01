# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
DEFS = ";".join("FactionDef/" + d for d in (
    "Jawa_HuttCartel", "Jawa_IndigenousTribes", "Jawa_Junkers",
    "OutlanderCivil", "TribeCivil", "Empire", "Pirate"))
F = ("pawnGroupMakers,xenotypeSet,humanlikeFaction,canStageAttacks,raidsForbidden,"
     "maxPawnCostPerTotalPointsCurve,techLevel,permanentEnemy,hidden,"
     "canUseAvoidGrid,autoFlee,mustStartOneEnemy,allowedArrivalTemperatureRange")
OUT = r"D:\Luke\dev\Rimworld\Transient\sixraid\defs3.json"
with RimBridge(host, port, token, timeout=300) as rb:
    r = rb.call("jawa/get_defs", {"defs": DEFS, "fields": F})
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(r, fh, indent=1, default=str, ensure_ascii=False)
print("->", OUT, "success:", r.get("success"))
