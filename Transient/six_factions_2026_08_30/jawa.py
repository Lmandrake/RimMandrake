import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
FACS=["Jawa_HuttCartel","Jawa_Junkers","Jawa_AscendantHelix"]
def dlg(rb): return sum(1 for w in rb.call("jawa/window_list_close",{}).get("windows",[]) if "Dialog_NodeTree" in w["type"])
def lords(rb): return rb.call("jawa/lord_pawn_move", {"action":"list"}).get("count",0)
with RimBridge(host, port, token) as rb:
    rb.call("jawa/window_list_close", {"action":"close","typeName":"Dialog_NodeTree","closeAll":True})
    rb.call("jawa/destroy_bulk", {"filter":"nonColonists","dryRun":False})
    for f in FACS:
        r=rb.call("jawa/faction_relations_set", {"faction":f,"other":"Player","kind":"Hostile","both":True})
        print("hostile %-20s ok=%s hostileNow=%s" % (f, r.get("success"), json.dumps(r.get("kind") or r.get("after"))[:120]))
    hs={x["defName"]:x["hostile"] for x in rb.call("jawa/list_factions",{"includeHidden":True}).get("factions",[])}
    print("verified hostile:", {f:hs.get(f) for f in FACS})
    for f in FACS:
        d0=dlg(rb); l0=lords(rb)
        rr=rb.call("jawa/fire_raid", {"faction":f,"points":3000,"strategy":"ImmediateAttack",
                                      "arrivalMode":"EdgeWalkIn","dryRun":False})
        time.sleep(1.2)
        n=sum(a.get("pawnsArrived",0) for a in (rr.get("arrived") or []))
        print("  %-20s subst=%-5s dialogs %d->%d lords %d->%d pawns=%d"
              % (f, (rr.get("actual") or {}).get("substituted"), d0, dlg(rb), l0, lords(rb), n))
        rb.call("jawa/window_list_close", {"action":"close","typeName":"Dialog_NodeTree","closeAll":True})
        rb.call("jawa/destroy_bulk", {"filter":"nonColonists","dryRun":False})
    print("--- restoring relations to Neutral/0 ---")
    for f in FACS:
        r=rb.call("jawa/faction_relations_set", {"faction":f,"other":"Player","kind":"Neutral","goodwill":0,"both":True})
        print("  restore %-20s ok=%s" % (f, r.get("success")))
    hs={x["defName"]:(x["hostile"],x["goodwill"]) for x in rb.call("jawa/list_factions",{"includeHidden":True}).get("factions",[])}
    print("after restore:", {f:hs.get(f) for f in FACS})
