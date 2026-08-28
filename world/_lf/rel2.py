import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=90); b.connect()
r=b.call('jawa/faction_relations_get',{'faction':'Player','includeNeutral':True}); r.pop('operation',None)
print("keys:", sorted(r.keys()))
print(json.dumps(r)[:1400])
