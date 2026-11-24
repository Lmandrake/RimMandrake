import re,pickle,kinds
from collections import Counter
S=pickle.load(open('scan3.pkl','rb'));seen=set()
A=Counter();N=Counter();R=Counter()
def add(k,c): A[k]+=c;N[k]+=1
FRM=re.compile(r"(grep|cat|tail|head|jq|awk)\b[^|;&\n]*ledger/events|glob\([^)]*ledger/events")
ex=[]
for x in S:
    ro=kinds.role(x)
    for i,t in enumerate(x['turns']):
        key=(t[4],round(t[0],3))
        if key in seen: continue
        seen.add(key)
        if i==0 or not t[2]: continue
        cm=' ;; '.join(c or '' for _,c,*_ in t[2])
        if FRM.search(cm) and './publish' not in cm:
            add('raw ledger read (strict)',t[0]);R[ro]+=t[0]
            if re.search(r"RIMMANDRAKE_[A-Z_]{8,}|OPS_[A-Z_]{6}",cm): add('  names one item',t[0])
            else: ex.append(cm[:160])
        if re.search(r'(cli\.py"?|rimflow) show ',cm) and './publish' not in cm: 
            add('cli show',t[0])
            if re.search(r'show [^|\n]*\|\s*(tail|head|sed|grep|cut)',cm): add('  show piped through a cut',t[0])
        # PROGRESS pure notes
        if re.search(r'(cli\.py"?|rimflow) note ',cm) and re.search(r'PROGRESS|STATE',cm) and './publish' not in cm: add('progress note turns',t[0])
        if re.search(r'lease\.renew',cm): add('lease.renew turns (often with other work)',t[0])
        if re.search(r'--help\b',cm): 
            add('--help turns',t[0])
            if re.search(r'(cli\.py|rimflow) (file|close|note|verify|drop|supersede|wait|spawn)|maturation\.py|red-seen|detached_helper|lessons|publish',cm): add('  --help of ledger, stage, launch, lesson, publish verbs',t[0])
for k,v in A.items(): print('%6.1fM n=%d avg %.0fk %s'%(v/1e6,N[k],v/N[k]/1e3,k))
print(R.most_common(5)); print(ex[:8])
