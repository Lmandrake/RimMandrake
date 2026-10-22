"""FlowWorks liquid live checks L7 (WATER_LEVELSET_SOLVE: review-map stations 1-2 settle flat, no 1,0,1 stripe, no deep blob
beside dry ground; run on the review map with --only L7, NEVER with --fresh-map), L2 (Dump drains: slow without a pump, fast with a pump on Pour), L4 (a ship/cargo tank on Fill
loads from our tank over a hose, then on Empty unloads), L5 (a capped Outflow hose spills its held liquid as filth at the open
end; a colonist cleans it) and L6 (liquid theft: a witness catches our Fill tank drawing a neutral faction's tank; the free end
names the faction; --theft-day: goodwill falls).

  python.exe src/RimMandrake/FlowWorks/northstar/liquid_checks.py [out.json] [--only L2,L4,L5,L6] [--fresh-map] [--theft-day]

L4/L5 PORTED 2026-10-16 from the Transient copy, which still staged filltank 100 (= 10 L since the litres re-base, a hundredth
of one level): L2/L4 then moved nothing and read as MOD FAILs (bench_live_20261016b). Every staging here is in tank units
(decilitres): FILL_UNITS, LEVEL. L5's 2026-10-16 FAIL (10,000 units spilled, 0 filth) was a MOD bug: RM_Filth_LiquidSpill's
placementMask Natural is refused on every natural terrain (SPILL_FILTH_FIX_SOIL_SAYS_NO); the row now also reads
RM_LiquidSpill.Unplaced, so a refused spill names itself instead of hiding behind the spilled-units count.
The re-run after that fix (bench_live_20261016b, filth [1,1], spilled 1 -> 10001, unplaced 0 -> 0) was a HARNESS FAIL: the row
counted filth THINGS, but vanilla FilthMaker.TryMakeFilth THICKENS the filth already on the cell (thickness < 5) instead of
spawning a second one, and the 1-unit spill during the Outflow phase had already laid that filth. 10,000 units = 3 pieces
(litresPerFilth 400 L = 4,000 units) = thickness 1 -> 4 on one thing. The row now sums RM_Filth_LiquidSpill THICKNESS in the
rect (read from Filth.Label, "{label} x{thickness}") and wants it to rise by exactly FilthCount(spilled, unitsPerFilth).

Promoted out of Transient/bench_live_20261011/fw_live_checks.py (debug_process.md: the checks that found real bugs persist).
Run from the repo root with python.exe, bridge held; map = a 250x250 FlowWorks-tier quicktest. Exit 0 = every row PASS.
Rows {id, status PASS|FAIL|UNMEASURED, class MOD|SITE|HARNESS, detail}; "could not ask" is UNMEASURED, never PASS.

WHY L6 IS TIMED (THEFT_ROW_REPAIR_WITNESS_WALKS_OFF, 2026-10-12): RM_LiquidTheft.TheftTick runs at TicksGame % 250 == 7. A lordless
neutral villager spawned at the start of a 1,000-tick watch WALKS OFF long before the first check, so the old row read
caught 0 -> 0 whatever the mod did (a probe that spawned the witness 3 ticks before the check read 0 -> 1 and the letter). So
here the witness is spawned at TicksGame % 250 == WITNESS_PHASE (3 ticks before the check), its position is read AT the check, and
a witness that is dead, downed or absent at the check makes the row UNMEASURED (HARNESS) -- a FAIL needs a live witness present.
The old --theft-day loop also let colonists idle (a Tantrum smashed our Fill tank before a day of touched ticks accrued): every
colonist is drafted before the day loop, and both tanks are refilled/emptied every REFILL_EVERY (2,000) ticks, so every
cycle is touched.
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

CYCLE = 250                 # RM_LiquidTheft.TheftTick cadence
# LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS: the filltank probe verb takes raw tank units (decilitres). The old "100" (drums) was
# above a 2x2 tank's 80; 120,000 = 12 kL = 75% of today's 160,000 capacity, the same "well filled" intent.
FILL_UNITS = 120000
from level_water import _volume_const  # noqa: E402  (constants read from RM_Volume.cs, never restated)
LEVEL = _volume_const("UnitsPerLevel", None)   # RM_Volume.UnitsPerLevel: one notch = 1,000 L = 10,000 dL
CHECK_PHASE = 7             # TicksGame % 250 == 7
WITNESS_PHASE = 4           # spawn here: 3 ticks before the check
REFILL_EVERY = 2000
DAY_TICKS = 60000
MAX_WITNESS_CYCLES = 4      # theft attempts (one fresh witness pair per cycle) before the row calls it a FAIL
THEFT = "RimMandrake.FlowWorks.Machinery.RM_LiquidTheft"
S_HOSE = "RimMandrake.FlowWorks.Hose.RM_HoseSettings"
S_MACH = "RimMandrake.FlowWorks.Machinery.RM_MachinerySettings"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
S_EG = "RimMandrake.ExplosiveGrowth.ExplosiveGrowthSettings"   # spillWaterEnabled: EG plants drink spill filth
L7_STATIONS = ("flow_drains", "flow_spreads")   # review-map stations 1 and 2 (review_map.station_list)
SPILL = "RimMandrake.FlowWorks.Machinery.RM_LiquidSpill"
SPILL_FILTH = "RM_Filth_LiquidSpill"   # the generic spill filth
# HARNESS (belt live 2026-10-22, L5 PASS 10-16 -> 'FAIL'): since cad23ba0e1 (owner 2026-10-18 "it's spilled water as per
# wetting the ground, plant growth") fresh water spills as Explosive Growth's RM_Filth_WaterSpill (mandrake.rm.biomes), not
# the generic spill filth: both count as the spill's pieces.
SPILL_FILTHS = (SPILL_FILTH, "RM_Filth_WaterSpill")
UNITS_PER_LITRE = _volume_const("UnitsPerLitre", None)   # RM_Volume.UnitsPerLitre (tank units are decilitres)
FW_PKG = "mandrake.rm.flowworks"


# ============================================================================ pure logic (selftest_liquid_checks.py)


def _reel_west(c):
    """validation_core.reel_west without the bridge-side import: the reel turns since a98046cbe9 and a bare op builds it
    NORTH; built West one square east keeps the 2x2 on [c, c+(1,1)] with the west outlet these scenes were proven with."""
    return "RM_HoseReel:%d,%d,3" % (c[0] + 1, c[1])

def _QS():
    """The shared quiet isolated test-site profile (Utils/modcheck/quiet_site.py)."""
    d = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Utils"), "modcheck")
    if d not in sys.path:
        sys.path.append(d)
    import quiet_site
    return quiet_site

def ticks_until(tick, phase, cycle=CYCLE):
    """Ticks to step so that tick % cycle == phase (0 if already there)."""
    return (phase - tick) % cycle


def witness_alive(w):
    """A witness counts only if it is present and neither dead nor downed at the check."""
    return bool(w) and not w.get("dead") and not w.get("downed")


def theft_verdict(drawn, caught0, caught1, letters0, letters1, witness_at_check, precondition=None):
    """(status, class, detail) for L6_theft_spotted_letter.

    UNMEASURED: a precondition failed; nothing was drawn (no theft to spot); or the witness was not alive and present at
    the check (we cannot tell 'LOS blocked' from 'walked off'). FAIL: a live witness was present at the check and the mod caught
    nothing / sent no letter. PASS: caught rose AND a letter arrived."""
    det = {"caught": [caught0, caught1], "letters": [letters0, letters1], "witnessAtCheck": witness_at_check, "drawn": drawn}
    if precondition:
        return "UNMEASURED", "SITE", dict(det, why=precondition)
    if caught0 is None or caught1 is None:
        return "UNMEASURED", "HARNESS", dict(det, why="RM_LiquidTheft.caught not readable")
    if not drawn or drawn <= 0:
        return "UNMEASURED", "SITE", dict(det, why="nothing was taken from their tank, so there was no theft to spot")
    if (caught1 or 0) > (caught0 or 0) and letters1 > letters0:
        return "PASS", "MOD", det
    if not any(witness_alive(w) for w in (witness_at_check or [])):
        return "UNMEASURED", "HARNESS", dict(det, why="no live witness present at the theft check: the harness lost him, not the mod")
    return "FAIL", "MOD", det


def goodwill_verdict(gw0, gw1, gc0, gc1, per, caught):
    if not caught:
        return "UNMEASURED", "HARNESS", {"why": "the theft was never caught"}
    if None in (gw0, gw1):
        return "UNMEASURED", "HARNESS", {"why": "goodwill not readable", "goodwill": [gw0, gw1]}
    det = {"goodwill": [gw0, gw1], "goodwillCharged": [gc0, gc1], "perDay": per}
    ok = float(gc1 or 0) - float(gc0 or 0) <= -float(per or 2) and gw1 < gw0   # settings read back as text: "1.5" is legal
    return ("PASS" if ok else "FAIL"), "MOD", det


def dump_no_pump_verdict(tank_trace, canal0, canal1, precondition=None):
    """L2a: the Dump tank loses units through an Outflow end with no pump AND the dry canal gained fill."""
    if tank_trace and None in tank_trace:        # an unreadable end reading is not an empty tank
        return "UNMEASURED", "HARNESS", {"tankUnits": tank_trace, "why": "a tank reading was unreadable"}
    drained = (tank_trace[0] or 0) - (tank_trace[-1] or 0) if tank_trace else None
    det = {"tankUnits": tank_trace, "drainedPer1000": drained, "canalFillSum": [canal0, canal1]}
    if precondition or not tank_trace or not tank_trace[0]:
        return "UNMEASURED", "SITE", dict(det, why=precondition or "tank never held liquid")
    return ("PASS" if drained > 0 and canal1 > canal0 else "FAIL"), "MOD", det


def dump_pump_verdict(tank_trace, reach0, reach1, no_pump_rate, precondition=None):
    """L2b: the pump on Pour drains the Dump tank strictly faster than the no-pump rate and wets the reach."""
    if tank_trace and None in tank_trace:
        return "UNMEASURED", "HARNESS", {"tankUnits": tank_trace, "why": "a tank reading was unreadable"}
    drained = (tank_trace[0] or 0) - (tank_trace[-1] or 0) if tank_trace else None
    det = {"tankUnits": tank_trace, "drainedPer1000": drained, "vsNoPump": no_pump_rate, "reachFillSum": [reach0, reach1]}
    if precondition or not tank_trace or not tank_trace[0]:
        return "UNMEASURED", "SITE", dict(det, why=precondition or "tank never held liquid")
    if no_pump_rate is None:
        return "UNMEASURED", "HARNESS", dict(det, why="the no-pump scene did not run: no slow rate to compare")
    return ("PASS" if drained > no_pump_rate and drained > 0 and reach1 > reach0 else "FAIL"), "MOD", det


def ship_fill_verdict(trace, precondition=None):
    """L4 Fill: trace = [[base, ship], ...]. PASS = the ship tank gained at least half a level AND our tank fell. (The hose
    primes itself out of the destination first -- ~50 units a laid cell -- so the bar is level-scale, not 'any gain'.)"""
    if precondition:
        return "UNMEASURED", "SITE", {"base_ship": trace, "why": precondition}
    if not trace or any(None in pair for pair in trace):
        return "UNMEASURED", "HARNESS", {"base_ship": trace, "why": "a tank reading was unreadable"}
    gain, fall = trace[-1][1] - trace[0][1], trace[0][0] - trace[-1][0]
    det = {"base_ship": trace, "shipGained": gain, "baseFell": fall}
    return ("PASS" if gain >= LEVEL // 2 and fall > 0 else "FAIL"), "MOD", det


def ship_empty_verdict(trace, precondition=None):
    """L4 Empty: the ship tank falls AND our tank rises."""
    if precondition:
        return "UNMEASURED", "SITE", {"base_ship": trace, "why": precondition}
    if not trace or any(None in pair for pair in trace):
        return "UNMEASURED", "HARNESS", {"base_ship": trace, "why": "a tank reading was unreadable"}
    fall, gain = trace[0][1] - trace[-1][1], trace[-1][0] - trace[0][0]
    det = {"base_ship": trace, "shipFell": fall, "baseGained": gain}
    return ("PASS" if fall > 0 and gain > 0 else "FAIL"), "MOD", det


def filth_pieces(units, per_filth):
    """RM_LiquidNetKernel.FilthCount: one piece per per_filth units, rounded up; any spill shows."""
    if units is None or units <= 0:
        return 0
    per = max(1, per_filth or 1)
    return max(1, (units + per - 1) // per)


def filth_thickness(label):
    """Vanilla Filth.Label is "FilthLabel" = "{0} x{1}" (or "{0} of {1} x{2}"): the trailing x<n> is the thickness."""
    m = re.search(r"x(\d+)\s*$", str(label or ""))
    return int(m.group(1)) if m else None


def spill_verdict(held0, held1, drained, filth0, filth1, unplaced0, unplaced1, precondition=None, expected=None):
    """L5: capping an Outflow end empties the hose (held -> 0, drained >= held) AND the spill shows as filth at the end.
    filth0/filth1 are the summed THICKNESS of the spill filth in the rect: vanilla thickens the filth on the cell (up to 5)
    before it spawns another thing, so a thing count stays flat. expected = pieces the spill made (FilthCount); when known
    the thickness must rise by exactly that. A spill the mod counted but could not place (RM_LiquidSpill.Unplaced rose) is
    a MOD FAIL that says so."""
    det = {"heldUnits": [held0, held1], "drained": drained, "filthThicknessInRect": [filth0, filth1],
           "expectedPieces": expected, "unplaced": [unplaced0, unplaced1]}
    if precondition:
        return "UNMEASURED", "SITE", dict(det, why=precondition)
    if held0 is None:                       # comp_read failed: the harness could not ask, the hose may be full
        return "UNMEASURED", "HARNESS", dict(det, why="the hose's held units were unreadable before the cap")
    if not held0:
        return "UNMEASURED", "SITE", dict(det, why="the hose held nothing before the cap")
    if None in (held1, drained, filth0, filth1):
        return "UNMEASURED", "HARNESS", dict(det, why="a reading was unreadable")
    rise = filth1 - filth0
    ok = held1 == 0 and drained >= held0 and rise > 0 and (expected is None or rise == expected)
    if not ok and unplaced0 is not None and unplaced1 is not None and unplaced1 > unplaced0:
        det["why"] = "the spill found no cell that takes the filth (RM_LiquidSpill.Unplaced %s -> %s)" % (unplaced0, unplaced1)
    return ("PASS" if ok else "FAIL"), "MOD", det


def clean_verdict(cleaner, paint, readback, filth_before, filth_left, ticks):
    """L5_colonists_clean_spill. Cleaning ENABLED is the precondition, not priority 1: with manual priorities off (the
    quicktest default) vanilla's GetPriority reads any non-zero priority back as 3 (live 20261018T233414: readBack 3,
    filth 9 -> 0 in 750 ticks, read UNMEASURED by the old == 1 test). An unreadable filth read is HARNESS, not SITE."""
    det = {"filth": [filth_before, filth_left], "ticks": ticks, "cleaner": cleaner}
    rb = str(readback)
    if not cleaner or (paint or {}).get("success") is False or not (rb.isdigit() and int(rb) > 0):
        return "UNMEASURED", "SITE", dict(det, why="precondition: cleaner %s, home paint %s, Cleaning priority %s" % (
            cleaner, (paint or {}).get("setCount"), readback))
    if filth_left is None:
        return "UNMEASURED", "HARNESS", dict(det, why="the spill filth was unreadable while waiting")
    return ("PASS" if filth_left == 0 else "FAIL"), "MOD", det


def free_end_verdict(fe, fname, lay_ok):
    """L6_free_end_names_their_faction. An unread free end (the hose census missed the reel) is UNMEASURED HARNESS, never a
    MOD FAIL; nor is a lay that failed or a faction with no name."""
    det = {"freeEnd": fe, "factionName": fname}
    if not lay_ok or not fname:
        return "UNMEASURED", "SITE", dict(det, why="no laid hose or no faction name to look for")
    if not fe:
        return "UNMEASURED", "HARNESS", dict(det, why="the hose census returned no free end for this reel")
    ok = fname in str(fe.get("describe")) and fe.get("portFaction") == fname
    return ("PASS" if ok else "FAIL"), "MOD", det


# ============================================================================ live driver
def levelset_verdict(rows, rows_before=None):
    """L7 (WATER_LEVELSET_SOLVE; owner 2026-10-16 at station 1: "levelset down to a smooth 0 or 1 ... not 0, deep, 0").
    rows = jawa/flowworks_excavation_rect rows of one station. Over dug, non-sink squares: a STRIPE is a dry square with wet
    squares of one surface on both sides of it in a line (the 1,0,1 the walk save showed); a STEP is two touching squares,
    at least one wet, whose surfaces (f - d) differ by 2 or more (a deep blob beside dry or shallow ground), not counting a
    square touching a natural source (the mouth, which the pond refills every pulse). PASS = water present, no stripe,
    no step. rows_before (the same rect one pulse earlier): a stripe counts only if it stood on the same square in both
    reads -- a one-square gap moving down a canal the pond still pays into is flow in transit, not unsettled water
    (LevelSetChecks.StripedSaveGathers: at most 1 while fed, standing on one square two pulses running: 0).
    Returns (status, class, detail)."""
    before = None
    if rows_before is not None:
        before = set(map(tuple, levelset_verdict(rows_before)[2].get("allStripes", [])))
    src, dug = set(), {}
    for r in rows or []:
        c = (r.get("x"), r.get("z"))
        if r.get("isSource"):
            src.add(c)
        elif r.get("isExcavated") and not r.get("isSink"):
            dug[c] = (int(r.get("d") or 0), min(int(r.get("f") or 0), int(r.get("d") or 0)))
    surf = {c: f - d for c, (d, f) in dug.items()}
    wet = [c for c, (d, f) in dug.items() if f > 0]
    det = {"dug": len(dug), "wet": len(wet)}
    if not wet:
        return "UNMEASURED", "SITE", dict(det, why="no water standing in the station's dug squares")
    stripes, steps = [], []
    for c, (d, f) in dug.items():
        if f == 0:
            for dx, dz in ((1, 0), (0, 1)):
                a, b = (c[0] - dx, c[1] - dz), (c[0] + dx, c[1] + dz)
                if a in dug and b in dug and dug[a][1] > 0 and dug[b][1] > 0 and surf[a] == surf[b]:
                    stripes.append(c)
                    break
        for dx, dz in ((1, 0), (0, 1)):
            n = (c[0] + dx, c[1] + dz)
            if n not in dug or (f == 0 and dug[n][1] == 0) or abs(surf[c] - surf[n]) < 2:
                continue
            if any((p[0] + ex, p[1] + ez) in src for p in (c, n) for ex, ez in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                continue
            steps.append([c, n])
    moving = []
    if before is not None:
        moving = [c for c in stripes if c not in before]
        stripes = [c for c in stripes if c in before]
    det.update(stripes=len(stripes), steps=len(steps), firstStripes=stripes[:6], firstSteps=steps[:4],
               wetSurfaces=sorted(set(surf[c] for c in wet)), allStripes=stripes, movingStripes=moving)
    return ("PASS" if not stripes and not steps else "FAIL"), "MOD", det


def parse_pond(txt):
    """ProofPondDepth's reply ("POND id=.. s=1 r=0 wet=100 census=deep:0,chest:64,...") -> dict, or None."""
    if not txt or not str(txt).startswith("POND "):
        return None
    d = {}
    for tok in str(txt).split()[1:]:
        if "=" not in tok:
            continue
        k, v = tok.split("=", 1)
        if k == "census":
            d[k] = {a: int(b) for a, b in (x.split(":") for x in v.split(",") if ":" in x)}
        elif v in ("True", "False"):
            d[k] = v == "True"
        else:
            try:
                d[k] = float(v) if "." in v else int(v)
            except ValueError:
                d[k] = v
    return d


def pond_depth_verdict(reads):
    """L8 (POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD; owner by card 2026-10-16 "Yes, ponds shallow out"; design §10). reads = the
    pond's ProofPondDepth replies (parse_pond) in time order while a pump draws it. PASS = the surface fell (s rose by one or
    more), every square that was wet at the brim is still wet while s == 1 (it shallowed, it did not shrink), and at s >= 1
    the census shows part-depth stages (chest/shallow/thin) instead of only full original water. A shrinking wet count at
    s == 1, or s >= 1 with no part-depth square, is a MOD FAIL. The surface never moving is SITE (the pump drew nothing);
    the model not applying (moving water, another liquid, limitless) is SITE. Returns (status, class, detail)."""
    reads = [r for r in (reads or []) if r]
    if len(reads) < 2:
        return "UNMEASURED", "HARNESS", {"why": "fewer than two pond reads", "reads": len(reads)}
    first, last = reads[0], reads[-1]
    det = {"s": [r.get("s") for r in reads], "wet": [r.get("wet") for r in reads], "census": last.get("census"),
           "stock": [first.get("stock"), last.get("stock")]}
    if not all(r.get("applies") for r in reads):
        return "UNMEASURED", "SITE", dict(det, why="the depth model does not apply to this body (limitless, moving or not water)")
    if not (last.get("s", 0) > first.get("s", 0)):
        return "UNMEASURED", "SITE", dict(det, why="the surface never fell: the pump drew nothing")
    brim = [r for r in reads if r.get("s") == 0]
    one = [r for r in reads if r.get("s") == 1 and r.get("r", 0) == 0]
    if brim and one and min(r["wet"] for r in one) < max(r["wet"] for r in brim):
        return "FAIL", "MOD", dict(det, why="the wet count shrank one level down: the pond shrank instead of shallowing")
    c = last.get("census") or {}
    if last.get("s", 0) >= 1 and c.get("chest", 0) + c.get("shallow", 0) + c.get("thin", 0) + c.get("deep", 0) == 0:
        return "FAIL", "MOD", dict(det, why="the surface fell but no square shows a part-depth stage")
    return "PASS", "MOD", det


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--only", default="", help="comma list: L2,L4,L5,L6,L7,L8 (L7 reads review-map stations 1-2; never with --fresh-map; L8 needs --l8-pond)")
    ap.add_argument("--l7-pulses", type=int, default=16, help="L7: flow pulses to run before reading (the save holds old-kernel state)")
    ap.add_argument("--l8-pond", default="", help="L8: x,z of a square of a LIMITED still-water pond a pump is drawing")
    ap.add_argument("--l8-pulses", type=int, default=40, help="L8: flow pulses to read across (one read a pulse)")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--theft-day", action="store_true", help="L6: also run one in-game day for the goodwill charge")
    ap.add_argument("--origin-l2", default="60,150")
    ap.add_argument("--origin-l2b", default="100,150")
    ap.add_argument("--origin-l6", default="60,172")
    ap.add_argument("--origin-l4", default="180,150")
    ap.add_argument("--origin-l5", default="20,172")
    a = ap.parse_args(argv)
    only = [b.strip().upper() for b in a.only.split(",") if b.strip()]
    import proof_hose as PH           # bridge-side imports only on a live run
    V = PH.V
    B = PH.PB()
    WATER = PH.LIQUID_WATER
    out = a.out or os.path.join(HERE, "liquid_checks_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "liquid_checks.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "detail": det})
        print("%-40s %-10s %-8s %s" % (rid, st, cls, json.dumps(det, default=str)[:300]), flush=True)
        save()

    def tg():
        g = B.call("rimworld/get_game_info")
        return g.get("ticksGame") or (g.get("state") or {}).get("tick")

    raw_ticks = B.ticks

    def ticks(n):
        t0 = tg()
        left = n
        while left > 0:
            k = min(1500, left)
            raw_ticks(k)
            left -= k
        t1 = tg()
        if t0 is not None and t1 is not None and t1 - t0 < n:
            raw_ticks(n - (t1 - t0))
    B.ticks = ticks

    def step_to(phase):
        t = tg()
        n = ticks_until(t, phase)
        if n:
            B.ticks(n)
        return tg()

    def sget(typ, field):
        return B.call("jawa/mod_settings_field", typeName=typ, action="get", field=field).get("value")

    def build(*ops, faction="player"):
        return B.call("jawa/build_batch", ops=";".join(o for o in ops if o), faction=faction, wipeExisting=False)

    def dig(c, depth):
        return B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=depth, setFill=-1)

    def proof(typ, method, arg):
        r = B.call("jawa/static_call", type=typ, method=method, args=arg)
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        return r.get("success") is True and not txt.startswith("REFUSED"), txt

    def fills(cells):
        xs, zs = [c[0] for c in cells], [c[1] for c in cells]
        ok, txt = proof("RimMandrake.FlowWorks.RM_PromotionProofs", "ProofFluidRow",
                        "%d,%d,%d,%d" % (min(xs), min(zs), max(xs) - min(xs) + 1, max(zs) - min(zs) + 1))
        got = {}
        for tok in (txt.split(" ", 3)[3] if ok and txt.count(" ") >= 3 else "").split(";"):
            if ":" in tok:
                xz, rest = tok.split(":", 1)
                x, z = map(int, xz.split(","))
                got[(x, z)] = int(rest.split("/", 3)[1])
        return sum(got.get(tuple(c), 0) for c in cells)

    def units(cell):
        return PH._tank(B, cell).get("units")

    def inspect(thing_id):
        r = B.call("jawa/inspect_string", thingIds=thing_id) or {}
        for t in r.get("things") or r.get("results") or []:
            return t.get("inspect") or []
        return []

    def tank_job(cell):
        tid = PH._tank(B, cell).get("id")
        if tid is None:
            return None
        for line in inspect("RM_LiquidTank%d" % tid) + inspect("RM_UniversalCargoTank%d" % tid):
            m = re.search(r"Job: (\w+)", str(line))
            if m:
                return m.group(1)
        return None

    def gizmo_cycle(cell, prefix, want, max_clicks=4):
        out_g = {"clicks": 0, "ok": False}
        B.call("rimworld/set_god_mode", enabled=True)
        try:
            B.call("rimworld/clear_selection")
            B.call("rimworld/click_cell", x=cell[0], z=cell[1])
            for _ in range(max_clicks + 1):
                gz = (B.call("rimworld/list_selected_gizmos") or {}).get("gizmos") or []
                g = next((q for q in gz if str(q.get("label") or "").startswith(prefix)), None)
                if g is None:
                    out_g["labels"] = [q.get("label") for q in gz][:20]
                    return out_g
                out_g["label"] = g.get("label")
                if g.get("label") == want:
                    out_g["ok"] = True
                    return out_g
                r = B.call("rimworld/execute_gizmo", gizmoId=g.get("gizmoId") or g.get("id"))
                out_g["clicks"] += 1
                if r.get("success") is False:
                    out_g["error"] = r
                    return out_g
            return out_g
        finally:
            B.call("rimworld/set_god_mode", enabled=False)
            B.call("rimworld/clear_selection")

    def set_job(tank, job):
        g = gizmo_cycle(tank, "Job:", "Job: " + job)
        g["readBack"] = tank_job(tank)
        g["ok"] = bool(g.get("ok")) and g["readBack"] == job
        return g

    def set_role(reel, role):
        g = gizmo_cycle(reel, "Free end:", "Free end: " + role)
        hid = PH._hose(B, reel).get("id")
        vals = ((B.call("jawa/comp_read", thing="RM_HoseReel%d" % hid, comp="CompHoseReel", members="freeEndRole") or {})
                .get("values") or {}) if hid is not None else {}
        g["readBack"] = vals.get("freeEndRole")
        g["ok"] = bool(g.get("ok")) and str(g["readBack"]) == role
        return g

    def letters(text):
        return [l for l in (B.call("jawa/letter_list").get("letters") or []) if text in json.dumps(l, default=str)]

    def goodwill(defname):
        return next((f.get("goodwill") for f in B.call("jawa/list_factions").get("factions") or []
                     if f.get("defName") == defname), None)

    def draft_all():
        got = []
        for p in (B.hp("colonists").get("pawns") or []):
            if B.hp("pawn:%d=draft" % p["id"]).get("success"):
                got.append(p["id"])
        return got

    class Plot(PH.Scene):
        def __init__(self, o):
            self.B = B
            self.o = o
            ox, oz = o
            self.channel = [(ox + 2 + k, oz + 6) for k in range(3)]
            self.pump = (ox + 3, oz + 7)
            self.battery = (ox + 6, oz + 6)
            self.reel = (ox + 3, oz + 8)
            self.end = (ox + 16, oz + 9)
            self.tank = (ox + 17, oz + 9)
            self.north_tank = (ox + 3, oz + 10)

        def rect(self, extra_h=0):
            return (self.o[0] - PH.RF_WEST, self.o[1], PH.RF_PW + PH.RF_WEST, PH.RF_PH + extra_h)

        def ready(self, rid, extra_h=0):
            return V.prepare_site(B, self.rect(extra_h), rows, rid)

    def xz(s):
        return tuple(int(v) for v in s.split(","))

    # ---------------------------------------------------------------- preflight
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, waited = V._wait_playing(B, leave_s=0)
    rm = B.call("jawa/running_mods", assembly="RimMandrakeFlowWorks", details=False) or {}
    running = [p.lower() for p in rm.get("packageIds") or []]
    B.hp("defaults")
    B.call("jawa/weather_set", weather="Clear", lockWeather=True)
    B.call("jawa/incident_queue_clear")
    B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
    # TESTENV_MEGAPEDE_HARDEN_GATECRASHER: a Megapede + 3 Spelopede reached the golden site mid liquid_heat from a dormant
    # hive; the shared quiet isolated profile clears hostile threat structures and turns the storyteller off (read back)
    res["quiet_site"] = _QS().site_profile_receipt(B, "flowworks_liquid_checks")
    drafted = draft_all()                   # nobody idles into a Tantrum next to our tanks
    res["settings_before"] = {f: sget(t, f) for t, f in (
        (S_HOSE, "tankModesEnabled"), (S_HOSE, "freeEndRolesEnabled"), (S_HOSE, "hoseHoldsLiquid"),
        (S_HOSE, "tankLitresPerCycle"), (S_HOSE, "dumpLitresPerCycle"), (S_MACH, "liquidTheftEnabled"),
        (S_MACH, "liquidTheftSightRange"), (S_MACH, "liquidTheftGoodwillPerDay"))}
    facs = B.call("jawa/list_factions").get("factions") or []
    nonhostile = [f for f in facs if not f.get("isPlayer") and not f.get("hostile") and not f.get("permanentEnemy")
                  and not f.get("hidden")]
    neutral = next((f for f in nonhostile if str(f.get("defName", "")).startswith("Outlander")), None) or \
        (nonhostile[0] if nonhostile else None)
    res["preflight"] = {"playing": ok, "flowworks": FW_PKG in running, "drafted": drafted, "neutral": neutral}
    good = ok and FW_PKG in running
    row("LC_preflight", "PASS" if good else "UNMEASURED", "HARNESS", res["preflight"])
    if not good:
        return 2

    # ---------------------------------------------------------------- L2
    def blk_L2():
        pa = Plot(xz(a.origin_l2))
        rate = None
        if pa.ready("L2a_site_ready"):
            canal = [pa.P(16 + k, 9) for k in range(3)]
            for c in canal:
                dig(c, 2)
            pa.build("RM_LiquidTank:%d,%d" % pa.north_tank, _reel_west(pa.reel))
            B.ticks(2)
            ft = B.hp("filltank:%d,%d=%s,%d" % (pa.north_tank + (WATER, FILL_UNITS)))
            lay = pa.lay(pa.P(15, 9))
            role = set_role(pa.reel, "Outflow")
            job = set_job(pa.north_tank, "Dump")
            f0 = fills(canal)
            tr = [units(pa.north_tank)]
            for _ in range(4):
                B.ticks(250)
                tr.append(units(pa.north_tank))
            f1 = fills(canal)
            pre = None if (ft.get("success") and lay.get("success") and role["ok"] and job["ok"]) else \
                "precondition: filltank %s, lay %s, role %s, job %s" % (ft.get("units"), lay.get("success"), role, job)
            st, cls, det = dump_no_pump_verdict(tr, f0, f1, pre)
            rate = det.get("drainedPer1000") if st != "UNMEASURED" else None   # an unmeasured slow scene is no yardstick
            row("L2_dump_tank_drains_without_pump", st, cls, dict(det, lay=lay, role=role, job=job))
        pb = Plot(xz(a.origin_l2b))
        if pb.ready("L2b_site_ready"):
            for c in pb.channel:
                dig(c, 2)
            pb.build("RM_LiquidPump:%d,%d" % pb.pump, "Battery:%d,%d" % pb.battery, "RM_UniversalPipe:%d,%d" % pb.P(3, 8),
                     "RM_UniversalPipe:%d,%d" % pb.P(3, 9), "RM_LiquidTank:%d,%d" % pb.north_tank)
            B.ticks(2)
            pb.charge()
            pw = PH._powered(B, pb.pump)
            ft = B.hp("filltank:%d,%d=%s,%d" % (pb.north_tank + (WATER, FILL_UNITS)))
            job = set_job(pb.north_tank, "Dump")
            ok_p, pour = proof("RimMandrake.FlowWorks.RM_NorthstarProofs", "ProofPump", "%d,%d;pour" % pb.pump)
            f0 = fills(pb.channel)
            tr = [units(pb.north_tank)]
            for _ in range(4):
                B.ticks(250)
                tr.append(units(pb.north_tank))
            f1 = fills(pb.channel)
            pre = None if (ft.get("success") and job["ok"] and ok_p and "pour=True" in pour and pw is not None) else \
                "precondition: filltank %s, job %s, pour %s, pump powered after %s" % (ft.get("units"), job, pour, pw)
            st, cls, det = dump_pump_verdict(tr, f0, f1, rate, pre)
            row("L2_pump_pour_drains_dump_fast", st, cls, dict(det, pumpProof=pour, job=job, pumpPoweredAfterTicks=pw))

    # ---------------------------------------------------------------- L6
    def blk_L6():
        if not neutral:
            row("L6_theft_spotted_letter", "UNMEASURED", "SITE", "no non-hostile, non-hidden faction in this world")
            return
        nf = neutral["defName"]
        s = Plot(xz(a.origin_l6))
        if not s.ready("L6_site_ready", extra_h=6):
            return
        s.build("RM_LiquidTank:%d,%d" % s.north_tank, _reel_west(s.reel))
        build("RM_LiquidTank:%d,%d" % s.tank, faction=nf)
        B.ticks(2)
        ft = B.hp("filltank:%d,%d=%s,%d" % (s.tank + (WATER, FILL_UNITS)))
        lay = s.lay(s.P(16, 9))
        B.ticks(70)
        fe = PH._hose(B, s.reel).get("freeEnd") or {}
        job = set_job(s.north_tank, "Fill")
        draft_all()
        cc0, l0 = sget(THEFT, "caught"), len(letters("Liquid theft"))
        u_start = units(s.tank)
        wx, wz = s.P(20, 13)                     # 5 cells NE of the foreign tank
        att, cc1, l1, at_check = [], cc0, l0, []
        for i in range(MAX_WITNESS_CYCLES):
            t_sp = step_to(WITNESS_PHASE)
            w = B.call("jawa/spawn_pawn", kindDef="Villager", x=wx, z=wz, faction=nf, count=2)
            ids = [p.get("id") for p in (w.get("pawns") or [])]
            t_chk = step_to(CHECK_PHASE + 2)     # passes the check at % 250 == 7
            plist = B.call("jawa/list_pawns", faction=nf, limit=40).get("pawns") or []
            at_check = [{k: q.get(k) for k in ("id", "x", "z", "downed", "dead")} for q in plist if q.get("id") in ids]
            cc1, l1 = sget(THEFT, "caught"), len(letters("Liquid theft"))
            att.append({"cycle": i, "spawnTick": t_sp, "checkTick": t_chk, "spawned": w.get("success"), "witnesses": at_check,
                        "caught": cc1})
            if (cc1 or 0) > (cc0 or 0):
                break
        drawn = (u_start or 0) - (units(s.tank) or 0)
        pre = None if (ft.get("success") and lay.get("success") and job["ok"]) else \
            "precondition: foreign filltank %s, lay %s, our job %s" % (ft.get("units"), lay.get("success"), job)
        st, cls, det = theft_verdict(drawn, cc0, cc1, l0, l1, at_check, pre)
        u_end = units(s.tank)
        unread = u_start is None or u_end is None
        row("L6_foreign_tank_drawn", ("UNMEASURED" if pre or unread else "PASS" if drawn > 0 else "FAIL"),
            "SITE" if pre else "HARNESS" if unread else "MOD",
            {"foreignUnits": [u_start, u_end], "ours": units(s.north_tank)})
        row("L6_theft_spotted_letter", st, cls, dict(det, attempts=att, faction=nf,
                                                     sightRange=res["settings_before"].get("liquidTheftSightRange")))
        fname = str(neutral.get("name") or "")
        row("L6_free_end_names_their_faction", *free_end_verdict(fe, fname, bool(lay.get("success"))))
        if not a.theft_day:
            row("L6_goodwill_after_a_day", "UNMEASURED", "HARNESS", "not run: pass --theft-day (ticks ~60,000)")
            return
        gw0, gc0 = goodwill(nf), sget(THEFT, "goodwillCharged")
        draft_all()
        for _ in range(DAY_TICKS // REFILL_EVERY + 1):       # every cycle touched
            B.hp("filltank:%d,%d=%s,%d" % (s.tank + (WATER, FILL_UNITS)))
            B.hp("filltank:%d,%d=%s,0" % (s.north_tank + (WATER,)))
            B.ticks(REFILL_EVERY)
        gw1, gc1 = goodwill(nf), sget(THEFT, "goodwillCharged")
        per = res["settings_before"].get("liquidTheftGoodwillPerDay")
        st, cls, det = goodwill_verdict(gw0, gw1, gc0, gc1, per, (cc1 or 0) > (cc0 or 0))
        row("L6_goodwill_after_a_day", st, cls, det)

    # ---------------------------------------------------------------- L4
    def blk_L4():
        s = Plot(xz(a.origin_l4))
        if not s.ready("L4_site_ready"):
            return
        s.build("RM_LiquidTank:%d,%d" % s.north_tank, _reel_west(s.reel))
        sb = s.build("RM_UniversalCargoTank:%d,%d" % s.tank)
        B.ticks(2)
        ship_def = "RM_UniversalCargoTank"
        if not PH._tank(B, s.tank):
            s.build("RM_LiquidTank:%d,%d" % s.tank)
            B.ticks(2)
            ship_def = "RM_LiquidTank"
        ft = B.hp("filltank:%d,%d=%s,%d" % (s.north_tank + (WATER, FILL_UNITS)))
        lay = s.lay(s.P(16, 9))
        jf = set_job(s.tank, "Fill")
        tr1 = [[units(s.north_tank), units(s.tank)]]
        for _ in range(4):
            B.ticks(250)
            tr1.append([units(s.north_tank), units(s.tank)])
        je = set_job(s.tank, "Empty")
        tr2 = [[units(s.north_tank), units(s.tank)]]
        for _ in range(4):
            B.ticks(250)
            tr2.append([units(s.north_tank), units(s.tank)])
        h = PH._hose(B, s.reel)
        pre1 = None if (ft.get("success") and lay.get("success") and jf["ok"]) else \
            "precondition: filltank %s, lay %s, job %s" % (ft.get("units"), lay.get("success"), jf)
        st, cls, det = ship_fill_verdict(tr1, pre1)
        row("L4_ship_tank_fill_loads", st, cls, dict(det, shipDef=ship_def, cargoBuild=sb.get("failed"), job=jf, lay=lay,
                                                     hose={k: h.get(k) for k in ("netLink", "credits", "creditedUnits")}))
        pre2 = pre1 or (None if je["ok"] else "precondition: Empty job %s" % je) or \
            (None if st == "PASS" else "Fill did not load the ship tank, so there is nothing to empty")
        st2, cls2, det2 = ship_empty_verdict(tr2, pre2)
        row("L4_ship_tank_empty_unloads", st2, cls2, dict(det2, job=je))
        row("L4_on_a_real_gravship", "UNMEASURED", "SITE",
            "no gravship fixture on a quicktest map: a plain %s stands in for the ship's tank (no ship-tank def exists)" % ship_def)

    # ---------------------------------------------------------------- L5
    def blk_L5():
        s = Plot(xz(a.origin_l5))
        if not s.ready("L5_site_ready"):
            return
        s.water()
        s.build("RM_LiquidPump:%d,%d" % s.pump, "Battery:%d,%d" % s.battery, _reel_west(s.reel))
        B.ticks(2)
        s.charge()
        pw = PH._powered(B, s.pump)
        lay = s.lay(s.P(16, 9))
        role = set_role(s.reel, "Outflow")
        B.ticks(600)

        def held():
            hid = PH._hose(B, s.reel).get("id")
            v = ((B.call("jawa/comp_read", thing="RM_HoseReel%d" % hid, comp="CompHoseReel", members="heldUnits,heldLiquid")
                  or {}).get("values") or {}) if hid is not None else {}
            u = str(v.get("heldUnits") or "")
            return (int(u) if u.lstrip("-").isdigit() else None), v.get("heldLiquid")

        def filth():
            lt = B.call("jawa/list_things", rect="%d,%d,%d,%d" % frect, limit=200, includePawns=False) or {}
            if lt.get("success") is False:
                return None
            # thickness, not things: vanilla thickens the filth already on the cell (SPILL_FILTH_FIX_SOIL_SAYS_NO re-run)
            tot = 0
            for t in lt.get("things") or []:
                if str(t.get("def") or t.get("defName") or "") not in SPILL_FILTHS:
                    continue
                k = filth_thickness(t.get("label"))
                if k is None:
                    return None
                tot += k
            return tot

        def unplaced():
            v = sget(SPILL, "Unplaced")
            return int(v) if str(v).lstrip("-").isdigit() else None

        frect = (s.P(14, 7)[0], s.P(14, 7)[1], 5, 5)        # the free end P(16,9) and its neighbours
        # HARNESS (SPILL_DIAGNOSE_TEN_THOUSAND_GONE_DRY, belt 13:45: +2 thickness where 3 pieces were made, SpilledUnits +10000
        # = every piece laid): Explosive Growth's plants DRINK standing-water filth (RM_WetSources.SpillFilthSource.Consume
        # destroys the whole filth thing, by design: owner 2026-10-18 "spilled water as per wetting the ground, plant growth"),
        # so the rect's thickness is not conserved while EG reads spills. Its spill-water read is off for the window, restored.
        eg0 = sget(S_EG, "spillWaterEnabled")
        if eg0 is not None:
            B.call("jawa/mod_settings_field", typeName=S_EG, action="set", field="spillWaterEnabled", value="False")
        try:
            h0, liq = held()
            n0, u0 = filth(), unplaced()
            net0 = B.hp("net:%d,%d" % s.pump)
            off = set_role(s.reel, "Capped")                   # an Outflow end capped stops the hose carrying
            B.ticks(900)                                       # lease = now+375, drain checked once per 250-tick cycle
            h1, _ = held()
            net1 = B.hp("net:%d,%d" % s.pump)
            n1, u1 = filth(), unplaced()
        finally:
            if eg0 is not None:
                B.call("jawa/mod_settings_field", typeName=S_EG, action="set", field="spillWaterEnabled", value=str(eg0))
        d0, d1 = net0.get("hoseDrainedUnits"), net1.get("hoseDrainedUnits")
        drained = (d1 - d0) if isinstance(d0, int) and isinstance(d1, int) else None
        pre = None if (lay.get("success") and role["ok"] and off["ok"] and pw is not None) else \
            "precondition: lay %s, Outflow %s, Capped %s, pump powered after %s" % (lay.get("success"), role, off, pw)
        sp0, sp1 = net0.get("spilledUnits"), net1.get("spilledUnits")
        lpf = sget(S_MACH, "litresPerFilth")
        per = int(float(lpf)) * UNITS_PER_LITRE if re.match(r"^\d+(\.\d+)?$", str(lpf)) else None   # a float setting may read back "400.0"
        want = filth_pieces(sp1 - sp0, per) if per and isinstance(sp0, int) and isinstance(sp1, int) else None
        st, cls, det = spill_verdict(h0, h1, drained, n0, n1, u0, u1, pre, expected=want)
        row("L5_switched_off_hose_spills", st, cls, dict(det, heldLiquid=liq, rect=frect,
                                                         spilledUnits=[net0.get("spilledUnits"), net1.get("spilledUnits")]))
        if st != "PASS":
            row("L5_colonists_clean_spill", "UNMEASURED", "SITE", "no spill filth to clean (L5 spill row %s)" % st)
            return
        pa = B.call("jawa/paint_area", area="Home", ops="%d,%d,%d,%d" % frect, value=True, createIfMissing=True)
        sp = B.call("jawa/spawn_pawn", kindDef="Colonist", faction="player", x=s.P(12, 11)[0], z=s.P(12, 11)[1], count=1,
                    xenotype="Baseliner")
        cid = ((sp.get("pawns") or [{}])[0]).get("id")
        wp = B.call("jawa/set_work_priority", pawnId=cid, workType="Cleaning", priority=1) if cid else {}
        left, waited = n1, 0
        while left and waited < 3000:
            B.ticks(250)
            waited += 250
            left = filth()
        row("L5_colonists_clean_spill", *clean_verdict(cid, pa, wp.get("readBack"), n1, left, waited))
        if cid:
            B.hp("pawn:%d=draft" % int(re.search(r"(\d+)$", str(cid)).group(1)))

    def blk_L7():
        """Review map stations 1-2 (flow_drains, flow_spreads), read in place: the setting is on, then after --l7-pulses
        flow pulses each station's dug squares hold no 1,0,1 stripe and no 2+ step (levelset_verdict)."""
        on = sget(S_FW, "levelSetEnabled")
        if str(on).strip().lower() != "true":
            row("L7_levelset_setting_on", "UNMEASURED" if on is None else "FAIL", "HARNESS" if on is None else "MOD",
                {"levelSetEnabled": on, "why": "field missing: the deployed DLL predates WATER_LEVELSET_SOLVE" if on is None else "switched off"})
            return
        row("L7_levelset_setting_on", "PASS", "MOD", {"levelSetEnabled": on})
        sys.path.insert(0, os.path.dirname(HERE))
        import review_map as RMAP
        st = {x["id"]: x for x in RMAP.station_list()}
        pulse = int(float(B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field="pulseIntervalTicks").get("value") or 250))
        B.ticks(max(1, a.l7_pulses) * pulse)
        for sid in L7_STATIONS:
            s_ = st.get(sid)
            if not s_:
                row("L7_%s_levels_flat" % sid, "UNMEASURED", "HARNESS", {"why": "station not in review_map.station_list"})
                continue
            (ox, oz), (sw, sh) = s_["origin"], s_["size"]
            x0 = 0 if s_["setup"].get("west_edge") else ox
            rect = dict(x=x0, z=oz, w=ox + sw - x0, h=sh, onlyNonZero=True, includeTerrain=False)
            ex0 = B.call("jawa/flowworks_excavation_rect", **rect)
            B.ticks(pulse)                     # second read one pulse later: a stripe must STAND to count
            ex = B.call("jawa/flowworks_excavation_rect", **rect)
            if "rows" not in ex or "rows" not in ex0:
                row("L7_%s_levels_flat" % sid, "UNMEASURED", "HARNESS", {"reply": str(ex)[:300]})
                continue
            st_, cls, det = levelset_verdict(ex["rows"], ex0["rows"])
            row("L7_%s_levels_flat" % sid, st_, cls, dict(det, station=s_["n"], rect=[x0, oz, ox + sw - x0, sh],
                                                          pulses=a.l7_pulses, ticksGame=ex.get("ticksGame")))

    def blk_L8():
        """OWED (never run live yet, 2026-10-16): POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD. A station pond drawn by a pump, read
        once a pulse through RM_PromotionProofs.ProofPondDepth (s, wet count, terrain census); pond_depth_verdict scores it.
        Needs a deployed DLL with ProofPondDepth and --l8-pond on a pond a running pump draws."""
        if not a.l8_pond:
            row("L8_pond_shallows_before_mud", "UNMEASURED", "HARNESS", {"why": "no --l8-pond x,z given"})
            return
        on = sget(S_FW, "pondDepthEnabled")
        if str(on).strip().lower() != "true":
            row("L8_pond_shallows_before_mud", "UNMEASURED" if on is None else "FAIL", "HARNESS" if on is None else "MOD",
                {"pondDepthEnabled": on, "why": "field missing: the deployed DLL predates POND_DEPTH" if on is None else "switched off"})
            return
        pulse = int(float(B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field="pulseIntervalTicks").get("value") or 250))
        reads = []
        for _ in range(max(2, a.l8_pulses)):
            ok, txt = proof("RimMandrake.FlowWorks.RM_PromotionProofs", "ProofPondDepth", a.l8_pond)
            reads.append(parse_pond(txt) if ok else None)
            if not ok and not reads[:-1]:
                row("L8_pond_shallows_before_mud", "UNMEASURED", "HARNESS", {"reply": txt[:300]})
                return
            B.ticks(pulse)
        st_, cls, det = pond_depth_verdict(reads)
        row("L8_pond_shallows_before_mud", st_, cls, dict(det, pond=a.l8_pond, pulses=a.l8_pulses))

    try:
        for nm, fn in (("L2", blk_L2), ("L4", blk_L4), ("L5", blk_L5), ("L6", blk_L6), ("L7", blk_L7), ("L8", blk_L8)):
            if only and nm not in only:
                continue
            print("== %s" % nm, flush=True)
            try:
                B.call("jawa/incident_queue_clear")
                fn()
            except Exception as ex:  # noqa: BLE001
                row("%s_block" % nm, "UNMEASURED", "HARNESS", {"raised": repr(ex)})
    finally:
        res["quiet_site_restore"] = _QS().restore_attached(B)
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        res["counts"] = {s_: sum(1 for r in rows if r["status"] == s_) for s_ in ("PASS", "FAIL", "UNMEASURED")}
        save()
        print("result:", out, json.dumps(res["counts"]))
    return 0 if all(r["status"] == "PASS" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
