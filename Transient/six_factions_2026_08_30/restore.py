import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    print("closed:", rb.call("jawa/window_list_close", {"action":"close","typeName":"Dialog_NodeTree","closeAll":True}).get("closedCount"))
    print("destroyed:", rb.call("jawa/destroy_bulk", {"filter":"nonColonists","dryRun":False}).get("matchedCount"))
    st=rb.call("rimbridge/get_bridge_status", {})["state"]
    print("paused:", st["paused"], "timeSpeed:", st["timeSpeed"])
    t1=rb.call("rimworld/get_game_info",{})["ticksGame"]; time.sleep(2); t2=rb.call("rimworld/get_game_info",{})["ticksGame"]
    print("ticksGame %d -> %d (frozen=%s)" % (t1,t2,t1==t2))
    print("remaining dialogs:", [w["type"] for w in rb.call("jawa/window_list_close",{}).get("windows",[])])
    print("hostiles on map:", rb.call("jawa/list_pawns",{"faction":"hostile","limit":500}).get("count"))
