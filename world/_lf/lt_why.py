# -*- coding: utf-8 -*-
"""Who are the ~16% with NEITHER piece? First hypothesis from the source: CorrectAgeForWearing
is the FIRST condition in the apparelRequired loop, so a juvenile is skipped for both."""
import sys, json, io, collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=300); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
ps=c('jawa/list_pawns',{'limit':400}).get('pawns') or []
X,Z=111,107
wear=[]; bare=[]
for i,k in enumerate(['Jawa_Tribal_Scavenger','Jawa_Colonist']):
    r=c('jawa/spawn_pawn',{'kindDef':k,'x':X-30+i*3,'z':Z-30,'faction':'Jawa_IndigenousTribes','count':20})
    for q in (r.get('pawns') or []):
        d=c('jawa/pawn_get',{'pawn':q['id']})
        pw=d.get('pawns')[0] if isinstance(d.get('pawns'),list) and d.get('pawns') else d
        ap=[a.get('def') for a in (pw.get('apparel') or [])]
        rec=dict(kind=k, stage=pw.get('developmentalStage'), age=pw.get('ageBiologicalYears'),
                 gender=pw.get('gender'), n=len(ap), ap=ap)
        (wear if 'guy762_JawaHood' in ap else bare).append(rec)
print("WEARING both/hood: %d      NEITHER: %d"%(len(wear), len(bare)))
def show(label, rows):
    print("\n%s (%d)"%(label,len(rows)))
    print("   stages :", dict(collections.Counter(str(r['stage']) for r in rows)))
    print("   ages   :", sorted({int(r['age']) for r in rows if r['age'] is not None})[:14])
    print("   genders:", dict(collections.Counter(str(r['gender']) for r in rows)))
show("WEARING", wear); show("NEITHER", bare)
for r in bare[:4]: print("   bare sample:", json.dumps(r['ap'])[:110], "stage=%s age=%s"%(r['stage'],r['age']))
json.dump({'wear':wear,'bare':bare}, open(r"D:\Luke\dev\Rimworld\world\_lf\lt_why.json","w"), indent=1)
