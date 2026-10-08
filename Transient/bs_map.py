import sys, os, json
root=os.getcwd()
U=os.path.join(root,"src","RimMandrake","Utils")
for p in (U, os.path.join(U,"modcheck")): sys.path.insert(0,p)
import runner
try:
    r=runner.ensure_playing_map(_gate=lambda: {"ok": True, "problems": []})
    print("ensure:",r)
except Exception as ex:
    print("ERR",repr(ex))
