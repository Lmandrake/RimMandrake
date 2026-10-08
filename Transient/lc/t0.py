import sys; sys.path.insert(0,"Transient/lc")
from h import *
with S() as s:
    pj(s.call("rimbridge/get_bridge_status"))
    pj(s.call("rimworld/get_game_info"))
    names=[t["name"] if isinstance(t,dict) else t for t in s.tools]
    print(len(names)); print([n for n in names if n.startswith("jawa/")])
