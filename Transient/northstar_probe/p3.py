import sys, json, time, os
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
def snap(s, tag):
    pw = rec(s, tag+"/pawns", "jawa/list_pawns", includeHealth=True, includeCorpses=True, limit=500)
    rec(s, tag+"/letters", "jawa/letter_list")
    rec(s, tag+"/rletters", "rimworld/list_letters")
    rec(s, tag+"/stats", "jawa/story_stats")
    rec(s, tag+"/fire", "jawa/list_things", defName="Fire")
    rec(s, tag+"/alerts", "jawa/alerts_list")
    rec(s, tag+"/clock", "jawa/time_clock")
    return pw
def step(s, tag, n):
    rec(s, tag, "rimworld/step_game_ticks", ticks=n, pauseFirst=True)
with Session(strict=False, quiet=True, focus=False) as s:
    pw = snap(s, "t0")
    col = [r for r in pw["pawns"] if r["isPlayer"] and r["intelligence"]=="Humanlike"]
    a,b,c = col[0], col[1], col[2]
    OUT["_colonists"] = [(x["id"],x["x"],x["z"]) for x in col]
    # B fire next to a
    rec(s,"B_fire_start","jawa/map_fire", action="start", rect="%d,%d,3,3"%(a["x"]+4,a["z"]+4), fireSize=1.0)
    rec(s,"B_fire_immediate","jawa/list_things", defName="Fire")
    step(s,"B_step60",60); snap(s,"B_after60")
    # C damage while paused on b
    rec(s,"C_damage","jawa/damage", thingId=b["id"], damageDef="Cut", amount=8, allowColonists=True)
    rec(s,"C_immediate","jawa/list_pawns", includeHealth=True, rect=None) if False else None
    p2 = rec(s,"C_immediate_pawns","jawa/list_pawns", includeHealth=True, limit=500)
    # D kill c
    rec(s,"D_kill","jawa/pawn_force_incapacitate", pawn=c["id"], action="kill")
    snap(s,"D_after_kill_nostep")
    step(s,"D_step10",10); snap(s,"D_after_kill_step10")
    # E hostile predator (no faction) + hostile raid
    rec(s,"E_spawn_wolf","jawa/spawn_pawn", kindDef="Wolf_Timber", x=a["x"]+8, z=a["z"]+8, faction="none")
    rec(s,"E_raid_dry","jawa/fire_raid", points=200.0, dryRun=True)
    rec(s,"E_raid","jawa/fire_raid", points=200.0, dryRun=False)
    snap(s,"E_after_raid_nostep")
    step(s,"E_step300",300); snap(s,"E_after_raid_300")
    # F mental break on a
    rec(s,"F_break","jawa/pawn_force_mental_break", pawn=a["id"], intensity="minor")
    snap(s,"F_after_break")
    rec(s,"F_mental","jawa/pawn_mental", action="list", pawn=a["id"])
    # G screenshot while paused
    rec(s,"G_shot","rimworld/take_screenshot", fileName="np_probe_%d"%int(time.time()), suppressMessage=True)
    rec(s,"G_drain","jawa/drain_log", limit=40)
open("Transient/northstar_probe/contracts_events.json","w").write(json.dumps(OUT, indent=1, default=str))
for k,v in OUT.items():
    if k.startswith("_"): continue
    r=v["result"]
    if k.endswith("/pawns") or k.endswith("/letters") or k.endswith("/rletters") or k.endswith("/alerts") or k.endswith("/clock"): continue
    print("%-24s %4dms %s" % (k, v["ms"], json.dumps(r, default=str)[:170]))
