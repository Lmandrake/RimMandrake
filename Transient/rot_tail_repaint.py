import sys, csv, json
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
live = {int(r['tile']): r for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\Transient\v24_tiles_live.csv'))}
tail = [t for t,r in live.items() if r['biome']=='AB_MycoticJungle' and float(r['temperature']) < -42]
print(f"tail tiles: {len(tail)}")
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    tools = rb.call("rimbridge/list_tools", {})
    # find world_tile_set declared params via client guard by asking the client
    try:
        r = rb.call("jawa/world_tile_set", {"probe_invalid_param_name": 1})
    except Exception as e:
        print("world_tile_set declares:", e)
