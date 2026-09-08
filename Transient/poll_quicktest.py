import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
deadline = time.time() + 150
while time.time() < deadline:
    try:
        with RimBridge(host, port, token) as rb:
            r = rb.call("jawa/list_pawns", {})
            print("list_pawns:", r)
            if r.get("success") and "No current map" not in str(r.get("message", "")):
                print("READY")
                break
    except Exception as e:
        print("poll exc:", repr(e))
    time.sleep(5)
else:
    print("TIMEOUT")
