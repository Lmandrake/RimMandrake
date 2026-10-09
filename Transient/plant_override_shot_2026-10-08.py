"""Clear the patch, respawn the four donor plants spaced out, frame and screenshot (confirmation of the state read)."""
import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\RimMandrake\src\RimMandrake\Utils")
import rimbridge_client as rb
h,p,t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=120.0); S.connect()
def call(n, **k):
    r = S.call(n, k) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
print(json.dumps(call("jawa/destroy_batch", rects="15,164,45,18", categories="Plant"))[:200])
defs = ["Plant_Brambles", "RG_Plant_CreepStern", "RG_Plant_Dervish", "RG_Plant_CrimsonCushion"]
for i, d in enumerate(defs):
    for k in range(10):
        call("rimworld/spawn_thing", defName=d, x=22 + k * 3, z=168 + i * 3)
print(json.dumps(call("jawa/clear_ui"))[:80])
print(json.dumps(call("rimworld/jump_camera_to_cell", x=36, z=172.5 if False else 172))[:60])
print(json.dumps(call("rimworld/set_camera_zoom", rootSize=11))[:60])
time.sleep(6)
print(json.dumps(call("rimworld/take_screenshot", fileName="plant_override_verify_2026-10-08"))[:200])
