from afk_lib import *
import json
X0,Z0,W,H = 74,208,16,14
print("tick", tick(), "safety", safety())
print("pre", wetn(rect(X0,Z0,W,H)), "wide", wetn(rect(40,180,100,70)))
print("fire:", sc(BMC,"FireFloodTrigger","74,214|false"))
out=[]
t0=tick()
for dt in (0,10,60,250,500,1000):
    if dt: step(dt - (tick()-t0))
    rows=rect(X0,Z0,W,H); wide=rect(40,180,100,70)
    cols=sorted(set(r["x"] for r in rows if (r.get("f") or 0)>0))
    outside=[(r["x"],r["z"],r["f"]) for r in wide if (r.get("f") or 0)>0 and not (X0<=r["x"]<X0+W and Z0<=r["z"]<Z0+H)]
    rep=sc(BMC,"Report").split("\n")[-1]
    import re
    m=re.search(r"phase=(\S+).*activeFloodCells=(\d+) raisedFillCells=(\d+)",rep)
    print("dt",tick()-t0,"wet",wetn(rows),"vol",vol(rows),"x",(cols[0],cols[-1]) if cols else None,"outside-wet",len(outside),outside[:5],"rep",m.groups() if m else rep[:200], flush=True)
print("safety", safety())
