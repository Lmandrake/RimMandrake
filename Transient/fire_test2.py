import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()

def show(tag, r): print(tag, "|", str(r)[:220]); return r

with RimBridge(host, port, token) as rb:
    t0 = rb.call("rimworld/get_game_info", {}).get("ticksGame")
    print("ticks at start:", t0)
    # 1. clear a pad
    show("clear", rb.call("jawa/destroy_batch", {"x1":220,"z1":10,"x2":242,"z2":40,"includePlants":True}))
    # 2. power first, then turret within connect radius
    show("cell", rb.call("rimworld/spawn_thing", {"defName":"VanometricPowerCell","x":228,"z":18}))
    show("turret", rb.call("rimworld/spawn_thing", {"defName":"BigLaserCannon","x":233,"z":20}))
    # 3. read back the pad
    for x,z in ((228,18),(233,20)):
        c = rb.call("rimworld/get_cell_info", {"x":x,"z":z})
        print(f"cell {x},{z}:", str(c.get("things"))[:160])
