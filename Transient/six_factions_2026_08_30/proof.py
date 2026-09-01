import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def wins(rb):
    r=rb.call("jawa/window_list_close", {})
    return [w["type"] for w in r.get("windows",[])]
def nodetrees(rb): return sum(1 for t in wins(rb) if "Dialog_NodeTree" in t)
def lords(rb): return rb.call("jawa/lord_pawn_move", {"action":"list"}).get("count",0)
with RimBridge(host, port, token) as rb:
    for t in rb.list_tools():
        if t["name"]=="jawa/window_list_close":
            print("PARAMS:", json.dumps((t.get("inputSchema") or {}).get("properties",{}))[:600]); print()
    rb.call("jawa/destroy_bulk", {"filter":"nonColonists","dryRun":False})
    print("dialogs before close:", nodetrees(rb))
    r=rb.call("jawa/window_list_close", {"action":"close","typeName":"Dialog_NodeTree","closeAll":True})
    print("close resp:", json.dumps({k:v for k,v in r.items() if k not in("operation","windows")})[:250])
    print("dialogs after close:", nodetrees(rb))
    for fac in ["Pirate","Empire","Salvagers"]:
        d0=nodetrees(rb); l0=lords(rb)
        rr=rb.call("jawa/fire_raid", {"faction":fac,"points":3000,"strategy":"ImmediateAttack",
                                      "arrivalMode":"EdgeWalkIn","dryRun":False})
        time.sleep(1.0)
        d1=nodetrees(rb); l1=lords(rb)
        n=sum(a.get("pawnsArrived",0) for a in (rr.get("arrived") or []))
        print("  %-10s dialogs %d->%d | lords %d->%d | pawns=%d | executed=%s"
              % (fac, d0, d1, l0, l1, n, rr.get("executed")))
        rb.call("jawa/window_list_close", {"action":"close","typeName":"Dialog_NodeTree","closeAll":True})
        rb.call("jawa/destroy_bulk", {"filter":"nonColonists","dryRun":False})
