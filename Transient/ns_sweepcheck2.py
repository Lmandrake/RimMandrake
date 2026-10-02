import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimdrive import Session
with Session(lock=None) as s:
    c = s.call("jawa/list_things", group="Corpse", limit=50)
    print("corpses on map:", c.get("countMatched"), [ (t.get("def"), t.get("position")) for t in (c.get("things") or [])][:5])
    p = s.call("jawa/list_pawns", limit=500, faction="nonplayer")
    print("nonplayer pawns:", p.get("count"), [q.get("name") for q in p.get("pawns", [])][:6])
