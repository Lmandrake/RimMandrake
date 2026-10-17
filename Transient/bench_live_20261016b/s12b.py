from afk_lib import *
sys.stdout.reconfigure(encoding="utf-8",errors="replace")
S="RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"; SL="RimMandrake.FlowWorks.RM_SlimeSlip"
A,Bk,C,D=46179,46183,46171,46175   # A bank, Bk stuck-in-canal, C,D parked
def rep(ids):
    parts=sc(SL,"ProofReport","reset").split(" | ")
    out=[]
    for x in parts:
        for i in ids:
            if "Human%d@"%i in x: out.append(x.replace("Human","H").replace(" fluid=RM_Fluid_"," ").replace("RM_",""))
    return out
def P(pid): return [q for q in pawns() if q["id"]==pid][0]
def tp(pid,x,z): return B.hp("pawn:%d=tp:%d,%d"%(pid,x,z)).get("success")
def go(pid,x,z):
    B.call("jawa/order_pawn",pawnId="Human%d"%pid,x=x,z=z,waitTicks=0,draft=True)
inslime=lambda c: 96<=c[0]<112 and 213<=c[1]<=215
def run(pid,n,every=50):
    path=[]
    for i in range(n//every):
        step(every); path.append(tuple(P(pid)["pos"]))
    return path
feed(); draft_all()
tp(C,104,203); tp(D,106,203)
def slip_counts(): 
    r=sc(SL,"ProofReport","x")
    import re
    return r
def counts(i):
    r=sc(SL,"ProofReport","x")
    for x in r.split(" | "):
        if "Human%d@"%i in x:
            import re; m=re.search(r"slips=(\d+) climbSlips=(\d+)",x); return (int(m.group(1)),int(m.group(2)))
    return (0,0)
sc(SL,"ProofReport","reset")
# 1 bank pawn to north bank
tp(A,104,210); go(A,104,219); p=run(A,900)
print("1 BANK->north: end",p[-1],"cells in slime canal",sum(map(inslime,p)),"x range",min(c[0] for c in p),max(c[0] for c in p),"slips",counts(A))
# 2 bank pawn ordered onto slime cell
tp(A,104,210); go(A,104,214); p=run(A,900)
print("2 WADE: end",p[-1],"samples in slime",sum(map(inslime,p)),"slips",counts(A))
# 3 stuck: Bk in canal middle, order out south bank
tp(Bk,100,214); sc(SL,"ProofReport","reset"); go(Bk,100,210); p=run(Bk,1500)
print("3 CLIMB-OUT: start (100,214) end",p[-1],"samples in slime",sum(map(inslime,p)),"of",len(p),"first out at",next((i*50 for i,c in enumerate(p) if not inslime(c)),None),"slips/climbSlips",counts(Bk))
# 4 natural pool
tp(A,106,221); sc(SL,"ProofReport","reset"); go(A,109,219); p=run(A,900)
print("4 NATURAL: end",p[-1],"slips/climbSlips",counts(A))
# 5 OFF
B.call("jawa/mod_settings_field",typeName=S,action="set",field="slimeSlipEnabled",value="False")
print("setting",B.call("jawa/mod_settings_field",typeName=S,action="get",field="slimeSlipEnabled").get("value"))
tp(A,104,210); sc(SL,"ProofReport","reset"); go(A,104,214); p=run(A,900)
print("5 OFF wade: end",p[-1],"samples in slime",sum(map(inslime,p)),"slips",counts(A))
tp(A,106,221); sc(SL,"ProofReport","reset"); go(A,109,219); p=run(A,600)
print("5b OFF natural: end",p[-1],"slips",counts(A))
B.call("jawa/mod_settings_field",typeName=S,action="set",field="slimeSlipEnabled",value="True")
print("restored",B.call("jawa/mod_settings_field",typeName=S,action="get",field="slimeSlipEnabled").get("value"))
for i in (A,Bk,C,D): tp(i,104,205)
draft_all(); print(safety())
