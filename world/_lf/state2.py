import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
print("game_info ->", json.dumps(b.call("rimworld/get_game_info",{}))[:700])
r=b.call("rimworld/list_mods",{})
ms=r.get("mods") or r.get("result",{}).get("mods") or []
act=[m for m in ms if m.get("active") or m.get("isActive")]
print("\nmods listed %d, active %d"%(len(ms),len(act)))
key=[m.get("name","") for m in act if any(k in (m.get("name","")+m.get("packageId","")).lower()
     for k in ("jawa","kotor","guy762","mandrake","galactic","xenotyperemix"))]
print("key active:", key)
