# -*- coding: utf-8 -*-
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e)}

print("=== UI_STATE_MAP_READS_NULL_1 ===")
u=c('rimworld/get_ui_state')
print("get_ui_state ->", json.dumps(u)[:500])
print("get_game_info ->", json.dumps({k:v for k,v in c('rimworld/get_game_info').items() if k!='operation'})[:200])
ps=c('jawa/list_pawns',{'limit':999}).get('pawns') or []
print("list_pawns    -> %d pawns on the map get_ui_state is describing"%len(ps))

print()
print("=== CAMERA_CANNOT_AIM_AT_ANIMALS_1 ===")
animals=[x for x in ps if not x.get('factionName') and x.get('intelligence')!='Humanlike']
humans =[x for x in ps if x.get('kindDef')=='Jawa_Tribal_Scavenger']
a=animals[0] if animals else None; hm=humans[0] if humans else None
print("animal:", {k:a.get(k) for k in ('name','kindDef','id','x','z')} if a else None)
print("human :", {k:hm.get(k) for k in ('name','kindDef','id','x','z')} if hm else None)
for label,who in (("HUMAN",hm),("ANIMAL",a)):
    if not who: continue
    for key in ('pawnName','pawnId'):
        v = who.get('name') if key=='pawnName' else who.get('id')
        r=c('rimworld/jump_camera_to_pawn',{key:v})
        print("  jump_camera_to_pawn %-6s %-8s=%-14s -> success=%s msg=%s"%(
            label,key,str(v)[:14],r.get('success'),(r.get('message') or '')[:70]))
    d=c('jawa/pawn_get',{'pawn':who.get('id')})
    pw=d.get('pawns')[0] if isinstance(d.get('pawns'),list) and d.get('pawns') else d
    print("  pawn_get position:", pw.get('position'))
if a:
    pos=(c('jawa/pawn_get',{'pawn':a['id']}).get('pawns') or [{}])[0].get('position') or {}
    X,Z=pos.get('x',a.get('x')),pos.get('z',a.get('z'))
    r=c('rimworld/screenshot_cell_rect',{'x':X-6,'z':Z-6,'width':13,'height':13,
                                         'fileName':'CHECK_animal_2026-08-26'})
    print("  screenshot_cell_rect at animal (%s,%s) -> success=%s %s"%(X,Z,r.get('success'),
          json.dumps({k:v for k,v in r.items() if k in ('path','file','message')})[:220]))
