import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    pawns = rb.call("jawa/list_pawns", {})["pawns"]
    gnk = [p for p in pawns if "GNKDroid" in p["kind"]]
    print("GNK pawns still listed:", json.dumps(gnk)[:400])
    things = rb.call("jawa/list_things", {"group": "All"})
    n = things.get("things", [])
    print("total things:", len(n))
    interesting = [t for t in n if "xplos" in json.dumps(t) or "Corpse" in json.dumps(t)]
    for t in interesting[:20]:
        print(t)
