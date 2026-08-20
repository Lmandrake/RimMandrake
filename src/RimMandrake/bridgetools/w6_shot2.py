import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
v = call("jawa/world_view", show=True, altitude=1100.0, northUp=True)
print("altitude set:", v.get("altitude"))
time.sleep(1.5)
v2 = call("jawa/world_view", show=True)   # read back after the updater has run
print("altitude after 1.5s of Update():", v2.get("altitude"))
D = ("LudeonTK.EditWindow_Log","LudeonTK.Dialog_DevPalette","LudeonTK.Dialog_Debug")
for _ in range(4):
    for wt in D: call("rimworld/close_window", windowType=wt)
    if (call("rimworld/get_ui_state").get("windowCount", 9) or 9) <= 1: break
    time.sleep(0.6)
sh = call("rimworld/take_screenshot", fileName="w6_whole_planet", suppressMessage=True)
print("saved:", sh.get("path"))
