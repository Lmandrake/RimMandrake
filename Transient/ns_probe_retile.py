import sys, json, time, os
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h,p,t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=240.0); S.connect()
def call(tool, **kw):
    r = S.call(tool, kw) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
def tile(n):
    r = call("jawa/world_tile_get", tiles=str(n)); x = r["tiles"][0]; return (x["biome"], x["temperature"], x["elevation"])
T = 7540
print("before", tile(T))
if tile(T)[0] != "RM_Pyrelands":
    call("jawa/world_tile_set", tiles=str(T), biome="RM_Pyrelands", temperature=50, rainfall=0, elevation=257); call("jawa/world_commit")
print("after set", tile(T))
name = "NS_probe_retile_persist"
call("rimworld/save_game", saveName=name); time.sleep(8)
print("saved?", os.path.exists(os.path.join(os.environ["USERPROFILE"], "AppData", "LocalLow", "Ludeon Studios", "RimWorld by Ludeon Studios", "Saves", name + ".rws")))
try: call("rimworld/load_game", saveName=name)
except Exception as ex: print("load raised", type(ex).__name__)
time.sleep(25)
t0=time.time()
while time.time()-t0<200:
    try:
        mi = call("jawa/map_info")
        if mi.get("success"): break
    except Exception: pass
    time.sleep(3)
print("after load", tile(T))
