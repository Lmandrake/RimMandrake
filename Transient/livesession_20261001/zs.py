from bx import call
from st_sandswim_lib import step
import collections
def census():
    out={}
    for d in ("Filth_Blood","Filth_BloodInsect","Filth_BloodAnimal"):
        r=call("jawa/list_things",{"defName":d,"rect":"195,165,30,30","limit":200}); out[d]=len(r.get("things") or [])
    r=call("jawa/list_things",{"rect":"195,165,30,30","limit":400}); out["corpses"]=[t.get("def") for t in r.get("things",[]) if str(t.get("def")).startswith("Corpse")]
    return out
print(0, census())
for i in range(4):
    step(600); print(i+1, census(), flush=True)
r=call("jawa/list_things",{"rect":"195,165,30,30","limit":400}); print(collections.Counter(t.get("def") for t in r.get("things",[])).most_common(12))
