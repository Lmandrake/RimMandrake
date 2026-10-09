import sys,json,collections
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
r=S.call("jawa/get_terrain_batch",rects="0,0,100,100")
cnt=collections.Counter(); first={}
for op in r["ops"].split(";"):
    n,rest=op.split(":"); x,z,w,h=map(int,rest.split(","))
    cnt[n]+=w*h; first.setdefault(n,(x,z))
print(dict(cnt)); print(first)
