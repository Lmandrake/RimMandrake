import sys, json, io, collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=300); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
r=c('jawa/list_pawns',{'includeCorpses':True,'limit':900})
ps=r.get('pawns') or []
dead=[x for x in ps if x.get('dead')]
print("pawns listed %d, dead %d"%(len(ps), len(dead)))
for x in dead[:12]:
    print("   %-16s %-22s xeno=%-22s dead=%s"%(x.get('id'), x.get('kindDef'), x.get('xenotype'), x.get('dead')))
print()
for pid in ('Human58390','Human58394'):
    hit=[x for x in ps if x.get('id')==pid]
    print("  %-14s in list(includeCorpses): %s"%(pid, json.dumps(hit)[:220] if hit else "ABSENT"))
print()
ct=c('jawa/cell_temperature',{'cell':'160,160'})
print("map now: outdoor=%.1f seasonal=%.1f"%(ct.get('outdoorTemp') or 0, ct.get('seasonalTemp') or 0))
print("colonists alive:", len(c('rimworld/list_colonists',{}).get('colonists') or []))
