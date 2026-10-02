import sys, json; sys.path.insert(0,"Transient")
from cp_lib import *
tl = S.list_tools(); tl = tl if isinstance(tl,list) else tl.get("tools", tl)
for t in tl:
    if t["name"]=="jawa/window_list_close": print(json.dumps(t.get("inputSchema"))[:900])
r=call("jawa/window_list_close", action="list"); print(J(r,500))
print(J(call("jawa/window_list_close", action="list"),400))
