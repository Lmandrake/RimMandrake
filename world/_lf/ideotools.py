import sys, json, io, re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
for x in b.list_tools():
    n=x.get('name','')
    if re.search(r'ideo|leader|precept|faction', n, re.I):
        print("###",n,"::",json.dumps(x.get('inputSchema') or {})[:400])
