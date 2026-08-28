# -*- coding: utf-8 -*-
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=300); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
c('jawa/map_commit',{'regions':True,'pathing':True,'power':True,'redraw':True})
rg=c('jawa/room_get',{'rect':'100,200,18,10'})
print((rg.get('message') or json.dumps(rg))[:200]); print()
for q in (rg.get('rooms') or []):
    print("id=%-5s role=%-16s cells=%-4s temp=%6.1f openRoof=%-3s proper=%-5s outdoors=%-5s"%(
        q.get('id'), q.get('role'), q.get('cellCount'), q.get('temperature') or 0,
        q.get('openRoofCount'), q.get('properRoom'), q.get('isOutdoors')))
    print("     stats:", json.dumps(q.get('stats')))
plan=json.load(io.open(r"D:\Luke\dev\Rimworld\world\_lf\tpl2_plan.json",encoding='utf-8'))
print("\nPLAN wanted:", [(x['id'],x['role']) for x in plan['rooms']])
print("GAME says  :", [q.get('role') for q in (rg.get('rooms') or [])])
json.dump(rg, io.open(r"D:\Luke\dev\Rimworld\world\_lf\tpl2_roomget.json","w",encoding='utf-8'), indent=1)
