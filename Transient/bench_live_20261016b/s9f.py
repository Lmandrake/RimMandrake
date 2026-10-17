from afk_lib import *
sys.stdout.reconfigure(encoding="utf-8",errors="replace")
S="RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
pid=44841
def body():
    b=B.call("jawa/flowworks_body_report",x=230,z=234).get("body") or {}; return round(b.get("stock"),2)
def eng(): e=B.call("jawa/flowworks_engine_state"); return e.get("sinkTransferredTotal"),e.get("overflowDestroyedTotal")
def des():
    r=B.call("jawa/designate_batch",action="query",designation="RM_FillInCanal",rect="228,228,16,14"); return [(d["x"],d["z"]) for d in r.get("designations",[]) if 228<=d["x"]<244 and 228<=d["z"]<242]
def canal(): rows=rect(228,228,16,14); return wetn(rows),vol(rows)
B.call("jawa/mod_settings_field",typeName=S,action="set",field="edgeSinksEnabled",value="False")
print(B.call("jawa/set_pawn_skill",pawn=pid,skill="Mining",level=20).get("success"))
print("before pond",body(),"canal",canal(),"eng",eng(),"des",len(des()))
cell=(242,234)
pr=B.call("jawa/flowworks_job_probe",x=cell[0],z=cell[1],kind="fillin",pawnId=pid,forced=True); wg=pr["workGiver"]
o=B.call("jawa/ordered_job",pawnId=pid,jobDef=wg["jobDef"],targetAX=cell[0],targetAZ=cell[1],waitTicks=60); print("accepted",o.get("accepted"))
t0=tick(); log=[]
for i in range(30):
    step(100)
    d=des(); c=rect(242,234,1,1,False)[0]; log.append((tick()-t0,body(),canal(),c["d"],c["f"],len(d)))
    if i%5==0: print(log[-1],eng(),flush=True)
    if cell not in d: break
step(750)
print("done at",log[-1],"eng",eng()); print("settled pond",body(),"canal",canal(),"cell",[(r["d"],r["f"]) for r in rect(242,234,1,1,False)])
print("neighbour cells", [(r["x"],r["d"],r["f"]) for r in rect(238,234,5,1,False)])
B.call("jawa/mod_settings_field",typeName=S,action="set",field="edgeSinksEnabled",value="True")
print("restored",B.call("jawa/mod_settings_field",typeName=S,action="get",field="edgeSinksEnabled").get("value"), safety())
