import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for i in range(6):
        r = rb.call("rimworld/step_game_ticks", {"ticks": 500})
        print("STEP", i, r.get("advancedTicks"), r.get("endTicksGame"))
        lp = rb.call("jawa/list_pawns", {})
        m = next((p for p in lp.get("pawns", []) if p.get("id") == "AA_Eyeling669122"), None)
        if m:
            print("  Marquee pos", m.get("x"), m.get("z"), "spawned=", m.get("spawned"))
        else:
            print("  Marquee NOT IN CENSUS (may be inside tank now)")
        tank = rb.call("jawa/list_things", {"rect": "171,139,1,2", "limit": 5, "defName": "RSW_BactaTank"})
        print("  tank things", json.dumps(tank.get("things"))[:300])
        insp = rb.call("jawa/inspect_string", {"thingIds": "RSW_BactaTank692523"})
        print("  inspect", json.dumps(insp.get("things"))[:400])
