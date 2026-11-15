import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint()
samples = [(130,153),(139,153),(130,162),(226,141),(230,145),(205,16),(34,172),(46,181),(110,88),(56,187)]
with RimBridge(h,p,tk) as rb:
    for (x,z) in samples:
        for dx in (-1,0,1):
            for dz in (-1,0,1):
                r = rb.call("rimworld/get_cell_info", {"x":x+dx,"z":z+dz})
                c = r.get("cell") or r
                terr = c.get("terrainDefName") or c.get("terrain")
                if terr and "Ash_Deep" not in str(terr):
                    print(x+dx, z+dz, json.dumps({k:v for k,v in c.items() if k not in ("things",)})[:400])
