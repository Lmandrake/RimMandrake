from bx import call
from st_sandswim_lib import step
import json
tid="SolarGenerator112594"
def rd():
    p=call("jawa/power_net",{"thing":tid}); t=call("jawa/map_info",{}).get("ticksGame")
    return t, json.dumps(p,default=str)[:350]
print(rd())
for i in range(8):
    step(7500); print(rd(), flush=True)
