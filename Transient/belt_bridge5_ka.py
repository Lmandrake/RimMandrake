import sys, json, re
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
P="RimMandrake.KineticArms.RM_KineticArmsProof"
def c(m,a):
    r=S.call("jawa/static_call", type=P, method=m, args=a); return str(r.get("result")) if r.get("success") else "CALLFAIL "+json.dumps(r,default=str)[:300]
names=c("Names","x"); print("names", names)
sc=[s for s in names.split(" ")[0].split(",") if s]
org=c("Origins",str(len(sc))).split(";"); print("origins", len(org))
c("Settings","reset")
for n,o in zip(sc,org):
    st=c("Stage","%s,%s"%(n,o))
    if not st.startswith("STAGED"): print("%-18s %s"%(n,st[:300])); continue
    m=re.search(r"ticks=(\d+)",st); S.call("rimworld/step_game_ticks", ticks=int(m.group(1)) if m else 90)
    print("%-18s %s"%(n,c("Verdict",n)[:300]))
c("Settings","reset")
