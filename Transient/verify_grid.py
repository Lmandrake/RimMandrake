import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
samples = [(203,180,"Turret_AutoChargeBlaster"),(136,178,"FT_TurretAA area"),(174,158,"VFEP row"),(160,141,"5x5 row"),(191,139,"Singularity row"),(148,167,"3x3 row")]
with RimBridge(host, port, token) as rb:
    for x,z,tag in samples:
        c = rb.call("rimworld/get_cell_info", {"x": x, "z": z})
        things = [t.get("defName") or t.get("label") for t in c.get("things", [])]
        print((x,z), tag, "->", things[:3])
