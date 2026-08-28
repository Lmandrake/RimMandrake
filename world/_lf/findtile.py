import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=200); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
r=c('jawa/world_objects_get',{'limit':40})
objs=r.get('objects') or r.get('worldObjects') or []
print("world objects: %d"%len(objs))
for q in objs[:10]:
    print("  ", json.dumps({k:v for k,v in q.items() if k in ('def','tile','faction','name','label')}))
ct=c('jawa/cell_temperature',{'cell':'150,150'})
print("\nseasonalTemp on the map:", ct.get('seasonalTemp'), "outdoor:", ct.get('outdoorTemp'))
