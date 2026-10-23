"""hp.py MAPID CMD [CMD...] -- run HoseProbe commands on a map, print compact JSON answers. 'census@x,z' filters census to reel x,z."""
import sys, json, time, os
sys.path.insert(0, r"src\RimMandrake\Utils"); sys.path.insert(0, r"src\RimMandrake\FlowWorks\northstar")
from rimbridge_client import RimBridge, resolve_endpoint
import joint_check as J
h_, p_, t_ = resolve_endpoint()
with RimBridge(h_, p_, t_) as B:
    if sys.argv[1] != "-":
        B.call("jawa/set_current_map", {"mapId": int(sys.argv[1])}); time.sleep(1.0)
    for cmd in sys.argv[2:]:
        if cmd.startswith("bridge:"):
            tool, args = cmd[7:].split("|", 1)
            print(cmd[:60], "->", json.dumps(B.call(tool, json.loads(args)), default=str)[:20000]); continue
        if cmd.startswith("census@"):
            x, z = [int(v) for v in cmd[7:].split(",")]
            c = J._probe(B, "census")
            hs = [h for h in (c.get("hoses") or []) if list(h.get("reel") or h.get("at") or [])[:2] == [x, z] or str(h).find("[%d, %d]" % (x, z)) >= 0]
            print(cmd, "->", json.dumps(hs, default=str)[:20000]); continue
        a = J._probe(B, cmd)
        print(cmd, "->", json.dumps(a, default=str)[:900])
