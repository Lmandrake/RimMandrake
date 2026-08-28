# -*- coding: utf-8 -*-
"""P4: no MECHANOID is named this way.  P5: a player-renamed animal is never overwritten."""
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e)}
def nameof(pid):
    d=c('jawa/pawn_get',{'pawn':pid})
    pw=d.get('pawns')[0] if isinstance(d.get('pawns'),list) and d.get('pawns') else d
    return pw.get('name')

print("=== P4: mechanoids ===")
for k in ('Mech_Scyther','Mech_Lancer','Mech_Centipede'):
    r=c('jawa/spawn_pawn',{'kindDef':k,'x':70,'z':70,'faction':'none','count':1})
    rows=r.get('pawns') or []
    if not rows: print("  %-16s spawn -> %s"%(k,(r.get('message') or '')[:70])); continue
    pid=rows[0]['id']; n0=nameof(pid)
    f=c('jawa/set_pawn_faction',{'pawn':pid,'faction':'player'})
    print("  %-16s before=%-22s after_faction_player=%-22s ok=%s"%(k,n0,nameof(pid),f.get('success')))

print("\n=== P5: a player-set name must survive ===")
ps=c('jawa/list_pawns',{'limit':999}).get('pawns') or []
tame=[x for x in ps if x.get('isPlayer') and x.get('intelligence')!='Humanlike']
if not tame:
    tame=[x for x in ps if (x.get('factionName') or '').lower().startswith('player')]
print("  tamed animals now in the colony:", len(tame))
if tame:
    a=tame[0]; pid=a['id']
    print("  taming-assigned name :", nameof(pid))
    c('jawa/set_pawn_identity',{'pawn':pid,'name':'OWNERNAME_TEST'})
    print("  after set_pawn_identity:", nameof(pid))
    c('jawa/set_pawn_faction',{'pawn':pid,'faction':'none'})
    c('jawa/set_pawn_faction',{'pawn':pid,'faction':'player'})
    print("  after none->player again:", nameof(pid), " <- P5 PASS if unchanged")
