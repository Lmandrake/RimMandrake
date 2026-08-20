import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=300.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
# make sure we are looking at the MAP, not the planet
call("jawa/world_view", show=False)
info = call("rimworld/get_game_info")
# lay a big obvious substructure slab plus a coloured floor patch beside it
print(call("jawa/set_substructure_batch", action="set", rect="100,100,20,20").get("changed"), "substructure cells")
print(call("jawa/set_terrain_layer", layer="under", rect="125,100,10,10", **{"def":"Sand"}).get("changed"), "under-terrain cells")
call("jawa/map_commit")
D = ("LudeonTK.EditWindow_Log","LudeonTK.Dialog_DevPalette","LudeonTK.Dialog_Debug")
for _ in range(4):
    for wt in D: call("rimworld/close_window", windowType=wt)
    if (call("rimworld/get_ui_state").get("windowCount", 9) or 9) <= 1: break
    time.sleep(0.5)
sh = call("rimworld/take_screenshot", fileName="m1_substructure", suppressMessage=True)
print("saved:", sh.get("path"))
