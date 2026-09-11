import sys, json, time, shutil, os
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
targets = json.load(open(r"D:\Luke\dev\Rimworld\Transient\final_review\closeup_targets.json"))
host, port, token = resolve_endpoint()
SH = r"D:\Luke\dev\Rimworld\Transient\final_review\shots"
with RimBridge(host, port, token) as rb:
    for name, tile in targets.items():
        rb.call("jawa/world_view", {"centerTile": tile, "altitude": 320, "northUp": True})
        time.sleep(0.7)
        s = rb.call("rimworld/take_screenshot", {})
        shutil.copy(s.get("path") or s.get("filePath"), os.path.join(SH, name + ".png"))
        print(name)
