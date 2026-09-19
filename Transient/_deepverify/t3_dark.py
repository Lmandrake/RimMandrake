import sys, json, collections; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,T=resolve_endpoint()
b=RimBridge(token=T,timeout=120); b.connect()
b.call("jawa/set_current_map",{"mapId":4},check=False)
pw=b.call("jawa/list_pawns",{"limit":20},check=False).get("pawns") or []
print("pawns before:",[(q.get("id"),q.get("kind")) for q in pw])
col=[q for q in pw if q.get("id","").startswith("Human")][0]; pid=col["id"]; x,z=int(col["x"]),int(col["z"])
r=b.call("jawa/set_draft",{"pawnId":pid,"drafted":True},check=False); print("draft:",r.get("success"),str(r.get("message"))[:60])
ci=b.call("rimworld/get_cell_info",{"x":x,"z":z},check=False); print("colonist cell glow before:", {k:ci.get(k) for k in ("glow","lightLevel","roofed","terrain")})
ops=";".join("Campfire:%d,%d,1"%(x+dx,z+dz) for dx,dz in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1)))
r=b.call("jawa/spawn_batch",{"ops":ops},check=False); print("campfires:", r.get("spawned"), r.get("thingsSpawned"), str(r.get("message"))[:80])
b.call("rimworld/step_game_ticks",{"ticks":60},check=False)
ci=b.call("rimworld/get_cell_info",{"x":x,"z":z},check=False); print("colonist cell after:", json.dumps({k:v for k,v in ci.items() if k not in ("operation",)})[:300])
th=b.call("jawa/list_things",{"defName":"Campfire","limit":10},check=False)["things"]; print("campfires on map:",len(th))
before={q.get("id") for q in pw}
for i in range(16):
    r=b.call("rimworld/step_game_ticks",{"ticks":1000},check=False)
    logs=(r.get("effects") or {}).get("logs") or []
    bad=[l for l in logs if "Exception" in str(l) or "NullReference" in str(l)]
    if bad: print("EXC at step",i,str(bad[0])[:200])
    pw2=b.call("jawa/list_pawns",{"limit":30},check=False).get("pawns") or []
    new=[q for q in pw2 if q.get("id") not in before]
    if new:
        print("AMBUSH after ~%d ticks:"%((i+1)*1000), [(q.get("id"),q.get("kind"),q.get("mentalState"),q.get("x"),q.get("z")) for q in new]); break
else: print("NO ambush after 16000 ticks")
b.call("rimworld/set_time_speed",{"speed":0},check=False)
