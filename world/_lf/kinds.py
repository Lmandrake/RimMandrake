import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
for f in ('geonos','jawa'):
    r=b.call('jawa/pawnkind_audit',{'filter':f,'limit':60,'includeHealthy':True})
    print("=== filter",f,"->",json.dumps({k:v for k,v in r.items() if k not in('reasons','kinds','rows','operation')})[:300])
    rows=r.get('kinds') or r.get('rows') or r.get('reasons') or []
    print(json.dumps(rows)[:1500]); print()
