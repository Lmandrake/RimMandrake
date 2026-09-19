import sys, json, time, collections; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,T=resolve_endpoint()
def B(t=120): b=RimBridge(token=T,timeout=t); b.connect(); return b
b=B()
b.call("rimworld/set_time_speed",{"speed":0},check=False)
home=b.call("jawa/map_info",{},check=False); print("home map:", {k:home.get(k) for k in ("mapId","biome","size","tile")})
pawns=b.call("jawa/list_pawns",{"faction":"player","limit":4},check=False)["pawns"]
p1,p2=pawns[0],pawns[1]; print("colonists", [(q["id"],q.get("name"),q["x"],q["z"]) for q in (p1,p2)])
x,z=int(p1["x"]),int(p1["z"])
b.call("jawa/spawn_batch",{"ops":"RUT_LanternDeepEmergence:%d,%d,1;RUT_LanternDeepMineshaft:%d,%d,1"%(x+6,z,x-6,z)},check=False)
em=b.call("jawa/list_things",{"defName":"RUT_LanternDeepEmergence","limit":2},check=False)["things"]
ms=b.call("jawa/list_things",{"defName":"RUT_LanternDeepMineshaft","limit":2},check=False)["things"]
print("emergence:",[(t["id"],t.get("x"),t.get("z")) for t in em]); print("mineshaft:",[(t["id"],t.get("x"),t.get("z")) for t in ms])
if not em or not ms: sys.exit("portal missing")
def maps():
    r=b.call("jawa/set_current_map",{"mapId":999},check=False); return (r.get("details") or {}).get("loadedMaps") or []
def enter(pid,tid,label):
    r=b.call("jawa/ordered_job",{"pawnId":pid,"jobDef":"EnterPortal","targetAId":tid},check=False); print(label,"job accepted:",r.get("accepted"),str(r.get("message"))[:80])
    before={m["mapId"] for m in maps()}
    for i in range(12):
        b.call("rimworld/step_game_ticks",{"ticks":1500},check=False)
        new=[m for m in maps() if m["mapId"] not in before]
        if new: print(label,"NEW map after ~%d ticks:"%((i+1)*1500), new[0]); return new[0]
    print(label,"NO new map; maps=",json.dumps(maps())[:300]); return None
d1=enter(p1["id"],em[0]["id"],"EMERGENCE")
d2=enter(p2["id"],ms[0]["id"],"MINESHAFT")
for d,label in ((d1,"EMERGENCE"),(d2,"MINESHAFT")):
    if not d: continue
    b.call("jawa/set_current_map",{"mapId":d["mapId"]},check=False)
    th=b.call("jawa/list_things",{"limit":6000},check=False).get("things") or []
    c=collections.Counter(t.get("def") for t in th)
    pw=b.call("jawa/list_pawns",{"limit":10},check=False).get("pawns") or []
    print(label,"deep mapId",d["mapId"],"things",len(th),"lanternstone walls",c.get("RUT_LanternstoneWall",0),"formations",sum(v for k,v in c.items() if "Formation" in (k or "")),"plants",sum(v for k,v in c.items() if k and k.startswith("RUT_") and any(s in k for s in ("Puffer","Thrakk","Ossk","Vellok","Prenna","Nurrik","Quorr","Zivvit","Kuvra","Brellik"))))
    print(label,"pawns on deep:",[(q.get("id"),q.get("kind"),q.get("name")) for q in pw])
print("ALL MAPS:", [(m["mapId"],m.get("biome")) for m in maps()])
