import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=300); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
s=c('jawa/thing_stats',{'pawn':'Human57127'})
for th in (s.get('things') or []):
    print("### %s  (%s)"%(th.get('defName'), th.get('id')))
    st=th.get('stats') or []
    diff=[q for q in st if q.get('defBase') is not None and q.get('value')!=q.get('defBase')]
    print("   %d stats, %d where the INSTANCE differs from the def"%(len(st), len(diff)))
    for q in diff[:8]:
        print("      %-28s instance=%-12s defBase=%s"%(q.get('defName'), q.get('value'), q.get('defBase')))
    print()
