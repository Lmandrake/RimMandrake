import sys, json, time, shutil, os
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
targets = json.load(open(r"D:\Luke\dev\Rimworld\Transient\final_review\stare_targets.json"))
host, port, token = resolve_endpoint()
SH = r"D:\Luke\dev\Rimworld\Transient\final_review\shots"
with RimBridge(host, port, token) as rb:
    rb.call("rimworld/close_window", {"windowType": "LudeonTK.Dialog_DevPalette"})
    for name, tile in targets.items():
        rb.call("jawa/world_view", {"centerTile": tile, "altitude": 900, "northUp": True})
        time.sleep(0.7)
        s = rb.call("rimworld/take_screenshot", {})
        src = s.get("path") or s.get("filePath")
        wsl = src.replace("C:\\", "/mnt/c/").replace("\\", "/")
        # copy on the python.exe side is fine with the D: path
        shutil.copy(src, os.path.join(SH, name + ".png"))
        print(name, "->", name + ".png")
