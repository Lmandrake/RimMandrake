import csv,sys,math,json
def arm(path,lo=0.5,hi=10.0):
    t=0.0; rows=[]
    for r in csv.DictReader(open(path)):
        ms=float(r['ms']); t+=ms/1000.0
        rows.append((t,ms,int(r['paused']),int(r['in_air'])))
    w=[x for x in rows if lo<=x[0]<=hi and not x[2]]
    s=sorted(x[1] for x in w); n=len(s)
    p99=s[max(0,math.ceil(0.99*n)-1)] if n else None
    air=[x for x in w if x[3]>0]
    first_air=min((x[0] for x in air),default=None); last_air=max((x[0] for x in air),default=None)
    st=[(round(x[0],1),round(x[1]),x[3]) for x in w if x[1]>40]
    mean=lambda L:round(sum(x[1] for x in L)/len(L),1) if L else None
    pre=[x for x in w if first_air and x[0]<first_air]; post=[x for x in w if last_air and x[0]>last_air]
    return dict(n=n,p99=p99,sum_s=round(sum(x[1] for x in w)/1000,2),mean=mean(w),air_win=(round(first_air,1) if first_air else None,round(last_air,1) if last_air else None),
                mean_pre=mean(pre),mean_air=mean(air),mean_post=mean(post),n_air=len(air),stalls=st)
for p in sys.argv[1:]:
    a=arm(p); print(p.split('/')[-1], json.dumps(a))
