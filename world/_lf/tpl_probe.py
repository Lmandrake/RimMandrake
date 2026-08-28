# -*- coding: utf-8 -*-
"""Before spending the run: does set_terrain_batch's `rect` form do ANYTHING?"""
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e)}
def terr(x,z): return c('rimworld/get_cell_info',{'x':x,'z':z}).get('cell',{}).get('terrainDefName')
X,Z=200,200
print("before            :", terr(X,Z))
r=c('jawa/set_terrain_batch',{'rect':'%d,%d,2,2'%(X,Z),'terrainDef':'Gravel'})
print("rect form  -> %-5s %s"%(r.get('success'),(r.get('message') or str(r))[:110]))
print("after rect form   :", terr(X,Z))
r=c('jawa/set_terrain_batch',{'ops':'Gravel:%d,%d,2,2'%(X,Z)})
print("ops  form  -> %-5s %s"%(r.get('success'),(r.get('message') or str(r))[:110]))
print("after ops form    :", terr(X,Z))
