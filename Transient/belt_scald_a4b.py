import sys, json
sys.path.insert(0, "Transient")
from belt_scald_probe import call
def sev(p):
    for h in call("jawa/pawn_get", pawn=p)["pawns"][0]["hediffs"]:
        if h["def"] == "RUT_ScaldExposure": return h["severity"]
call("rimworld/pause_game", pause=True)
a0, b0 = sev("Human634"), sev("Human637"); print("t0", a0, b0)
r = call("rimworld/step_game_ticks", ticks=5000, timeoutMs=240000, pauseFirst=True); print(str(r)[:200])
a1, b1 = sev("Human634"), sev("Human637"); print("t1", a1, b1)
da, db = a1 - a0, b1 - b0
print("delta unprot %.6f  boilsuit %.6f  ratio %.4f   expected unprot/2500t %.6f" % (da, db, db/da if da else -1, 0.6/60000*5000))
