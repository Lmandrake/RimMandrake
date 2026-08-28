# -*- coding: utf-8 -*-
"""LIVE_HALF_OF_LOAD_1 J4/J5 - will a Jawa sow? Does it still harvest and chop?
Mechanism first: what does the game think its Plants skill IS?"""
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=300); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
made={}
for kind,xeno,tag in (('Colonist','MandrakeJawa','JAWA'),('Colonist','Baseliner','BASELINER')):
    r=c('jawa/spawn_pawn',{'kindDef':kind,'x':120 if tag=='JAWA' else 122,'z':190,
                           'faction':'PlayerColony','count':1,'xenotype':xeno})
    got=r.get('pawns') or []
    if not got: print(tag,"SPAWN FAILED",(r.get('message') or '')[:80]); continue
    made[tag]=got[0]['id']
    print("%-10s spawned %s as %s"%(tag, got[0]['id'], got[0].get('xenotype')))
print()
for tag,pid in made.items():
    d=c('jawa/pawn_get',{'pawn':pid})
    pw=d.get('pawns')[0] if isinstance(d.get('pawns'),list) and d.get('pawns') else d
    sk={s.get('skill') or s.get('def'):s for s in (pw.get('skills') or [])}
    pl=sk.get('Plants') or {}
    st=c('jawa/pawn_stats',{'pawn':pid,'stats':'PlantWorkSpeed,PlantHarvestYield,WorkSpeedGlobal'})
    stats={q['defName']:round(q['value'],3) for q in (st.get('stats') or [])}
    print("%-10s Plants skill record: %s"%(tag, json.dumps(pl)[:170]))
    print("%-10s stats: %s"%("", json.dumps(stats)))
    dis=pw.get('workDisables') or pw.get('disabledWork')
    print("%-10s workDisables=%s  traits=%s"%("", dis, json.dumps([x.get('def') for x in (pw.get('traits') or [])])[:120]))
    print()
json.dump(made, io.open(r"D:\Luke\dev\Rimworld\world\_lf\j45_pawns.json","w",encoding='utf-8'))
