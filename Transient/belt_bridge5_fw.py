import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
def j(x,n=600): return json.dumps(x,default=str)[:n]
K=["RM_Lommerel","RM_Silloch","RM_Brathek","RM_Nemmel","RM_Grolth","RM_Gorrameth","RM_Skreth","RM_SkrethMatron"]
ids=[]
for i,k in enumerate(K):
    r=S.call("jawa/spawn_pawn", kindDef=k, x=30+i*8, z=120, faction="none", count=1)
    ids.append(((r.get("pawns") or [{}])[0]).get("id")); print("spawn",k,r.get("success"),ids[-1], j(r.get("message"),100))
S.run(10)
r=S.call("jawa/thing_graphic", rect="25,115,70,12")
for t in r.get("things") or r.get("results") or []:
    if t.get("id") in ids or t.get("thingId") in ids or any((t.get("def") or t.get("defName") or "")==k for k in K):
        print("GFX", j(t,500))
print("keys", list(r.keys()))
f=S.call("jawa/faction_relations_get", faction="RM_FactionDef_SkrethBrood", other="RM_FactionDef_KurrethSwarm")
print("REL", j(f,1200))
