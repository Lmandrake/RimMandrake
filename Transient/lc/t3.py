import sys; sys.path.insert(0,"Transient/lc")
from h import *
with S() as s:
    r=s.call("rimbridge/get_lua_reference"); print(str(r)[:3500])
    r=s.call("jawa/type_probe",typeName="RimMandrake.RustCathedral.Hum.RM_RustCathedralHumProof"); print(str(r)[:1500])
