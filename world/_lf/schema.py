import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
want={"rimworld/start_debug_game","jawa/tile_settleable","rimworld/take_screenshot","jawa/world_view"}
for x in b.list_tools():
    if x.get("name") in want:
        print("###", x["name"], "-", (x.get("description") or "")[:200])
        print(json.dumps(x.get("inputSchema") or x.get("input_schema") or {})[:700]); print()
