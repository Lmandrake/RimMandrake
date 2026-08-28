import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
r=b.call('jawa/list_pawns',{'limit':40})
ps=r.get('pawns') or []
print("pawns on map:", len(ps))
for x in ps[:8]:
    print("  ", {k:x.get(k) for k in ('name','kindDef','faction','xenotype','pos') if k in x})
print("keys:", sorted(ps[0].keys()) if ps else "none")
