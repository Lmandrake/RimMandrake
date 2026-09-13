import sys, time, shutil, os
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
SH = r"D:\Luke\dev\Rimworld\Transient\final_review\beauty"
os.makedirs(SH, exist_ok=True)
comps = [
  ("A_crater_portrait", 11942, 240),
  ("B_scald_and_seas",  11817, 460),   # centered between Scald and Twilight Sea
  ("C_ring_wide",       11942, 1400),  # wide, ring in frame
  ("D_limb_drama",      8160, 700),    # Scald toward the limb
]
with RimBridge(host, port, token) as rb:
    rb.call("rimworld/close_window", {"windowType": "RimWorld.WorldInspectPane"})
    rb.call("jawa/clear_ui", {})
    for name, tile, alt in comps:
        v = rb.call("jawa/world_view", {"centerTile": tile, "altitude": alt, "northUp": True})
        time.sleep(1.5)
        s = rb.call("rimworld/take_screenshot", {"suppressMessage": True})
        shutil.copy(s.get("path") or s.get("filePath"), os.path.join(SH, name + ".png"))
        print(name, "alt", alt, "->", v.get("altitude"))
        time.sleep(1.2)
