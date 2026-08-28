import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
r=b.call('jawa/faction_leader_get',{}); r.pop('operation',None)
print("top-level keys:", sorted(r.keys()))
for k,v in r.items():
    if isinstance(v,list) and v:
        print("list key '%s' -> %d rows, row keys=%s"%(k,len(v),sorted(v[0].keys())))
        for q in v[:3]: print("   ", json.dumps(q)[:250])
        break
