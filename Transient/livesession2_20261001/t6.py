import json
from bx import call
OUT={}
def log(k, v):
    OUT[k] = v; print(k, json.dumps(v, default=str)[:700], flush=True)
    json.dump(OUT, open("t6.json", "w"), indent=1, default=str)
def snap():
    ps = call("jawa/list_pawns", {"limit": 500, "includeHealth": True, "includeCorpses": True}).get("pawns") or []
    out=[]
    for p in ps:
        if p.get("kindDef") in ("RSW_KraytDragon","RM_Muurrok") or p.get("isPlayer"):
            hs=[h.get("def") for h in (p.get("health") or {}).get("hediffs", [])]
            out.append((p["id"], p.get("x"), p.get("z"), p.get("dead"), p.get("downed"), hs[:8]))
    return out
for i in range(8):
    call("rimworld/step_game_ticks", {"ticks": 500}, 300)
    log(f"s{i}", snap())
th = call("jawa/list_things", {"group": "Filth", "limit": 5000})
cnt = {}
for t in th.get("things") or []:
    d = t.get("def")
    if str(d).startswith("RM_Filth"): cnt[d] = cnt.get(d, 0) + 1
log("rm_filth", cnt)
log("letters", [(l.get("label") if not isinstance(l.get("label"), dict) else l["label"].get("RawText"), l.get("arrivalTick")) for l in call("jawa/letter_list", {}).get("letters", [])][-8:])
log("wild", call("jawa/get_defs", {"defs": "BiomeDef/RM_Stillsand", "fields": "wildAnimals"}, 60))
