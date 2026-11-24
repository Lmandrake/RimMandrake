import re,sys
from kinds import S,role,kind
from collections import Counter
tot=Counter()
rows=[]
for x in S:
    if role(x)!='mod: in-game driver' or x['total']<1.0e6: continue
    prep=0;done=False;n=0;C=Counter()
    for i,t in enumerate(x['turns']):
        cmds=' ;; '.join(c or '' for _,c,_,_ in t[2])
        names=[nm for nm,_,_,_ in t[2]]
        if not done:
            if re.search(r'waitfor\.py run|runner\.sh (main|\w)|nohup|batch\.py|setsid|scene_runner\.py|validation\.py"? --|northstar_full|modcheck.*run ',cmds) and i>3: done=True;C['prep_end_turn']=i
            else:
                prep+=t[0] if i else 0
                C['prep']+=t[0] if i else 0
                continue
        if re.search(r'waitfor\.py|sleep \d\d',cmds) or 'Monitor' in names: C['wait']+=t[0];C['nwait']+=1
        elif re.search(r'SUMMARY\.md|rows\.jsonl|make_rows|strange\.jsonl|collect_shots|chain_rows|peek\.py|overrides\.json|red-seen|shots\.py',cmds): C['records']+=t[0]
        elif re.search(r'\./publish|cli\.py',cmds): C['land_ledger']+=t[0]
        elif any(nm in('Edit','Write') for nm in names) or re.search(r"write\(s|replace\(",cmds): C['repair edits']+=t[0]
        elif re.search(r'selftest_',cmds): C['tests']+=t[0]
        elif re.search(r'build_match|maturation\.py|rerun_relation|stage_record',cmds): C['stage tools']+=t[0]
        else: C['diagnose/other']+=t[0]
    rows.append((x['total'],x['p'].split('clones-RIMMANDRAKE-')[-1][:50],{k:round(v/1e3) if k not in('prep_end_turn','nwait') else v for k,v in C.items()}))
    tot.update(C); tot['total']+=x['total'];tot['start']+=x['turns'][0][0]
for r in sorted(rows,reverse=True)[:30]: print(round(r[0]/1e6,1),r[1],r[2])
print({k:round(v/1e6,1) for k,v in tot.items()},len(rows),tot['prep_end_turn'],tot['nwait'])
