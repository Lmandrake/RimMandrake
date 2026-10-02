import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
for i in range(20):
    with RimBridge(host, port, token) as rb:
        try:
            r = rb.call("jawa/list_pawns", {})
            print(i, "list_pawns:", r.get("success"), r.get("message", "")[:120], "count=", len(r.get("pawns", [])) if isinstance(r.get("pawns"), list) else None)
            if r.get("success") and isinstance(r.get("pawns"), list):
                print("READY")
                break
        except Exception as e:
            print(i, "EXC", repr(e))
    time.sleep(5)
