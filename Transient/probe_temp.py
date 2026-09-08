import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for tool,args in [("jawa/world_tile_get",{"range":"14301-14303","limit":5}),
                      ("jawa/world_layers",{})]:
        try:
            r=rb.call(tool,args)
            print(f"== {tool}:", json.dumps(r)[:600])
        except Exception as e:
            print(f"== {tool} ERR:", e)
