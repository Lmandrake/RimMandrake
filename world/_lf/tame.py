# -*- coding: utf-8 -*-
"""LIVE_HALF_OF_LOAD_1 rows P2-P5: does a tamed animal get a CORPUS name or '<Race> 1'?"""
import sys, json, io, collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e)}
for x in b.list_tools():
    if x.get('name')=='jawa/set_pawn_faction':
        print("schema ::", json.dumps(x.get('inputSchema') or {})[:600]); print()
ps=c('jawa/list_pawns',{'limit':999}).get('pawns') or []
animals=[x for x in ps if not x.get('factionName') and x.get('intelligence')!='Humanlike'
         and not x.get('isMechanoid')]
print("wild animals available:", len(animals))
done=[]
for a in animals[:15]:
    before=a.get('name')
    r=c('jawa/set_pawn_faction',{'pawn':a['id'],'faction':'player'})
    after=c('jawa/pawn_get',{'pawn':a['id']})
    pw=after.get('pawns')[0] if isinstance(after.get('pawns'),list) and after.get('pawns') else after
    done.append((a.get('kindDef'),before,pw.get('name'),r.get('success')))
    print("  %-22s %-22s -> %-24s ok=%s %s"%(a.get('kindDef'),before,pw.get('name'),r.get('success'),
          (r.get('message') or '')[:50]))
json.dump(done, open(r"D:\Luke\dev\Rimworld\world\_lf\tame_evidence.json","w"), indent=1)
