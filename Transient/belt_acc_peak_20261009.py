import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
w=S.call("jawa/weather_set",weather="RM_PeakstormLight",lockWeather=True); print(w.get("success"),str(w.get("message"))[:80])
seen=[];ws=[]
for i in range(10):
    r=S.call("jawa/static_call",type="RimMandrake.FloodedCanyon.RM_PeakstormDustProof",method="ProofState",args="-")
    res=str(r.get("result","")) if isinstance(r,dict) else str(r)
    seen.append(res[:150]); print(i,S.ticks(),res[:150],flush=True)
    if "weather=RM_PeakstormLight" not in res: break
    m=dict(kv.split("=",1) for kv in res.split(" ") if "=" in kv); ws.append(m.get("reversed"))
    S.run(270)
print("SET",sorted(set(ws)))
S.call("jawa/weather_set",weather="Clear",lockWeather=False)
