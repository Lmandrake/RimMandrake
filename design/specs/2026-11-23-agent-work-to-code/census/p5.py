import re,pickle,kinds
from collections import Counter,defaultdict
S=pickle.load(open('scan3.pkl','rb'));seen=set()
u=Counter();un=Counter();cls=Counter();cn=Counter();test=Counter();tn=Counter();rg=Counter();rgs=[]
ph=Counter()
for x in S:
    ro=kinds.role(x);T=[]
    for i,t in enumerate(x['turns']):
        key=(t[4],round(t[0],3))
        if key in seen: continue
        seen.add(key);T.append((i,t))
    for j,(i,t) in enumerate(T):
        if i==0 or not t[2]: continue
        cm=' ;; '.join(c or '' for _,c,*_ in t[2]);hd=' '.join(h or '' for *_,h in t[2])
        if ro=='mod: in-game driver':
            m=re.search(r'game_instance|modset_builder|deploy_custom|modlist_swap|bridgetools/build|winbuild|game_lock|bridge (take|release)|HOST_GUARD|modset_swaps|ModsConfig|SUMMARY\.md|rows\.jsonl|make_rows|strange\.jsonl|overrides\.json|chain_rows|visit_rows|scene_rows_add|waitfor|/tasks/|\bsleep \d\d|lease\.renew|collect_shots|runner\.sh',cm)
            if m: u['driver mechanical union']+=t[0];un['driver mechanical union']+=1
        if './publish' in cm and 'PUBLISHED' not in hd and re.search(r'REFUSED|usage: publish|failed to push|Blocked by project|pathspec',hd):
            c=t[0]
            for q in range(j+1,min(j+8,len(T))):
                tt=T[q][1];c+=tt[0]
                if 'PUBLISHED' in ' '.join(h or '' for *_,h in tt[2]): break
            if re.search(r'nothing to publish|usage: publish|pathspec|Blocked by project|without a pathspec',hd): k='form (command shape)'
            elif re.search(r'non-fast-forward|failed to push|kept moving|timed out',hd): k='race on origin'
            elif re.search(r'conflict',hd): k='replay conflict'
            elif re.search(r'check\(s\) red|pre-push hook|RED',hd): k='a check is red'
            else: k='other refusal'
            cls[k]+=c;cn[k]+=1
        if re.search(r'python3? [^\n;|&]*(selftest_|run_selftests)',cm):
            cs=re.findall(r'(selftest_\w+)',cm)
            test['exec']+=t[0];tn['exec']+=1
            if len(set(cs))==1 and not re.search(r'write\(|<<|publish',cm): test['one test, nothing else written']+=t[0];tn['one test, nothing else written']+=1
        if re.search(r'(grep|python3? -|cat)[^\n]*ledger/events|ledger/events[^\n]*(grep|json)',cm):
            if re.search(r'RIMMANDRAKE_[A-Z_]{8,}|RIMMASTER_',cm): rg['names one item']+=t[0]
            else: rg['search by word or event']+=t[0]
for d,n in((u,un),(cls,cn),(test,tn),(rg,Counter())):
    for k,v in d.most_common(): print('%6.1fM n=%d %s'%(v/1e6,n[k],k))
