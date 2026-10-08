import sys, os, json
root=os.getcwd(); U=os.path.join(root,"src","RimMandrake","Utils")
for p in (U, os.path.join(U,"modcheck")): sys.path.insert(0,p)
from rimdrive import Session
with Session(lock=None) as s:
    r=s.call("jawa/static_call", type="RimMandrake.Utinni.FallLineArrivals.FallLineGateProof", method="ProofGate", args="x")
    print(json.dumps(r)[:400])
    print(s._rb.__class__, )
