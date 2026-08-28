import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=200); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
best=None
for X in range(20, 220, 20):
    for Z in range(20, 220, 20):
        r=c('rimworld/get_cells_info',{'x':X,'z':Z,'width':18,'height':10})
        cells=r.get('cells') or []
        if len(cells)<180: continue
        occ=sum(1 for q in cells if (q.get('solidThingDefs') or []))
        walk=sum(1 for q in cells if q.get('walkable'))
        if best is None or occ<best[0]: best=(occ,X,Z,walk)
        if occ==0:
            print("CLEAR rect at %d,%d  (walkable %d/180)"%(X,Z,walk)); best=(0,X,Z,walk); break
    if best and best[0]==0: break
print("best:", best)
