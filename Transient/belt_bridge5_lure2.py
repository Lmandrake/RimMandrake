import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
did=sys.argv[1]
p=(S.call("jawa/pawn_get", pawn=did).get("pawns") or [{}])[0]; print("drazzik", p.get("position"), p.get("curJob") or p.get("job"), [h.get("def") for h in p.get("hediffs") or []])
X,Z=p["position"]["x"],p["position"]["z"]
m=S.call("jawa/spawn_pawn", kindDef="Muffalo", x=X+6, z=Z, faction="none", count=2); print("muffalo", m.get("message"))
for i in range(12):
    r=S.call("jawa/inspect_string", thingIds=did)
    ins=[l for l in ((r.get("things") or [{}])[0].get("inspect") or []) if "decision" in l.lower()]
    print("tick", r.get("ticksGame"), ins)
    S.run(90)
