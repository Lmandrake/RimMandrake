import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
deadline = time.time() + 100
ok = False
while time.time() < deadline:
    try:
        with RimBridge(host, port, token) as rb:
            r = rb.call("jawa/list_pawns", {})
            msg = r.get("message", "")
            print("poll:", r.get("success"), msg)
            if r.get("success") and "No current map" not in msg:
                ok = True
                break
    except Exception as e:
        print("poll error:", repr(e))
    time.sleep(5)
print("READY" if ok else "STILL NOT READY")
