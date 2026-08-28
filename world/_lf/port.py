# -*- coding: utf-8 -*-
"""WORLD_PORT_SURVIVES_BRIDGE_1 - validate the LIVE world against the authored bundles.
world_tile_validate reads RAW tile fields. NOTHING IS WRITTEN."""
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e),"success":False}
CSVS=[(r"D:\Luke\dev\Rimworld\world\_lf\live_tiles.csv","live export taken today (CONTROL)"),
      (r"D:\Luke\dev\Rimworld\world\_final\live_tiles.csv","_final bundle 2026-08-25 08:25"),
      (r"D:\Luke\dev\Rimworld\world\ASHKARR_VIVIFIED_2026-08-24_tiles.csv","VIVIFIED bundle 2026-08-24"),
      (r"D:\Luke\dev\Rimworld\world\ASHKARR_DRAFT_2026-08-24_tiles.csv","DRAFT bundle 2026-08-24")]
out={}
for path,label in CSVS:
    r=c('jawa/world_tile_validate',{'path':path,'maxRows':30000,'limit':40})
    print("=== %s"%label)
    print("    rows=%s matched=%s mismatched=%s matchPct=%s tol=%s raw=%s"%(
        r.get('rows'),r.get('matched'),r.get('mismatched'),r.get('matchPct'),
        r.get('tolerance'),r.get('readRawFields')))
    bf=r.get('byField') or {}
    if bf: print("    byField:", json.dumps(bf)[:300])
    for q in (r.get('diffs') or [])[:4]: print("      ", json.dumps(q)[:210])
    out[label]={k:r.get(k) for k in ('rows','matched','mismatched','matchPct','byField','tolerance','readRawFields')}
    print()
# dry-run import: what WOULD a port change?
r=c('jawa/world_tile_import',{'path':CSVS[2][0],'apply':False,'maxRows':30000,'sampleRows':6})
print("=== world_tile_import DRY RUN against the VIVIFIED bundle (apply=false)")
print("   ", (r.get('message') or json.dumps(r))[:400])
json.dump(out, open(r"D:\Luke\dev\Rimworld\world\_lf\port_result.json","w"), indent=1)
