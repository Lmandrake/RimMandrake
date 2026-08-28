import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
for probe in ('Ugnaught','Twilek','KelDor','Chiss','Wookiee'):
    try:
        r=b.call('jawa/spawn_pawn',{'kindDef':'Colonist','x':110,'z':110,'faction':'none',
                                    'count':1,'xenotype':probe})
        r.pop('operation',None)
        print("%-10s -> success=%s %s"%(probe, r.get('success'), json.dumps(r.get('suggestions') or r.get('details') or r.get('message'))[:180]))
    except Exception as e:
        print(probe,"ERR",str(e)[:200])
