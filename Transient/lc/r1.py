import sys,time,json; sys.path.insert(0,"Transient/lc")
sys.path.insert(0,"src/RimMandrake/Utils/modcheck")
from h import *
import bland_world as bw
H="RimMandrake.RustCathedral.Hum."
def sc(s,t,m,a=""):
    r=s.call("jawa/static_call",type=H+t,method=m,args=a); return r.get("result") if r.get("success") else "FAIL "+str(r.get("message"))[:200]
with S() as s:
    print("retile",bw.retile(s,"RM_RustCathedral")["applied"])
    wait(s,300)
    print("band",sc(s,"RM_MapComponent_BiomeAttitude","GetBand","current"),"state",sc(s,"RM_LineCycle","ProofState"))
    print("readout no reader:",repr(sc(s,"RM_HumReading","Readout","current")))
    cols=[q for q in pawns(s) if q.get("isPlayer") and q["kind"]=="Colonist" and not q.get("downed")]
    c=cols[0]["id"]
    r=s.call("jawa/pawn_traits",action="add",pawn=c,trait="RM_HumReader",degree=0); print("trait add",str(r)[:200])
    print("readout with reader:",repr(sc(s,"RM_HumReading","Readout","current")))
    r=s.call("jawa/pawn_traits",action="remove",pawn=c,trait="RM_HumReader"); print("trait remove",str(r)[:160])
    print("readout removed:",repr(sc(s,"RM_HumReading","Readout","current")))
    b0=sc(s,"RM_MapComponent_BiomeAttitude","GetBand","current")
    r=s.call("jawa/fire_incident",incidentDef="RM_LineCycle"); print("fire",str(r)[:300])
    wait(s,120)
    print("band after fire",sc(s,"RM_MapComponent_BiomeAttitude","GetBand","current"),"was",b0,"state",sc(s,"RM_LineCycle","ProofState"))
