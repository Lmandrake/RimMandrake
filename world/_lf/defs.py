import sys, json, io, re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
names=[x.get('name') for x in b.list_tools()]
print([n for n in names if 'def' in n.lower()])
for x in b.list_tools():
    if 'def' in (x.get('name') or '').lower():
        print("###",x['name'],"::",json.dumps(x.get('inputSchema') or {})[:400])
