import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
def j(x,n=500): return json.dumps(x,default=str)[:n]
# Rehearsal COPY of the canonical save (bridge4); never saved over.
r=S.call("rimworld/load_game_ready", saveName="BAZAAR_VTE_UNWIND_REHEARSAL_20261009", timeoutMs=600000, ignoreModCompatibility=True)
print("load", j(r,400))
w=S.call("jawa/window_list"); print("windows", j(w,800))
