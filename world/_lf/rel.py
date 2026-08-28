import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=90); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e),"success":False}
r=c('jawa/faction_relations_get',{'faction':'Player','includeNeutral':True})
rows=r.get('rows') or r.get('relations') or []
for q in rows:
    n=json.dumps(q)
    if 'Droid' in n or 'Blackstar' in n or 'Geonos' in n: print("  ", n[:190])
