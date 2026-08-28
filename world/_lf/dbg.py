# -*- coding: utf-8 -*-
"""READ ONLY. Targeted search, never an enumeration, never an execute."""
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
for x in b.list_tools():
    if x.get('name')=='rimworld/search_debug_actions':
        print("keys:", sorted((x.get('inputSchema',{}).get('properties') or {}).keys()))
for q in ('generate map','change map','biome'):
    r=b.call('rimworld/search_debug_actions',{'query':q,'limit':10}); r.pop('operation',None)
    rows=r.get('actions') or r.get('results') or []
    print("\n=== query %-14s -> %s rows"%(q, len(rows) if isinstance(rows,list) else r.get('message')))
    for a in (rows or [])[:8]:
        print("   ", json.dumps({k:a.get(k) for k in ('path','label','actionType','category')})[:170])
