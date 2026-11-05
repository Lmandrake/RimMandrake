"""SUMP_GLASSWALK_SPEED_RATIO_1 live clause A1: glasswalk's real speed against TileGranite, timed exactly.

Run under python.exe from the repo root (bridge held by the caller):
    python.exe "$(wslpath -w src/RimMandrake/TheSump/prove_glasswalk_speed.py)" < /dev/null
Exit 0 = A1 holds, 1 = it does not (or could not be measured).

Builds a one-cell lane in a roofed room on a throwaway map, lit by TorchLamps (every lane cell glow >= LIT before every
walk, else UNMEASURED: in the dark Core's MoveSpeed StatPart_Glow slows every colonist x0.80), then walks one colonist (ordered Goto = Jog urgency, glasswalk
slip OFF) over 12 cells of each floor, twice. The 2026-10-10 scene timed with scenelib.run(10), which plays at least
200 ms at speed 4 (~80 ticks a sample) against 120-200 tick walks; this one advances rimworld/step_game_ticks STEP ticks at
a time and times by the game's own ticksGame, so a crossing is placed within STEP ticks (per-cell error <= STEP/12);
a step that does not advance ticksGame by exactly STEP (a free-running game, a truncated step) is UNMEASURED.

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
SPEED_DRIFT = 0.05  # cells/s: the timed pawn's MoveSpeed must hold across walks (live 2026-11-04: 4.416 on every read)
LAMPS = (2, 7, 12, 17)  # TorchLamps in the lane's north wall row: a roofed room is otherwise dark
LIT = 0.30          # Core MoveSpeed StatPart_Glow: x0.80 at glow 0 rising to x1.00 at 0.30. Live 2026-11-03 the unlit
                    # room read "Multiplier for light 0%: x80%" (jawa/stat_explain) and every colonist was 3.5-3.7 c/s.


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


def clock():
    """The game's own ticksGame (jawa/time_clock), or None on a blind read. Live 2026-11-04 the proof counted the ticks it
    REQUESTED while the game clock ran between bridge calls: walks read 2 and 26 ticks for 12 cells (T=13.6 needs ~163)."""
    r = S.call("jawa/time_clock")
    v = r.get("ticksGame") if isinstance(r, dict) else None
    return v if isinstance(v, int) and not isinstance(v, bool) else None


WHY = {"walk": None}    # why the last walk_exact returned None (printed by main)


def in_band(ms):
    return bool(ms) and abs(60.0 / ms - STANDARD_T) <= T_TOL


def light_lane(sc):
    """Wall the lane's north side, with TorchLamps (refuelled) instead of walls at LAMPS."""
    S.call("jawa/spawn_batch", ops=";".join("Wall:%d,%d" % (sc.x + dx, sc.z + 2) for dx in range(0, 20) if dx not in LAMPS),
           stuff="BlocksGranite")
    S.call("jawa/spawn_batch", ops=";".join("TorchLamp:%d,%d" % (sc.x + dx, sc.z + 2) for dx in LAMPS))
    r = S.call("jawa/list_things", defName="TorchLamp", rect=sc.rect)
    for t in ((r.get("things") if isinstance(r, dict) else None) or []):
        S.call("jawa/thing_refuel", thingId=t["id"], amount=100)


def lane_dark(sc):
    """None when every lane cell (x+1..x+18, z+1) reads groundGlow >= LIT; else the readings (a blind read is dark)."""
    r = S.call("jawa/glow_at", rect="%d,%d,%d,%d" % (sc.x + 1, sc.z + 1, 18, 1))
    cells = (r.get("cells") if isinstance(r, dict) else None) or []
    glows = [c.get("groundGlow") for c in cells]
    ok = len(glows) == 18 and all(isinstance(v, (int, float)) and v >= LIT for v in glows)
    return None if ok else glows


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
    if max(ms) - min(ms) > SPEED_DRIFT:
        # each walk is judged against ONE T: a pawn whose speed moved between walks (granite at T 12.35, glass at 13.73,
        # both in band) would read a delta that is not the floor's (GPT review gen11)
        return 1, ("RESULT SUMP_GLASSWALK_SPEED_RATIO_1/A1 UNMEASURED pawn MoveSpeed drifted between walks %s (> %.2f)"
                   % (speeds, SPEED_DRIFT))
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
    WHY["walk"] = None
    t0 = clock()
    if t0 is None:
        WHY["walk"] = "blind ticksGame read before the walk"
        return None
    x = px(pid)
    if clock() != t0 or x is None or x >= sc.x + X0:
        # ticks that ran before t0 (a burst during the Goto order) may have carried the pawn into the span: the crossing
        # of X0 would be missed and the walk undercounted
        WHY["walk"] = "pawn not seen west of the span on a still clock at timing start (x=%s, ticksGame %s)" % (x, t0)
        return None
    prev, ta = t0, None
    while prev - t0 < 1200:
        step(STEP)
        now = clock()
        # Exact or nothing: a step must advance the game's own clock by exactly STEP (a free-running game or a truncated
        # step moves the pawn for ticks nobody counted), and the clock must not move while the position is read.
        if now is None or now - prev != STEP:
            WHY["walk"] = "clock not exact: step of %d advanced ticksGame %s -> %s (game running or step truncated)" % (
                STEP, prev, now)
            return None
        x = px(pid)
        after = clock()
        if after != now:
            WHY["walk"] = "clock moved during the position read: ticksGame %s -> %s (game running)" % (now, after)
            return None
        if x is None:
            WHY["walk"] = "blind position read"
            return None     # a blind step could hide a crossing: the walk is unmeasured, never skipped
        t, prev = now - t0, now
        if ta is None and x >= sc.x + X0:
            ta = t
        if ta is not None and x >= sc.x + X1:
            return t - ta
    WHY["walk"] = "pawn did not cross the timed span in 1200 ticks"
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
        light_lane(sc)
        S.call("jawa/map_commit", full=True)
        dark = lane_dark(sc)
        if dark is not None:
            print("RESULT SUMP_GLASSWALK_SPEED_RATIO_1/A1 UNMEASURED lane not lit (glow < %.2f slows every colonist "
                  "x0.80): %s" % (LIT, dark))
            return 1
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
                    dark = lane_dark(sc)
                    if dark is not None:
                        print("RESULT SUMP_GLASSWALK_SPEED_RATIO_1/A1 UNMEASURED lane went dark before walk %d %s: %s"
                              % (rep, terr, dark))
                        return 1
                    ms = move_speed(pid)
                    speeds.append(ms)
                    w = walk_exact(sc, pid)
                    speeds.append(move_speed(pid))  # after the walk too: a change during it reaches the drift gate
                    res[terr].append(w)
                    print(rep, terr, "ticks/12 cells =", w, "MoveSpeed =", ms, flush=True)
                    if w is None:
                        print("RESULT SUMP_GLASSWALK_SPEED_RATIO_1/A1 UNMEASURED walk %d %s: %s" % (rep, terr, WHY["walk"]))
                        return 1
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
