"""Close-up screenshot of a cell rect (python.exe; run from repo root).
Usage: shoot.py name cx cz rootSize [name cx cz rootSize ...]   (cx,cz = centre cell, may be fractional)"""
import sys, time, json
sys.path.insert(0, "src/RimMandrake/Utils")
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint()
B = rb.RimBridge(host=h, port=p, token=t, timeout=120.0)
B.connect()
def call(tool, kw):
    r = B.call(tool, kw, check=False) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
a = sys.argv[1:]
call("jawa/clear_ui", {"all": True})
call("jawa/screenshot_mode", {"enabled": True})
for i in range(0, len(a), 4):
    name, cx, cz, rs = a[i], float(a[i+1]), float(a[i+2]), float(a[i+3])
    call("rimworld/jump_camera_to_cell", {"x": int(cx), "z": int(cz)})
    call("rimworld/set_camera_zoom", {"rootSize": rs})
    time.sleep(1.5)
    r = call("jawa/take_screenshot", {"fileName": name})
    print(name, (r.get("filePath") or r.get("message")) if isinstance(r, dict) else r)
    time.sleep(2.5)
call("jawa/screenshot_mode", {"enabled": False})
