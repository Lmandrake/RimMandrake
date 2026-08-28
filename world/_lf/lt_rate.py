# -*- coding: utf-8 -*-
"""A settled-map census across all four kinds, to get an honest rate."""
import sys, json, io, collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=300); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
KINDS=['Jawa_Colonist','Jawa_Tribal_Scavenger','Jawa_Tribal_Slinger','Jawa_Tribal_Elder']
tot=collections.Counter(); bare=[]
gi=c('rimworld/get_game_info'); print("map ticks now:", gi.get('ticksGame'))
for i,k in enumerate(KINDS):
    r=c('jawa/spawn_pawn',{'kindDef':k,'x':60+i*4,'z':60,'faction':'Jawa_IndigenousTribes','count':12})
    rows=r.get('pawns') or []
    robe=hood=0
    for q in rows:
        d=c('jawa/pawn_get',{'pawn':q['id']})
        pw=d.get('pawns')[0] if isinstance(d.get('pawns'),list) and d.get('pawns') else d
        ap=[a.get('def') for a in (pw.get('apparel') or [])]
        robe += 1 if 'guy762_Robes_jawa' in ap else 0
        hood += 1 if 'guy762_JawaHood' in ap else 0
        if 'guy762_JawaHood' not in ap:
            bare.append(dict(kind=k, stage=pw.get('developmentalStage'), age=pw.get('ageBiologicalYears'),
                             gender=pw.get('gender'), ap=ap))
        for badd in ('Apparel_WarVeil','Apparel_TribalHeaddress','Apparel_PlateArmor'):
            if badd in ap: tot[badd]+=1
    tot['n']+=len(rows); tot['robe']+=robe; tot['hood']+=hood
    print("  %-24s n=%-3d robe=%-3d hood=%-3d"%(k,len(rows),robe,hood))
print("\nTOTAL this batch: n=%d  robe=%d  hood=%d  intruders=%s"%(
    tot['n'],tot['robe'],tot['hood'],
    {k:v for k,v in tot.items() if k.startswith('Apparel_')} or "none"))
if bare:
    print("\nthe %d without a hood:"%len(bare))
    for r in bare[:8]:
        print("   %-24s stage=%-8s age=%-4s gender=%-7s %s"%(r['kind'],r['stage'],r['age'],r['gender'],json.dumps(r['ap'])[:90]))
json.dump({'tot':dict(tot),'bare':bare}, open(r"D:\Luke\dev\Rimworld\world\_lf\lt_rate.json","w"), indent=1)
