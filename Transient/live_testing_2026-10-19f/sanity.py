import json, os, sys, time
sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint(); out = {}
with RimBridge(h, p, t, timeout=120.0) as rb:
    for tool in ("rimworld/get_game_info", "rimworld/list_colonists"):
        try: out[tool] = rb.call(tool, {})
        except Exception as e: out[tool] = "ERR " + str(e)[:300]
json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)
gi = out["rimworld/get_game_info"]; lc = out["rimworld/list_colonists"]
print(str(gi)[:400]); print("colonists:", len(lc.get("colonists", [])) if isinstance(lc, dict) else lc)
