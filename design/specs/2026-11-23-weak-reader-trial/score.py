import json,random,statistics as st
from collections import defaultdict
CASES=json.load(open("cases.json")); R=[json.loads(l) for l in open("raw/answers.jsonl")]
G={g["case"]:g.get("grades",{}) for g in json.load(open("raw/grades_all.json"))}
def outcome(r,grades=G):
    if not r["ok"] or not r["parsed"]: return "FAILED"
    if r["told"]=="no": return "NOT_TOLD"
    g=grades.get(r["case"],{}).get(f"{r['model']}|{r['arm']}|{r['n']}")
    return {"C":"CORRECT","W":"WRONG",None:"UNGRADED"}[g]
def act(r):
    g=G.get(r["case"],{}).get(f"{r['model']}|{r['arm']}|{r['n']}"); return g=="C"
def table():
    T=defaultdict(lambda:defaultdict(int)); per=defaultdict(list); anyact=defaultdict(list)
    kind={c["case"]:c["kind"] for c in CASES}
    for r in R:
        o=outcome(r); k=kind[r["case"]]; T[k,r["model"],r["arm"]][o]+=1
        if o not in("FAILED","UNGRADED"):
            per[r["case"],r["model"],r["arm"]].append(o=="CORRECT"); anyact[r["case"],r["model"],r["arm"]].append(act(r))
    return T,per,anyact,kind
def ci(d,n=10000):
    rnd=random.Random(1); b=sorted(st.mean(rnd.choices(d,k=len(d))) for _ in range(n)); return b[int(.025*n)],b[int(.975*n)]
if __name__=="__main__":
    T,per,anyact,kind=table(); out={"outcomes":{},"diff":{},"cases":{}}
    for k in("STYLE","BINDING","CORRECTION","CONTROL"):
        for m,a in(("sonnet","none"),("sonnet","old"),("sonnet","new"),("opus","old"),("opus","new")):
            t=T[k,m,a]; n=sum(t.values()); out["outcomes"][f"{k}|{m}|{a}"]=dict(t)
            print(f"{k:10} {m:6} {a:4} n={n:2} "+" ".join(f"{o}={t[o]}" for o in("CORRECT","WRONG","NOT_TOLD","FAILED","UNGRADED"))+f" correct={100*t['CORRECT']/n:.0f}%")
        for name,src in(("stated rule correct",per),("act right, TOLD ignored",anyact)):
          for m in("sonnet","opus"):
            d=[100*(st.mean(src[c["case"],m,"new"])-st.mean(src[c["case"],m,"old"])) for c in CASES if c["kind"]==k]
            lo,hi=ci(d); out["diff"][f"{k}|{m}|{name}"]=dict(mean=st.mean(d),lo=lo,hi=hi,sd=st.stdev(d))
            print(f"   diff {m:6} {name:24} new-old={st.mean(d):+.0f} [{lo:+.0f},{hi:+.0f}] sd={st.stdev(d):.0f}")
    print()
    for c in CASES:
        row={f"{m}_{a}":sum(per[c["case"],m,a]) for m,a in(("sonnet","none"),("sonnet","old"),("sonnet","new"),("opus","old"),("opus","new"))}
        nt={a:sum(1 for r in R if r["case"]==c["case"] and r["model"]=="sonnet" and r["arm"]==a and outcome(r)=="NOT_TOLD") for a in("old","new")}
        ro={a:sum(anyact[c["case"],"sonnet",a]) for a in("none","old","new")}
        out["cases"][c["case"]]=dict(correct=row,not_told=nt,act_right=ro); print(c["case"],row,"not_told",nt,"act_right",ro)
    allc=[c["case"] for c in CASES]; f=lambda a:100*st.mean(st.mean(anyact[c,"sonnet",a]) for c in allc)
    print("act right over all cases: none %.0f old %.0f new %.0f"%(f("none"),f("old"),f("new")))
    json.dump(out,open("scores.json","w"),indent=1)
