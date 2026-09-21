import sys, json, time, collections; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge
T=open(r"Transient\_bridge_token.txt").read().strip()
def B(t=60): b=RimBridge(token=T,timeout=t); b.connect(); return b
b=B(25)
import json as _j; print("pawn keys:", list(b.call("jawa/list_pawns",{"faction":"player","limit":1},check=False)["pawns"][0].keys())[:14])
pass

for i in range(12):
    time.sleep(5)
    try:
        b=B(); r=b.call("jawa/map_info",{},check=False)
        if r.get("success"): print("surface map ready ~%ds"%((i+1)*5)); break
    except Exception as e: pass
b=B()
p=b.call("jawa/list_pawns",{"faction":"player","limit":3},check=False)["pawns"][0]
pid=p["id"]; x,z=int(p.get("x",p.get("pos",{}).get("x",125))),int(p.get("z",p.get("pos",{}).get("z",125)))
b.call("jawa/spawn_batch",{"ops":"RUT_LanternDeepEmergence:%d,%d,1"%(x+6,z)},check=False)
tid=b.call("jawa/list_things",{"defName":"RUT_LanternDeepEmergence","limit":1},check=False)["things"][0]["id"]
r=b.call("jawa/ordered_job",{"pawnId":pid,"jobDef":"EnterPortal","targetAId":tid},check=False); print("job accepted:", r.get("accepted"))
for i in range(8):
    b.call("rimworld/step_game_ticks",{"ticks":1500},check=False)
    r=b.call("jawa/set_current_map",{"mapId":999},check=False)
    maps=(r.get("details") or {}).get("loadedMaps") or []
    deep=[m for m in maps if m.get("biome")=="RUT_LanternDeeps"]
    if deep: print("pocket map:", deep[0]); break
if not deep: sys.exit("no pocket map")
b.call("jawa/set_current_map",{"mapId":deep[0]["mapId"]},check=False)
r=b.call("jawa/list_things",{"limit":6000},check=False); things=r.get("things") or []
c=collections.Counter(t.get("def") for t in things)
print("TOTAL:",len(things)); print("by def:", dict(c.most_common(30)))
