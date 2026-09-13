import sys, time, shutil, os
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
SH = r"D:\Luke\dev\Rimworld\Transient\final_review\beauty"
comps = [
  ("E_cap_portrait",  14301, 300),   # the lake tight
  ("F_cap_and_ring",  14301, 1100),  # cap wide, ring + shadow
  ("G_night_limb",    8110, 800),    # nightside ladder with cap at limb
]
with RimBridge(host, port, token) as rb:
    for name, tile, alt in comps:
        rb.call("jawa/world_view", {"centerTile": tile, "altitude": alt, "northUp": True})
        time.sleep(1.5)
        s = rb.call("rimworld/take_screenshot", {"suppressMessage": True})
        shutil.copy(s.get("path") or s.get("filePath"), os.path.join(SH, name + ".png"))
        print(name)
        time.sleep(1.2)
