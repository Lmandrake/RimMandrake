import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e),"success":False}
for tool in ('jawa/world_links_validate','jawa/world_objects_validate','jawa/world_lint',
             'jawa/world_cache_audit','jawa/tile_cache_audit','jawa/world_mutators_audit'):
    r=c(tool,{'limit':40})
    print("=== %s"%tool)
    print("   ", (r.get('message') or json.dumps(r))[:420])
    for k in ('findings','issues','asymmetric','nonAdjacent','hidden','problems','total'):
        if k in r:
            v=r[k]
            print("     %-14s %s"%(k, (len(v) if isinstance(v,list) else json.dumps(v))))
    print()
