import re,pickle,kinds
from collections import Counter,defaultdict
S=pickle.load(open('scan3.pkl','rb'));seen=set()
SEG=re.compile(r'(?:;|&&|\|\||\n)')
def pure_ll(c):
    c=re.sub(r'--(text|why|evidence|reason|title|spec|criteria|verify|owner-said|m)\s+("([^"\\]|\\.)*"|\'[^\']*\'|"\$\(cat <<.*)','',c,flags=re.S)
    c=re.sub(r'-m\s+("([^"\\]|\\.)*"|\'[^\']*\')','',c,flags=re.S)
    hit=False
    for s in SEG.split(c):
        s=re.sub(r'\|.*','',s).strip()
        if not s: continue
        if re.match(r'(timeout \d+ )?(python3 \S*cli\.py|rimflow|\./publish|\./sync|git (add|commit|pull|push|fetch|merge-base|status|log -1|rev-parse)|\./mirror)',s):
            hit=True;continue
        if re.match(r'(cd |echo|date|set -o|set -e|rc=|[A-Z_a-z]+=|true$|tail|head|grep|cat /tmp|\#|done$|fi$|then|printf|export |sleep \d$|wc )',s): continue
        return False
    return hit
def verbs(c):
    v=set()
    for m in re.finditer(r'(?:cli\.py"?|rimflow) (\w+)',c): v.add(m.group(1))
    if './publish' in c: v.add('publish')
    if re.search(r'\./sync|git (pull|fetch)',c): v.add('sync')
    if re.search(r'git (add|commit)',c): v.add('commit')
    return v
RD={'show','queue','next','status','incidents','namecheck'}
tot=Counter();n=Counter();by=defaultdict(Counter);vb=Counter();vn=Counter()
runs=set();col=Counter();cn=0
perrun=Counter()
for x in S:
    ro=kinds.role(x);prev=False
    for i,t in enumerate(x['turns']):
        key=(t[4],round(t[0],3))
        if key in seen: continue
        seen.add(key)
        if i==0 or not t[2]: prev=False;continue
        cs=[c for nm,c,*_ in t[2] if nm=='Bash']
        ok=len(cs)==len(t[2]) and all(pure_ll(c or '') for c in cs)
        v=set().union(*[verbs(c or '') for c in cs]) if cs else set()
        if ok and v and not v<=RD|{'sync'}:
            tot['pure landing/ledger-writing turns']+=t[0];n['pure landing/ledger-writing turns']+=1;by['p'][ro]+=t[0];perrun[x['p']]+=1
            k='+'.join(sorted(v-{'commit','sync'})) or 'sync/commit'
            vb[k]+=t[0];vn[k]+=1
            if prev: col[ro]+=t[0];cn+=1
            prev=True
        else: prev=False
print(tot,n);print([(a[:25],round(b/1e6,1)) for a,b in by['p'].most_common(9)])
for k,v in vb.most_common(22): print('%5.1fM %d %s'%(v/1e6,vn[k],k))
print('consecutive',cn,sum(col.values())/1e6,'runs',len(perrun),'median',sorted(perrun.values())[len(perrun)//2])
