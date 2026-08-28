# -*- coding: utf-8 -*-
"""Both my pawns show job=None. Is that the pawns, or the field? Read a subject I did NOT create."""
import sys, json, io, collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=300); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
made=json.load(io.open(r"D:\Luke\dev\Rimworld\world\_lf\j45_pawns.json",encoding='utf-8'))
ps=c('jawa/list_pawns',{'faction':'player','limit':100}).get('pawns') or []
print("player-faction pawns: %d"%len(ps))
for x in ps[:14]:
    mine = x['id'] in made.values()
    print("   %-14s %-12s job=%-22s drafted=%-5s downed=%-5s %s"%(
        x.get('name'), x.get('kindDef'), str(x.get('job'))[:22], x.get('drafted'), x.get('downed'),
        "<- MINE" if mine else ""))
print()
lc=c('rimworld/list_colonists',{})
rows=lc.get('colonists') or []
print("rimworld/list_colonists: %d rows"%len(rows))
for q in rows[:8]:
    print("   %-14s job=%-26s drafted=%s mentalState=%s"%(q.get('name'), str(q.get('job'))[:26], q.get('drafted'), q.get('mentalState')))
print()
for tag,pid in made.items():
    d=c('jawa/pawn_get',{'pawn':pid})
    pw=d.get('pawns')[0] if isinstance(d.get('pawns'),list) and d.get('pawns') else d
    print("  %-10s pos=%s needs=%s"%(tag, pw.get('position'), json.dumps(pw.get('needs'))[:140]))
    ps2=c('jawa/set_player_settings',{'pawnId':pid}) if False else None
