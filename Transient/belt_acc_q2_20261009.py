import sys,json,time
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
for i in range(20):
    g=S.call("rimworld/get_game_info"); st=g.get("state",{})
    if st.get("playable") or st.get("programState")=="Playing": break
    time.sleep(3)
print(st)
print(json.dumps(S.call("jawa/static_call",type="RimMandrake.FlowWorks.Rivers.RM_RiverWorksProof",method="ProofTaken",args="-"),default=str)[:400])
print(json.dumps(S.call("jawa/shade_probe"),default=str)[:700])
print(json.dumps(S.call("jawa/map_info"),default=str)[:400])
