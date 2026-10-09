import sys; sys.path.insert(0,"Transient")
from belt_lc6_lib import *
call("jawa/spawn_batch", ops="RM_GlowTank:100,120")
t=call("jawa/list_things", defName="RM_GlowTank")["things"][0]["id"]
show(call("jawa/inspect_string", thingIds=t),500)
show(call("jawa/comp_read", thing=t, comp="Refuelable"),300)
