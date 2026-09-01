import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    try:
        r = rb.call("jawa/destroy_batch", {"rects":[{"x1":220,"z1":10,"x2":242,"z2":40}]})
        print("dict-rect:", str(r)[:200])
    except Exception as e:
        print("dict-rect ERR:", str(e)[:200])
        r = rb.call("jawa/destroy_batch", {"rects":["220,10,242,40"]})
        print("str-rect:", str(r)[:200])
    c = rb.call("rimworld/spawn_thing", {"defName":"VanometricPowerCell","x":228,"z":18})
    print("cell:", str(c)[:150])
    t = rb.call("rimworld/spawn_thing", {"defName":"BigLaserCannon","x":233,"z":20})
    print("turret:", str(t)[:150])
    for x,z in ((228,18),(233,20)):
        ci = rb.call("rimworld/get_cell_info", {"x":x,"z":z})
        print(f"cell {x},{z}:", str(ci.get("things"))[:160])
