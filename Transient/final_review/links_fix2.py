import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
OUT = r"D:\Luke\dev\Rimworld\Transient\final_review"
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/world_links_get", {"range": "0-21871", "onlyLinked": True, "limit": 25000})
    assert r.get("success") is True, r.get("message")
    tiles = r.get("tiles") or []
    print("link-bearing tiles:", len(tiles))
    print("sample:", json.dumps(tiles[0])[:300])
    json.dump(tiles, open(OUT + r"\links.json", "w"))
