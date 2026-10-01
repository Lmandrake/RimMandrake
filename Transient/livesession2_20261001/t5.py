"""Event creatures: krayt attack, muurrok emergence, Long Hunger."""
import json
from bx import call
OUT = {}
def log(k, v):
    OUT[k] = v; print(k, json.dumps(v, default=str)[:500], flush=True)
    json.dump(OUT, open("t5.json", "w"), indent=1, default=str)
def kinds(ks):
    ps = call("jawa/list_pawns", {"limit": 500, "includeHealth": True, "includeCorpses": True}).get("pawns") or []
    return [(p["id"], p.get("kindDef"), p.get("x"), p.get("z"), p.get("dead"), p.get("factionName")) for p in ps if p.get("kindDef") in ks]
def letters():
    return [(l.get("label") if not isinstance(l.get("label"), dict) else l["label"].get("RawText"), l.get("arrivalTick")) for l in call("jawa/letter_list", {}).get("letters", [])]
K = ("RSW_KraytDragon", "RSW_GreaterKraytDragon", "RM_Muurrok")
log("wild_before", kinds(K))
for inc in ("RUT_KraytAttack", "RM_MuurrokEmergence"):
    d = call("jawa/fire_incident", {"incidentDef": inc, "dryRun": True}, 60)
    f = call("jawa/fire_incident", {"incidentDef": inc}, 120)
    d2 = call("jawa/fire_incident", {"incidentDef": inc, "dryRun": True}, 60)
    log(inc, {"dry": d.get("canFireNow"), "fired": f.get("fired"), "msg": f.get("message"), "dry_after": d2.get("canFireNow")})
for i in range(8):
    call("rimworld/step_game_ticks", {"ticks": 500}, 300)
    log(f"s{i}", {"pawns": kinds(K)})
log("letters", letters()[-10:])
for inc in ("RUT_LongHungerSurfaces", "RUT_LongHunger"):
    try:
        d = call("jawa/fire_incident", {"incidentDef": inc, "dryRun": True}, 60)
        log("dry_" + inc, {k: d.get(k) for k in ("success", "canFireNow", "message")})
    except Exception as e:
        log("dry_" + inc, str(e))
