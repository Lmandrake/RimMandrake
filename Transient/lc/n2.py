import sys,time,json; sys.path.insert(0,"Transient/lc")
from h import *
CT="RimMandrake.Cauldron.RM_CauldronSettings"; FT="RimMandrake.FeverWood.RM_FeverWoodSettings"
DY="RimMandrake.FeverWood.RM_WorldComponent_DeepYoung"
def nettles(s): return things(s,"RM_RavenNettle").get("countMatched")
def sc(s,t,m,a=""):
    r=s.call("jawa/static_call",type=t,method=m,args=a); return r.get("result") if r.get("success") else "FAIL "+str(r.get("message"))[:200]
def setf(s,t,f,v): return s.call("jawa/mod_settings_field",typeName=t,action="set",field=f,value=str(v).lower())
def getf(s,t,f): return s.call("jawa/mod_settings_field",typeName=t,action="get",field=f)
with S() as s:
    print("tick",s._ticks()); print("retile still",s.call("jawa/map_info").get("mapBiome"))
    print("bold0",sc(s,DY,"get_BoldnessMultiplier"),"|",sc(s,DY,"RestlessnessLine"))
    print("get",str(getf(s,FT,"broodRansomEnabled"))[:200])
    c=[q for q in pawns(s) if q.get("isPlayer") and q["kind"]=="Colonist" and not q.get("downed")][0]
    r=s.call("rimworld/spawn_thing",defName="RM_SekkulaathYoungCask",x=c["x"]+1,z=c["z"]+1,stackCount=1); print("spawn cask",str(r)[:300])
    print("cask count",things(s,"RM_SekkulaathYoungCask").get("countMatched"))
    print("set cauldron off",str(setf(s,CT,"condensateGardensEnabled",False))[:160])
    n0=nettles(s); print("nettles at off start",n0)
    t0=time.time(); st=s._ticks()
    for i in range(7):
        wait(s,2500); print(i,s._ticks(),"nettles",nettles(s),"bold",sc(s,DY,"get_BoldnessMultiplier"),"%.0fs"%(time.time()-t0),flush=True)
    print("line",sc(s,DY,"RestlessnessLine"))
    setf(s,FT,"broodRansomEnabled",False); print("bold toggle off",sc(s,DY,"get_BoldnessMultiplier"),sc(s,DY,"RestlessnessLine"))
    setf(s,FT,"broodRansomEnabled",True); print("bold restored",sc(s,DY,"get_BoldnessMultiplier"))
    print("restore cauldron",str(setf(s,CT,"condensateGardensEnabled",True))[:100],str(getf(s,CT,"condensateGardensEnabled"))[:120])
