"""cell_things.py x0 z0 x1 z1: list every thing (def, category, position) in a rect of the live map (visit 8 strange-thing probe)."""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6, "src", "RimMandrake", "Utils"))
import validation_core as V
B = V.Bridge()
x0, z0, x1, z1 = map(int, sys.argv[1:5])
th = []
for q in ({"group": "Corpse"}, {"group": "Filth"}, {}):
    th += (B.call("jawa/list_things", limit=20000, **q) or {}).get("things") or []
seen = set()
for t in th:
    k = (t.get("def"), t.get("x"), t.get("z"), t.get("id"))
    if k in seen or not (x0 <= (t.get("x") or -1) <= x1 and z0 <= (t.get("z") or -1) <= z1):
        continue
    seen.add(k)
    print({kk: t.get(kk) for kk in ("id", "def", "x", "z", "label")})
