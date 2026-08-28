# -*- coding: utf-8 -*-
"""TEMPLATE_ENGINE_ACCEPTANCE_1 criteria 1 and 2, now that jawa/room_get exists."""
import sys, json, io, collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
R=r"D:\Luke\dev\Rimworld\world\_lf"
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=300); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
X0,Z0,W,H=100,200,18,10
print("1. clear the ground")
r=c('jawa/destroy_batch',{'rects':'%d,%d,%d,%d'%(X0,Z0,W,H)})
if not r.get('success'):
    r=c('jawa/destroy_batch',{'ops':'%d,%d,%d,%d'%(X0,Z0,W,H)})
print("   destroy ->", r.get('success'), (r.get('message') or json.dumps(r))[:130])

print("2. build")
calls=json.load(io.open(R+r"\tpl2_calls.json",encoding='utf-8'))
plan =json.load(io.open(R+r"\tpl2_plan.json",encoding='utf-8'))
def translate(call):
    tool, prm = call['tool'], dict(call['params'])
    if tool in ('jawa/set_terrain_batch','jawa/set_roof_batch') and 'rect' in prm:
        d = prm.pop('terrainDef', None) or prm.pop('roofDef', None)
        prm = {'ops': '%s:%s'%(d, prm.pop('rect'))}
    return tool, prm
placed=0
for call in calls:
    tool,prm=translate(call)
    r=c(tool,prm)
    if 'placed' in r: placed+=r['placed']
    print("   %-26s %s %s"%(tool.split('/')[-1], r.get('success'), (r.get('message') or '')[:70]))
print("   total placed:", placed)

print("\n3. jawa/room_get  <- CRITERION 1 and 2")
rg=c('jawa/room_get',{'rects':'%d,%d,%d,%d'%(X0,Z0,W,H)})
print("   ", (rg.get('message') or json.dumps(rg))[:160])
rooms=rg.get('rooms') or []
for q in rooms:
    print("   id=%-5s role=%-14s cells=%-4s temp=%6.1f openRoof=%-3s proper=%-5s outdoors=%s"%(
        q.get('id'), q.get('role'), q.get('cellCount'), q.get('temperature') or 0,
        q.get('openRoofCount'), q.get('properRoom'), q.get('isOutdoors')))
    print("        stats:", json.dumps(q.get('stats')))
print("\n   PLAN wanted:", [ (x['id'],x['role']) for x in plan['rooms'] ])
print("   GAME says  :", [ q.get('role') for q in rooms ])
json.dump({'plan':plan['rooms'],'rooms':rooms}, io.open(R+r"\tpl2_rooms.json","w",encoding='utf-8'), indent=1)
