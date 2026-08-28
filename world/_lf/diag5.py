# -*- coding: utf-8 -*-
import sys, json, io, collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e)}
ps=c('jawa/list_pawns',{'limit':999}).get('pawns') or []
cnt=collections.Counter(x.get('name') for x in ps)
amb=[x for x in ps if not x.get('factionName') and cnt[x.get('name')]>1][:2]
jaw=[x for x in ps if x.get('kindDef')=='Jawa_Tribal_Scavenger'][:2]
print("HYPOTHESIS: jump_camera_to_pawn's pawnId = 'Thing_' + jawa/list_pawns id\n")
for x in amb+jaw:
    raw=x['id']
    for cand in (raw, 'Thing_'+raw):
        r=c('rimworld/jump_camera_to_pawn',{'pawnId':cand})
        print("  %-22s pawnId=%-22s -> success=%s"%(x.get('kindDef'),cand,r.get('success')))
print("\n=> an AMBIGUOUSLY named animal, addressed by id:")
if amb:
    r=c('rimworld/jump_camera_to_pawn',{'pawnId':'Thing_'+amb[0]['id']})
    print("   %s (%s) -> success=%s"%(amb[0]['name'],amb[0]['id'],r.get('success')))
    pos=(c('jawa/pawn_get',{'pawn':amb[0]['id']}).get('pawns') or [{}])[0].get('position') or {}
    s=c('rimworld/take_screenshot',{'fileName':'CHECK_camera_animal_2026-08-26'})
    print("   screenshot after aiming ->", s.get('success'), (s.get('path') or s.get('file') or '')[:110])
