from bx import call
import collections, sys
for d in ("RM_Filth_DisturbedSand","RM_Filth_DragMark"):
    r=call("jawa/list_things",{"defName":d,"limit":200}); print(d, r.get("success"), r.get("message"), [(t.get("x"),t.get("z")) for t in r.get("things",[])][:20])
r=call("jawa/list_things",{"rect":"25,40,12,12","limit":300}); print(collections.Counter(t.get("def") for t in r.get("things",[])))
r=call("jawa/list_things",{"rect":"35,25,12,12","limit":300}); print(collections.Counter(t.get("def") for t in r.get("things",[])))
