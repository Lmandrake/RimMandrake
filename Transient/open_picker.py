import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/open_window_by_type", {"windowType": "aRandomKiwi.RimThemes.Dialog_ThemesList"})
    print("OPEN:", json.dumps(r)[:250])
    import time; time.sleep(1.5)
    shot = rb.call("rimworld/take_screenshot", {})
    print("SHOT:", json.dumps(shot).split("Screenshots")[1][:40] if "Screenshots" in json.dumps(shot) else json.dumps(shot)[:200])
