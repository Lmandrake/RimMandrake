import re
import kinds
from kinds import S
from collections import Counter
c=Counter();n=Counter();ex=[]
heads=Counter()
for x in S:
    if kinds.role(x)!='Conductor window': continue
    T=x['turns']
    for i,t in enumerate(T):
        cmds=' ;; '.join(q or '' for _,q,_,_ in t[2])
        if i and re.search(r'detached/|\.out\.json',cmds) and re.search('python3 -c|jq|cat',cmds): 
            c['fetch run result']+=t[0];n['fetch run result']+=1
            # next turn
            if i+1<len(T):
                nx=T[i+1]
                if not nx[2]:
                    c['then a report turn']+=nx[0];n['then a report turn']+=1
                    if re.search(r'[Nn]othing (in it |here )?(needs|is owed|for) you|needs you|one more plain',nx[3]): pass
        elif i and re.search('seat_restart|handoff|queue CONDUCTOR|owed',cmds): c['owed/wake reading']+=t[0];n['owed/wake reading']+=1
        elif i and re.search(r'\./pipe (show|why|log)|game_lock.*query|detached_helper\.py status|account_usage|switching_plan|MATURATION_NOW',cmds): c['state reads']+=t[0];n['state reads']+=1
        elif i and re.search(r'detached_helper\.py launch',cmds): c['launch helper']+=t[0];n['launch helper']+=1
        elif i and re.search(r'cat > \S*brief|_brief\.md|brief\.md',cmds): c['write brief']+=t[0];n['write brief']+=1
        elif i and 'Start-Process' in cmds: c['open page']+=t[0];n['open page']+=1
        elif i and 'conductor/log' in cmds: c['log']+=t[0];n['log']+=1
        elif i and './publish' in cmds: c['publish']+=t[0];n['publish']+=1
        elif i and re.search(r'cli\.py (note|file|close|raise|drop|wait)',cmds): c['ledger']+=t[0];n['ledger']+=1
        elif not t[2]: c['text to owner']+=t[0];n['text to owner']+=1; 
        elif i==0: c['start']+=t[0];n['start']+=1
        else: c['other']+=t[0];n['other']+=1
for k,v in c.most_common(): print('%6.1fM n=%d avg %.0fk %s'%(v/1e6,n[k],v/n[k]/1e3,k))
