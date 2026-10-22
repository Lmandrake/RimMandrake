"""REACH MAP live proof (REACH_MAP_BUILD_WALLS_AND_DEPTH_AGREE; spec Transient/pile_2026-10-21/reachability_review.md §4
"De-risk first"; the debug_process rule: the functional script ships with the build item and grows with each live session).

  python.exe src/RimMandrake/FlowWorks/northstar/reach_map_proof.py [out.json] [--origin X,Z] [--fresh-map] [--only a,b]

Run from the repo root with python.exe; the bridge must be held. Exit 0 = every MEASURED row PASS; 1 = a FAIL; 2 = a row
could not be measured. Written offline 2026-10-21; first live 5/5 PASS 2026-10-22 (b5e399067a). REACH_THROTTLE_HOLDS
(WALL_REACH_TUNE_REBUILDS_TENFOLD) is owed its first live run.

Owner ruling this proves (2026-10-21 ~21:20 PDT, by card "3: the wall-aware reach map, kept per pawn class"): "Have to say
(3) and let's look carefully (make a note) to measure how often that bug case occurs."

THE BAR (every pair row): the pawn's full CanReach (vanilla + every FlowWorks postfix) == A* found, for the same walk its
pather would ask (ByPawn, the pit and swim offset grids), read by RM_WallReach.ProofReachPair "pawnId;x,z[;touch]":
  "REACHPAIR canReach=T|F found=T|F veto=T|F inScope=T|F cls=N band=K agree=T|F".
Each scene also asks the opposite pawn (the control) so a row cannot pass by everything reading False.

Scenes (plot coords from --origin, default 150,150; 60 x 50 cleared by validation_core.prepare_site; dig by
jawa/flowworks_excavation_drive, 8 notches = 4 m):
  W  base (6,4): drawbridge_proof's scene A without the bridge: trench x=1..4 at z=0, granite walls z=+-1 x=-2..9, caps
     (-3,0)/(10,0). Colonist far (7,0) -> the winch-side square (-2,0): the MEASURED failure (drawbridge_live_rerun4.json:
     the far pawn was offered the lower job). Control: a colonist at (-2,0) -> (0,0).          -> REACH_WINCH_SITE
  G  base (12,30): a walled compound (x=-7..-1, z=-7..7); its east wall x=-1 has the drawbridge GATE at (-1,0) and a plain
     gap at (-1,4); a second wall x=0 leaves only (0,0) (the hinge anchor) and (0,4); a moat x=1..4, z=-6..6, 4 m, with a
     steel drawbridge (0,0)-(5,0) lowered over it (hinge A, no winch). A hostile assault 45 east LOCKS the map, so the gate
     is shut to everyone (Building_DrawbridgeGate.PawnCanOpen). Colonist inside (-4,0) -> outside (8,0): vanilla walks the
     gap and the moat floor, the depth grid walks the gate square and the leaf; no single route.
     Control: after jawa/kill_hostiles and 70 ticks (unlocked), the same pair reads reachable.  -> REACH_LOCKED_GATE
  D  base (36,30): the same compound with a PLAYER door at (-1,0) (jawa/build_batch faction=player; spawn_batch leaves a
     door factionless and vanilla lets a wild animal open a factionless door) and an earth causeway at z=0 (the moat dug
     at x=1..4 except z=0). A wild Muffalo inside (-4,0) -> outside (8,0) (the player's door is shut to it, the gap ends at
     the moat). Control: a drafted colonist at (-4,1) -> (8,0) (opens the door).               -> REACH_ANIMAL_DOOR_TRENCH
  S  base (48,8): a deep-water ring (WaterDeep, Chebyshev 2..3) round an island; no dug square. A non-swimmer at (6,0) ->
     the island (0,0). The pawn is chosen by its class (cls has bit 16, RM_WallReachMath.NonSwimmer): a player Mech_Militor
     first (mechanoids sink), then a Colonist with humanlikesSwim set off (restored after); none qualifies -> UNMEASURED SITE. Control: none (no swimmer is guaranteed on every list).
                                                                                                -> REACH_NONSWIMMER_MOAT
Every pair is read after ticks(70): the 1.6 pathfinder reads walls/depth only when the map TICKS (GatherData, the
drawbridge_proof HARNESS note of 2026-10-22), and the reach map rebuilds at most once per 60 ticks.

Reads kept in the result (not bars): RM_PocketGrid.ProofPocketTiming (de-risk step 1: per-band rebuild ms, rebuilds per 1000
ticks, the wall-aware builds' ms) before and after the scenes, and RM_WallReach.ProofReach (queries, vetoes, the RESIDUAL
counter: path failures after a CanReach yes, by faction/class and suspect door) -> REACH_RESIDUAL_READ (PASS when it reads).

OWED (always UNMEASURED here): REACH_RESIDUAL_SOAK -- the owner's measurement proper: ProofReachReset, then a long soak on a
dug, walled colony on his full list (raids, animals, hauling), then ProofReach; the residual count per 1000 ticks is the
number he asked for.

ANTI-GUESSING NOTES
- A pair read with inScope=False means the veto never judged it (no dug square / no swim water it sinks in / a flyer): a
  scene staging fault, SITE, never a PASS.
- found comes from FindPathNow with the pather's own customizers; a pawn mid-job may carry canBashDoors from its job: the
  pawns here are fresh, drafted or wild, so the class reads as staged (cls is in every detail).
- REACH_WINCH_FIX_GHOST_ROAD_RETURNS (live 2026-10-22, run WITHOUT --fresh-map): on a reused map the (band, class) labelling
  already existed, and the walls staged here reached it only at the next GatherData, which 1.6 runs only on a tick some pawn
  asks for a path; ProofReachPair asks CanReach BEFORE its own A* (which gathers), so REACH_WINCH_SITE read canReach=True
  found=False. Fixed in the mod (RegionDirtyer walkability hook). A fresh map hid it: the first query built the labels.
- The gate shuts only while the map is LOCKED: FreeHostileCount(current|true) >= 1 is a precondition (SITE when not).
- WALL_REACH_TUNE_REBUILDS_TENFOLD (2026-10-22 residual soak: ~1000 wall-aware builds per 1000 ticks against the throttle's
  8 per 60): the bridge steps time with the game PAUSED (safe_advance / step_game_ticks: DoSingleTick inside a paused frame),
  and the paused-frame hook rebuilt every stale labelling unthrottled on every frame. Fixed in the mod (RM_WallReach.PausedFrame:
  a paused frame whose clock moved is throttled). REACH_THROTTLE_HOLDS reads builds over a quiet stepped window: the bar is
  entries x (ticks/60 + 2); steppedFrames must have moved (else the window was not stepped, or the DLL predates the fix).
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
UTILS = os.path.abspath(os.path.join(HERE, "..", "..", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)

REACH = "RimMandrake.FlowWorks.RM_WallReach"
POCKET = "RimMandrake.FlowWorks.RM_PocketGrid"
DPROOF = "RimMandrake.FlowWorks.Pits.RM_DrawbridgeProofs"
DB = "RimMandrake.FlowWorks.Pits.RM_Drawbridges"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
DEEP = 8
SETTLE = 70
NONSWIMMER_BIT = 16

ROW_IDS = ["REACH_WINCH_SITE", "REACH_LOCKED_GATE", "REACH_ANIMAL_DOOR_TRENCH", "REACH_NONSWIMMER_MOAT", "REACH_RESIDUAL_READ",
           "REACH_THROTTLE_HOLDS"]
QUIET = 600
OWED = {"REACH_RESIDUAL_SOAK": "the owner's residual measurement: ProofReachReset, a long soak on a dug walled colony on his "
                               "full list, then ProofReach; residual per 1000 ticks is the number"}
# The C# the rows call (selftest_reach_map_proof checks each exists in source and answers its word).
PROOFS = {
    (REACH, "ProofReachPair"): "REACHPAIR",
    (REACH, "ProofReach"): "WALLREACH",
    (REACH, "ProofReachReset"): "RESET",
    (REACH, "ProofReachForce"): "FORCE",
    (POCKET, "ProofPocketTiming"): "POCKETTIME",
    (DPROOF, "ProofMakeDrawbridge"): "DRAW",
}


# ============================================================================ verdicts (pure)
def parse(txt):
    kv = {}
    for tok in str(txt).split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            kv[k] = v
    return kv


def pair_verdict(subject, control=None, want_subject=False, want_control=True):
    """subject: the pair whose two halves lied before (expect canReach == found == want_subject, inScope True).
    control: the opposite pawn (expect canReach == found == want_control). UNMEASURED when a read is missing or the veto never
    judged the subject (a staging fault, never a pass)."""
    if not subject or "canReach" not in subject:
        return "UNMEASURED", "SITE"
    if subject.get("inScope") != "True":
        return "UNMEASURED", "SITE"
    if subject.get("found") != str(want_subject):
        return "UNMEASURED", "SITE"      # the scene does not cut (or open) the route as staged: A* is the referee
    ok = subject.get("canReach") == subject.get("found")
    if control is not None:
        if "canReach" not in control:
            return "UNMEASURED", "SITE"
        ok = ok and control.get("canReach") == control.get("found") == str(want_control)
    return ("PASS" if ok else "FAIL"), "MOD"


def throttle_verdict(kv0, kv1, ticks, min_ticks=60):
    """WALL_REACH_TUNE_REBUILDS_TENFOLD: two ProofReach reads round a quiet stepped window of `ticks`. The throttle allows each
    labelling one rebuild per min_ticks (+2 for the window's edges); more is the bug. UNMEASURED/HARNESS when a read is
    missing or steppedFrames never moved (no stepped frame seen: an old DLL or an unpaused window proves nothing);
    UNMEASURED/SITE when no build happened at all (nothing went stale, so a pre-fix DLL would pass it too)."""
    try:
        b0, b1 = int(kv0["builds"]), int(kv1["builds"])
        s0, s1 = int(kv0["steppedFrames"]), int(kv1["steppedFrames"])
        entries = max(int(kv0["entries"]), int(kv1["entries"]))
    except (KeyError, TypeError, ValueError):
        return "UNMEASURED", "HARNESS", None
    if s1 <= s0:
        return "UNMEASURED", "HARNESS", None
    if b1 <= b0:
        return "UNMEASURED", "SITE", None    # nothing went stale (no pawn pathed): the throttle was never tested
    bar = entries * (ticks // min_ticks + 2)
    return ("PASS" if b1 - b0 <= bar else "FAIL"), "MOD", {"builds": b1 - b0, "bar": bar, "entries": entries,
                                                            "steppedFrames": s1 - s0}


def has_bit(kv, bit):
    try:
        c = int(kv.get("cls"))
        return c >= 0 and (c & bit) != 0      # cls=-1: not in scope (live 2026-10-21: -1 read as every bit set)
    except (TypeError, ValueError):
        return False


def compound_walls(include_gate_square=False):
    """Scene G/D walls, relative to the scene base: the compound x=-7..-1, z=-7..7 (east wall x=-1 open at z=0 and z=4), and
    the second wall x=0, z=-6..6 open at z=0 and z=4."""
    cells = set()
    for x in range(-7, 0):
        cells.add((x, -7))
        cells.add((x, 7))
    for z in range(-7, 8):
        cells.add((-7, z))
        if z not in (0, 4) or (include_gate_square and z == 0):
            cells.add((-1, z))
    for z in range(-6, 7):
        if z not in (0, 4):
            cells.add((0, z))
    return sorted(cells)


def winch_walls():
    return sorted([(x, z) for x in range(-2, 10) for z in (-1, 1)] + [(-3, 0), (10, 0)])


def ring(c, r0, r1):
    """Chebyshev ring r0..r1 round c, as WaterDeep set_terrain_batch ops (one square each)."""
    out = []
    for dx in range(-r1, r1 + 1):
        for dz in range(-r1, r1 + 1):
            if r0 <= max(abs(dx), abs(dz)) <= r1:
                out.append((c[0] + dx, c[1] + dz))
    return out


# ============================================================================ live
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="150,150")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--only", default="")
    a = ap.parse_args(argv)
    only = [r for r in a.only.split(",") if r] or ROW_IDS
    import proof_hose as PH           # noqa: E402  (bridge-side imports only on a live run)
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "reach_map_proof_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "reach_map_proof.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}
    import driver_stamp
    driver_stamp.stamp(res, B.call)

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "detail": det})
        print("%-28s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:300]), flush=True)
        save()

    def static(ty, method, arg="-"):
        # HARNESS (live 2026-10-21): args="" makes static_call look for a 0-parameter overload ("No public static ProofReach
        # with 0 params"); the one-string-arg proofs need a non-empty arg, ignored by them.
        r = B.call("jawa/static_call", type=ty, method=method, args=arg) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        return (parse(txt) if r.get("success") is True and not txt.startswith("REFUSED") else {}), txt

    def pair(pid, c, touch=False):
        return static(REACH, "ProofReachPair", "%s;%d,%d%s" % (pid, c[0], c[1], ";touch" if touch else ""))

    def sset(f, v):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v)) or {"success": False}

    def sget(f):
        return (B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f) or {}).get("value")

    def dig(c, n=DEEP):
        return B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=-1) or {}

    def walls(cells):
        if cells:
            B.call("jawa/spawn_batch", ops=";".join("Wall:%d,%d" % c for c in cells), stuff="BlocksGranite")

    def spawn(c, kind="Colonist", faction="player", draft=False):
        r = B.call("jawa/spawn_pawn", kindDef=kind, x=c[0], z=c[1], faction=faction, count=1) or {}
        pid = ((r.get("pawns") or [{}])[0]).get("id")
        if pid and draft:
            B.call("jawa/set_draft", pawnId=pid, drafted=True)
        return pid

    def num_id(pid):
        """jawa/spawn_pawn answers 'Human41594'; the proofs take the thingIDNumber."""
        s = "".join(ch for ch in str(pid) if ch.isdigit())
        return s or str(pid)

    def ticks(n):
        r = B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}
        return r.get("success") is not False

    def hostile_faction():
        probe = B.call("jawa/spawn_pawn", kindDef="Mercenary_Gunner", x=0, z=0, faction="?", count=1, _answer=True) or {}
        avail = (probe.get("details") or {}).get("available") or []
        return next((f["def"] for f in avail if f.get("hostile") and str(f.get("def")).startswith("Pirate")),
                    next((f["def"] for f in avail if f.get("hostile") and f.get("def") not in ("Entities", "Mechanoid", "Insect")),
                         "Pirate"))

    ox, oz = (int(v) for v in a.origin.split(","))

    def at(base):
        return lambda dx, dz: (ox + base[0] + dx, oz + base[1] + dz)

    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    before = {"reachSeesWallsAndCliffs": sget("reachSeesWallsAndCliffs")}
    res["settings_before"] = before
    try:
        probe_kv, probe_txt = static(REACH, "ProofReach")
        if not probe_txt.startswith("WALLREACH"):
            for rid in only:
                row(rid, "UNMEASURED", "HARNESS", {"why": "the loaded FlowWorks predates RM_WallReach", "probe": probe_txt[:200]})
            return 2
        if not ok or not V.prepare_site(B, (ox, oz, 60, 50), rows, "REACH_site_ready"):
            row("REACH_site", "UNMEASURED", "SITE", {"why": "site not ready / not playing"})
            return 2
        if sset("reachSeesWallsAndCliffs", True).get("success") is False:
            row("REACH_settings", "UNMEASURED", "HARNESS", {"why": "mod_settings_field set refused"})
            return 2
        res["timing_before"] = static(POCKET, "ProofPocketTiming")[1]
        static(REACH, "ProofReachReset")

        if "REACH_WINCH_SITE" in only:
            P = at((6, 4))
            for i in range(1, 5):
                dig(P(i, 0))
            walls([P(*c) for c in winch_walls()])
            far = spawn(P(7, 0), draft=True)
            near = spawn(P(-2, 0), draft=True)
            ticks(SETTLE)
            s_kv, s_txt = pair(num_id(far), P(-2, 0))
            c_kv, c_txt = pair(num_id(near), P(0, 0))
            st, cls = pair_verdict(s_kv, c_kv)
            row("REACH_WINCH_SITE", st, cls, {"far": s_txt, "winchSide": c_txt})

        if "REACH_LOCKED_GATE" in only:
            P = at((12, 30))
            for x in range(1, 5):
                for z in range(-6, 7):
                    dig(P(x, z))
            walls([P(*c) for c in compound_walls()])
            dkv, dtxt = static(DPROOF, "ProofMakeDrawbridge", "%d,%d;%d,%d;steel;A" % (P(0, 0) + P(5, 0)))
            B.call("jawa/build_batch", ops="RM_DrawbridgeGate:%d,%d" % P(-1, 0), stuff="Steel", faction="player")
            col = spawn(P(-4, 0), draft=True)
            fac = hostile_faction()
            ids = [i for i in (spawn(P(45, k), kind="Mercenary_Gunner", faction=fac) for k in (0, 2)) if i]
            if ids:
                B.call("jawa/lord_assault_spawn", pawns=",".join(str(i) for i in ids))
            ticks(SETTLE)
            locked = (B.call("jawa/static_call", type=DB, method="FreeHostileCount", args="current|true") or {}).get("result")
            s_kv, s_txt = pair(num_id(col), P(8, 0))
            B.call("jawa/kill_hostiles")
            ticks(SETTLE)
            c_kv, c_txt = pair(num_id(col), P(8, 0))
            det = {"locked": s_txt, "unlocked": c_txt, "bridge": dtxt, "freeHostiles": locked}
            if dkv.get("ok") != "True" or str(locked) in ("None", "0"):
                row("REACH_LOCKED_GATE", "UNMEASURED", "SITE", dict(det, why="drawbridge not built or the map never locked"))
            else:
                st, cls = pair_verdict(s_kv, c_kv)
                row("REACH_LOCKED_GATE", st, cls, det)

        if "REACH_ANIMAL_DOOR_TRENCH" in only:
            P = at((36, 30))
            for x in range(1, 5):
                for z in range(-6, 7):
                    if z != 0:
                        dig(P(x, z))
            walls([P(*c) for c in compound_walls()])
            B.call("jawa/build_batch", ops="Door:%d,%d" % P(-1, 0), stuff="Steel", faction="player")
            muf = spawn(P(-4, 0), kind="Muffalo", faction="none")
            col = spawn(P(-4, 1), draft=True)
            ticks(SETTLE)
            s_kv, s_txt = pair(num_id(muf), P(8, 0))
            c_kv, c_txt = pair(num_id(col), P(8, 0))
            st, cls = pair_verdict(s_kv, c_kv)
            row("REACH_ANIMAL_DOOR_TRENCH", st, cls, {"wildMuffalo": s_txt, "colonist": c_txt})

        if "REACH_NONSWIMMER_MOAT" in only:
            P = at((48, 8))
            B.call("jawa/set_terrain_batch", ops=";".join("WaterDeep:%d,%d,1,1" % P(*c) for c in ring((0, 0), 2, 3)))
            tried = []
            chosen = None
            SWIM = "RimMandrake.FlowWorks.Swimming.RM_SwimSettings"
            hs = (B.call("jawa/mod_settings_field", typeName=SWIM, action="get", field="humanlikesSwim") or {}).get("value")
            # live 2026-10-21: a Colonist, a Muffalo and a Chicken all swim; RM_SwimMath.Classify sinks mechanoids
            # (mechanoidsSink) and, with humanlikesSwim off, humanlikes. A mech first, then a colonist with that setting off.
            for kind, fac, sink_humans in (("Mech_Militor", "player", False), ("Colonist", "player", True)):
                if sink_humans:
                    B.call("jawa/mod_settings_field", typeName=SWIM, action="set", field="humanlikesSwim", value="False")
                pid = spawn(P(6, 0), kind=kind, faction=fac, draft=(kind == "Colonist"))
                if not pid:
                    continue
                ticks(SETTLE)
                kv, txt = pair(num_id(pid), P(0, 0))
                tried.append({"kind": kind, "read": txt})
                if has_bit(kv, NONSWIMMER_BIT):
                    chosen = (kv, txt)
                    break
            if hs is not None:
                B.call("jawa/mod_settings_field", typeName=SWIM, action="set", field="humanlikesSwim", value=str(hs))
            if chosen is None:
                row("REACH_NONSWIMMER_MOAT", "UNMEASURED", "SITE", {"why": "no spawned pawn reads as a non-swimmer", "tried": tried})
            else:
                st, cls = pair_verdict(chosen[0])
                row("REACH_NONSWIMMER_MOAT", st, cls, {"nonSwimmer": chosen[1], "tried": tried})

        if "REACH_RESIDUAL_READ" in only:
            kv, txt = static(REACH, "ProofReach")
            row("REACH_RESIDUAL_READ", "PASS" if txt.startswith("WALLREACH") and "RESIDUAL fails=" in txt else "UNMEASURED",
                "MOD" if txt.startswith("WALLREACH") else "HARNESS", {"read": txt})
        if "REACH_THROTTLE_HOLDS" in only:
            ticks(SETTLE)                       # let the scenes' forced rebuilds land before the quiet window
            kv0, t0 = static(REACH, "ProofReach")
            stepped = ticks(QUIET)
            kv1, t1 = static(REACH, "ProofReach")
            st, cls, det = throttle_verdict(kv0, kv1, QUIET)
            row("REACH_THROTTLE_HOLDS", st, cls, {"before": t0, "after": t1, "window": QUIET, "stepped": stepped, "verdict": det})
        res["timing_after"] = static(POCKET, "ProofPocketTiming")[1]
        for rid, why in OWED.items():
            row(rid, "UNMEASURED", "OWED", {"why": why})
    finally:
        for f, v in before.items():
            if v is not None:
                sset(f, v)
        save()
    measured = [r for r in rows if r["class"] in ("MOD",)]
    if any(r["status"] == "FAIL" for r in measured):
        return 1
    return 0 if measured and all(r["status"] == "PASS" for r in measured) else 2


if __name__ == "__main__":
    sys.exit(main())
