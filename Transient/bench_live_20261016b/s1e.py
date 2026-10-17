from afk_lib import *
t0=tick()
for i in range(80):
    rows=rect(0,228,68,14)
    lo=sum(1 for r in rows if r["z"]==233 and r["f"]>0); up=sum(1 for r in rows if r["z"]==237 and r["f"]>0)
    b=B.call("jawa/flowworks_body_report",x=62,z=233).get("body")
    xs=[r["x"] for r in rows if r["z"]==233 and r["f"]>0]
    print("t",tick(),"lower wet",lo,"upper wet",up,"pond",round(b["stock"],2),"wet x range",(min(xs),max(xs)) if xs else None,flush=True)
    if lo==0: break
    if i%8==7: feed(); draft_all()
    try: step(250)
    except Exception as e: print("STOP",str(e)[:100]); feed(); draft_all()
print(safety())
