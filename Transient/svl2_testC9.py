import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/map_commit", {})
    print("MAP_COMMIT", json.dumps(r)[:800])
    td = rb.call("jawa/get_defs", {"defs": "ThingDef/RSW_BactaTank"})
    # not useful for live power state; check via get_cell_info / list_things
    lt = rb.call("jawa/list_things", {"rect": "171,139,1,2", "limit": 5, "defName": "RSW_BactaTank"})
    print("TANK", json.dumps(lt)[:1500])
