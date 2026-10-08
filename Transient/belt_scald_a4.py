import sys, json, time
sys.path.insert(0, "Transient")
from belt_scald_probe import call
A, B = "Human634", "Human637"
def hed(pid):
    r = call("jawa/pawn_get", pawn=pid)
    hs = r.get("hediffs") or (r.get("pawn") or {}).get("hediffs") or []
    return [(h.get("def") or h.get("defName"), h.get("severity")) for h in hs if "Scald" in str(h)], r
print("clear", call("jawa/pawn_gear", pawn=A, action="clear", clearWhat="apparel").get("success"), call("jawa/pawn_gear", pawn=B, action="clear", clearWhat="apparel").get("success"))
w = call("jawa/pawn_gear", pawn=B, action="wear", **{"def": "RM_Apparel_BoilSuit"}); print("wear", str(w)[:200])
for p in (A, B): print(p, "ArmorRating_Heat", str(call("jawa/pawn_stats", pawn=p, stats="ArmorRating_Heat"))[:300])
print("weather", str(call("jawa/weather_set", weather="RUT_ScaldSteam", lockWeather=True))[:200])
print("cond", str(call("jawa/game_condition", action="start", condition="RUT_ScaldSteamCarrier", durationTicks=600000))[:200])
call("rimworld/pause_game", pause=False)
for i in range(8):
    r = call("rimworld/step_game_ticks", ticks=2500)
    time.sleep(1)
    print(i, "A", hed(A)[0], "B", hed(B)[0], str(call("jawa/weather_get").get("weather"))[:80], flush=True)
