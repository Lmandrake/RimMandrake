import json,glob,os,time,sys
OUT=os.environ.get("SCAN_DIR","/home/mandrake/.seat-tmp/scan")+"/"
from datetime import datetime
root=os.path.expanduser("~/.claude/projects/-home-mandrake-rm-bench/")
now=time.time()
out=open(OUT+"calls.jsonl","w")
turns=open(OUT+"turns.jsonl","w")
def P(ts): return datetime.fromisoformat(ts.replace('Z','+00:00')).timestamp()
nsess=0
for f in sorted(glob.glob(root+"*.jsonl")):
    if now-os.path.getmtime(f)>7.2*86400: continue
    sid=os.path.basename(f)[:8]
    name=None; pend={}; lastts=None
    rows=[]
    for l in open(f):
        try:d=json.loads(l)
        except: continue
        if d.get('type')=='agent-name' and not name: name=d['agentName']
        rows.append(d)
    if name!='CONDUCTOR': continue
    nsess+=1
    prev_ts=None
    for d in rows:
        ts=d.get('timestamp')
        t=d.get('type')
        gap=None
        if ts and t in('assistant','user'):
            gap=(P(ts)-prev_ts) if prev_ts else None
            prev_ts=P(ts)
        if t=='assistant' and ts:
            msg=d.get('message',{}); c=msg.get('content')
            if isinstance(c,list):
                for b in c:
                    if b.get('type')=='tool_use':
                        pend[b['id']]=dict(sid=sid,ts=ts,name=b['name'],inp=b.get('input',{}),gap=gap)
        elif t=='user' and ts:
            msg=d.get('message',{}); c=msg.get('content')
            if isinstance(c,list):
                for b in c:
                    if b.get('type')=='tool_result' and b.get('tool_use_id') in pend:
                        p=pend.pop(b['tool_use_id'])
                        r=b.get('content')
                        if isinstance(r,list): r=' '.join(x.get('text','') for x in r if isinstance(x,dict))
                        r=r or ''
                        p['rts']=ts; p['dur']=P(ts)-P(p['ts']); p['rlen']=len(r); p['rhead']=r[:300]; p['rfull']=r[:3000]; p['rtail']=r[-400:]; p['err']=bool(b.get('is_error'))
                        p['inp']={k:(v if not isinstance(v,str) else v[:4000]) for k,v in p['inp'].items()}
                        out.write(json.dumps(p)+"\n")
            # human turn?
            if d.get('promptId') or d.get('turnOrigin'):
                if isinstance(c,str) or (isinstance(c,list) and any(b.get('type')=='text' for b in c)):
                    txt=c if isinstance(c,str) else ' '.join(b.get('text','') for b in c if b.get('type')=='text')
                    turns.write(json.dumps(dict(sid=sid,ts=ts,origin=d.get('turnOrigin') or d.get('origin'),len=len(txt),head=txt[:300]))+"\n")
for p in pend.values(): pass
print(nsess)
