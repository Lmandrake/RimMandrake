import json,re,sys
P=json.load(open("/mnt/d/ClaudeWork/scratch/weak_reader_trial/pool.json"))
def blocks(t):
    out=[];cur=[]
    for l in t.split("\n"):
        if re.match(r"\s*([-*]|\d+\.) |\s*$|\|",l) and cur: out.append("\n".join(cur));cur=[]
        if l.strip(): cur.append(l)
    if cur: out.append("\n".join(cur))
    return out
def near(path,term,cap=700):
    for r in P:
        if r["path"].endswith(path):
            for side in("old","new"):
                bs=blocks(r[side])
                for b in bs:
                    if term.lower() in re.sub(r"\s+"," ",b).lower():
                        yield side,r["head"][:50],re.sub(r"\s+"," ",b)[:cap]
if __name__=="__main__":
    for a in sys.argv[1:]:
        p,t=a.split("::"); print("####",p,"::",t)
        for s,h,b in near(p,t): print(" ",s,"|",h,"|",b)
