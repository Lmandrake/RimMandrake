import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
for x in b.list_tools():
    if x.get('name') in ('jawa/world_tile_import','jawa/world_tile_validate','jawa/world_tile_export'):
        print("###",x['name'])
        print("   desc:", (x.get('description') or '')[:260])
        print("   keys:", sorted((x.get('inputSchema',{}).get('properties') or {}).keys()))
