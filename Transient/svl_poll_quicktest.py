import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
for i in range(14):
    time.sleep(10)
    try:
        with RimBridge(host, port, token) as rb:
            r = rb.call("jawa/list_pawns", {})
            msg = json.dumps(r)[:300]
            print(f"poll {i} ({time.strftime('%H:%M:%S')}):", msg)
            if r.get("success") and "No current map" not in msg:
                print("QUICKTEST_MAP_READY")
                break
    except Exception as e:
        print(f"poll {i} exception:", repr(e))
