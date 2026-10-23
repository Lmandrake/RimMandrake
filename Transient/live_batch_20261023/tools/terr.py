"""terr.py MAPID X0 Z0 W H OUT -- ascii terrain map: . majority, R SoilRich, others letters"""
import sys, json, time, collections
sys.path.insert(0, r"src\RimMandrake\Utils"); sys.path.insert(0, r"src\RimMandrake\FlowWorks"); sys.path.insert(0, r"src\RimMandrake\FlowWorks\northstar")
from rimbridge_client import RimBridge, resolve_endpoint
import site_spec as SS
mid,x0,z0,w,h = map(int, sys.argv[1:6]); out=sys.argv[6]
H,P,T = resolve_endpoint()
with RimBridge(H,P,T) as B:
    if mid>=0: B.call("jawa/set_current_map", {"mapId": mid}); time.sleep(0.5)
    t={}
    for x in range(x0,x0+w,50):
        for z in range(z0,z0+h,50):
            r=B.call("jawa/get_terrain_batch", {"rects":"%d,%d,%d,%d"%(x,z,min(50,x0+w-x),min(50,z0+h-z))})
            t.update(SS.parse_ops(r.get("ops")))
c=collections.Counter(t.values()); print(c.most_common(12))
keys={d:ch for d,ch in zip([k for k,_ in c.most_common()], ".gabcdefhijklmnopqrstuvwxyzABCDEFGHIJ")}
keys['SoilRich']='#'
with open(out,'w') as f:
    f.write(json.dumps(keys)+"\n")
    for z in range(z0+h-1,z0-1,-1):
        f.write("%3d "%z+''.join(keys.get(t.get((x,z)),'?') if t.get((x,z))!=c.most_common(1)[0][0] else '.' for x in range(x0,x0+w))+"\n")
