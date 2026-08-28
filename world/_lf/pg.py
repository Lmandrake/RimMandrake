import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
ps=b.call('jawa/list_pawns',{'limit':999}).get('pawns') or []
j=[x for x in ps if x.get('kindDef')=='Jawa_Tribal_Scavenger'][0]
d=b.call('jawa/pawn_get',{'pawn':j['id']}); d.pop('operation',None)
pw=d.get('pawns')[0] if isinstance(d.get('pawns'),list) else d
print("pawn_get keys:", sorted(pw.keys()))
for k in ('stats','temperature','comfortableTemperature','genes','xenotype','workDisables','disabledWork'):
    if k in pw: print("  %s = %s"%(k, json.dumps(pw[k])[:300]))
print()
g=b.call('jawa/pawn_genes',{'pawn':j['id'],'action':'list'}); g.pop('operation',None)
print("pawn_genes ->", json.dumps(g)[:700])
