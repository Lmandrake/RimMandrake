import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
rb = RimBridge(host=host, port=port, token=token).connect()
pts = {
  "Holmes(112,12)": (112,12),
  "Hicks(144,26)": (144,26),
  "Metti(98,14)": (98,14),
  "Shulla819018(126,17)": (126,17),
  "Shulla819017(127,14)": (127,14),
  "Shulla822719(96,11)": (96,11),
  "Ollopom(62,9)": (62,9),
  "Dactillion(69,13)": (69,13),
}
for name, (x,z) in pts.items():
    ci = rb.call("rimworld/get_cell_info", {"x": x, "z": z}).get("cell", {})
    print(name, "terrain=", ci.get("terrainDefName"), "isWater=", ci.get("isWater"), "things=", [t.get("defName") for t in (ci.get("things") or [])])
