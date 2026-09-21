import sys, json, time; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge
T="4f3c0a7aa74e4446ac19465c14fd54a9"
b=RimBridge(token=T,timeout=60); b.connect()
def call(t,p={}):
    r=b.call(t,p,check=False); return r
print("step:", json.dumps(call("rimworld/step_game_ticks",{"ticks":1500}))[:200])
for i in range(6):
    r=call("jawa/set_current_map",{"mapId":999})  # refused: lists loaded maps
    print("maps:", json.dumps(r)[:400])
    if '"mapId": 1' in json.dumps(r) or "RUT_LanternDeeps" in json.dumps(r) or "1" in str((r or {}).get("loadedMaps","")): break
    print("step:", json.dumps(call("rimworld/step_game_ticks",{"ticks":1500}))[:120])
p=call("jawa/list_pawns",{"faction":"player","limit":5})
print("pawns on current map:", [(q.get("id"),q.get("job") or q.get("curJob")) for q in (p.get("pawns") or [])][:4])
