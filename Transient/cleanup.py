import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
things = ["Megascarab22480","Megascarab22532","Megascarab22552",
          "BigLaserCannon22478","Turret_Sniper22521","VFES_Turret_Ballista22550",
          "Turret_Zapper22562","VanometricPowerCell22477","VanometricPowerCell22570"]
with RimBridge(host, port, token) as rb:
    for t in things:
        try:
            r = rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: Destroy", "thingId": "Thing_"+t})
            ok = r.get("success")
        except Exception as e:
            ok = "ERR " + str(e)[:60]
        print(t, "->", ok)
    # verify: pawns gone, cells empty-ish, still paused
    ps = rb.call("jawa/list_pawns", {})
    scars = [s for s in ps.get("pawns", []) if "egascarab" in str(s.get("kind"))]
    print("scarabs left:", len(scars))
    ins = rb.call("jawa/inspect_string", {"rect": "220,10,242,40"})
    print("pad things left:", str(ins.get("count") or ins)[:150])
    import time
    t0 = rb.call("rimworld/get_game_info", {}).get("ticksGame"); time.sleep(2)
    t1 = rb.call("rimworld/get_game_info", {}).get("ticksGame")
    print("paused check:", t0, "==", t1, t0 == t1)
