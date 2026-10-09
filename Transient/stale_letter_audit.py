#!/usr/bin/env python3
"""Replay tonight's art ruling/rejected events against the snapshot current at click time vs the one used.
Usage: stale_letter_audit.py > out. Read-only."""
import json,subprocess,datetime as dt,re,sys,collections
def g(*a): return subprocess.run(['git',*a],capture_output=True,text=True).stdout
def ts(x):
    if not x: return None
    d=dt.datetime.fromisoformat(x.replace('Z','+00:00').replace('-0700','-07:00'))
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)
ev=[json.loads(l) for l in open('infrastructure/state/art/events/BENCH.jsonl')]
T0=ts('2026-10-08T20:00:00-07:00')
cache={}
def versions(snap):
    if snap in cache: return cache[snap]
    vs=[]
    for l in g('log','--format=%h',"--",snap).split():
        try: d=json.loads(g('show',f'{l}:{snap}'))
        except Exception: continue
        vs.append((ts(d.get('built')),l,d))
    try: d=json.load(open(snap)); vs.append((ts(d.get('built')),'WORKTREE',d))
    except Exception: pass
    vs.sort(key=lambda x:x[0] or T0)
    cache[snap]=vs; return vs
def at_click(snap,click):
    cur=None
    for b,h,d in versions(snap):
        if b and b<=click: cur=(b,h,d)
    return cur
def pics(d,row,col):
    c=(((d.get('rows') or {}).get(row) or {}).get('columns') or {}).get(col)
    if c is None: return None
    return set(c.values()) if isinstance(c,dict) else set([c])
rows=[]
for e in ev:
    if e['type'] not in('ruling','rejected') or e['ts']<'2026-10-08T20': continue
    via=e.get('via') or ''
    if not via.endswith('.decisions.json'): continue
    sheet=re.sub(r'\.decisions\.json$','',via.split('/')[-1])
    snap=f'infrastructure/state/art/sheets/{sheet}.snapshot.json'
    t=e.get('target') or {}
    row=e.get('row') or t.get('row'); col=e.get('column') or t.get('column')
    shas=set(t.get('shas') or ([e['sha']] if e.get('sha') else []) )
    if t.get('sha'): shas.add(t['sha'])
    click=ts(e.get('at'))
    if not row or not col or click is None: rows.append((e,'NOROWCOL',None)); continue
    old=at_click(snap,click)
    if not old: rows.append((e,'NOSNAP',None)); continue
    op=pics(old[2],row,col)
    # picture set the event recorded vs old snapshot column
    if op is None: verdict='LETTER_ABSENT_IN_OLD'
    elif shas<=op: verdict='ok'
    else: verdict='DIFFERS'
    rows.append((e,verdict,(old[1],old[0].isoformat() if old[0] else None,sorted(op) if op else None)))
c=collections.Counter((r[0]['type'],r[1]) for r in rows); print(c,file=sys.stderr)
for e,v,o in rows:
    if v!='ok':
        print(json.dumps({'id':e['id'],'type':e['type'],'verdict':e.get('verdict'),'via':e['via'].split('/')[-1],'row':e.get('row') or (e.get('target') or {}).get('row'),'col':e.get('column') or (e.get('target') or {}).get('column'),'at':e.get('at'),'recorded':sorted((e.get('target') or {}).get('shas') or [e.get('sha')] ),'check':v,'oldsnap':o}))
