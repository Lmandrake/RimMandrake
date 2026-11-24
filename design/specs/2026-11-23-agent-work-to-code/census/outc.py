import json,glob,os,re,sys
sys.path.insert(0,'/home/mandrake/rm/relentless/clones/RIMMANDRAKE_FIND_AGENT_WORK_THAT_PYTHON_CAN_DO_TOKEN_FREE.det/src/RimMandrake/rimflow')
import role_launch as rl
cut=1795492604-7*86400
for role in('operations','conductor','designer'):
    n=t=0;C={}
    for f in glob.glob('/mnt/d/ClaudeWork/rimmandrake/dispatcher/roles/rm-role-%s-*.json'%role):
        if os.path.getmtime(f)<cut: continue
        try:d=json.load(open(f))
        except Exception: continue
        w=rl.run_tokens(d,'opus') or 0;r=d.get('result') or ''
        n+=1;t+=w
        pub=bool(re.search(r'\b[0-9a-f]{10,12}\b',r))
        if re.search(r'fixed in|Fixed in|I fixed|published (a|the|my) fix|fix:|\*\*Fix',r) and pub: k='fixed code'
        elif re.search(r're-?ack|acked|acknowledged|took .*incident|new plan|daily deep read',r,re.I): k='incident re-read and re-acked'
        elif re.search(r'no (fix|item|action|ticket)|needs? no|nothing (to|is|for)|filed no|expected|already',r,re.I): k='read, no act'
        else: k='other'
        C.setdefault(k,[0,0,[]]);C[k][0]+=1;C[k][1]+=w;C[k][2].append(os.path.basename(f))
    print(role,n,t/1e6)
    for k,v in C.items(): print('  ',k,v[0],round(v[1]/1e6,2),v[2][:2])
