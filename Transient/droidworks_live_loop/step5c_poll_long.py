import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
deadline = time.time() + 480
ok = False
last_err = None
while time.time() < deadline:
    try:
        with RimBridge(host, port, token) as rb:
            r = rb.call("jawa/list_pawns", {})
            msg = r.get("message", "")
            print("poll:", r.get("success"), msg, flush=True)
            if r.get("success") and "No current map" not in msg:
                ok = True
                break
    except Exception as e:
        last_err = repr(e)
        print("poll error:", last_err, flush=True)
    time.sleep(15)
print("READY" if ok else "STILL NOT READY after 480s, last_err=" + str(last_err))
