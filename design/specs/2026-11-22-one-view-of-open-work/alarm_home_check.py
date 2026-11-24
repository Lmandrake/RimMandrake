#!/usr/bin/env python3
"""Every OPEN alarm in alarms.json names an item, and that item is open in the ledger (rimflow's own replay, so a spawned
or reopened item reads open). A kind that ops_watch_rules.json exempts from a ticket (guard_exempt_kinds) needs no item.
Exit 1 lists each alarm without an open home. Run from the repo root:
    python3 design/specs/2026-11-22-one-view-of-open-work/alarm_home_check.py /mnt/d/ClaudeWork/rimmandrake/ops_watch/alarms.json
"""
import fnmatch, json, sys
sys.path.insert(0, 'src/RimMandrake/rimflow')
import model
world = model.replay()
items = world.items
exempt = json.load(open('src/RimMandrake/Utils/ops_watch_rules.json')).get('guard_exempt_kinds', [])
bad = []
for k, v in json.load(open(sys.argv[1])).items():
    if v.get('state') != 'OPEN' or any(fnmatch.fnmatch(k, x) for x in exempt): continue
    i = v.get('item'); it = items.get(i) if i else None
    if it is None or it.state not in model.OPEN_STATES: bad.append((k, i, it and it.state))
for b in bad: print('NO OPEN HOME', b)
print('open alarms without an open item:', len(bad)); sys.exit(1 if bad else 0)
