import sys, json, io
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
FAIL=["Pirate","Entities","AM_EnemyPirate","TribalHostile","DP_GenericHostile","Salvagers"]
WORK=["Empire","Mechanoid","Insect","AncientsHostile","HoraxCult"]
defs=";".join("FactionDef/"+f for f in FAIL+WORK)
with RimBridge(host, port, token) as rb:
    r=rb.call("jawa/get_defs", {"defs":defs,
        "fields":"pawnGroupMakers,humanlikeFaction,raidsForbidden,permanentEnemy,hidden,temporary,maxPawnCostPerTotalPointsCurve,techLevel,canUseAvoidGrid,earliestRaidDays,raidArrivalLayerWhitelist,raidArrivalLayerBlacklist,allowedArrivalTemperatureRange,xenotypeSet,pawnGroupMakerKinds"})
with io.open("pgm.json","w",encoding="utf-8") as fh: json.dump(r,fh,indent=1,ensure_ascii=False)
print("KEYS", [k for k in r.keys() if k!="operation"])
print(json.dumps(r, ensure_ascii=False)[:1200])
