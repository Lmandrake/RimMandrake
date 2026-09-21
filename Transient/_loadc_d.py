import sys, json, time, collections, re; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge
T="0370ddcc7f524e24a54e6cff36301136"
def B(t=90): b=RimBridge(token=T,timeout=t); b.connect(); return b
b=B()
p=b.call("jawa/list_pawns",{"faction":"player","limit":3},check=False)["pawns"][0]
pid=p["id"]; x,z=int(p["x"]),int(p["z"]); print("colonist",pid,p.get("name"),"at",x,z)
b.call("jawa/spawn_batch",{"ops":"RUT_LanternDeepEmergence:%d,%d,1"%(x+6,z)},check=False)
th=b.call("jawa/list_things",{"defName":"RUT_LanternDeepEmergence","limit":1},check=False)["things"]
if not th: sys.exit("portal not spawned")
tid=th[0]["id"]; print("portal",tid)
r=b.call("jawa/ordered_job",{"pawnId":pid,"jobDef":"EnterPortal","targetAId":tid},check=False); print("job accepted:", r.get("accepted"), r.get("message"))
deep=None
for i in range(10):
    b.call("rimworld/step_game_ticks",{"ticks":1500},check=False)
    r=b.call("jawa/set_current_map",{"mapId":999},check=False)
    maps=(r.get("details") or {}).get("loadedMaps") or []
    deep=[m for m in maps if m.get("biome")=="RUT_LanternDeeps"]
    if deep: print("pocket map after ~%d ticks:"%((i+1)*1500), deep[0]); break
if not deep: sys.exit("no pocket map; maps="+json.dumps(maps)[:300])
b.call("jawa/set_current_map",{"mapId":deep[0]["mapId"]},check=False)
b.call("rimworld/step_game_ticks",{"ticks":600},check=False)
r=b.call("jawa/list_things",{"limit":6000},check=False); things=r.get("things") or []
c=collections.Counter(t.get("def") for t in things)
print("TOTAL:",len(things)); print("by def:", dict(c.most_common(30)))
pw=b.call("jawa/list_pawns",{"limit":10},check=False); print("pawns on Deep:", [(q.get("id"),q.get("kind")) for q in (pw.get("pawns") or [])][:6])
