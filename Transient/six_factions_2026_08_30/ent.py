import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def dlg(rb): return sum(1 for w in rb.call("jawa/window_list_close",{}).get("windows",[]) if "Dialog_NodeTree" in w["type"])
NEEDLES=["no usable PawnGroupMakers","has no PawnGroupMakers","Cannot generate pawns","Exception while generating","No raid strategy found","Got no pawns"]
with RimBridge(host, port, token) as rb:
    rb.call("jawa/window_list_close", {"action":"close","typeName":"Dialog_NodeTree","closeAll":True})
    rb.call("jawa/destroy_bulk", {"filter":"nonColonists","dryRun":False})
    for fac in ["Entities","AM_EnemyPirate","TribalHostile","DP_GenericHostile"]:
        base={n:len(rb.call("jawa/drain_log",{"limit":40,"contains":n}).get("messages") or []) for n in NEEDLES}
        d0=dlg(rb)
        r=rb.call("jawa/fire_raid", {"faction":fac,"points":3000,"strategy":"ImmediateAttack",
                                     "arrivalMode":"EdgeWalkIn","dryRun":False})
        time.sleep(1.0)
        d1=dlg(rb)
        n=sum(a.get("pawnsArrived",0) for a in (r.get("arrived") or []))
        print("%-18s dialogs %d->%d pawns=%d" % (fac,d0,d1,n))
        for nd in NEEDLES:
            rows=[m.get("text","") for m in (rb.call("jawa/drain_log",{"limit":40,"contains":nd}).get("messages") or [])]
            if len(rows)>base[nd]: print("     +LOG %-30s :: %s" % (nd, rows[-1][:160]))
        rb.call("jawa/window_list_close", {"action":"close","typeName":"Dialog_NodeTree","closeAll":True})
        rb.call("jawa/destroy_bulk", {"filter":"nonColonists","dryRun":False})
