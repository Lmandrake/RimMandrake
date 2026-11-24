import json,glob,os,sys,re,pickle,time,datetime
from multiprocessing import Pool
sys.path.insert(0,'/home/mandrake/rm/relentless/clones/RIMMANDRAKE_FIND_AGENT_WORK_THAT_PYTHON_CAN_DO_TOKEN_FREE.det/src/RimMandrake/rimflow')
import role_launch as rl
W={m:{k:float(v)/4.0 for k,v in p.items()} for m,p in rl.MODEL_PRICES.items()}
CUT=1795492604-7*86400   # this run's launch
CUTISO=datetime.datetime.utcfromtimestamp(CUT).strftime('%Y-%m-%dT%H:%M:%S')
def cost(model,u):
    m=W.get(model) or W.get(re.sub(r'\[.*\]','',model or ''))
    if not m: return None
    cc=u.get('cache_creation') or {}
    w5=cc.get('ephemeral_5m_input_tokens',0) or 0; w1=cc.get('ephemeral_1h_input_tokens',0) or 0
    tot=u.get('cache_creation_input_tokens',0) or 0
    if w5+w1!=tot: w5,w1=0,tot
    return ((u.get('input_tokens') or 0)*m['input_tokens']+w5*m['cache_write_5m']+w1*m['cache_write_1h']+(u.get('cache_read_input_tokens') or 0)*m['cache_read_input_tokens']+(u.get('output_tokens') or 0)*m['output_tokens'])
def scan(p):
    msgs={};order=[];first=None;cwd=None;results={};heads={}
    unk=set()
    try: fh=open(p,errors='replace')
    except OSError: return None
    for line in fh:
        if '"assistant"' not in line and first is not None and '"tool_result"' not in line: continue
        try:d=json.loads(line)
        except Exception: continue
        if cwd is None: cwd=d.get('cwd')
        t=d.get('type')
        if t=='user':
            c=(d.get('message') or {}).get('content')
            if first is None:
                if isinstance(c,list): c=' '.join(x.get('text','') for x in c if isinstance(x,dict) and x.get('type')=='text')
                if c: first=c[:3000]
            if isinstance((d.get('message') or {}).get('content'),list):
                for x in d['message']['content']:
                    if isinstance(x,dict) and x.get('type')=='tool_result':
                        cc=x.get('content'); n=len(cc) if isinstance(cc,str) else sum(len(y.get('text','')) for y in (cc or []) if isinstance(y,dict))
                        results[x.get('tool_use_id')]=n; tx=cc if isinstance(cc,str) else ' '.join(y.get('text','') for y in (cc or []) if isinstance(y,dict)); heads[x.get('tool_use_id')]=(tx if len(tx)<900 else tx[:450]+' ... '+tx[-450:])
        elif t=='assistant':
            m=d.get('message') or {}; i=m.get('id')
            if (d.get('timestamp') or '')<CUTISO: continue
            if i not in msgs: msgs[i]=dict(model=m.get('model'),u=m.get('usage') or {},tools=[],text='',ts=d.get('timestamp')); order.append(i)
            r=msgs[i]
            u=m.get('usage') or {}
            if (u.get('output_tokens') or 0)>=(r['u'].get('output_tokens') or 0): r['u']=u
            for x in m.get('content') or []:
                if x.get('type')=='tool_use':
                    inp=x.get('input') or {}
                    r['tools'].append((x.get('name'),inp.get('command') or inp.get('file_path') or inp.get('skill') or inp.get('description') or '',len(json.dumps(inp)),x.get('id')))
                elif x.get('type')=='text': r['text']+=x.get('text','')[:300]
    turns=[]
    for i in order:
        r=msgs[i]
        if r['model'] in (None,'<synthetic>'): continue
        c=cost(r['model'],r['u'])
        if c is None: unk.add(r['model']);continue
        u=r['u'];turns.append((c,r['model'],[(n,cmd[:6000],l,results.get(tid,0),heads.get(tid,'')) for n,cmd,l,tid in r['tools']],r['text'][:300],r['ts'],(u.get('output_tokens') or 0),u.get('cache_creation_input_tokens') or 0,u.get('cache_read_input_tokens') or 0))
    if not turns: return None
    return dict(p=p,cwd=cwd,first=first,turns=turns,unk=list(unk),total=sum(t[0] for t in turns),size=os.path.getsize(p))
if __name__=='__main__':
    fs=[]
    for r,_,ff in os.walk(os.path.expanduser('~/.claude/projects')):
        for f in ff:
            if f.endswith('.jsonl'):
                q=os.path.join(r,f)
                if os.path.getmtime(q)>CUT: fs.append(q)
    with Pool(8) as P: out=[x for x in P.imap_unordered(scan,fs,chunksize=4) if x]
    pickle.dump(out,open('/mnt/d/ClaudeWork/rimmandrake/scratch/a2c/scan3.pkl','wb'))
    print(len(fs),len(out),sum(x['total'] for x in out)/1e6, set(u for x in out for u in x['unk']))
