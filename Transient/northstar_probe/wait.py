import sys, time
sys.path.insert(0, "src/RimMandrake/Utils")
from rimdrive.session import Session
t0=time.time()
while time.time()-t0<180:
    with Session(strict=False, quiet=True, focus=False) as s:
        r=s.call("jawa/map_info")
        if r.get("success"): print("MAP READY", int(time.time()-t0),"s", {k:r.get(k) for k in ("sizeX","mapBiome","mapParent")}); break
    time.sleep(6)
