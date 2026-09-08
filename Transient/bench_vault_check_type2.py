import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
# at: x=125,z=25,w=51,h=51
cells = [
    ("outer wall corner", 125, 25),
    ("outer wall N-mid (door?)", 150, 25),
    ("garrison band", 140, 40),
    ("garrison band 2", 160, 60),
    ("core wall", 145, 45),
    ("core interior", 150, 50),
]
with RimBridge(host, port, token) as rb:
    for label, x, z in cells:
        res = rb.call("rimworld/get_cell_info", {"x": x, "z": z})
        print(label, x, z, "->", json.dumps(res))
