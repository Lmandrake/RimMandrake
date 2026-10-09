import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
out={}
# --- CRACKEDLANDS_PEAKSTORM_DUST_REVERSAL_1.A2
w=S.call("jawa/weather_set",weather="RM_PeakstormLight",lockWeather=True); out["weather_set"]=w.get("success"),str(w.get("message"))[:100]
seen=[];ws=set()
for i in range(10):
    r=S.call("jawa/static_call",type="RimMandrake.FloodedCanyon.RM_PeakstormDustProof",method="ProofState",args="")
    res=str(r.get("result","")) if isinstance(r,dict) else str(r)
    seen.append(res[:140])
    if "weather=RM_PeakstormLight" not in res: break
    m=dict(kv.split("=",1) for kv in res.split(" ") if "=" in kv); ws.add(m.get("reversed"))
    t0=S.ticks(); S.run(270)
out["peakstorm"]={"reversed_set":sorted(map(str,ws)),"n":len(seen),"first":seen[0],"last":seen[-1]}
print(json.dumps(out,default=str),flush=True)
# --- TICKER_NEVER_FIRES_FIX_1.A1
x,z=40,300
with S.Scene("creep",x-8,z-8,17,17) as sc:
    r=S.call("jawa/spawn_batch",ops="RUT_DyingCreep:%d,%d"%(x,z)); out["creep_spawn"]=json.dumps(r,default=str)[:200]
    hist=[]
    t0=S.ticks()
    for k in range(10):
        a=S.call("jawa/list_things",defName="RUT_DyingCreep"); b=S.call("jawa/list_things",defName="RUT_DeadCreep")
        na=a.get("count",a.get("total",len(a.get("things",[])))) if isinstance(a,dict) else None
        nb=b.get("count",b.get("total",len(b.get("things",[])))) if isinstance(b,dict) else None
        hist.append((S.ticks()-t0,na,nb))
        print(hist[-1],flush=True)
        S.run(2500)
    a=S.call("jawa/list_things",defName="RUT_DyingCreep"); b=S.call("jawa/list_things",defName="RUT_DeadCreep")
    out["creep_hist"]=hist
    out["creep_final"]=(json.dumps(a,default=str)[:200],json.dumps(b,default=str)[:200])
S.call("jawa/weather_set",weather="Clear",lockWeather=False)
print(json.dumps(out,default=str))
