import json,glob,os,time,sys,re,pickle
sys.path.insert(0,'src/RimMandrake/rimflow')
import role_launch as rl
cut=time.time()-7*86400
rows=[]
for p in glob.glob('/mnt/d/ClaudeWork/rimmandrake/dispatcher/detached/*.json'):
    if p.endswith('.out.json'): continue
    if os.path.getmtime(p)<cut-86400: continue
    try:r=json.load(open(p))
    except Exception as e: print('bad',p,e);continue
    if r.get('at',0)<cut: continue
    try: t,b=rl.tokens_v2(r)
    except Exception as e: t,b=None,'err %s'%e
    rows.append(dict(p=p,unit=r.get('unit'),item=r.get('item') or '',model=r.get('model'),t=t,b=b,env=r.get('env') or {},status=r.get('status'),result=r.get('result'),session=r.get('session'),at=r['at'],brief=r.get('brief_file'),clone=r.get('clone'),ended=r.get('ended')))
pickle.dump(rows,open('/mnt/d/ClaudeWork/rimmandrake/scratch/a2c/rows.pkl','wb'))
print(len(rows),sum(x['t'] or 0 for x in rows)/1e6, sum(x['t'] is None for x in rows))
from collections import Counter,defaultdict
print(Counter(x['env'].get('RM_CONTROL_STAGE') for x in rows).most_common())
c=defaultdict(lambda:[0,0])
for x in rows:
    k=re.sub(r'RIMMANDRAKE_|RIMMASTER_','',x['item']).split('_')[0]
    c[k][0]+=1;c[k][1]+=(x['t'] or 0)
for k,v in sorted(c.items(),key=lambda z:-z[1][1])[:60]: print(k,v[0],round(v[1]/1e6,2))
