import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils")
from rimdrive.session import Session
OUT = {}
def rec(s, key, tool, **p):
    t=time.time()
    try: r = s.call(tool, **p)
    except Exception as e: r = {"EXC": type(e).__name__, "msg": str(e)[:300]}
    if isinstance(r, dict): r.pop("operation", None)
    OUT[key] = {"tool": tool, "params": p, "ms": int((time.time()-t)*1000), "result": r}
    return r
with Session(strict=False, quiet=True, focus=False) as s:
    rec(s,"time_clock","jawa/time_clock")
    rec(s,"map_info","jawa/map_info")
    pw = rec(s,"list_pawns_health","jawa/list_pawns", includeHealth=True, includeCorpses=True, limit=500)
    rec(s,"letter_list","jawa/letter_list")
    rec(s,"rimworld_list_letters","rimworld/list_letters")
    rec(s,"alerts","jawa/alerts_list")
    rec(s,"weather","jawa/weather_get")
    rec(s,"story_stats","jawa/story_stats")
    rec(s,"debug_settings","jawa/debug_settings", action="list")
    rec(s,"windows","jawa/window_list_close", action="list")
    rec(s,"fire_defName","jawa/list_things", defName="Fire")
    rec(s,"fire_group","jawa/list_things", group="Fire")
    rec(s,"fire_group_any","jawa/list_things", group="Fire", includePawns=False, limit=5)
    rec(s,"drain_log","jawa/drain_log", limit=20)
    rec(s,"get_ui_state","rimworld/get_ui_state")
    rec(s,"incident_queue_clear_dry","jawa/incident_queue_clear")  # ALSO measures what it reports; clearing at t=0 is harmless
    rows = (pw.get("pawns") or []) if isinstance(pw, dict) else []
    col = [r for r in rows if r.get("isPlayer")]
    OUT["_summary"] = {"pawns": len(rows), "colonists": len(col), "colonist_ids": [c.get("id") for c in col][:6]}
    if col:
        pid = col[0]["id"]
        rec(s,"pawn_need_list","jawa/pawn_need", action="list", pawn=pid)
        rec(s,"pawn_mental_list","jawa/pawn_mental", action="list", pawn=pid)
        rec(s,"pawn_break","jawa/pawn_break_thresholds", pawn=pid)
open("Transient/northstar_probe/contracts_raw.json","w").write(json.dumps(OUT, indent=1, default=str))
for k,v in OUT.items():
    if k.startswith("_"): print(k, v); continue
    r=v["result"]; ok = r.get("success") if isinstance(r,dict) else None
    print("%-26s %5dms success=%s keys=%s" % (k, v["ms"], ok, list(r.keys())[:9] if isinstance(r,dict) else type(r)))
