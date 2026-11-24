import re,pickle,kinds
from collections import Counter,defaultdict
S=pickle.load(open('scan3.pkl','rb'));seen=set()
hc=Counter();hn=Counter();cw=0;cwn=0;pw=0;pwn=0;use=Counter();still=0;stilln=0
cli=Counter();dr=Counter();waitrole=Counter();gl=Counter()
cold=Counter()
for x in S:
    ro=kinds.role(x);prev=False
    for i,t in enumerate(x['turns']):
        key=(t[4],round(t[0],3))
        if key in seen: continue
        seen.add(key)
        if i==0 or not t[2]: prev=False;continue
        cm=' ;; '.join(c or '' for _,c,*_ in t[2]);hd=' '.join(h or '' for *_,h in t[2])
        for w in('logwait.py','await_lifecycle','thing_contact_sheet','animal_contact_sheet','waitfor.py','red-seen','rerun_relation','run_selftests.py','mod_next.py','maturation.py next','detached_helper.py status','detached_helper.py result','detached_helper.py show','incident','code_review_status','scene_runner.py','helper_receipts','test_process','lessons.py'):
            if w in cm: use[w]+=1
        for m in re.finditer(r'(\S+\.py"?(?: [a-z][\w-]*)?|rimflow(?: \w+)?|\./\w+(?: \w+)?)\s+[^;|&\n]*--help',cm):
            nm=re.sub(r'.*/','',m.group(1)).strip('"');hc[nm]+=t[0]/len(t[2]);hn[nm]+=1
        iswait=bool(re.search(r'waitfor\.py (job|line|unit|pid|file)|\bsleep \d\d|until .{0,120}sleep|while .{0,160}sleep|/tasks/',cm)) and not re.search(r'write\(|<<',cm)
        if iswait:
            pw+=t[0];pwn+=1
            if prev: cw+=t[0];cwn+=1;waitrole[ro]+=t[0]
        prev=iswait
print('wait turns',pw/1e6,pwn,'consecutive repeats',cw/1e6,cwn,[(a[:22],round(b/1e6,1)) for a,b in waitrole.most_common(6)])
print(use)
for k,v in hc.most_common(28): print(round(v/1e6,2),hn[k],k)
