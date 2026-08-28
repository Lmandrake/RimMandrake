import sys, json, io, collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
ps=b.call('jawa/list_pawns',{'limit':999}).get('pawns') or []
print("total pawns on map:", len(ps))
c=collections.Counter((x.get('kindDef'), x.get('factionName'), x.get('xenotype')) for x in ps)
for k,v in sorted(c.items(), key=lambda kv:-kv[1]):
    if k[1] or 'awa' in str(k[0]) or 'eonos' in str(k[0]):
        print("%3d  %-26s %-26s %s"%(v,k[0],k[1],k[2]))
