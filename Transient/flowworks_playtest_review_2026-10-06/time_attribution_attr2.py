import json,glob,os,re,statistics,datetime,collections,sys
P=os.path.expanduser('~/.claude/projects/')
dirs=['-home-mandrake-rm-bench','-home-mandrake-rm-foundry','-mnt-d-Luke-dev-RimMandrake']
CUT=datetime.datetime(2026,9,28).timestamp()
KW=re.compile(r'flowworks|northstar|validation_v2|review_map|extensions\.py',re.I)
BR=re.compile(r'validation_v2|extensions\.py|review_map|rimbridge_client|run_[a-z_]+\.py|prove_[a-z_]+\.py')
SS=re.compile(r'screenshot',re.I)
IMG=re.compile(r'\.(png|jpe?g|bmp|webp)$',re.I)
def ts(s): return datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
def cat(name,inp):
    s=json.dumps(inp)
    if name=='Read' and IMG.search(inp.get('file_path','')): return 'image_read'
    if SS.search(s): return 'screenshot'
    if name=='Bash':
        if BR.search(inp.get('command','')): return 'bridge_script'
        c=inp.get('command','')
        if 'python.exe' in c or 'winbuild' in c: return 'bash_pyexe_other'
        if re.search(r'sleep|until|wait',c): return 'bash_wait'
        if re.search(r'\bgit\b|publish',c): return 'bash_git'
        if re.search(r'rimflow|game |bridge|modcheck|modlist|deploy',c): return 'bash_tooling'
        return 'bash_other'
    if name=='Agent': return 'agent'
    return 'other_tool'
IDLE=600
res=[]
for d in dirs:
  for f in glob.glob(P+d+'/*.jsonl'):
    if os.path.getmtime(f)<CUT: continue
    txt=open(f,errors='ignore').read()
    if not KW.search(txt): continue
    ev=[]
    for l in txt.splitlines():
        try:j=json.loads(l)
        except:continue
        if j.get('type') in('assistant','user') and not j.get('isSidechain') and 'timestamp' in j:
            ev.append(j)
    ev=[e for e in ev if ts(e['timestamp'])>=CUT]
    if len(ev)<5: continue
    ev.sort(key=lambda e:e['timestamp'])
    tot=collections.Counter(); idle=collections.Counter(); cnt=collections.Counter()
    pend={} # id->(cat)
    interp=[]; cur_interp=None; last_img_cat=None
    prev=None; prev_kind=None; lastcats=set()
    for e in ev:
        t=ts(e['timestamp']); c=e['message']['content']
        if prev is not None:
            dt=t-prev
            if pend: key=sorted(set(pend.values()))
            elif prev_kind=='user': key=['model_after_'+last_img_cat] if last_img_cat else ['model']
            else: key=['model_stream']
            if dt>IDLE:
                for k in key: idle[k]+=dt/len(key)
                cnt['idle_gaps']+=1
                if cur_interp is not None and prev_kind=='user': cur_interp=None
            else:
                for k in key: tot[k]+=dt/len(key)
                if not pend and prev_kind=='user' and last_img_cat: cur_interp=(cur_interp or 0)+dt
        if isinstance(c,list):
            if e['type']=='assistant':
                if prev_kind=='user' and cur_interp is not None and last_img_cat:
                    interp.append(cur_interp)
                cur_interp=None
                for b in c:
                    if b.get('type')=='tool_use':
                        k=cat(b['name'],b['input']); pend[b['id']]=k; cnt[k]+=1
                prev_kind='assistant'
            else:
                got=[]
                for b in c:
                    if b.get('type')=='tool_result' and b['tool_use_id'] in pend:
                        got.append(pend.pop(b['tool_use_id']))
                if got:
                    last_img_cat=next((g for g in got if g in('image_read','screenshot')),None)
                else: last_img_cat=None
                prev_kind='user'
        else:
            prev_kind='user'; last_img_cat=None
        prev=t
    res.append((os.path.basename(f)[:8],d[-6:],ev[0]['timestamp'][:16],tot,idle,cnt,interp,ev[-1]['timestamp'][:16]))
res.sort(key=lambda r:r[2])
def m(x): return f"{x/60:.1f}"
A=collections.Counter();I=collections.Counter();C=collections.Counter();ALLI=[]
out=["# time attribution\n","sessions: %d\n"%len(res)]
for sid,dd,st,tot,idle,cnt,interp,en in res:
    act=sum(tot.values())
    out.append(f"- {sid} {dd} {st}..{en} active {m(act)}m idle {m(sum(idle.values()))}m | "+", ".join(f"{k} {m(v)}" for k,v in tot.most_common(6))+f" | n: ss={cnt['screenshot']} img={cnt['image_read']} br={cnt['bridge_script']} interp_med={statistics.median(interp) if interp else 0:.0f}s")
    A.update(tot);I.update(idle);C.update(cnt);ALLI+=interp
SUB=[r for r in res if r[5]['bridge_script']>=5 or r[5]['screenshot']>=5]
act=sum(A.values())
out.append(f"\nOVERALL active {m(act)} min ({act/3600:.1f} h); idle>10min excluded {m(sum(I.values()))} min in {C['idle_gaps']} gaps")
for k,v in A.most_common(): out.append(f"  {k}: {m(v)} min = {100*v/act:.1f}%")
out.append("idle by what it followed: "+", ".join(f"{k} {m(v)}" for k,v in I.most_common()))
out.append("counts: "+str(dict(C)))
if ALLI: out.append(f"image/screenshot interpretation model time: n={len(ALLI)} median {statistics.median(ALLI):.1f}s mean {statistics.mean(ALLI):.1f}s total {m(sum(ALLI))}m")
open(sys.argv[1],'w').write("\n".join(out)+"\n")
print("\n".join(out))

B=collections.Counter();BI=collections.Counter();BC=collections.Counter();SI=[]
for r in SUB: B.update(r[3]);BI.update(r[4]);BC.update(r[5]);SI+=r[6]
a=sum(B.values())
o=["\nLIVE-TESTING SUBSET (>=5 bridge-script or >=5 screenshot calls): %d sessions, active %.1f h, idle excluded %.1f h"%(len(SUB),a/3600,sum(BI.values())/3600)]
for k,v in B.most_common(): o.append(f"  {k}: {m(v)} min = {100*v/a:.1f}%")
mod=sum(v for k,v in B.items() if k.startswith('model')); o.append(f"  MODEL TOTAL (generation incl. thinking): {100*mod/a:.1f}%")
o.append("counts: "+str(dict(BC)))
if SI: o.append(f"interp n={len(SI)} median {statistics.median(SI):.1f}s")
open(sys.argv[1],'a').write("\n".join(o)+"\n"); print("\n".join(o))
