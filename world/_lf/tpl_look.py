# -*- coding: utf-8 -*-
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e)}
print("one cell, ALL keys:", json.dumps(c('rimworld/get_cell_info',{'x':176,'z':171}).get('cell',{}))[:700])
print()
for (x,z) in ((176,171),(176,172),(181,171),(182,171),(183,171),(184,171)):
    cell=c('rimworld/get_cell_info',{'x':x,'z':z}).get('cell',{})
    print("  (%d,%d) terrain=%-22s things=%s"%(x,z,cell.get('terrainDefName'),
          [t.get('def') if isinstance(t,dict) else t for t in (cell.get('things') or [])]))
print()
for d in ('Shelf','Table1x2c','DiningChair'):
    g=c('jawa/get_def',{'defName':d,'defType':'ThingDef'})
    dd=g.get('def') or g
    sz=json.dumps(dd.get('size') or dd.get('graphicData',{}).get('drawSize') or 'n/a')
    print("  %-14s size=%s"%(d, sz))
