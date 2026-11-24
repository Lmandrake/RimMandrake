import pickle,os,re
from collections import defaultdict,Counter
S=pickle.load(open('/mnt/d/ClaudeWork/rimmandrake/scratch/a2c/scan.pkl','rb'))
seen=set();dup=0
for x in S:
    k=[]
    for t in x['turns']:
        key=(t[4],round(t[0],3))
        if key in seen: dup+=t[0];continue
        seen.add(key);k.append(t)
    x['turns']=k;x['total']=sum(t[0] for t in k)
print('dup',dup/1e6)
pickle.dump(S,open('/mnt/d/ClaudeWork/rimmandrake/scratch/a2c/scan2.pkl','wb'))
d=Counter()
for x in S:
    k=x['p'].split('/projects/')[1].split('/')[0]
    if k.endswith('-det'): d[k.split('clones-')[1][:-4]]+=x['total']
for k,v in d.most_common(150): print(round(v/1e6,1),k[:100])
print(len(d),sum(d.values())/1e6)
