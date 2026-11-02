"""SUMP_GLASSWALK_SPEED_RATIO_1 live clause A1: glasswalk's real speed against TileGranite, timed exactly.

Run under python.exe from the repo root (bridge held by the caller):
    python.exe "$(wslpath -w src/RimMandrake/TheSump/prove_glasswalk_speed.py)" < /dev/null
Exit 0 = A1 holds, 1 = it does not (or could not be measured).

Builds a one-cell lane in a roofed room on a throwaway map, then walks one colonist (ordered Goto = Jog urgency, glasswalk
slip OFF) over 12 cells of each floor, twice. The 2026-10-10 scene timed with scenelib.run(10), which plays at least
200 ms at speed 4 (~80 ticks a sample) against 120-200 tick walks; this one advances rimworld/step_game_ticks STEP ticks at
a time, so a crossing is placed within STEP ticks (per-cell error <= STEP/12).

A1 holds when the timed pawn IS a standard colonist (the item: "re-measure on a 13 ticks/cell pawn"):
  T = 60 / MoveSpeed within T_TOL of 13.04 (roofed, so no weather factor); any other pawn -> UNMEASURED, exit 1.
  The pawn is a Baseliner colonist picked from up to PICK_TRIES spawns until one lands in that band.
and, for that T:
  granite ticks/cell within TOL of T                       (the instrument sees the pawn's base cost)
  glass - granite ticks/cell within TOL of RM_Glasswalk pathCost 3   (the engine ADDS pathCost: test_glasswalk_speed_model.py)
  so a standard colonist (T = 13.04) gets 13.04 / 16.04 = 0.81, the spec's "~80%". The ratio at this pawn's T is printed.
"""
import os
import statistics as st
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
from scenes import scenelib as S  # noqa: E402

TILE = 114502
ST = "RimMandrake.EnvironmentalHazards.RM_EnvironmentalHazardsSettings"
PATH_COST = 3
STEP = 2            # ticks per exact step
TOL = 0.75          # ticks/cell
X0, X1 = 4, 16      # timed span: 12 cells, start/stop effects excluded
STANDARD_T = 60.0 / 4.6
T_TOL = 0.7         # ticks/cell: MoveSpeed 4.37..4.85 counts as "a 13 ticks/cell pawn"
PICK_TRIES = 6


def px(pid):
    r = S.call("jawa/pawn_get", pawn=pid)
    if not isinstance(r, dict):
        return None     # a text error is a blind reading, never a crash
    return ((r.get("pawns") or [{}])[0].get("position") or {}).get("x")


def move_speed(pid):
    r = S.call("jawa/pawn_stats", pawn=pid, stats="MoveSpeed")
    for row in (r.get("stats") or []) if isinstance(r, dict) else []:
        if row.get("defName") == "MoveSpeed":
            v = row.get("value")
            try:
                return float(v)
            except (TypeError, ValueError):
                return None
    return None


def step(n):
    return S.need(S.call("rimworld/step_game_ticks", ticks=n, timeoutMs=60000), "step_game_ticks")


def in_band(ms):
    return bool(ms) and abs(60.0 / ms - STANDARD_T) <= T_TOL


def pick_standard_pawn(sc):
    """Spawn Baseliner colonists at (1,1) (outside the timed span) until one has T within T_TOL of 13.04."""
    tried = []
    for _ in range(PICK_TRIES):
        pid = sc.colonist(1, 1)
        S.call("jawa/set_pawn_xenotype", pawnId=pid, xenotype="Baseliner", clearEndogenes=True)
        ms = move_speed(pid)
        tried.append(ms)
        if in_band(ms):
            return pid, tried
        sc.kill(pid)
    return None, tried


def judge(g, s, speeds):
    """Pure verdict. g, s: ticks/cell samples on granite and glass; speeds: MoveSpeed readings of the timed pawn.
    Returns (exit code, RESULT line). UNMEASURED unless the pawn is a ~13 ticks/cell pawn and both floors have 2 samples."""
    ms = [v for v in speeds if v]
    if len(g) < 2 or len(s) < 2 or not ms or len(ms) != len(speeds):
        return 1, "RESULT SUMP_GLASSWALK_SPEED_RATIO_1/A1 UNMEASURED granite=%s glass=%s MoveSpeed=%s" % (g, s, speeds)
    T = 60.0 / st.mean(ms)
    if not all(in_band(v) for v in ms):
        return 1, ("RESULT SUMP_GLASSWALK_SPEED_RATIO_1/A1 UNMEASURED pawn T=%.2f ticks/cell (MoveSpeed=%s) is not a "
                   "13 ticks/cell pawn (|T-%.2f|<=%.2f required)" % (T, speeds, STANDARD_T, T_TOL))
    gm, sm = st.mean(g), st.mean(s)
    delta = sm - gm
    # Every sample, not only the means: an average can hide two wrong walks ([10, 16] means 13).
    ok_base = abs(gm - T) <= TOL and all(abs(v - T) <= TOL for v in g)
    ok_add = abs(delta - PATH_COST) <= TOL and all(abs(v - (T + PATH_COST)) <= TOL for v in s)
    verdict = 0 if (ok_base and ok_add) else 1
    return verdict, ("RESULT SUMP_GLASSWALK_SPEED_RATIO_1/A1 %s T=%.2f granite=%.2f (|g-T|<=%.2f: %s) glass=%.2f "
                     "delta=%.2f (|delta-%d|<=%.2f: %s) ratio=%.3f law=%.3f"
                     % ("PASS" if verdict == 0 else "FAIL", T, gm, TOL, ok_base, sm, delta, PATH_COST, TOL, ok_add,
                        gm / sm, T / (T + PATH_COST)))


def walk_exact(sc, pid):
    """Walk from the lane's west end to its east end; return ticks spent between x>=X0 and x>=X1 (exact steps)."""
    S.call("jawa/ordered_job", pawnId=pid, jobDef="Goto", targetAX=sc.x + 1, targetAZ=sc.z + 1, waitTicks=1)
    for _ in range(80):
        step(20)
        x = px(pid)
        if x is not None and x <= sc.x + 1:
            break
    step(20)
    S.call("jawa/kill_hostiles")
    S.call("jawa/ordered_job", pawnId=pid, jobDef="Goto", targetAX=sc.x + 18, targetAZ=sc.z + 1, waitTicks=1)
    t, ta = 0, None
    while t < 1200:
        step(STEP)
        t += STEP
        x = px(pid)
        if x is None:
            return None     # a blind step could hide a crossing: the walk is unmeasured, never skipped
        if ta is None and x >= sc.x + X0:
            ta = t
        if ta is not None and x >= sc.x + X1:
            return t - ta
    return None


def main():
    S.call("jawa/set_game_speed", speed=0)
    mid = S.biome_map(TILE, "RM_GreySea", surface_biome="RM_GreySea")
    sc = None
    verdict = 1
    try:
        sc = S.Scene("glass", 40, 60, 20, 4)
        sc.__enter__()
        sc.room(roof=True)
        S.call("jawa/spawn_batch", ops=";".join("Wall:%d,%d" % (sc.x + dx, sc.z + 2) for dx in range(0, 20)),
               stuff="BlocksGranite")
        pid, tried = pick_standard_pawn(sc)
        print("picked", pid, "MoveSpeed tries", tried, flush=True)
        if pid is None:
            print("RESULT SUMP_GLASSWALK_SPEED_RATIO_1/A1 UNMEASURED no 13 ticks/cell colonist in %d spawns: MoveSpeed=%s"
                  % (PICK_TRIES, tried))
            return 1
        S.call("jawa/pawn_need", pawn=pid, action="need", need="Mood", level=1.0)
        res = {"TileGranite": [], "RM_Glasswalk": []}
        speeds = []
        with S.setting(ST, glasswalkSlipEnabled="False"):
            for rep in range(2):
                for terr in ("TileGranite", "RM_Glasswalk"):
                    sc.floor(terr, (1, 1, 18, 1))
                    S.call("jawa/map_commit", full=True)
                    ms = move_speed(pid)
                    speeds.append(ms)
                    w = walk_exact(sc, pid)
                    res[terr].append(w)
                    print(rep, terr, "ticks/12 cells =", w, "MoveSpeed =", ms, flush=True)
        g = [w / float(X1 - X0) for w in res["TileGranite"] if w]
        s = [w / float(X1 - X0) for w in res["RM_Glasswalk"] if w]
        verdict, line = judge(g, s, speeds)
        print(line, flush=True)
    finally:
        try:
            S.call("jawa/set_game_speed", speed=0)
            if sc is not None:
                sc.teardown()
        except Exception as e:
            print("teardown", e)
        S.drop_map(mid, TILE, back=0)
    return verdict


if __name__ == "__main__":
    sys.exit(main())
