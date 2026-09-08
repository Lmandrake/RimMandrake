import sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()

def snap(rb, x, z, w, h):
    r = rb.call("jawa/list_things", {"rect": f"{x},{z},{w},{h}", "includePawns": True})
    return [(t.get("def"), t.get("x"), t.get("z")) for t in r.get("things", [])]

with RimBridge(host, port, token) as rb:
    # isolated site A: full-charge GNK
    r = rb.call("rimworld/execute_debug_action", {
        "path": "Actions\\Spawn Pawn...\\RSW_DW_OuterRim_GNKDroid", "x": 60, "z": 60})
    print("spawn A", r.get("success"), r.get("message"))
    time.sleep(0.5)
    lp = rb.call("jawa/list_pawns", {})
    aid = sorted([p["id"] for p in lp.get("pawns", []) if p.get("kind") == "RSW_DW_OuterRim_GNKDroid"],
                 key=lambda i: int(''.join(filter(str.isdigit, i))))[-1]
    print("A id:", aid)
    ga = rb.call("jawa/pawn_get", {"pawn": aid})
    ax = ga["pawns"][0]["position"]["x"]; az = ga["pawns"][0]["position"]["z"]
    print("A actual position:", ax, az)
    r = rb.call("jawa/pawn_need", {"pawn": aid, "need": "RSW_DW_Power", "action": "need", "level": 1.0})
    print("set A power 1.0", r.get("success"))
    before_a = snap(rb, ax-8, az-8, 16, 16)
    r = rb.call("jawa/damage", {"damageDef": "Bomb", "amount": 2000, "thingId": aid, "allowColonists": True})
    print("kill A", r.get("success"), r.get("message"))
    time.sleep(1)
    after_a = snap(rb, ax-8, az-8, 16, 16)
    print("A before:", before_a)
    print("A after :", after_a)

    # isolated site B: 5%-charge GNK, far away
    r = rb.call("rimworld/execute_debug_action", {
        "path": "Actions\\Spawn Pawn...\\RSW_DW_OuterRim_GNKDroid", "x": 60, "z": 180})
    print("spawn B", r.get("success"), r.get("message"))
    time.sleep(0.5)
    lp = rb.call("jawa/list_pawns", {})
    bid = sorted([p["id"] for p in lp.get("pawns", []) if p.get("kind") == "RSW_DW_OuterRim_GNKDroid"],
                 key=lambda i: int(''.join(filter(str.isdigit, i))))[-1]
    print("B id:", bid)
    gb = rb.call("jawa/pawn_get", {"pawn": bid})
    bx = gb["pawns"][0]["position"]["x"]; bz = gb["pawns"][0]["position"]["z"]
    print("B actual position:", bx, bz)
    r = rb.call("jawa/pawn_need", {"pawn": bid, "need": "RSW_DW_Power", "action": "need", "level": 0.05})
    print("set B power 0.05", r.get("success"))
    before_b = snap(rb, bx-8, bz-8, 16, 16)
    r = rb.call("jawa/damage", {"damageDef": "Bomb", "amount": 2000, "thingId": bid, "allowColonists": True})
    print("kill B", r.get("success"), r.get("message"))
    time.sleep(1)
    after_b = snap(rb, bx-8, bz-8, 16, 16)
    print("B before:", before_b)
    print("B after :", after_b)

    rb.call("rimworld/jump_camera_to_cell", {"x": ax, "z": az})
    rb.call("jawa/clear_ui", {})
    ssA = rb.call("rimworld/take_screenshot", {"fileName": "droidworks_a1_gnk_A_100pct.png"})
    print("screenshot A:", ssA.get("path"))

    rb.call("rimworld/jump_camera_to_cell", {"x": bx, "z": bz})
    rb.call("jawa/clear_ui", {})
    ssB = rb.call("rimworld/take_screenshot", {"fileName": "droidworks_a1_gnk_B_5pct.png"})
    print("screenshot B:", ssB.get("path"))
