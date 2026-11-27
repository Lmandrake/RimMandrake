import sqlite3,os,time,json,glob,statistics as st,collections
now=time.time(); since=now-7*86400
def q(v):
    v=sorted(v); return v[len(v)//2], v[int(len(v)*0.9)-1] if len(v)>1 else v[0]
c=sqlite3.connect('file:'+os.path.expanduser('~/.local/state/rimmandrake/control/control.db')+'?mode=ro',uri=True)
rows=c.execute("select family,stage,role,model,state,admitted_at,started_at,ended_at,result from runs").fetchall()
def ts(x):
    try: return float(x)
    except: 
        import datetime
        try: return datetime.datetime.fromisoformat(str(x).replace('Z','+00:00')).timestamp()
        except: return None
print("sample row",rows[-1])
agg=collections.defaultdict(lambda:{'n':0,'dur':[],'wait':[]})
for f,s,r,m,state,a,sa,e,res in rows:
    sa_,e_,a_=ts(sa),ts(e),ts(a)
    if not sa_ or sa_<since: continue
    k=(f,s,r)
    agg[k]['n']+=1
    if e_ and e_>=sa_: agg[k]['dur'].append(e_-sa_)
    if a_ and sa_>=a_: agg[k]['wait'].append(sa_-a_)
print("PIPELINE RUNS, 7 days, control.db runs: family/stage/role n total_h median_min p90_min | wait median_s")
out=[]
for k,v in agg.items():
    if v['dur']:
        t=sum(v['dur']); med,p90=q(v['dur']); w=q(v['wait'])[0] if v['wait'] else None
        out.append((t,k,v['n'],med,p90,w))
for t,k,n,med,p90,w in sorted(out,reverse=True)[:15]:
    print(k,n,round(t/3600,1),'h',round(med/60,1),round(p90/60,1),'| wait',None if w is None else round(w))
# tick steps
n=0;tot=collections.Counter()
for l in open('/mnt/d/ClaudeWork/rimmandrake/dispatcher/tick_steps.jsonl'):
    try:d=json.loads(l)
    except: continue
    import datetime
    at=datetime.datetime.fromisoformat(d['at'].replace('Z','+00:00')).timestamp()
    if at<since: continue
    n+=1
    for k,v in d.items():
        if isinstance(v,(int,float)) and not isinstance(v,bool): tot[k]+=v
print("PIPELINE TICK: n",n,{k:round(v/n,2) for k,v in tot.items()},"total_h",round(tot['total']/3600,2), "left mean (s)", round(tot['left']/n,1))
# detached
D='/mnt/d/ClaudeWork/rimmandrake/dispatcher/detached/'
durs=[];waits=[]
for f in glob.glob(D+'*.finish.log'):
    base=os.path.basename(f)[:-len('.finish.log')]
    try: t0=int(base.rsplit('-',1)[1])
    except: continue
    if t0<since: continue
    durs.append(os.path.getmtime(f)-t0)
print("DETACHED HELPER RUNS 7d: n",len(durs),"total_h",round(sum(durs)/3600,1),"median_min %.1f p90_min %.1f"%tuple(x/60 for x in q(durs)))
