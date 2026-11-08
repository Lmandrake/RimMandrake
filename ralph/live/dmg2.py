"""dmg2.py -- every recorded non-pawn damage event, grouped by victim def and instigator (what a 'satisfied' raid counted)."""
import sys
from collections import Counter
import fwb
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
B = fwb.FW()
d = B.call("jawa/damage_log", pawnsOnly=False, kind="damage", limit=4096) or {}
ev = d.get("events") or []
print(len(ev), "events; oldest tick", d.get("oldestRetainedTick"))
c = Counter()
for e in ev:
    if e.get("victimIsPawn"):
        continue
    c[(e.get("victimDef"), e.get("victimFaction"), e.get("damageDef"), e.get("instigatorDef"), e.get("instigatorFaction"))] += float(e.get("totalDealt") or 0)
for k, v in c.most_common(15):
    print(round(v, 1), k)
for e in [e for e in ev if not e.get("victimIsPawn")][:3]:
    print({k: e.get(k) for k in ("tick", "victimDef", "victimId", "cell", "x", "z", "origin")})
