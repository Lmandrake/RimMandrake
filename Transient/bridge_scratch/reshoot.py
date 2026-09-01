import sys, json, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
rb = RimBridge(host, port, token, timeout=600.0); rb.connect()
def call(t, **p):
    r = rb.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
print("screenshot_mode:", json.dumps(call("jawa/screenshot_mode", enabled=True))[:200])
for label, alt, tile in (("ashkarr_territories_clean", 470, 8858),
                         ("ashkarr_territories_sunspire", 300, 12828)):
    call("jawa/world_view", show=True, centerTile=tile, altitude=alt, northUp=True)
    time.sleep(4)
    call("jawa/clear_ui", devWindows=True, clearSelection=True)
    time.sleep(2)
    r = call("jawa/take_screenshot", fileName=label)
    print(label, json.dumps({k: r.get(k) for k in ("success","fileName","message")}))
    time.sleep(2)
s = call("jawa/world_map_mode")
print("mode:", s.get("modeAfter"), "| worldRendered:", s.get("worldRendered"))
