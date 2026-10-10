import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
for tid in ["RM_Silloch691666","RM_Brathek691667","RM_Grolth691668","RM_Skreth691669","RM_Skreth691670"]:
    r=S.call("jawa/thing_graphic", thing=tid)
    t=(r.get("things") or [{}])[0]
    print("GFX", tid, {k:t.get(k) for k in ("graphicClass","graphicPath","resolvedPath","materialName","textureName","isErrorMaterial","error","errorMaterial") if k in t}, (r.get("refused") or "")[:1])
