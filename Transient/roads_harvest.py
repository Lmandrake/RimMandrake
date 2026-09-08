import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    lk = rb.call("jawa/world_links_get", {"range": "0-21871", "limit": 22000})
    rows = lk.get("tiles") or lk.get("rows") or []
    print("links rows:", len(rows))
    print("sample row:", json.dumps(rows[0])[:500])
    json.dump(rows, open(r"D:\Luke\dev\Rimworld\Transient\links_raw.json", "w"))

    ob = rb.call("jawa/world_objects_get", {"limit": 5000})
    o = ob.get("objects") or ob.get("rows") or []
    print("\nworld objects:", len(o))
    print("sample:", json.dumps(o[0])[:400] if o else "none")
    json.dump(o, open(r"D:\Luke\dev\Rimworld\Transient\objects_raw.json", "w"))

    lm = rb.call("jawa/world_landmarks_get", {"limit": 5000})
    L = lm.get("landmarks") or lm.get("rows") or []
    print("\nlandmarks:", len(L))
    print("sample:", json.dumps(L[0])[:400] if L else "none")
    json.dump(L, open(r"D:\Luke\dev\Rimworld\Transient\landmarks_raw.json", "w"))
