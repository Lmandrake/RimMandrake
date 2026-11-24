import pickle
from collections import defaultdict,Counter
from kinds import S,role,kind
RT=Counter();K=Counter();KN=Counter();RK=defaultdict(Counter);RN=Counter();RKN=defaultdict(Counter)
for x in S:
    if not x['turns']: continue
    r=role(x)
    if r.startswith('other: '): r='other (calibration, tmp, misc)'
    RT[r]+=x['total'];RN[r]+=1
    for i,t in enumerate(x['turns']):
        ks=[kind(a,b) for a,b,_,_ in t[2]] or ['text only']
        c=t[0]; cw,cr=t[6],t[7]
        if i==0: K['(start: first context write)']+=c;KN['(start: first context write)']+=1;RK[r]['(start: first context write)']+=c;continue
        if cw>60000 and cw>cr: K['(cache rebuilt)']+=c;KN['(cache rebuilt)']+=1;RK[r]['(cache rebuilt)']+=c;continue
        for kk in ks: K[kk]+=c/len(ks);KN[kk]+=1;RK[r][kk]+=c/len(ks);RKN[r][kk]+=1
T=sum(RT.values());print(T/1e6)
for k,v in RT.most_common(24): print('%7.1fM %5.1f%% n=%d  %s'%(v/1e6,100*v/T,RN[k],k))
for k,v in K.most_common(34): print('%7.1fM %5.1f%% calls=%d avg=%.1fk %s'%(v/1e6,100*v/T,KN[k],v/KN[k]/1e3,k))
for r,_ in RT.most_common(22):
    print(r,RN[r],'; '.join('%s %.1fM/%d'%(k,v/1e6,RKN[r][k]) for k,v in RK[r].most_common(16)))
