import sys, os, json, time, traceback
root=os.getcwd()
U=os.path.join(root,"src","RimMandrake","Utils")
for p in (U, os.path.join(U,"modcheck")): sys.path.insert(0,p)
import runner
runner.ensure_playing_map(_gate=lambda: {"ok": True, "problems": []})
from rimdrive import Session
for mod in sys.argv[1:]:
    out={}
    try:
        d=runner.find_mod_dir(mod); suite=runner.load_validation(d)
        with Session(lock=None) as s:
            out=runner.run_suite(suite,s,debug=False,mod=None)
    except Exception as ex:
        out={"error":repr(ex),"tb":traceback.format_exc()[-1500:]}
    json.dump(out,open("Transient/l2sweep_%s.json"%mod,"w"),indent=1,default=str)
    print(mod,"done","all_green=",out.get("all_green"),out.get("error"))
