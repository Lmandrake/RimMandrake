import json,glob,subprocess,os,datetime as D,statistics as S
def ts(s): return D.datetime.fromisoformat(s.replace('Z','+00:00'))
out=[]; gaps=[]
for f in sorted(glob.glob('Transient/biome_ffar/*_sheet_2026-10-*.decisions.json')):
    if '.gate.tmp' in f: continue
    d=json.load(open(f)).get('decisions') or {}
    t=sorted(ts(r['decidedAt']) for r in d.values() if isinstance(r,dict) and r.get('decidedAt'))
    if not t: continue
    html=f.replace('.decisions.json','.html')
    c=subprocess.run(['git','log','--diff-filter=A','--format=%aI','--',html],capture_output=True,text=True).stdout.split()
    built=ts(c[-1]) if c else None
    g=[(b-a).total_seconds() for a,b in zip(t,t[1:]) if (b-a).total_seconds()<600]
    gaps+=g
    # sessions: split at >30 min
    sess=1+sum(1 for a,b in zip(t,t[1:]) if (b-a).total_seconds()>1800)
    active=sum(g)
    out.append((os.path.basename(f)[:45],len(d),len(t),built.strftime('%m-%d %H:%M') if built else '?',
        t[0].astimezone().strftime('%m-%d %H:%M'),t[-1].astimezone().strftime('%m-%d %H:%M'),sess,round(active/60,1),
        round(((t[0]-built).total_seconds()/3600),1) if built else None))
print(f"{'sheet':45s} rows ruled built first_click last_click sittings active_min build->first_click_h")
for o in out: print(*o)
print('per-click gap seconds (gaps<10min): n',len(gaps),'median',S.median(gaps),'p75',sorted(gaps)[int(.75*len(gaps))],'p90',sorted(gaps)[int(.9*len(gaps))])
