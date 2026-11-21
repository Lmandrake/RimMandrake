import sys, json, collections
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    r = rb.call("jawa/get_terrain_batch", {"rects": "0,0,250,250"})
    tally = collections.Counter()
    for op in str(r.get("ops") or "").split(";"):
        d,_,rr = op.partition(":")
        try: ox,oz,ow,oh = (int(v) for v in rr.split(","))
        except ValueError: continue
        tally[d] += ow*oh
    print(sum(tally.values()), dict(tally.most_common()))
