import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
for t in ["jawa/time_clock","jawa/list_maps"]:
    print(t, str(S.call(t))[:600])
