import re
import pickle
import kinds
from collections import Counter,defaultdict
S=pickle.load(open('scan3.pkl','rb'));seen=set()
LL={'land (publish, commit, sync)','ledger write'}
def writes(c): return bool(re.search(r"write\(|replace\(|cat >|<<|Edit",c or ''))
out=Counter();n=Counter();rr=defaultdict(Counter)
pub_fix=Counter()
for x in S:
    ro=kinds.role(x); T=[]
    for i,t in enumerate(x['turns']):
        key=(t[4],round(t[0],3))
        if key in seen: continue
        seen.add(key);T.append((i,t))
    runlen=0
    for j,(i,t) in enumerate(T):
        if not t[2] or i==0: runlen=0;continue
        ks=[kinds.kind(a,b) for a,b,_,_,_ in t[2]]
        cm=' ;; '.join(b or '' for _,b,_,_,_ in t[2]); hd=' ;; '.join(h or '' for *_,h in t[2])
        pure=all(k in LL or k=='stage record tools' and 'lease.renew' in cm for k in ks)
        if pure:
            out['pure land/ledger turns']+=t[0];n['pure land/ledger turns']+=1;rr['pure land/ledger turns'][ro]+=t[0]
            runlen+=1
            if runlen>1: out['  2nd+ in a consecutive row (collapsible)']+=t[0];n['  2nd+ in a consecutive row (collapsible)']+=1
        else: runlen=0
        if all(k=='wait' for k in ks) or ('/tasks/' in cm and not writes(cm)):
            out['pure wait/poll turns']+=t[0];n['pure wait/poll turns']+=1;rr['pure wait/poll turns'][ro]+=t[0]
        if './publish' in cm and 'PUBLISHED' not in hd and re.search(r'REFUSED|usage: publish|failed to push|Blocked by project|pathspec',hd):
            c=t[0];m=1
            for q in range(j+1,min(j+8,len(T))):
                tt=T[q][1];c+=tt[0];m+=1
                if 'PUBLISHED' in ' '.join(h or '' for *_,h in tt[2]): break
            out['publish refused: refusal to next PUBLISHED (max 7 turns)']+=c;n['publish refused: refusal to next PUBLISHED (max 7 turns)']+=1
            rr['publish refused: refusal to next PUBLISHED (max 7 turns)'][ro]+=c
        if re.search(r'python3? [^\n;|&]*selftest_',cm):
            out['selftest exec turns']+=t[0];n['selftest exec turns']+=1
            if re.search(r'\bplant|git apply|\.patch|mutant|git show [^ ]*:|worktree|parent',cm): out['  red/green or planted-fault exec turns']+=t[0];n['  red/green or planted-fault exec turns']+=1;rr['  red/green or planted-fault exec turns'][ro]+=t[0]
        if re.search(r'modledger\.py append',cm): out['modledger append turns']+=t[0];n['modledger append turns']+=1
        if len(t[2])==1 and 'lease.renew' in cm and len(cm)<420: out['lease renew, nothing else']+=t[0];n['lease renew, nothing else']+=1
        if re.search(r'(grep|python3? -)[^\n]*ledger/events|ledger/events[^\n]*(grep|json)',cm): out['item history by raw ledger grep']+=t[0];n['item history by raw ledger grep']+=1;rr['item history by raw ledger grep'][ro]+=t[0]
        if re.search(r'test_table\.json|rows\.jsonl|stage_record\.json|scenes\.json',cm) and re.search(r'python3? (-|<<)|jq ',cm) and not re.search(r'write\(|json\.dump\(',cm): out['ad hoc reads of table, rows, stage record']+=t[0];n['ad hoc reads of table, rows, stage record']+=1;rr['ad hoc reads of table, rows, stage record'][ro]+=t[0]
        if re.search(r'--help\b',cm) : out['--help turns']+=t[0];n['--help turns']+=1;rr['--help turns'][ro]+=t[0]
        if re.search(r'usage: |unrecognized arguments|are required: |invalid choice',hd) and '--help' not in cm: out['wrong-flag turns']+=t[0];n['wrong-flag turns']+=1
        if not ro.startswith('list item') and re.search(r'(grep|sed -n|cat|head)[^|;\n]*src/RimMandrake/(rimflow|Utils)/[a-z_/]*\.py',cm) and not writes(cm): out['reads tool source, in runs not about tools']+=t[0];n['reads tool source, in runs not about tools']+=1;rr['reads tool source, in runs not about tools'][ro]+=t[0]
for k,v in out.most_common(): print('%6.1fM n=%d avg %.0fk %s | %s'%(v/1e6,n[k],v/n[k]/1e3,k,'; '.join('%s %.1f'%(a[:24],b/1e6) for a,b in rr[k].most_common(5))))
