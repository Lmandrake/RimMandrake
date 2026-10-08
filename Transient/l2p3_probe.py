import sys, os, json
root=os.getcwd(); U=os.path.join(root,"src","RimMandrake","Utils")
for p in (U, os.path.join(U,"modcheck")): sys.path.insert(0,p)
from rimdrive import Session
with Session(lock=None) as s:
    for d,f in (("BiomeDef/Desert","modExtensions"),("BiomeDef/ExtremeDesert","modExtensions"),("RimMandrake.MovingDunes.RM_DuneMaterialDef/RM_Dunes_Sand","defName"),("RimMandrake.MovingDunes.RM_DuneGlobalsDef/RM_Dunes_Globals","defName")):
        r=s.call("jawa/get_defs",defs=d,fields=f)
        print(d,"->",json.dumps([x.get("fields") or x.get("found") for x in r.get("defs",[])]),r.get("notFound"))
    r=s.call("jawa/static_call",type="RimMandrake.MovingDunes.MovingDunesProof",method="ProofMath",args="x"); print(str(r)[:300])
