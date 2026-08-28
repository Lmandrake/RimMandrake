# -*- coding: utf-8 -*-
"""LIVE_HALF_OF_LOAD_1 rows N3 and the gene evidence behind T1/T2/N1/N2.
Reads the INSTANCE gene list, never the def."""
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
X=['RimMandrakeUgnaught','RimMandrakeTwilek','RimMandrakeKelDor','MandrakeJawa',
   'RimMandrakeChiss','RimMandrakeWookiee','Baseliner']
out={}
x0=75
for i,xn in enumerate(X):
    r=b.call('jawa/spawn_pawn',{'kindDef':'Colonist','x':x0+i*2,'z':95,'faction':'none',
                                'count':1,'xenotype':xn})
    rows=r.get('pawns') or r.get('rows') or []
    if not (r.get('success') and rows):
        print("%-22s SPAWN FAILED %s"%(xn,(r.get('message') or '')[:80])); continue
    pid=rows[0]['id']
    g=b.call('jawa/pawn_genes',{'pawn':pid,'action':'list'})
    genes=(g.get('endogenes') or [])+(g.get('xenogenes') or [])
    temp=sorted([q for q in genes if 'Temp' in q or 'Furskin' in q or 'Insulat' in q])
    out[xn]=dict(readBackXeno=g.get('xenotype'), n=len(genes), temp=temp,
                 plants=[q for q in genes if 'Plant' in q or 'Work' in q])
    print("%-22s xeno_readback=%-22s genes=%-3d temp=%s"%(xn,g.get('xenotype'),len(genes),temp))
print()
print("N3  — any pawn carrying BOTH MinTemp_SmallDecrease AND MinTemp_SmallIncrease:")
bad=[k for k,v in out.items() if 'MinTemp_SmallDecrease' in v['temp'] and 'MinTemp_SmallIncrease' in v['temp']]
print("    ", bad or "NONE — none of the %d xenotypes read back carries both"%len(out))
print()
print("J6  — plant/work genes on the Jawa instance:", out.get('MandrakeJawa',{}).get('plants'))
json.dump(out, open(r"D:\Luke\dev\Rimworld\world\_lf\gene_evidence.json","w"), indent=1)
