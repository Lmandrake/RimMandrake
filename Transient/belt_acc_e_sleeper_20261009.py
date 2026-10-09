import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
out={}
out["map"]=str(S.call("jawa/time_clock"))[:200]
with S.Scene("sleepe",40,40,14,8) as sc:
    try:
        sc.put("RM_SleeperVenomvine",2,2)
        sc.put("RM_SleeperVenomvine",10,2)
        out["hare_pawn"]=str(sc.pawn("Hare",3,2))[:80]
        out["col"]=str(sc.colonist(9,2))[:80]
        out["things0"]=[json.dumps(t)[:160] for t in (sc.things().get("things") or [])]
        sc.hare_ok=True
        S.run(300)
        out["things1"]=[json.dumps(t)[:160] for t in (sc.things().get("things") or [])]
    except Exception as e: out["ERR"]=str(e)[:300]
print(json.dumps(out,default=str))
