import sys, json, collections
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
t = S.call("jawa/list_things", rect="0,0,100,100", limit=2000, includePawns=False)
c = collections.Counter(x.get("def") for x in t.get("things") or [])
print([(k,v) for k,v in c.items() if any(w in k for w in ("urret","Mortar","Sentry","Gun","Trap","Spike","Cannon","Auto"))])
pg=(S.call("jawa/pawn_get", pawn="Human29120").get("pawns") or [{}])[0]
print([ (h.get("def"), h.get("part"), h.get("source")) for h in pg.get("hediffs",[])][:6])
d=S.call("jawa/damage_log", limit=8); print(str(d)[:1200])
