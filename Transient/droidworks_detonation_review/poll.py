import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
for i in range(20):
    with RimBridge(host, port, token) as rb:
        try:
            lp = rb.call("jawa/list_pawns", {})
            print(i, "list_pawns:", json.dumps(lp)[:200])
            if lp.get("success", True) is not False:
                print("MAP READY")
                break
        except Exception as e:
            print(i, "exc:", e)
    time.sleep(3)
