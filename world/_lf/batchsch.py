import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
for x in b.list_tools():
    if x.get('name') in ('jawa/set_terrain_batch','jawa/set_roof_batch','jawa/build_batch'):
        s=x.get('inputSchema') or {}
        print("###",x['name'],"accepted keys:", sorted((s.get('properties') or {}).keys()))
