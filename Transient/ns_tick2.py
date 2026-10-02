import sys; sys.path.insert(0,"Transient")
from cp_lib import *
r=call("jawa/time_clock"); print(r.get("ticksGame"), r.get("paused"))
