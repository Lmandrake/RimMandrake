import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimdrive import Session
with Session(lock=None) as s:
    r = s.call("jawa/spawn_pawn", kindDef="Rat", x=30, z=30, faction="none", count=1)
    row = r["pawns"][0]; print("row keys", json.dumps(row)[:500])
    x = row.get("x"); z = row.get("z")
    if x is None and isinstance(row.get("position"), dict): x, z = row["position"].get("x"), row["position"].get("z")
    s.track("pawn", row["id"], x, z); print("tracked at", x, z, "sweep", s.sweep())
    c = s.call("jawa/list_things", group="Corpse", limit=50); print("corpses:", c.get("countMatched"), [t.get("def") for t in c.get("things", [])])
