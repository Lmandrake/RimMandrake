import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    try:
        r = rb.call("tools/list")
    except Exception as e:
        r = None; print("tools/list failed:", str(e)[:200])
    if r:
        names = []
        for k in ("tools","result","items"):
            v = r.get(k)
            if isinstance(v, list):
                names = [x.get("name") or x.get("id") or str(x)[:40] for x in v]; break
        print("TOOL COUNT:", len(names))
        for n in sorted(names):
            if any(s in n.lower() for s in ("ninefold","god","quicktest","scenario","load","new_game","start","map","theme","jawa")):
                print("  ", n)
