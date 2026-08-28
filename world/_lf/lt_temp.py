# -*- coding: utf-8 -*-
"""The temperature table the owner asked for - with the APPAREL CONFOUND removed.

ComfyTemperatureMin/Max include worn apparel's insulation, so a first pass that spawns
pawns in randomly-generated clothing compares clothing, not xenotypes. Every pawn here is
STRIPPED first, then read, so the only thing left moving the number is genes."""
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=300); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
X=[('Baseliner','none - THE REFERENCE POINT'),
   ('RimMandrakeUgnaught','none'),('RimMandrakeTwilek','none'),('RimMandrakeKelDor','none'),
   ('MandrakeJawa','MinTemp_SmallDecrease + MaxTemp_SmallIncrease'),
   ('RimMandrakeChiss','MinTemp_LargeDecrease + MaxTemp_SmallDecrease'),
   ('RimMandrakeWookiee','Furskin + MinTemp_SmallDecrease + MaxTemp_SmallIncrease')]
rows=[]
for i,(xn,genes) in enumerate(X):
    r=c('jawa/spawn_pawn',{'kindDef':'Colonist','x':40+i*2,'z':40,'faction':'none','count':1,'xenotype':xn})
    got=r.get('pawns') or []
    if not got: print("  %-22s SPAWN FAILED %s"%(xn,(r.get('message') or '')[:60])); continue
    pid=got[0]['id']
    clr=c('jawa/pawn_gear',{'pawn':pid,'action':'clear','clearWhat':'apparel'})
    d=c('jawa/pawn_get',{'pawn':pid})
    pw=d.get('pawns')[0] if isinstance(d.get('pawns'),list) and d.get('pawns') else d
    left=[a.get('def') for a in (pw.get('apparel') or [])]
    s=c('jawa/pawn_stats',{'pawn':pid,'stats':'ComfyTemperatureMin,ComfyTemperatureMax'})
    v={q['defName']:q['value'] for q in (s.get('stats') or [])}
    rows.append((xn,v.get('ComfyTemperatureMin'),v.get('ComfyTemperatureMax'),genes,left))
    print("  %-22s strip=%-5s leftover=%-2d  %8.2f ... %7.2f"%(
        xn, clr.get('success'), len(left), v.get('ComfyTemperatureMin') or 0, v.get('ComfyTemperatureMax') or 0))
print("\n%-22s %10s %10s   genes"%("xenotype","comfyMin","comfyMax"))
for xn,lo,hi,g,left in rows:
    print("%-22s %10.2f %10.2f   %s%s"%(xn,lo or 0,hi or 0,g," ⚠ %d apparel left"%len(left) if left else ""))
base=[r for r in rows if r[0]=='Baseliner']
if base:
    blo,bhi=base[0][1],base[0][2]
    print("\ndelta from the stripped Baseliner (%.2f ... %.2f):"%(blo,bhi))
    for xn,lo,hi,g,_ in rows:
        if xn=='Baseliner': continue
        print("  %-22s %+7.2f  %+7.2f"%(xn, lo-blo, hi-bhi))
json.dump([dict(x=r[0],lo=r[1],hi=r[2],genes=r[3],left=r[4]) for r in rows],
          open(r"D:\Luke\dev\Rimworld\world\_lf\lt_temp.json","w"), indent=1)
