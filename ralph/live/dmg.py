"""dmg.py -- player-owned things below full hit points (what a raid's 'satisfied with the damage' trigger counted)."""
import json
import sys
import fwb
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
B = fwb.FW()
kw = dict(faction="player", limit=5000)
if len(sys.argv) > 1:
    kw["def"] = sys.argv[1]
d = B.call("jawa/list_things", **kw) or {}
rows = next((v for v in d.values() if isinstance(v, list) and v and isinstance(v[0], dict)), [])
print(len(rows), "player things; keys:", sorted(rows[0].keys())[:30] if rows else d.get("message"))
dam = []
for r in rows:
    h = r.get("hitPoints", r.get("hp"))
    m = r.get("maxHitPoints", r.get("maxHp"))
    if h is not None and m and h < m:
        dam.append((r.get("def"), r.get("x"), r.get("z"), h, m))
print(len(dam), "damaged, total missing", sum(m - h for *_, h, m in dam))
for x in dam[:40]:
    print(x)
