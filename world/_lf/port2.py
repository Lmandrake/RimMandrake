# -*- coding: utf-8 -*-
"""The other half of the criteria: links (rivers/roads) and objects (settlements). READ ONLY."""
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e),"success":False}
for x in b.list_tools():
    if x.get('name') in ('jawa/world_links_validate','jawa/world_objects_validate'):
        print("###",x['name'],"keys:",sorted((x.get('inputSchema',{}).get('properties') or {}).keys()))
        print("    ",(x.get('description') or '')[:200])
print()
F=r"D:\Luke\dev\Rimworld\world\_final"
V=r"D:\Luke\dev\Rimworld\world"
for tool,paths in (('jawa/world_links_validate',[(F+r"\live_links.csv","_final links 2026-08-25"),
                                                 (V+r"\ASHKARR_VIVIFIED_2026-08-24_links.csv","VIVIFIED links")]),
                   ('jawa/world_objects_validate',[(F+r"\live_settlements.csv","_final settlements 2026-08-25"),
                                                 (V+r"\ASHKARR_VIVIFIED_2026-08-24_settlements.csv","VIVIFIED settlements")])):
    for path,label in paths:
        r=c(tool,{'path':path,'maxRows':40000,'limit':30})
        print("=== %-34s %s"%(label, (r.get('message') or '')[:150]))
        for k in ('rows','matched','mismatched','matchPct','missing','extra','byField'):
            if k in r: print("     %-12s %s"%(k, json.dumps(r[k])[:200]))
        for q in (r.get('diffs') or [])[:3]: print("       ", json.dumps(q)[:180])
