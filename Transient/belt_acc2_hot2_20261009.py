import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
LOG = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"
def cnt(): return open(LOG, encoding="utf-8", errors="ignore").read().count("Root level exception")
g = S.call("jawa/get_defs", defs="PawnKindDef/RM_Drazzik", fields="lifeStages")
print("before", json.dumps(g.get("defs"), default=str)[:400])
r = S.call("jawa/hot_reload_defs"); print("hot", json.dumps({k: r.get(k) for k in r if k not in ("operation", "state")}, default=str)[:300], flush=True)
for i in range(20):
    time.sleep(3)
    gi = S.call("rimworld/get_game_info")
    st = (gi.get("state") or {}) if isinstance(gi, dict) else {}
    print(i, st.get("programState"), st.get("longEventPending"), flush=True)
    if st.get("programState") == "Playing" and not st.get("longEventPending") and i > 2: break
print("exc", cnt())
