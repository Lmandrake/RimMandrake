import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=20) as rb:
    colonists = rb.call("rimworld/list_colonists", {})["colonists"]
    p = next(c for c in colonists if c["name"] == "Jackalope")
    print("pos:", p["position"], "job:", p["job"])
    for x in range(107, 118):
        for z in range(114, 121):
            r = rb.call("rimworld/get_cell_info", {"x": x, "z": z})
            names = [t["defName"] for t in r["cell"]["things"]]
            if any("Graffiti" in n for n in names):
                print("MARK AT", x, z, names)
