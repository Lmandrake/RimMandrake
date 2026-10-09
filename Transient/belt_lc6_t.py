import sys; sys.path.insert(0,"Transient")
from belt_lc6_lib import *
print(call("jawa/get_defs", defs="ThingDef/RUT_DyingCreep;ThingDef/RUT_DeadCreep", fields="defName").get("notFound"))
show(call("jawa/spawn_batch", ops="RUT_DyingCreep:180,180"),150)
for i in range(14):
    step(2000)
    a=call("jawa/list_things", defName="RUT_DyingCreep").get("countMatched"); d=call("jawa/list_things", defName="RUT_DeadCreep").get("countMatched")
    print(i, (i+1)*2000, "dying", a, "dead filth", d)
    if a==0 and d: break
