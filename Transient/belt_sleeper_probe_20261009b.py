import sys
sys.path.insert(0,"Transient")
from belt_lc6_lib import *
for f in ("strangler","weeper","lure"):
  for m in ("on","off"):
    show(call("jawa/static_call", type="RimMandrake.LeaningScrub.RM_FourFormsProof", method="ProofForm", args=f+"|"+m),800)
