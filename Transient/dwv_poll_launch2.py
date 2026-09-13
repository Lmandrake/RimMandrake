import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
for i in range(200):
    try:
        host, port, token = resolve_endpoint()
        with RimBridge(host, port, token) as rb:
            r = rb.call("rimworld/get_ui_state", {})
            print(i, time.strftime("%H:%M:%S"), r.get("programState"), r.get("inEntryScene"))
            if r.get("success"):
                break
    except Exception as e:
        print(i, time.strftime("%H:%M:%S"), "not up yet:", str(e)[:80])
    time.sleep(20)
