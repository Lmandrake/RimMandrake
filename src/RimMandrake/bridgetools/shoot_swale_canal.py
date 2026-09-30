"""SWALE_CANAL_ART_REFERENCE_1: regenerate the debug map as RM_FloodedCanyon, cut a real FlowWorks
channel (RM_MapComponent_Excavation Deepen/TrySetDriverFill via jawa/flowworks_excavation_drive) in
three segments - dry, half-filled, full - and screenshot it at review zoom.
Windows python.exe, repo root: python.exe src/RimMandrake/bridgetools/shoot_swale_canal.py"""
import sys, json, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=300.0); S.connect()
def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    if isinstance(r, dict): r.pop("operation", None)
    return r
tile = call("jawa/map_info").get("tile")
call("jawa/world_tile_set", tiles=str(tile), biome="RM_FloodedCanyon", hilliness="Flat"); call("jawa/world_commit")
call("rimworld/execute_debug_action", path=r"Actions\Regenerate Current Map"); time.sleep(5)
for _ in range(100):
    if call("rimworld/get_ui_state").get("programState") == "Playing": break
    time.sleep(3)
X0, Z0 = 110, 120
call("jawa/clear_area", rect="%d,%d,%d,%d" % (X0 - 3, Z0 - 6, 36, 14))
cells = []
for i in range(30):                       # a gentle S-curve, 3 wide
    zc = Z0 + (0 if i < 10 else (1 if i < 20 else 2))
    for w in (-1, 0, 1): cells.append((X0 + i, zc + w, i))
res = {"dry": 0, "half": 0, "full": 0}
for x, z, i in cells:
    seg = "dry" if i < 10 else ("half" if i < 20 else "full")
    fill = {"dry": 0, "half": 1, "full": 2}[seg]
    r = call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=2, setFill=fill)
    if r.get("success"): res[seg] += 1
print("dug:", res, "sample report:", json.dumps(call("jawa/canal_cell_report", x=X0 + 25, z=Z0 + 2))[:300])
call("rimworld/step_game_ticks", ticks=60, timeoutMs=60000)
shots = []
for name, (x, w) in {"swale_all": (X0 - 2, 34), "swale_dry": (X0, 10), "swale_half": (X0 + 10, 10), "swale_full": (X0 + 20, 10)}.items():
    s = call("rimworld/screenshot_cell_rect", x=x, z=Z0 - 3, width=w, height=8, paddingCells=2, fileName=name)
    shots.append((name, s.get("path") or s.get("filePath") or s.get("savedPath") or str(s)[:200]))
for s in shots: print(s)
