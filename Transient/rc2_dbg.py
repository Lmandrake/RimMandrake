import sys, os, json
root=os.getcwd(); U=os.path.join(root,"src","RimMandrake","Utils")
for p in (U, os.path.join(U,"modcheck")): sys.path.insert(0,p)
import runner
from rimdrive import session as S
orig=S.Session.call
def call(self,tool,**p):
    if tool=="jawa/static_call": print("STATIC_CALL params:",p,flush=True)
    return orig(self,tool,**p)
S.Session.call=call
runner.ensure_playing_map(_gate=lambda: {"ok": True, "problems": []})
from rimdrive import Session
d=runner.find_mod_dir(sys.argv[1]); suite=runner.load_validation(d)
if sys.argv[2]!='ALL': suite.chains=[c for c in suite.chains if c[0]==sys.argv[2]]
with Session(lock=None) as s:
    out=runner.run_suite(suite,s,debug=False,mod=None)
for c in out["chains"]:
    for k in c["components"]: print(k["name"],k["verdict"],str(k["detail"])[:300])
