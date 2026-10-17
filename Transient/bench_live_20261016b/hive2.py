from afk_lib import *
r=B.call("jawa/destroy_batch",rects="192,144,1,1;200,143,1,2",categories="Building"); print(str(r)[:300])
for d in ("GlowPod","Hive"):
    r=B.call("jawa/list_things",defName=d); print(d,[(t.get("x"),t.get("z"),t.get("faction")) for t in r.get("things",[])])
B.call("jawa/incident_queue_clear")
