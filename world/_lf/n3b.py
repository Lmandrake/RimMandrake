import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
r=b.call('jawa/spawn_pawn',{'kindDef':'Colonist','x':80,'z':80,'faction':'none','count':1,
                            'xenotype':'RimMandrakeWookiee'})
r.pop('operation',None)
print(json.dumps(r, indent=1)[:900])
