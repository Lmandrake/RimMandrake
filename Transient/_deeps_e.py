import sys, json; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge
T="4f3c0a7aa74e4446ac19465c14fd54a9"
b=RimBridge(token=T,timeout=90); b.connect()
def call(t,p={}): return b.call(t,p,check=False)
print("switch:", json.dumps(call("jawa/set_current_map",{"mapId":1}))[:150])
mi=call("jawa/map_info",{}); print("map_info:", json.dumps(mi)[:300])
crystals=["RUT_Lanternstone_Small","RUT_Lanternstone_Medium","RUT_Lanternstone_Large","RUT_Lanternstone_Huge"]
flora=["RUT_DeepNuitae","RUT_DeepArpeau","RUT_DeepGreyLady","RUT_DeepDulcisPlant","RUT_Mycelium","RUT_Gleamtip","RUT_Fungusfern","RUT_CrystaltipBrambles","RUT_YumBulbs","RUT_Crystalcap","RUT_LuminousSpout"]
counts={}
for d in crystals+flora+["RUT_LanternstoneWall","RUT_LanternstoneChunk"]:
    r=call("jawa/list_things",{"defName":d,"limit":500}); n=len(r.get("things") or []); counts[d]=n
print("COUNTS:", json.dumps(counts))
pw=call("jawa/list_pawns",{"limit":10}); print("pawns here:", [(q.get("id"),q.get("kind")) for q in (pw.get("pawns") or [])][:6])
