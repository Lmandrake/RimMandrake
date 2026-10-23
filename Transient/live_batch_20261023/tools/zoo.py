"""zoo.py LABEL -- census non-colonist pawns on maps 0 and 48 -> Transient/live_batch_20261023/zoo_<LABEL>.json"""
import sys, json, time
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h_, p_, t_ = resolve_endpoint(); out = {}
with RimBridge(h_, p_, t_) as B:
    cur = (B.call("jawa/map_info", {}) or {}).get("mapId")
    for mid in (0, 48):
        B.call("jawa/set_current_map", {"mapId": mid}); time.sleep(0.8)
        r = B.call("jawa/list_pawns", {}) or {}
        ps = r.get("pawns") or []
        keep = []
        for p in ps:
            fac = str(p.get("faction") or p.get("factionName") or "")
            col = p.get("isColonist") or p.get("colonist")
            if col or p.get("isPlayer") and p.get("kindDef")=="Colonist" or p.get("kindDef")=="Colonist": continue
            keep.append("%s|%s|%s|%s,%s|%s" % (p.get("kindDef") or p.get("kind") or p.get("def"), p.get("label") or p.get("name"), fac, p.get("x"), p.get("z"), "prisoner" if p.get("isPrisoner") or p.get("prisoner") else ""))
        out[mid] = sorted(keep)
        print(mid, len(ps), "pawns,", len(keep), "non-colonist; keys:", sorted(ps[0].keys())[:30] if ps else None)
    if isinstance(cur, int): B.call("jawa/set_current_map", {"mapId": cur})
json.dump(out, open(r"Transient\live_batch_20261023\zoo_%s.json" % sys.argv[1], "w"), indent=1)
for k, v in out.items():
    for x in v: print(" ", k, x)
