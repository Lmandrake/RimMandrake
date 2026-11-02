"""SUMP_WALKWAYS_1 A3 (glasswalk slip stagger), FOUNDRY 2026-10-10. python.exe from repo root.
ONE pawn, one walled glasswalk lane: ticks for x=4 -> x=16 (12 cells, start/stop effects excluded), slip off x2.
The speed cap is proved by src/RimMandrake/TheSump/prove_glasswalk_speed.py.
Slip: chance 1.0 vs off on glass, extra travel time. Prints RESULT lines."""
import sys, json, os, statistics as st
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from scenes import scenelib as S
TILE = 114502; ST = "RimMandrake.EnvironmentalHazards.RM_EnvironmentalHazardsSettings"
def calm(): S.call("jawa/kill_hostiles"); S.call("jawa/set_game_speed", speed=0)
def px(pid): return ((S.call("jawa/pawn_get", pawn=pid).get("pawns") or [{}])[0].get("position") or {}).get("x")
def walk(sc, a, x0, x1):
    """Goto start, wait there, then time x0 -> x1 at 10-tick resolution."""
    S.call("jawa/ordered_job", pawnId=a, jobDef="Goto", targetAX=sc.x + 1, targetAZ=sc.z + 1, waitTicks=1)
    for _ in range(80):
        S.run(20)
        if px(a) is not None and px(a) <= sc.x + 2: break
    S.run(40); calm()
    S.call("jawa/ordered_job", pawnId=a, jobDef="Goto", targetAX=sc.x + 18, targetAZ=sc.z + 1, waitTicks=1)
    # Exact 2-tick steps: S.run(10) plays >=200 ms at speed 4 (~80 ticks a sample), which gave the false 0.65 speed ratio
    # of 2026-10-10 (SUMP_GLASSWALK_SPEED_RATIO_1).
    t = 0; ta = None
    while t < 1500:
        S.call("rimworld/step_game_ticks", ticks=2, timeoutMs=60000); t += 2; x = px(a)
        if ta is None and x is not None and x >= sc.x + x0: ta = t
        if ta is not None and x is not None and x >= sc.x + x1: return t - ta
    return None
S.call("jawa/set_game_speed", speed=0)
mid = S.biome_map(TILE, "RM_GreySea", surface_biome="RM_GreySea")
try:
    sc = S.Scene("glass", 40, 60, 20, 4); sc.__enter__(); sc.room(roof=True)
    S.call("jawa/spawn_batch", ops=";".join("Wall:%d,%d" % (sc.x + dx, sc.z + 2) for dx in range(0, 20)), stuff="BlocksGranite")
    a = sc.colonist(1, 1); S.call("jawa/pawn_need", pawn=a, action="need", need="Mood", level=1.0)
    # The speed half moved to src/RimMandrake/TheSump/prove_glasswalk_speed.py (SUMP_GLASSWALK_SPEED_RATIO_1).
    res = {"RM_Glasswalk": []}
    sc.floor("RM_Glasswalk", (1, 1, 18, 1)); S.call("jawa/map_commit", full=True)
    with S.setting(ST, glasswalkSlipEnabled="False"):
        for rep in range(2):
            res["RM_Glasswalk"].append(walk(sc, a, 4, 16)); print(rep, "RM_Glasswalk", res["RM_Glasswalk"][-1], flush=True)
    g = [x for x in res["RM_Glasswalk"] if x]
    with S.setting(ST, glasswalkSlipEnabled="True", glasswalkSlipChancePerSweep=1.0):
        t_on = walk(sc, a, 4, 16)
    print("RESULT SUMP_WALKWAYS_1/A3-slip %s glass slip_off=%s slip_chance1.0=%s ticks per 12 cells" % ("PASS" if t_on and g and t_on > 1.3 * st.mean(g) else "UNMEASURED", res["RM_Glasswalk"], t_on), flush=True)
finally:
    calm()
    try: sc.teardown()
    except Exception as e: print("teardown", e)
    S.drop_map(mid, TILE, back=0)
