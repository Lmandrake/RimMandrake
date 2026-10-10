"""SUMP_WALKWAYS_1 A3 (glasswalk speed cap ~80% + slip stagger), FOUNDRY 2026-10-10. python.exe from repo root, ~8 min.
ONE pawn, one walled lane, floor alternated glass/granite x3 each (slip off): ticks for x=4 -> x=16 (12 cells, start/stop effects excluded).
A two-pawn lane swap earlier gave 0.57 but identical-surface runs of the same pawn were not shown to repeat, so this repeats.
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
    t0 = S.ticks(); ta = tb = None
    while S.ticks() - t0 < 1500:
        S.run(10); x = px(a)
        if ta is None and x is not None and x >= sc.x + x0: ta = S.ticks()
        if tb is None and x is not None and x >= sc.x + x1: tb = S.ticks(); break
    return (tb - ta) if (ta and tb) else None
S.call("jawa/set_game_speed", speed=0)
mid = S.biome_map(TILE, "RM_GreySea", surface_biome="RM_GreySea")
try:
    sc = S.Scene("glass", 40, 60, 20, 4); sc.__enter__(); sc.room(roof=True)
    S.call("jawa/spawn_batch", ops=";".join("Wall:%d,%d" % (sc.x + dx, sc.z + 2) for dx in range(0, 20)), stuff="BlocksGranite")
    a = sc.colonist(1, 1); S.call("jawa/pawn_need", pawn=a, action="need", need="Mood", level=1.0)
    res = {"RM_Glasswalk": [], "TileGranite": []}
    with S.setting(ST, glasswalkSlipEnabled="False"):
        for rep in range(3):
            for terr in ("TileGranite", "RM_Glasswalk"):
                sc.floor(terr, (1, 1, 18, 1)); S.call("jawa/map_commit", full=True)
                res[terr].append(walk(sc, a, 4, 16)); print(rep, terr, res[terr][-1], flush=True)
    g = [x for x in res["RM_Glasswalk"] if x]; n = [x for x in res["TileGranite"] if x]
    ratio = (st.mean(n) / st.mean(g)) if g and n else 0
    print("RESULT SUMP_WALKWAYS_1/A3-speed %s glass=%s granite=%s (ticks per 12 cells) speed_ratio=%.2f spec~0.80 (13 ticks/cell + pathCost 3)" % ("PASS" if 0.72 <= ratio <= 0.90 else ("UNMEASURED" if not g or not n else "FAIL"), res["RM_Glasswalk"], res["TileGranite"], ratio), flush=True)
    sc.floor("RM_Glasswalk", (1, 1, 18, 1)); S.call("jawa/map_commit", full=True)
    with S.setting(ST, glasswalkSlipEnabled="True", glasswalkSlipChancePerSweep=1.0):
        t_on = walk(sc, a, 4, 16)
    print("RESULT SUMP_WALKWAYS_1/A3-slip %s glass slip_off=%s slip_chance1.0=%s ticks per 12 cells" % ("PASS" if t_on and g and t_on > 1.3 * st.mean(g) else "UNMEASURED", res["RM_Glasswalk"], t_on), flush=True)
finally:
    calm()
    try: sc.teardown()
    except Exception as e: print("teardown", e)
    S.drop_map(mid, TILE, back=0)
