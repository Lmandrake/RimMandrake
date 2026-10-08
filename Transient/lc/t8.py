import sys; sys.path.insert(0,"Transient/lc")
from h import *
with S() as s:
    r=s.call("jawa/get_defs",defs="ThingDef/RM_RavenNettle",fields="plant.fertilityMin,plant.sowTags,plant.wildClusterRadius,plant.cavePlant,plant.purpose"); print(str(r)[:700])
    pj(things(s,"RM_RavenNettle"))
    print(str(s.call("jawa/biome_probe",plants="RM_RavenNettle"))[:600])
