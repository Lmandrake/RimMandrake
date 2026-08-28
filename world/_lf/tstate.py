import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=240); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
gi=c('rimworld/get_game_info'); print("ticks", gi.get('ticksGame'), "maps", gi.get('mapCount'))
for lab,cell in (("indoor","103,205"),("outdoor","140,200")):
    r=c('jawa/cell_temperature',{'cell':cell})
    print("  %-8s %s"%(lab, json.dumps({k:v for k,v in r.items() if k!='operation'})[:200]))
rg=c('jawa/room_get',{'rect':'100,200,18,10'})
for q in (rg.get('rooms') or []):
    if (q.get('cellCount') or 0)>1:
        print("  room %-12s cells=%-3s temp=%.1f"%(q.get('role'), q.get('cellCount'), q.get('temperature') or 0))
