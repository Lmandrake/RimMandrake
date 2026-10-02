import sys, json; sys.path.insert(0,"Transient")
from cp_lib import *
tl = S.list_tools()
tl = tl if isinstance(tl,list) else tl.get("tools", tl)
for t in tl:
    n = t.get("name","")
    if "destroy" in n or n=="jawa/list_things":
        print(json.dumps(t)[:2500])
