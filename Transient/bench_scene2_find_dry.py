import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
WATER = {"WaterDeep", "WaterOceanDeep", "WaterOceanShallow", "WaterShallow", "WaterMovingChestDeep", "WaterMovingShallow", "Marsh", "Mud"}

candidates = [
    (30, 30, 24, 24),
    (75, 30, 24, 24),
    (30, 75, 24, 24),
    (75, 75, 24, 24),
    (120, 30, 24, 24),
    (120, 75, 24, 24),
]

with RimBridge(host, port, token) as rb:
    for i in range(15):
        pawns = rb.call("jawa/list_pawns", {})
        if pawns.get("success"):
            player = [p for p in pawns.get("pawns", []) if p.get("isPlayer")]
            print("player colonists:", [(p["name"], p["x"], p["z"]) for p in player])
            break
        import time; time.sleep(2)

    for x, z, w, h in candidates:
        corners = [(x, z), (x + w, z), (x, z + h), (x + w, z + h), (x + w // 2, z + h // 2)]
        terrains, fogged = [], []
        for cx, cz in corners:
            ci = rb.call("rimworld/get_cell_info", {"x": cx, "z": cz}).get("cell", {})
            terrains.append(ci.get("terrainDefName"))
            fogged.append(ci.get("fogged"))
        wet = [t for t in terrains if t in WATER]
        fog = [f for f in fogged if f]
        print(f"rect {x},{z},{w},{h} -> terrains {terrains} fogged={fogged} {'WET' if wet else 'dry'} {'FOGGED' if fog else 'clear'}")
