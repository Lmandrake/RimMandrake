import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
r=S.call("jawa/drain_log",limit=400,errorsOnly=True)
t=json.dumps(r,default=str)
print("drain success",r.get("success") if isinstance(r,dict) else "?", "len",len(t))
for k in ("Graphic_Linked","get_MatSingle","ExplosiveKnockback","RM_Knockback","excavation load repair","KineticArms","Could not resolve cross-reference"):
    print(k, t.count(k))
print(t[:1500])
import re
msgs=[m["text"] for m in r.get("messages",[]) if "cross-ref" in m["text"] or m.get("type")=="Error"]
seen=set()
for m in msgs:
    k=re.sub(r"\s+"," ",m)[:170]
    if k not in seen: seen.add(k); print("MSG",k)
