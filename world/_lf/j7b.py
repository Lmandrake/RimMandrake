import sys, json, io, collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=90); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e),"success":False}
before={x['id'] for x in (c('jawa/list_pawns',{'limit':999}).get('pawns') or [])}
r=c('jawa/fire_raid',{'faction':'Mechanoid','points':500,'spawnCenter':'5,240','dryRun':False})
print("fire_raid ->", r.get('success'), json.dumps(r.get('resolved'))[:200])
after=c('jawa/list_pawns',{'limit':999}).get('pawns') or []
new=[x for x in after if x['id'] not in before]
print("arrived:", len(new), dict(collections.Counter((x.get('kindDef'),x.get('factionName')) for x in new)))
# relations on each arrival - J8's real question
for x in new[:3]:
    rr=c('jawa/pawn_relations',{'pawn':x['id'],'action':'list'})
    rel=rr.get('relations') or rr.get('direct') or []
    print("   %-20s relations=%s"%(x.get('kindDef'), len(rel) if isinstance(rel,list) else rel))
print("paused:", c('rimworld/get_cell_info',{'x':125,'z':125}).get('state',{}).get('paused'))
