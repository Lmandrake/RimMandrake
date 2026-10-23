"""hpq.py MAPID CMD... -- FlowWorks probe queries via validation_core.Bridge.hp on MAPID."""
import sys, json, time
sys.path.insert(0, r"src\RimMandrake\Utils")
import validation_core as V
B = V.Bridge()
B.call("jawa/set_current_map", mapId=int(sys.argv[1])); time.sleep(0.5)
for c in sys.argv[2:]:
    print(c, "->", json.dumps(B.probe_of("RimMandrake.FlowWorks.Hose.HoseProbe", c), default=str)[:1500])
