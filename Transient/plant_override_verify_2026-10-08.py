"""DONOR_PLANT_OVERRIDE_VERIFY_1: resolve the live graphic of the four donor (ReGrowth) plants overridden by
UtinniPatches loose PNGs (5cb5cc22e); compares resolved texture size/name to the override files. Run with python.exe."""
import sys, json, time, hashlib
sys.path.insert(0, r"D:\Luke\dev\RimMandrake\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
mode = sys.argv[1]
if mode == "state":
    print(json.dumps(call("rimworld/get_ui_state"))[:400])
elif mode == "start":
    r = call("rimworld/start_debug_game_ready", timeoutMs=300000, readiness="mapData", pauseIfNeeded=True)
    print(json.dumps(r)[:400])
elif mode == "spawn":
    defs = ["Plant_Brambles", "RG_Plant_CreepStern", "RG_Plant_Dervish", "RG_Plant_CrimsonCushion"]
    for i, d in enumerate(defs):
        for k in range(14):
            r = call("rimworld/spawn_thing", defName=d, x=22 + k * 2, z=168 + i * 3)
        print(d, json.dumps(r)[:200])
elif mode == "read":
    r = call("jawa/thing_graphic", rect="15,160,45,25", defs="Plant_Brambles,RG_Plant_CreepStern,RG_Plant_Dervish,RG_Plant_CrimsonCushion", limit=200)
    json.dump(r, open(r"D:\Luke\dev\_rmscratch\plant_override_read.json", "w"), indent=1)
    from collections import defaultdict
    g = defaultdict(set)
    for t in r.get("things", []):
        g[t["defName"]].add((t.get("variantIndex"), t.get("variantPath") or t.get("resolvedPath"), t.get("textureName"), str(t.get("textureSize")), t.get("badTex")))
    for d, s in g.items():
        print(d); [print("   ", x) for x in sorted(s, key=str)]
    print("count", r.get("count"), "complete", r.get("isCompleteList"), "success", r.get("success"))
