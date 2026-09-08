import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for x in range(78, 106):
        for z in range(82, 92):
            ci = rb.call("rimworld/get_cell_info", {"x": x, "z": z}).get("cell", {})
            for t in ci.get("things", []):
                dn = t.get("defName", "")
                if dn not in ("Filth_DriedBlood", "Filth_AnimalFilth", "Filth_Trash"):
                    print(x, z, dn)
