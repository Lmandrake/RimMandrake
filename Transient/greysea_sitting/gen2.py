import sys, json, collections
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h,p,t = rb.resolve_endpoint(); S = rb.RimBridge(host=h,port=p,token=t,timeout=300.0); S.connect()
def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    if isinstance(r, dict): r.pop("operation",None); r.pop("state",None)
    return r
print("REASSERT", call("jawa/static_call", type="RimMandrake.DivingInteraction.RM_SeabedFloorLife", method="ReassertAll"))
print("MDINIT", call("jawa/static_call", type="MapDesigner.HelperMethods", method="InitBiomeDefaults"))
b = call("jawa/biome_probe", biomes="RM_SeabedFloor_GreySea")["biomes"][0]
print("DENS", b["animalDensity"], b["plantDensity"])
best=None
for start in range(0, 119904, 2000):
    r = call("jawa/world_tile_get", range="%d-%d"%(start,start+199), limit=200)
    for tl in r.get("tiles",[]):
        if tl.get("biome")=="Ocean" and (tl.get("elevation") or 0) < -400:
            best=tl; break
    if best: break
print("TILE", best)
g = call("jawa/world_tile_map_generate", tile=best["tile"] if "tile" in best else best["id"], layer="RM_SeabedLayer", biome="RM_SeabedFloor_GreySea")
print("GEN", json.dumps(g)[:700])
