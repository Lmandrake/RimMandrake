import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    r = rb.call("rimworld/save_game", {"saveName": "WORLDMAP_V4_oasis_rivers_2026-09-07"})
    print("save_game (PATH NOT TRUSTED):", json.dumps(r)[:400])
