import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=120); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
for x,z in ((249,249),(199,199),(187,179),(170,170)):
    r=c('rimworld/get_cell_info',{'x':x,'z':z})
    ok = r.get('success') and r.get('cell')
    print("  (%3d,%3d) %s %s"%(x,z,"OK " if ok else "OUT", (r.get('cell') or {}).get('terrainDefName') or (r.get('message') or '')[:40]))
r=c('rimworld/get_cells_info',{'x':170,'z':170,'width':18,'height':10})
cells=r.get('cells') or []
occ=[q for q in cells if (q.get('solidThingDefs') or [])]
print("rect 170,170,18,10 -> %d cells readable, %d already occupied"%(len(cells), len(occ)))
