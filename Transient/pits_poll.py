import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

for i in range(20):
    try:
        with RimBridge(host, port, token) as rb:
            r = rb.call("jawa/list_pawns", {})
            print(i, json.dumps(r)[:200])
            if r.get("success") is not False and "No current map" not in json.dumps(r):
                print("READY")
                break
    except Exception as e:
        print(i, "ERR", e)
    time.sleep(3)
