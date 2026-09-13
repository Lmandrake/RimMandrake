import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
for i in range(20):
    try:
        with RimBridge(host, port, token) as rb:
            r = rb.call("jawa/list_pawns", {})
            msg = r.get("message","")
            print(i, r.get("success"), msg[:80])
            if r.get("success") and "No current map" not in msg:
                break
    except Exception as e:
        print(i, "exc", str(e)[:150])
    time.sleep(5)
