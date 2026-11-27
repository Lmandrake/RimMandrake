import re,collections,datetime
def dur(s):
    t=0
    for n,u in re.findall(r"([0-9.]+)(ms|us|min|h|s|d)",s):
        n=float(n); t+=n*{'us':1e-6,'ms':1e-3,'s':1,'min':60,'h':3600,'d':86400}[u]
    return t
agg=collections.defaultdict(lambda:[0,0.0,0.0,[]])
first=last=None
for l in open('wall.j'):
    m=re.search(r"\]: (\S+?)\.service: Consumed (.*?) CPU time over (.*?) wall clock time",l)
    if not m: continue
    u,cpu,wall=m.groups()
    # keep rm-* units only, and group detached helper units
    u=re.sub(r"-\d{9,}$","",u)
    if u.startswith("rm-detached-"): u="rm-detached-*"
    if not (u.startswith("rm-") or u.startswith("claude-seat")): continue
    w=dur(wall);c=dur(cpu)
    a=agg[u];a[0]+=1;a[1]+=w;a[2]+=c;a[3].append(w)
print("unit | runs in 7d | total wall h | total CPU h | median s | p90 s")
for u,(n,w,c,l) in sorted(agg.items(),key=lambda x:-x[1][1])[:22]:
    l=sorted(l);print("%-38s %6d %8.1f %8.1f %8.1f %8.1f"%(u,n,w/3600,c/3600,l[len(l)//2],l[int(len(l)*.9)-1]))
