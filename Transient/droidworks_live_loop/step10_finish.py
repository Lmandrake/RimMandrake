import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()

kg_ids = ['RSW_DW_Race_guy762_DroidRace_ADMkI18331', 'RSW_DW_Race_guy762_DroidRace_ADMkI18332', 'RSW_DW_Race_guy762_DroidRace_ADMkI18333']
spikePawn = 'RSW_DW_Race_guy762_DroidRace_ADMkI18336'

with RimBridge(host, port, token) as rb:
    print("=== check1 full pawn snapshot (post-597-tick) ===")
    for pid in kg_ids:
        g = rb.call("jawa/pawn_get", {"pawn": pid})
        print(pid, json.dumps(g.get("pawns", [{}])[0], default=str)[:1200])

    print("=== spike pawn full snapshot (downed check) ===")
    g = rb.call("jawa/pawn_get", {"pawn": spikePawn})
    print(json.dumps(g.get("pawns", [{}])[0], default=str)[:1500])

    print("=== corpses on map ===")
    things = rb.call("jawa/list_things", {"group": "Corpse"})
    print(json.dumps(things, default=str)[:3000])

    print("=== terrain scan near GNK site ===")
    tb = rb.call("jawa/get_terrain_batch", {"rects": "128,90,20,20"})
    print(json.dumps(tb, default=str)[:2500])

    rb.call("rimworld/jump_camera_to_cell", {"x": 138, "z": 100})
    rb.call("jawa/clear_ui", {})
    ss = rb.call("rimworld/take_screenshot", {"fileName": "droidworks_a1_gnk_detonation_result.png"})
    print("=== screenshot ===")
    print(json.dumps(ss, default=str)[:1500])
