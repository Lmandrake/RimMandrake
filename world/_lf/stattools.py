import sys, json, io, re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
for x in b.list_tools():
    n=x.get("name","")
    if re.search(r'stat|gene|temperature|comfort|work|tame|animal|name', n, re.I):
        print("###",n,"|",(x.get("description") or "").split(".")[0][:100])
