import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
for i in range(20):
    try:
        with RimBridge(h,p,t) as rb:
            r = rb.call("jawa/list_pawns", {})
            if r.get("success") and "mapId" in json.dumps(r):
                print(f"try {i}: READY", json.dumps(r)[:300])
                break
            print(f"try {i}:", json.dumps(r)[:200])
    except Exception as e:
        print(f"try {i}: ERR", str(e)[:200])
    time.sleep(3)
