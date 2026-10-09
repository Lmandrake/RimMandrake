import sys; sys.path.insert(0,"Transient")
from belt_lc6_lib import *
r=call("jawa/drain_log", limit=800, errorsOnly=True)
print(len(r["messages"]), r.get("totalInBuffer"))
seen=set()
for m in r["messages"]:
    t=m["text"]
    if any(k in t for k in ("extures","Texture2D","MatFrom","STARTUP_TIMING","downloadUrl","empty display name","burnedDef","world-targeting","cross-reference","Patch operation","Could not find a type named","UI/")): continue
    k=t[:120]
    if k in seen: continue
    seen.add(k); print("-", t[:330].replace("\n"," | "))
