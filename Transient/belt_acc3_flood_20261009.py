import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
W=100
walk={}
for x0 in range(0,W,25):
    for z0 in range(0,W,25):
        off=0
        while True:
            r=S.call("rimworld/get_cells_info",x=x0,z=z0,width=25,height=25,offset=off)
            for c in r["cells"]: walk[(c["x"],c["z"])]=c["walkable"]
            pg=r["page"]; off+=pg["returned"]
            if off>=pg["total"] or pg["returned"]==0: break
print("cells",len(walk),"walkable",sum(walk.values()))
start=(50,50)
seen={start}; st=[start]
while st:
    x,z=st.pop()
    for dx,dz in((1,0),(-1,0),(0,1),(0,-1)):
        n=(x+dx,z+dz)
        if n in walk and walk[n] and n not in seen: seen.add(n); st.append(n)
print("reached",len(seen))
res=[]
for d in ["RM_BrineElder","RM_GreyFloorWreckHull","RM_GreyFloorWreckSpine"]:
    r=S.call("jawa/list_things",defName=d,limit=100)
    for t in r.get("things",[]):
        pos=t.get("position") or t.get("cell") or t
        res.append((d,{k:t.get(k) for k in ("position","cell","x","z","size","rect")}))
print(json.dumps(res)[:1500])
json.dump({"walk":[list(k)+[v] for k,v in walk.items()],"seen":[list(s) for s in seen]},open("Transient/belt_acc3_flood_20261009.json","w"))
