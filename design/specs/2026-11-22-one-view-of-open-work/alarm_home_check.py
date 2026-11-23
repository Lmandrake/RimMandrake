#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_KEEP_ALARM_ITEMS_OPEN_FOUR_OF_SIX_POINT_AT_CLOSED: every OPEN alarm in alarms.json names
an item, and that item is open in the ledger. Exit 1 lists each alarm without an open home. Run from the repo root:
    python3 design/specs/2026-11-22-one-view-of-open-work/alarm_home_check.py /mnt/d/ClaudeWork/rimmandrake/ops_watch/alarms.json
"""
import json,glob,sys
ST={'file':'open','claim':'open','start':'open','wait':'open','unwait':'open','block':'open','unblock':'open','release':'open','reclaim':'open','implemented':'open','close':'closed','drop':'closed','supersede':'closed','verify':'closed'}
s={}
for f in glob.glob('infrastructure/state/ledger/events/*.jsonl'):
    for l in open(f):
        try: e=json.loads(l)
        except ValueError: continue
        if 'id' in e and e.get('event') in ST: s.setdefault(e['id'],[]).append((e.get('ts',''),ST[e['event']]))
a=json.load(open(sys.argv[1]))
bad=[]
for k,v in a.items():
    if v.get('state')!='OPEN': continue
    i=v.get('item'); st=sorted(s[i])[-1][1] if i in s else None
    if st!='open': bad.append((k,i,st))
for b in bad: print('NO OPEN HOME',b)
print('open alarms without an open item:',len(bad)); sys.exit(1 if bad else 0)
