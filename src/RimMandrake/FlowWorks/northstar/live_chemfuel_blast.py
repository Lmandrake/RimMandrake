#!/usr/bin/env python3
"""Live proof: lit chemfuel is an explosion that knocks back (RIMMANDRAKE_PROVE_LIT_CHEMFUEL_BLAST_THROWS_WITH_KNOCKBACK,
owner 2026-11-25).

Offline, FuelFire_chemfuel_ignition_blast_once_sized_like_a_vanilla_stack (selftest_flowworks_stock.py --only FuelFire_*)
proves the rule: an Inferno body (chemfuel, propane) that first lights fires ONE flame GenExplosion.DoExplosion, radius by
vanilla's own chemfuel stack rule (Chemfuel CompProperties_Explosive: 1.1 + sqrt((items-1) x 0.037), items = litres / 200,
capped at its stackLimit 150 -> 3.448). This script proves the running game throws pawns with it through ExplosiveKnockback
(EK). Needs the explosiveknockback_visit tier (FlowWorks + EK). Scene, relative to --origin (ox, oz):

  pit     3x3, x=ox..ox+2, z=oz-1..oz+1, dug 4 notches (2 m) and filled with 2 m of RM_Fluid_Chemfuel
          (36 levels = 360,000 dL = 180 items -> the 150 cap -> r 3.448)
  light   the pit's east-middle square (ox+2, oz): the blast centre
  pawns   three drafted player colonists on dry ground, each on its own ray from the centre so no flight meets another:
            inside  (ox+3, oz)    d=1, east    (d/r 0.29: EK's force throws a 60 kg pawn at d/r <~ 0.77)
            edge    (ox+2, oz+3)  d=3, north   (inside r but near its rim, d/r 0.87)
            outside (ox+2, oz-5)  d=5, south   (beyond r)

Rows (each reads the EK journal, RM_KnockbackProof.Journal, and the pawn's square before and after):

  A1 inside   EK journals a launch for it from this blast and it lands >= 1 square farther from the centre;
  A2 edge     the blast reaches it (an EK row from this blast) and EK throws it no farther than the inside pawn (falloff);
              the flame sets it alight and a burning pawn runs about by itself, so its own walk is recorded, not judged;
  A3 outside  no EK row from this blast and it has not moved.

Can-see for all three: RM_LiquidFireProof.ProofIgnitionBlasts shows exactly one blast, fired, at the lit square with the
expected radius; no blast is a FAIL of the mod (the lit body should have exploded), a failed read is UNMEASURED.

    python3 live_chemfuel_blast.py [--origin 120,150] [--ticks 180]

Before it spawns, it vanishes every pawn (any faction) on its site plus SQUAT_MARGIN and reads back none; at the end it vanishes
its own three while another colonist stays on the map, so a rerun at the same origin starts clean.

Exit 0 when all three hold, 1 when one fails, 2 when it could not measure. Settings it touches are restored.
"""
import argparse
import json
import math
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
for p in (HERE, UTILS):
    if p not in sys.path:
        sys.path.insert(0, p)

FIRE = "RimMandrake.FlowWorks.RM_LiquidFireProof"
FILL = "RimMandrake.FlowWorks.RM_FluidIdentityProof"
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
EK = "RimMandrake.ExplosiveKnockback.RM_KnockbackProof"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
# The live proof runs under Windows python.exe (WSL cannot reach the bridge on Windows loopback); same folder either way.
OUT = (("D:/" if os.name == "nt" else "/mnt/d/") + "ClaudeWork/rimmandrake/scratch/chemfuel_blast/live")
CHEMFUEL = "RM_Fluid_Chemfuel"
DEPTH_LEVELS, FILL_M = 4, 2.0          # 4 notches x 0.5 m = 2 m, filled to the brim (RM_LevelSolve.U = 1 level = 0.5 m)
SETTINGS = {"canalFireEnabled": True, "chemfuelIgnitionBlastEnabled": True, "rainDousesLiquidFireEnabled": False}
# Vanilla's Chemfuel ThingDef (its CompProperties_Explosive radius and expand, its stackLimit) and RM_Liquid_Chemfuel's bottle (200 L):
R0, EXPAND, MAX_ITEMS, DL_PER_ITEM = 1.1, 0.037, 150, 2000
R_TOL = 0.01                           # Report prints the radius to 2 decimals (F2)
FIRE_CHECK_TICKS = 30   # RM_FireMath.FireCheckIntervalTicks: the fire state is read once per this many ticks
# The blast burns and throws the colonists by design: the governor's hurt/downed latch is waived for the ticks after the
# light only (the narrowing pit_exposure_raised_ladder_live.py uses); a modal, a clock jump or the colony lost still stop.
BLAST_STOP_ON = "clock_discontinuity,modal_stuck,colony_loss,cancel"
# A pawn left on the site by an earlier run stood in the inside pawn's flight lane and EK blocked the launch ("blocked, stop:
# Pawn"), and one sharing the outside pawn's square walked it off by one (live 2026-11-27 01:14, ArchBig): destroy_batch never
# removes pawns and remove_intruders never matches colonists, so the scene vanishes every pawn on its site plus this margin.
SQUAT_MARGIN = 3    # squares: a burning pawn runs about (A2's walk was 5.6 squares in 180 ticks, live 2026-11-27 01:08)
TRACE_STEP = 20     # ticks between position reads: a colonist walks ~4.6 squares/s = ~1.5 squares in 20 ticks
                    # (Human MoveSpeed 4.6, Races_Humanlike.xml)


# ============================================================================ pure (selftest_live_chemfuel_blast.py)
def expected_radius(body_dl):
    """The offline rule's radius for a body of body_dl decilitres (RM_FuelFireMath.IgnitionBlastRadius, Inferno, first light)."""
    items = min(MAX_ITEMS, max(1, body_dl // DL_PER_ITEM))
    return R0 + math.sqrt((items - 1) * EXPAND)


def parse_blasts(txt):
    """ "IGNITIONBLASTS 122,150 r=3.45 t=900 fired ..." -> [{"x","z","r","t","fired"}] or None when not that reply."""
    if not txt or not txt.startswith("IGNITIONBLASTS"):
        return None
    return [{"x": int(m.group(1)), "z": int(m.group(2)), "r": float(m.group(3)), "t": int(m.group(4)),
             "fired": m.group(5) == "fired"}
            for m in re.finditer(r"(-?\d+),(-?\d+) r=([\d.]+) t=(-?\d+) (fired|queued)", txt)]


def parse_journal(txt):
    """EK journal text, one JSON object a line -> list of dicts (junk lines dropped)."""
    out = []
    for ln in (txt or "").splitlines():
        ln = ln.strip()
        if ln.startswith("{"):
            try:
                out.append(json.loads(ln))
            except ValueError:
                pass
    return out


def v_blast(blasts, lit, r_want):
    """Can-see: exactly one blast, fired, at the lit square, radius r_want. -> (status, detail)."""
    if blasts is None:
        return "UNMEASURED", {"why": "ProofIgnitionBlasts read failed"}
    mine = [b for b in blasts if (b["x"], b["z"]) == tuple(lit)]
    ok = (len(blasts) == 1 and len(mine) == 1 and mine[0]["fired"] and abs(mine[0]["r"] - r_want) <= R_TOL)
    return ("PASS" if ok else "FAIL"), {"blasts": blasts, "rWant": round(r_want, 3), "rTol": R_TOL}


def blast_exps(rows, lit):
    """EK explosion ids whose request rows are centred on the lit square."""
    return {r.get("exp") for r in rows if r.get("type") == "request" and r.get("centre") == list(lit)}


def squatters(pawn_rows, rect, margin=SQUAT_MARGIN):
    """Ids of live, spawned pawns of ANY faction standing on rect (x, z, w, h) widened by margin: an earlier run's colonists
    included, which no site sweep matches."""
    rx, rz, rw, rh = rect
    return sorted(r["id"] for r in pawn_rows
                  if not r.get("dead") and r.get("spawned", True) and r.get("x") is not None and r.get("z") is not None
                  and rx - margin <= r["x"] < rx + rw + margin and rz - margin <= r["z"] < rz + rh + margin)


def own_to_remove(pawn_rows, own_ids):
    """The scene's own pawns to vanish at the end: all of them while another live colonist stays on the map, else none
    (the sweep can take the map's starting colonists, and a map left with no colonist ends the colony; the next run's sweep
    clears what stays)."""
    own = set(own_ids)
    others = [r for r in pawn_rows if r.get("id") not in own and r.get("isPlayer") and r.get("intelligence") == "Humanlike"
              and not r.get("dead") and r.get("spawned", True)]
    return sorted(own) if others else []


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def thrown(mine, lit):
    """EK's own throw for one pawn: the sum over its launch rows of (|to - centre| - |from - centre|), 0.0 with none.
    A burning pawn runs about on its own (vanilla's fire response, drafted or not), so its square after the ticks mixes
    walking with the throw; this reads only what EK launched."""
    t = 0.0
    for r in mine:
        if r.get("type") == "launch" and r.get("from") and r.get("to"):
            t += dist(r["to"], lit) - dist(r["from"], lit)
    return t


def v_pawn(role, pid, start, end, rows, exps, lit, inside_throw=None):
    """One pawn's row. start/end are (x, z) or None; rows the parsed journal; exps this blast's EK ids.
    inside: a launch row and it lands >= 1 square farther from the centre (EK's land row, else its square after);
    edge: an EK row from this blast and EK threw it no farther than the inside pawn (falloff); its own walking is recorded
    as "walk", not judged; outside: no row from this blast and no move."""
    if start is None or end is None or None in start or None in end:
        return "UNMEASURED", {"why": "%s position read failed" % role, "start": start, "end": end}
    mine = [r for r in rows if r.get("thing") == pid and r.get("exp") in exps]
    land = [r for r in rows if r.get("thing") == pid and r.get("type") == "land" and r.get("at")]
    walk = dist(end, lit) - dist(start, lit)
    if land and role == "inside":
        end = tuple(land[-1]["at"])
    gain = dist(end, lit) - dist(start, lit)
    det = {"pid": pid, "start": start, "end": end, "gain": round(gain, 2), "throw": round(thrown(mine, lit), 2),
           "walk": round(walk, 2), "rows": [r.get("type") for r in mine],
           "skips": [r.get("reason") for r in mine if r.get("type") == "skip"]}
    if role == "inside":
        ok = any(r.get("type") == "launch" for r in mine) and gain >= 1.0
    elif role == "edge":
        if inside_throw is None:
            return "UNMEASURED", dict(det, why="no inside reading to compare with")
        ok = bool(mine) and thrown(mine, lit) <= inside_throw + 1e-6
        det["insideThrow"] = round(inside_throw, 2)
    else:
        ok = not mine and tuple(start) == tuple(end)
    return ("PASS" if ok else "FAIL"), det


# ============================================================================ live
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--origin", default="120,150")
    ap.add_argument("--ticks", type=int, default=180, help="ticks after the light for flights to land (3 s)")
    ap.add_argument("--out-dir", default=OUT)
    a = ap.parse_args(argv)
    import validation_core as V
    B = V.Bridge()
    os.makedirs(a.out_dir, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    res = {"script": "live_chemfuel_blast.py", "started": stamp, "rows": {}, "log": []}

    def save():
        with open(os.path.join(a.out_dir, "result_%s.json" % stamp), "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)

    def sc(typ, method, arg=""):
        r = B.call("jawa/static_call", type=typ, method=method, args=arg) or {}
        txt = str(r.get("result") if r.get("result") is not None else "")
        res["log"].append([method, arg, txt[:300]])
        return txt if r.get("success") and not txt.startswith("REFUSED") else None

    def sget(f):
        return (B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f) or {}).get("value")

    def sset(f, v):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))

    def where(pid):
        r = B.call("jawa/pawn_get", pawn=pid) or {}
        q = ((r.get("pawns") or [{}])[0]).get("position") or {}
        return (q.get("x"), q.get("z")) if q else None

    def unmeasured(why):
        res["rows"]["site"] = {"status": "UNMEASURED", "why": why}
        print("UNMEASURED: %s" % why)
        return 2

    ox, oz = (int(v) for v in a.origin.split(","))
    pit = [(ox + i, oz + j) for i in range(3) for j in (-1, 0, 1)]
    lit = (ox + 2, oz)
    places = {"inside": (ox + 3, oz), "edge": (ox + 2, oz + 3), "outside": (ox + 2, oz - 5)}
    site = (ox - 2, oz - 7, 13, 14)
    saved = {}
    pids = {}
    H = V._helpers()
    if (B.call("rimworld/get_ui_state") or {}).get("programState") != "Playing":
        print("UNMEASURED: the game is not Playing")
        return 2
    try:
        B.call("rimworld/pause_game", pause=True)
        B.call("jawa/kill_hostiles")
        for f in SETTINGS:
            saved[f] = sget(f)
        res["settingsBefore"] = saved
        # A run before this one leaves its channel fire in the map's fire state, and ProofResetRect empties the pit without
        # touching it: a refill read as still burning and never lit fresh (live 2026-11-27, "FIRE burning 9" on the light,
        # no blast). Fire off for one check makes RM_LiquidFire.Tick ExtinguishAll the whole map's fire state.
        sset("canalFireEnabled", False)
        B.ticks(FIRE_CHECK_TICKS + 1)
        for f, v in SETTINGS.items():
            sset(f, v)
        sc(NSP, "ProofResetRect", "%d;%d;%d;%d" % site)
        rows = []
        if not V.prepare_site(B, site, rows, "CFB_site"):
            return unmeasured("site not ready: %s" % rows[:2])
        B.call("rimworld/pause_game", pause=True)
        for x, z in pit:
            r = B.call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=DEPTH_LEVELS, setBodyWaterM=0.0) or {}
            if not r.get("success"):
                return unmeasured("dig (%d,%d) refused: %r" % (x, z, str(r)[:160]))
        for x, z in pit:
            if not (sc(FILL, "ProofFillWithFluid", "%d,%d,%s,%s" % (x, z, FILL_M, CHEMFUEL)) or "").startswith("FILLED"):
                return unmeasured("chemfuel fill (%d,%d) refused" % (x, z))
        body = sum((B.call("jawa/flowworks_excavation_report", x=x, z=z) or {}).get("waterDl") or 0 for x, z in pit)
        res["bodyDl"] = body
        if body < DL_PER_ITEM:
            return unmeasured("the pit holds %d dL, under one item" % body)
        r_want = expected_radius(body)
        cold = sc(FIRE, "ProofReport", "x") or ""
        if not cold.startswith("FIRE burning 0 | front pending 0"):
            return unmeasured("the map holds fire before the light (%r): a fresh light is not testable" % cold[:120])
        squat = squatters(H.read_pawns(B, health=False), site)
        if squat:
            H._kill_ids(B, set(squat), "cfb_squatters", lambda x: True, action="vanish")
        left = squatters(H.read_pawns(B, health=False), site)
        res["squatters"] = {"vanished": squat, "left": left}
        if left:
            return unmeasured("pawns still on the site after the sweep: %s" % left)
        for role, c in places.items():
            got = B.call("jawa/spawn_pawn", kindDef="Colonist", x=c[0], z=c[1], faction="player", count=1) or {}
            pid = ((got.get("pawns") or [{}])[0]).get("id")
            if not pid:
                return unmeasured("%s colonist did not spawn: %r" % (role, str(got)[:160]))
            res.setdefault("draft", {})[role] = B.call("jawa/set_draft", pawnId=pid, drafted=True)
            pids[role] = pid
        start = {role: where(pid) for role, pid in pids.items()}
        res["pawns"] = {"ids": pids, "start": start}
        if sc(EK, "Clear", "x") is None:
            return unmeasured("EK journal clear refused: is ExplosiveKnockback loaded?")
        litr = sc(FIRE, "ProofIgnite", "%d,%d" % lit)
        if not litr or not litr.startswith("LIT"):
            return unmeasured("the pit did not light: %r" % res["log"][-1])
        blast = v_blast(parse_blasts(sc(FIRE, "ProofIgnitionBlasts", "x")), lit, r_want)
        trace = [[0, {role: where(pid) for role, pid in pids.items()}]]
        prior, B.stop_on = B.stop_on, BLAST_STOP_ON
        try:
            for t in range(TRACE_STEP, a.ticks + 1, TRACE_STEP):     # a walk moves ~1 square a step, a flight jumps
                B.ticks(TRACE_STEP)
                trace.append([t, {role: where(pid) for role, pid in pids.items()}])
        finally:
            B.stop_on = prior
        res["trace"] = trace
        end = dict(trace[-1][1])
        jr = parse_journal(sc(EK, "Journal", "4000"))
        exps = blast_exps(jr, lit)
        res.update(blast=blast, end=end, journalRows=len(jr), journal=jr, exps=sorted(e for e in exps if e is not None))
        print("blast %s %s" % (blast[0], json.dumps(blast[1], default=str)[:300]))
        verdicts = {}
        verdicts["A1"] = v_pawn("inside", pids["inside"], start["inside"], end["inside"], jr, exps, lit)
        throw_in = verdicts["A1"][1].get("throw")
        verdicts["A2"] = v_pawn("edge", pids["edge"], start["edge"], end["edge"], jr, exps, lit, throw_in)
        verdicts["A3"] = v_pawn("outside", pids["outside"], start["outside"], end["outside"], jr, exps, lit)
        if blast[0] != "PASS":
            verdicts = {k: (blast[0], dict(d, why="the can-see blast row is %s" % blast[0], own=s))
                        for k, (s, d) in verdicts.items()}
        for k, (st, det) in sorted(verdicts.items()):
            res["rows"][k] = {"status": st, "detail": det}
            print("%s %s %s" % (k, st, json.dumps(det, default=str)[:400]))
        sts = [st for st, _ in verdicts.values()]
        return 0 if all(s == "PASS" for s in sts) else (1 if "FAIL" in sts else 2)
    finally:
        if pids:    # the next run finds a clean site (an earlier run's colonists blocked its lanes)
            try:
                gone = own_to_remove(H.read_pawns(B, health=False), pids.values())
                res["ownPawnsVanished"] = gone
                if gone:
                    H._kill_ids(B, set(gone), "cfb_own_pawns", lambda x: True, action="vanish")
            except Exception as ex:  # noqa: BLE001 - the next run's sweep still clears them; the verdict stands
                res["ownPawnsLeft"] = repr(ex)
        for f, v in saved.items():
            if v is not None:
                sset(f, v)
        save()
        print("result: %s" % os.path.join(a.out_dir, "result_%s.json" % stamp))


if __name__ == "__main__":
    sys.exit(main())
