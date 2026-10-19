"""walls_slots_live.py -- ONE map, ONE driver run that discharges the seven owed live rows A2..A8 of
BIG_CREATURES_DESIGN_WALLS_AND_SLOTS (Huge Things phase 1, built in 6a540188a4), in the style of
src/RimMandrake/FlowWorks/northstar/live_session.py. Plan, tier and "can it share the FlowWorks session": section 8 of
design/RimMandrake/flowworks_live_session_plan_2026-10-18.md. Design (the bars): design/RimMandrake/big_creatures_walls_and_slots_2026-10-18.md
section 3 (table), 4 (squeeze), 5 (rules), 7 (these tests).

  python3    src/RimMandrake/HugeThings/northstar/walls_slots_live.py --dry-run        # plan + zones + time budget, no bridge
  python3    src/RimMandrake/HugeThings/northstar/walls_slots_live.py --mock           # every path offline (FakeHugeGame)
  python3    src/RimMandrake/HugeThings/northstar/walls_slots_live.py --mock --mock-fault hold   # a broken mod, rows must FAIL
  python.exe src/RimMandrake/HugeThings/northstar/walls_slots_live.py                   # LIVE: bridge held, the
                                                      # `flowworks_hugethings` tier (Large Pawns on), a fresh Playing quicktest map
  options: --only A2,A3 (a PARTIAL run: never recordable)  --skip A5  --full-ladder (all 6 thicknesses, not the compressed set)
           --wave 64 (lanes at once)  --long-restless (wait out the restlessness meter instead of extrapolating it)
           --frame-budget-ms 150  --out-dir DIR  --list  --table (print design section 3 from the kernel mirror and exit)

PASS 3 (2026-10-19): every lane is a SEALED zone (a deep-water moat; see "Lane geometry"), so the structure under test is the
only way to the goal; per-lane tick budgets come from the expectation; blocks run their lanes on one clock; the tick is
read once per advance. ESTIMATED ~12 min of wall time at ~60 ticks/s (see --dry-run).

BLOCKS (cheapest first; every block clears the arena it uses, so blocks may reuse ground):
  B0  preflight   tier truth (jawa/running_mods: Huge Things + Large Pawns), the cast read LIVE (Breadth / Passage by
                  static_call), the bridge can place natural rock (a 1-cell probe), settings snapshot
  B1  A8          zero-tick reads: the new settings read back at the owner's defaults, the settings dialog group, wall and
                  creature inspect lines (needs the lanes of B3, so its wall line is read there; this block reads defaults only)
  B2  A2          canyon lanes: open-sky natural-rock gaps 1..P wide, per cast member
  B3  A3 (+A8)    thickness ladder: wood / granite, roofed / open, thickness 1..B (compressed to the informative cells)
  B4  A4          sandwich (wood-air-wood-air-wood, straight and diagonal), five solid wood, the plug between rock outcrops
  B5  A6          scrape (ten crossings of a 2-wide built gap) and the roof pair (granite, free-standing vs roofed)
  B6  A7          door (wild vs tamed), two creatures in the same tick, a wall destroyed under an approaching titan,
                  save + reload mid-squeeze and mid-smash (the save is OWED to the joint look: see rows)
  B7  A5          pen: calm fed wild B3 stays, hungry restlessness climbs (rate measured, the 100% breakout extrapolated
                  unless --long-restless), shot it breaks out within 30 s, 3-thick granite ring never breaks

Every row: {id, item, criterion, status PASS|FAIL|UNMEASURED|SKIP, class MOD|SITE|HARNESS|OWED, detail, block, eyes}.
"Could not ask" is UNMEASURED, never PASS. Ledger-ready `rimflow verify` lines for PASS/FAIL criteria go to verify_lines.txt;
they are NOT run (the driving agent runs them after reading the evidence).

CLASSES (live-debugging-proof-harness): MOD = the mod behaved against the bar on a site that was read back as built;
SITE = the lane was not what the row needs (wall not placed, rock not placeable, the moat not painted or leaked: the
creature reached the goal with every wall standing, roof not as staged); HARNESS = the bridge, the clock, the creature
(died, never started, juvenile) or the script.

THINGS THIS SCRIPT KNOWS THAT THE DESIGN DOCUMENT DOES NOT (read from the built code, WallsSlotsUtility.WallEligible / KindAt):
- A creature breaks only walls it is not friendly to: a TAMED (player) creature never breaks the player's walls, and a wall of
  its own faction is "Protected". So the ladder, sandwich, plug, scrape, roof and pen creatures are WILD (faction none), and
  the tamed rows of the door test expect a tame creature to stay put or squeeze, never break.
- A door is one cell wide. For a creature of passage width P a 1-wide gap is below half width (TooNarrow) from P = 3 up, so
  design section 7 test 8's "the tamed B 3 squeezes through the door" cannot be true of the built kernel: B 3 is checked
  against the kernel (expect: it does not use the door), B 2 (P 2, half width 1) is the squeezing creature. Reported, not hidden.
- Restlessness rises 1.0 per day per cause: a full meter is 30,000 to 60,000 ticks. The default run measures the RATE over
  a few thousand ticks and infers the breakout (debug_process.md "Long-duration properties"); --long-restless waits.

ANTI-GUESSING: every bridge tool named here is in src/RimMandrake/bridgetools/JawaBench.BridgeTools (jawa/*) or already used by
a committed script (rimworld/open_mod_settings, rimworld/get_ui_layout); every defName was read from a Defs file or the
vanilla index. The static_call targets are public static methods of RimMandrake.TitanicCreatures.WallsSlotsUtility.
Unknown: how a bridge places NATURAL ROCK (spawn_batch / build_batch with the rock ThingDef is TRIED and read back; when it
cannot, every rock row is UNMEASURED/HARNESS with that reason, never a PASS).
"""
import argparse
import json
import math
import os
import re
import sys
import time
import traceback
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
FW_NORTHSTAR = os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "northstar")
for _p in (UTILS, FW_NORTHSTAR, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

ITEM = "BIG_CREATURES_DESIGN_WALLS_AND_SLOTS"
MOD_ID = "mandrake.rm.hugethings"
LARGEPAWNS_ID = "neku.largepawns"
SETTINGS = "RimMandrake.HugeThings.RM_HugeThingsSettings"
UTIL = "RimMandrake.TitanicCreatures.WallsSlotsUtility"
KEYED = os.path.join(REPO, "src", "RimMandrake", "HugeThings", "Languages", "English", "Keyed", "RM_HugeThings.xml")
TPS_STEP = 60.0                 # MEASURED: step_game_ticks ~60 ticks/s (bench_live_20261012/SITTING.md)
CALL_S = 0.15                   # ESTIMATED wall seconds per bridge call
MAP_DEFAULT = (250, 250)
WOOD_HP, GRANITE_HP = 195.0, 510.0   # MEASURED via RimSage, design section 3 (Wall 300 x stuff factor 0.65 / 1.7)
ROCK = "Granite"                 # vanilla natural rock ThingDef (building.isNaturalRock); the probe reads it back

# The cast: slot -> (kind/race defName, why this one). Read from Defs; the LIVE breadth is read in B0 and used for every bar
# (a juvenile or a changed baseBodySize shifts it; the slot name is a label, never the expectation).
CAST = {
    "B2": ("Elephant", "vanilla, baseBodySize 4 (the T1 floor): B 2, 2x2 under Large Pawns"),
    "B3": ("RM_Hwelgrue", "TheRot/Defs/Fauna/RM_Hwelgrue.xml baseBodySize 8: B 3"),
    "B4": ("RM_Totchak", "Scarlands/Defs/ThingDefs_Races/RM_Totchak.xml baseBodySize 14: B 4"),
    "B6": ("RM_Oommok", "Stillsand/Defs/ThingDefs_Races/RM_Oommok.xml baseBodySize 36: B 6"),
}
PLANNED_B = {"B2": 2, "B3": 3, "B4": 4, "B6": 6}

# The new settings at the owner's 2026-10-18 card defaults (RM_HugeThingsSettings.cs).
DEFAULTS = {"wallsSlotsEnabled": True, "squeezeEnabled": True, "squeezeSlowdownAtHalf": 2.0, "trampleBudgetPerBreadth": 100.0,
            "blowDamagePerBreadth": 20.0, "holdLineFactor": 1.0, "roofWallHpFactor": 1.5, "roofWallDamageFactor": 0.6667,
            "scrapeEnabled": True, "temperamentEnabled": True, "breadth2BreakingEnabled": True, "trenchStepEnabled": True}

# ============================================================================ kernel mirror (pure; RM_WallsSlotsKernel.cs)
# Mirrors the Verse-free kernel line for line so the bars are computed, not typed. selftest: --table and the A1 fuzz (offline,
# already green in HugeThings/Source/SelfTest) are the cross-check; the section-3 table below is asserted by selftest().


def breadth_of(body_size, override=0):
    if override > 0:
        return override
    if not (body_size > 0) or math.isinf(body_size):
        return 1
    return max(1, int(math.floor(math.sqrt(body_size) + 0.5)))


def passage(b, footprint):
    return max(max(1, b), max(1, footprint))


def min_squeeze(p):
    return (max(1, p) + 1) // 2


def gap_band(slot, p):
    p = max(1, p)
    if slot >= p:
        return "walk"
    if slot >= 1 and 2 * slot >= p:
        return "squeeze"
    return "narrow"


def squeeze_cost(slot, p, at_half=2.0):
    p = max(1, p)
    k = min(4.0, max(1.0, at_half))
    if slot >= p:
        return 1.0
    if gap_band(slot, p) != "squeeze":
        return float("inf")
    return 1.0 + (k - 1.0) * 2.0 * (1.0 - float(slot) / p)


def hold_thickness(b, hold_line=1.0):
    h = max(0.25, hold_line)
    return max(1, int(math.ceil(h * max(1, b) - 1e-4)))


def stops_up_to(thickness, hold_line=1.0):
    b = 0
    for cand in range(1, 65):
        if thickness >= hold_thickness(cand, hold_line):
            b = cand
        else:
            break
    return b


def trample_budget(b, per=100.0):
    return max(0.0, per) * max(1, b)


def blow_damage(b, roofed, per=20.0, roof_dmg=0.6667):
    d = max(0.0, per) * max(1, b)
    return d * min(1.0, max(0.25, roof_dmg)) if roofed else d


def counted_hp(hp, roofed, roof_hp=1.5):
    return max(0.0, hp) * (min(3.0, max(1.0, roof_hp)) if roofed else 1.0)


def decide(b, thickness, hp_sum, forbidden=False, b2_breaks=True, hold_line=1.0, per=100.0):
    if thickness <= 0:
        return "open"
    if b <= 1:
        return "hold"
    if thickness >= hold_thickness(b, hold_line):
        return "hold"
    if forbidden:
        return "forbidden"
    if b == 2 and not b2_breaks:
        return "hold"
    return "break" if hp_sum <= trample_budget(b, per) else "smash"


def blows_for(hp, b, roofed, per=20.0, roof_dmg=0.6667):
    return int(math.ceil(hp / blow_damage(b, roofed, per, roof_dmg) - 1e-9))


def lane_expect(b, t, mat_hp, roofed, **kw):
    """The verdict and blow count for a solid wall of thickness t (layers) of material HP mat_hp, from B, per design section 3."""
    hp_sum = t * counted_hp(mat_hp, roofed, kw.get("roof_hp", 1.5))
    v = decide(b, t, hp_sum, False, kw.get("b2_breaks", True), kw.get("hold_line", 1.0), kw.get("per", 100.0))
    blows = t * blows_for(mat_hp, b, roofed, kw.get("blow", 20.0), kw.get("roof_dmg", 0.6667)) if v == "smash" else 0
    return dict(verdict=v, blows=blows, hp_sum=hp_sum, hold_at=hold_thickness(b, kw.get("hold_line", 1.0)))


def ladder_ts(b, mat_hp, roofed, full=False, **kw):
    """The thicknesses worth a lane: every one in full mode; else t = 1, B-1, B, and both sides of each verdict change."""
    top = max(hold_thickness(b), 1)
    top = min(6, top)
    if full:
        return list(range(1, 7))
    out, prev = set([1, top]), None
    if top - 1 >= 1:
        out.add(top - 1)
    for t in range(1, top + 1):
        v = lane_expect(b, t, mat_hp, roofed, **kw)["verdict"]
        if prev is not None and v != prev:
            out.update((t - 1, t))
        prev = v
    return sorted(x for x in out if 1 <= x <= 6)


def selftest():
    """Design section 3 table, cell for cell (blows per cell of a lone wall), and section 4's squeeze cost table."""
    rows = [  # B, lone wood, roofed wood, lone granite, roofed granite  (verdict/blows), holds at
        (2, ("break", 0), ("smash", 8), ("smash", 13), ("smash", 20)),
        (3, ("break", 0), ("break", 0), ("smash", 9), ("smash", 13)),
        (4, ("break", 0), ("break", 0), ("smash", 7), ("smash", 10)),
        (5, ("break", 0), ("break", 0), ("smash", 6), ("smash", 8)),
        (6, ("break", 0), ("break", 0), ("break", 0), ("smash", 7)),
        (10, ("break", 0), ("break", 0), ("break", 0), ("break", 0)),
    ]
    bad = []
    for b, *cells in rows:
        for (hp, roofed), want in zip(((WOOD_HP, False), (WOOD_HP, True), (GRANITE_HP, False), (GRANITE_HP, True)), cells):
            e = lane_expect(b, 1, hp, roofed)
            if (e["verdict"], e["blows"]) != want:
                bad.append("B%d hp%s roofed=%s: %s != %s" % (b, hp, roofed, (e["verdict"], e["blows"]), want))
    for p, s, want in ((2, 1, 2.0), (3, 2, 1.67), (4, 2, 2.0), (4, 3, 1.5), (6, 3, 2.0), (6, 5, 1.33)):
        if abs(squeeze_cost(s, p) - want) > 0.01:
            bad.append("squeeze P%d S%d %.2f != %.2f" % (p, s, squeeze_cost(s, p), want))
    for bs, want in ((1, 1), (2.25, 2), (6.24, 2), (6.25, 3), (12.24, 3), (12.25, 4), (20.25, 5), (30.25, 6), (100, 10)):
        if breadth_of(bs) != want:
            bad.append("breadth %.2f -> %d != %d" % (bs, breadth_of(bs), want))
    # X1/X8: sandwich T = 2, hp 585 > 400 -> smash; five solid wood holds at B 4
    if decide(4, 2, 3 * WOOD_HP) != "smash" or decide(4, 5, 5 * WOOD_HP) != "hold":
        bad.append("sandwich/five-solid bars")
    return bad


# ============================================================================ pure helpers
def parse_cell(v):
    """(x, z) from {'x':..,'z':..}, [x,z], [x,y,z] or 'x,z' / '(x, y, z)'; None when unreadable."""
    try:
        if isinstance(v, dict):
            return int(v.get("x")), int(v.get("z"))
        if isinstance(v, (list, tuple)):
            return (int(v[0]), int(v[-1])) if len(v) >= 2 else None
        nums = re.findall(r"-?\d+", str(v))
        if len(nums) >= 3:
            return int(nums[0]), int(nums[-1])
        if len(nums) == 2:
            return int(nums[0]), int(nums[1])
    except (TypeError, ValueError):
        pass
    return None


def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def rect_str(r):
    return "%d,%d,%d,%d" % tuple(r)


def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def overlaps(a, b, gap=0):
    ax, az, aw, ah = a
    bx, bz, bw, bh = b
    return not (ax + aw + gap <= bx or bx + bw + gap <= ax or az + ah + gap <= bz or bz + bh + gap <= az)


def shelf_pack(sizes, region, gap=6):
    """sizes: [(name, w, h)]. Left-to-right, row by row inside region (x, z, w, h); raises when something does not fit."""
    rx, rz, rw, rh = region
    x, z, row_h, out = rx, rz, 0, {}
    for n, w, h in sizes:
        if x + w > rx + rw:
            x, z, row_h = rx, z + row_h + gap, 0
        if w > rw or z + h > rz + rh:
            raise ValueError("lane %s (%dx%d) does not fit region %s" % (n, w, h, region))
        out[n] = (x, z, w, h)
        x += w + gap
        row_h = max(row_h, h)
    return out


# Lane geometry (cells). PASS 3 (2026-10-19): every lane is SEALED. Pass 2's 41-tall walls had open ends, and the mod was
# right to walk round them: WallsSlotsDecider.TryStart breaks (or squeezes) toward a REACHABLE goal only when the walk round
# costs > titanClearingDetourFactor (2.5) x the way through and saves >= 240 ticks (TitanClearing.Worth), and a 41-tall
# wall's detour is ~2.3x. With the full rule on (temperament off) an UNREACHABLE goal is always worth breaking for, so each
# lane zone is ringed by a one-cell moat of deep water (Impassable terrain: no thing to destroy, so the breach path can only
# cross the lane's own structure) and its interior is painted Soil (one walking cost for every lane, which the canyon cost
# rows need). The structure spans the interior edge to edge; lane_leaks() flood-fills the plan and refuses a leaky layout.
# The terrain is painted back to Soil when the lane is cleared (a quicktest map is disposable; the moat must not cut a later
# block's lanes).
LEAD = 7               # ring at offset 0, creature at START_OFF, the structure at offset LEAD
START_OFF = 3
GOAL_PAST = 4          # the goal is this many cells past the structure's far face
LANE_H = 13            # interior 11: a B6 (Large Pawns footprint 4, passage 6) fits with room
LANE_H_TALL = 21       # the diagonal sandwich (goal offset DIAG_DZ)
DIAG_DZ = 6
CANYON_H = 13          # the canyon rock spans the interior except its gap (the gap is the only way through)
CANYON_LEN = 8         # a squeeze run of 8 cells (MaxSqueezeCells 30); the cost window is the 6 interior cells (entry and exit steps differ)
ZONE_GAP = 2           # sealed zones need no detour room between them
MOAT, FLOOR = "WaterDeep", "Soil"   # WaterDeep passability Impassable (RimSage, 1.6 TerrainDef); Soil the vanilla base soil
# Per-lane tick budgets (ESTIMATED from the bars, not measured): the decision is taken at the path start, so a held lane shows
# its verdict at once; a smash takes one blow a second (WallsSlots.SmashIntervalTicks 60).
WALK_BUDGET = 720      # spawn to past the structure: ~12 cells at <= 30 ticks a cell + the order latency
HOLD_BUDGET = 600      # held / too narrow: nothing happens; long enough for a wrong smash to show
BLOW_TICKS = 60


def smash_budget(blows):
    return WALK_BUDGET + int(blows * BLOW_TICKS * 1.3)


class Lane(object):
    """One staged lane: geometry in absolute cells, what to build, the creature, and the expectation (filled after B0)."""

    def __init__(self, lid, row, slot, kind, zone, **kw):
        self.id, self.row, self.slot, self.kind, self.zone = lid, row, slot, kind, zone
        self.walls = {}            # cell -> (def, stuff)
        self.rocks = set()
        self.roof = []             # rects 'RoofConstructed' over the lane
        self.sealed = kw.pop("sealed", True)
        self.faction = kw.pop("faction", "none")
        self.cast = kw.pop("cast", None)
        self.budget = kw.pop("budget", WALK_BUDGET)
        self.start = self.goal = None
        self.expect = {}
        self.meta = dict(kw)
        self.out = {}

    @property
    def x0(self):
        return self.zone[0]

    @property
    def z0(self):
        return self.zone[1]

    @property
    def iz0(self):
        """First interior row (the ring is the zone's border)."""
        return self.zone[1] + 1

    @property
    def ih(self):
        return self.zone[3] - 2

    @property
    def zc(self):
        return self.zone[1] + self.zone[3] // 2


def moat_rects(zone):
    x, z, w, h = zone
    return [(x, z, w, 1), (x, z + h - 1, w, 1), (x, z + 1, 1, h - 2), (x + w - 1, z + 1, 1, h - 2)]


def moat_cells(zone):
    out = set()
    for rx, rz, rw, rh in moat_rects(zone):
        for i in range(rx, rx + rw):
            for j in range(rz, rz + rh):
                out.add((i, j))
    return out


def lane_leaks(lane, open_cells=()):
    """Flood fill of the PLAN (pure): can the start reach the goal through the lane without crossing a wall, a rock or the
    moat? open_cells are blocked too (a canyon's gap: the gap is a legal way through, everything else must be sealed).
    A sealed lane must answer False, or a creature can walk round its structure and the row tests nothing."""
    x, z, w, h = lane.zone
    blocked = set(lane.walls) | set(lane.rocks) | set(open_cells) | (moat_cells(lane.zone) if lane.sealed else set())
    lo_x, hi_x, lo_z, hi_z = (x, x + w - 1, z, z + h - 1) if lane.sealed else (x - 8, x + w + 7, z - 8, z + h + 7)
    seen, todo = {lane.start}, [lane.start]
    while todo:
        cx, cz = todo.pop()
        if (cx, cz) == lane.goal:
            return True
        for nx, nz in ((cx + 1, cz), (cx - 1, cz), (cx, cz + 1), (cx, cz - 1)):
            if lo_x <= nx <= hi_x and lo_z <= nz <= hi_z and (nx, nz) not in blocked and (nx, nz) not in seen:
                seen.add((nx, nz))
                todo.append((nx, nz))
    return False


def wall_column(lane, x, z0, h, stuff="WoodLog", door_at=None):
    for z in range(z0, z0 + h):
        lane.walls[(x, z)] = ("Door" if door_at is not None and z == door_at else "Wall", stuff)


def wall_across(lane, x, stuff="WoodLog", door_at=None):
    """A wall column spanning the lane's interior edge to edge (moat to moat)."""
    wall_column(lane, x, lane.iz0, lane.ih, stuff, door_at)


def set_ends(lane, struct_x1, dz=0):
    """Start START_OFF cells into the lane, goal GOAL_PAST cells past the structure's last column struct_x1."""
    lane.start, lane.goal = (lane.x0 + START_OFF, lane.zc), (struct_x1 + GOAL_PAST, lane.zc + dz)


def build_ladder_lane(lid, slot, mat, roofed, t, zone, budget=WALK_BUDGET, sealed=True):
    """A solid wall of thickness t across the sealed lane, wild creature west, goal east. Wood = WoodLog, granite = BlocksGranite."""
    stuff = "WoodLog" if mat == "wood" else "BlocksGranite"
    ln = Lane(lid, "A3", slot, "ladder", zone, mat=mat, roofed=roofed, t=t, cast=slot, budget=budget, sealed=sealed)
    wx = zone[0] + LEAD
    for i in range(t):
        wall_across(ln, wx + i, stuff)
    set_ends(ln, wx + t - 1)
    if roofed:
        ln.roof.append((wx - 3, zone[1], t + 6, zone[3]))
    ln.meta.update(wx=wx, hp=WOOD_HP if mat == "wood" else GRANITE_HP)
    return ln


def build_canyon_lane(lid, slot, s, zone, budget=WALK_BUDGET):
    """A natural-rock block CANYON_LEN thick across the sealed lane with one open-sky gap s cells wide at its middle."""
    ln = Lane(lid, "A2", slot, "canyon", zone, s=s, cast=slot, budget=budget)
    rx = zone[0] + LEAD
    gap0 = ln.iz0 + (ln.ih - s) // 2
    for x in range(rx, rx + CANYON_LEN):
        for z in range(ln.iz0, ln.iz0 + ln.ih):
            if not (gap0 <= z < gap0 + s):
                ln.rocks.add((x, z))
    set_ends(ln, rx + CANYON_LEN - 1)
    zc = gap0 + s // 2
    ln.start, ln.goal = (ln.start[0], zc), (ln.goal[0], zc)
    ln.meta.update(rx=rx, gap_rows=(gap0, gap0 + s - 1))
    ln.meta["gap_cells"] = [(x, z) for x in range(rx, rx + CANYON_LEN) for z in range(gap0, gap0 + s)]
    return ln


# ============================================================================ cast (read live) and expectations
class Cast(object):
    def __init__(self):
        self.live = {}      # slot -> dict(b, p, f, line, kind)

    def b(self, slot):
        return self.live.get(slot, {}).get("b") or PLANNED_B[slot]

    def p(self, slot):
        return self.live.get(slot, {}).get("p") or self.b(slot)


# ============================================================================ session
class Session(object):
    def __init__(self, args, out_dir):
        self.args, self.out_dir = args, out_dir
        self.rows, self.notes, self.timing, self.env = [], [], {}, {}
        self.mock, self.dry = args.mock, args.dry_run
        self.B = None
        self.cast = Cast()
        self.size = MAP_DEFAULT
        self.arena = None
        self._pawn_cache = (None, None)
        self.saved_settings = {}
        self.rock_ok = None
        self.tick0 = 0
        self._tick = None          # the game tick, cached until the next advance (pass 2: ~3 map_info calls per lane per poll)
        self.calls = 0

    # ---- output
    def say(self, s):
        print(s, flush=True)

    def row(self, rid, cid, status, cls, detail, block, eyes=False):
        r = dict(id=rid, item=ITEM, criterion=cid, status=status, cls=cls, detail=detail, block=block, eyes=eyes)
        self.rows.append(r)
        self.say("  %-40s %-10s %-7s %s %s" % (rid, status, cls, cid, json.dumps(detail, default=str)[:170]))
        self.save()
        return r

    def save(self):
        p = os.path.join(self.out_dir, "session.json")
        with open(p + ".tmp", "w", encoding="utf-8") as f:
            json.dump(dict(script="walls_slots_live.py", mode="mock" if self.mock else "live", env=self.env, timing=self.timing,
                           arena=self.arena, cast=self.cast.live, rows=self.rows, notes=self.notes, args=vars(self.args)), f,
                      indent=1, default=str)
        os.replace(p + ".tmp", p)

    # ---- bridge
    def call(self, tool, **kw):
        if self.B is None:
            return {}
        self.calls += 1
        try:
            return self.B.call(tool, **kw) or {}
        except Exception as ex:  # noqa: BLE001 - a failed call is an UNMEASURED reading, never a crash of the session
            return {"success": False, "error": "call raised: %s" % ex}

    def static(self, method, arg):
        r = self.call("jawa/static_call", type=UTIL, method=method, args=arg)
        txt = str(r.get("result") if r.get("result") is not None else r.get("message") or r.get("error") or "")
        return (r.get("success") is True and not txt.startswith("REFUSED")), txt

    def now(self):
        """The game tick. Cached between advances: the session pauses the game and moves it only through advance(), so one read
        per advance is exact (pass 2 read map_info ~3 times per lane per poll: most of its 2.7 ticks per wall second)."""
        if self.B is None:
            return 0
        if self.mock:
            return self.B.tick
        if self._tick is not None:
            return self._tick
        mi = self.call("jawa/map_info")
        v = mi.get("ticksGame") or mi.get("tick") or mi.get("gameTick")
        if v is None:
            v = (self.call("jawa/flowworks_engine_state") or {}).get("ticksGame")
        self._tick = int(v or 0)
        return self._tick

    def advance(self, n):
        n = int(n)
        if self.B is None or n <= 0:
            return
        self._pawn_cache = (None, None)
        self._tick = None
        if self.mock:
            self.B.advance(n)
            return
        r = self.call("jawa/safe_advance", action="start", ticks=n, frameBudgetMs=float(self.args.frame_budget_ms),
                      timeoutMs=max(60000, n * 100))
        if not r.get("success"):
            self.B.ticks(n)

    # ---- settings (snapshot before the first write, restored in finally)
    # Pass 2 was stopped by hand mid-B3, so its finally never ran and temperamentEnabled stayed False: the next run's
    # A8_defaults read that as a mod FAIL. The snapshot is now also written to UNRESTORED (live runs only) until it is
    # restored; the next run restores it first and its A8 row says which fields a killed run had left changed.
    UNRESTORED = os.path.join(REPO, "Transient", "walls_slots_live", "UNRESTORED_SETTINGS.json")

    def _persist_snapshot(self):
        if self.mock:
            return
        try:
            os.makedirs(os.path.dirname(self.UNRESTORED), exist_ok=True)
            with open(self.UNRESTORED, "w", encoding="utf-8") as f:
                json.dump(self.saved_settings, f)
        except OSError:
            pass

    def restore_left_over(self):
        """Settings a killed run changed and never restored: put them back before anything reads them. Returns the fields."""
        if self.mock or not os.path.exists(self.UNRESTORED):
            return {}
        try:
            with open(self.UNRESTORED, encoding="utf-8") as f:
                old = json.load(f)
        except (OSError, ValueError):
            return {}
        for k, v in old.items():
            self.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=k, value=str(v))
        try:
            os.remove(self.UNRESTORED)
        except OSError:
            pass
        return old

    def sget(self, f):
        return self.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=f).get("value")

    def sset(self, f, v):
        if f not in self.saved_settings:
            old = self.sget(f)
            if old is None:
                raise RuntimeError("could not read %s before changing it; refusing to overwrite the player's setting" % f)
            self.saved_settings[f] = old
            self._persist_snapshot()
        r = self.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=f, value=str(v))
        return r.get("success") is True

    def restore_settings(self):
        for f, v in list(self.saved_settings.items()):
            self.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=f, value=str(v))
        self.saved_settings.clear()
        if not self.mock:
            try:
                os.remove(self.UNRESTORED)
            except OSError:
                pass

    # ---- the world
    def pawns(self):
        """list_pawns once per game tick (every lane polled at the same tick shares one call)."""
        t = self.now()
        if self._pawn_cache[0] == t:
            return self._pawn_cache[1]
        kw = dict(rect=rect_str(self.arena_used)) if getattr(self, "arena_used", None) else {}
        r = self.call("jawa/list_pawns", limit=500, **kw)
        by = {}
        for p in r.get("pawns") or []:
            c = parse_cell(p.get("position") if p.get("position") is not None else (p.get("x"), p.get("z")))
            by[str(p.get("id"))] = dict(cell=c, dead=bool(p.get("dead")), downed=bool(p.get("downed")), kind=p.get("kind"),
                                        faction=p.get("faction"))
        self._pawn_cache = (t, by)
        return by

    def things(self, rect, defs=None):
        kw = dict(rect=rect_str(rect), limit=4000)
        if defs:
            kw["defName"] = defs
        r = self.call("jawa/list_things", **kw)
        out = []
        for t in r.get("things") or r.get("results") or []:
            # pass 2 (2026-10-19, HARNESS): jawa/list_things puts x/z at the thing's TOP level (no "position"), so every
            # read cell was None: "walls built 0 of N" and "Granite did not appear" on maps where both stood (probed live)
            c = parse_cell(t.get("position") if t.get("position") is not None else (t.get("x"), t.get("z")))
            out.append(dict(id=t.get("id"), d=t.get("def") or t.get("defName"), cell=c, hp=fnum(t.get("hitPoints")),
                            maxhp=fnum(t.get("maxHitPoints")), stuff=t.get("stuff"), faction=t.get("faction")))
        return out

    def inspect(self, thing_id):
        r = self.call("jawa/inspect_string", thingIds=str(thing_id))
        lines = []
        for t in r.get("things") or r.get("results") or []:
            ins = t.get("inspect")
            lines += ins if isinstance(ins, list) else ([ins] if ins else [])
        return [str(x) for x in lines]

    def clear(self, rect, floor=False):
        """Everything built, planted or dropped in rect, roofs removed, rock left to the stager. Pawns are never touched by
        destroy_batch; ours are killed by kill_pawns. floor=True also paints the rect back to FLOOR (a lane's moat gone)."""
        self.call("jawa/destroy_batch", rects=rect_str(rect), categories="All")
        self.call("jawa/set_roof_batch", ops="None:%s" % rect_str(rect))
        if floor:
            self.call("jawa/set_terrain_batch", ops="%s:%s" % (FLOOR, rect_str(rect)))

    def kill_strays(self, rect):
        """Wild animals and visitors standing in rect (never the player's: faction filter 'nonplayer'); returns how many."""
        r = self.call("jawa/list_pawns", rect=rect_str(rect), faction="nonplayer", limit=200)
        ids = [str(p.get("id")) for p in r.get("pawns") or [] if not p.get("dead")]
        self.kill_pawns(ids)
        return len(ids)

    def kill_pawns(self, ids):
        for i in ids:
            self.call("jawa/damage", damageDef="Bomb", amount=100000, thingId=i, allowColonists=False)

    def build(self, lane):
        """Floor and moat, walls, rock and roof of a lane; returns (placed_walls, placed_rocks, moat_failed_cells).
        Walls are the PLAYER's (build_batch's default is no faction, and a tame creature breaks an unowned wall: the door rows'
        "never breaks the player's walls" needs them owned); a wild creature (no faction) is friendly to no wall."""
        moat_bad = 0
        if lane.sealed and self.args.mock_fault != "unsealed":        # the fault: pass 2's open-ended lanes
            x, z, w, h = lane.zone
            tops = ["%s:%d,%d,%d,%d" % (FLOOR, x + 1, z + 1, w - 2, h - 2)] + ["%s:%s" % (MOAT, rect_str(r)) for r in moat_rects(lane.zone)]
            r = self.call("jawa/set_terrain_batch", ops=";".join(tops))
            moat_bad = int(r.get("cellsFailedVerify") or 0) if r.get("success") else len(moat_cells(lane.zone))
        ops = {}
        for (x, z), (d, stuff) in lane.walls.items():
            ops.setdefault((d, stuff), []).append("%s:%d,%d" % (d, x, z))
        placed = 0
        for (d, stuff), lst in ops.items():
            for ch in chunks(lst, 150):
                r = self.call("jawa/build_batch", ops=";".join(ch), stuff=stuff, faction="player", wipeExisting=True, readBack=0)
                placed += int(r.get("placed") or r.get("count") or (len(ch) if r.get("success") else 0))
        rocks = 0
        if lane.rocks:
            for ch in chunks(sorted(lane.rocks), 150):
                r = self.call("jawa/spawn_batch", ops=";".join("%s:%d,%d" % (ROCK, x, z) for x, z in ch))
                rocks += len(ch) if r.get("success") else 0
        for rc in lane.roof:
            self.call("jawa/set_roof_batch", ops="RoofConstructed:%s" % rect_str(rc))
        return placed, rocks, moat_bad


# ============================================================================ the shared-clock scheduler (FlowWorks')
def _scheduler():
    """run_shared / Wait from the FlowWorks live session (one scheduler for both sessions); a tiny local copy on failure."""
    try:
        import live_session as LS
        return LS.Wait, LS.run_shared
    except Exception:  # noqa: BLE001

        class Wait(object):
            def __init__(self, ticks, until=None, every=60):
                self.ticks, self.until, self.every, self.timed_out = int(ticks), until, max(1, int(every)), False

        def run_shared(gens, advance, now, log=print):
            out, t0 = {}, now()
            live = {n: g for n, g in gens.items()}
            while live:
                step = 60
                for n, g in list(live.items()):
                    try:
                        w = next(g)
                        step = min(step, max(1, w.ticks))
                    except StopIteration:
                        out[n] = "done"
                        live.pop(n)
                    except Exception as ex:  # noqa: BLE001
                        out[n] = "crashed: %s" % ex
                        live.pop(n)
                if live:
                    advance(step)
            return out, now() - t0
        return Wait, run_shared


Wait, run_shared = _scheduler()


# ============================================================================ lane runner (a generator for the shared clock)
POLL_FAR, POLL_NEAR, POLL_GAP = 120, 30, 10
# Job report strings (HugeThings Defs/JobDefs/RM_JobDefs.xml). PASS 3 (HARNESS): pass 2 matched "smash" / "squeez", which the
# creature's OWN inspect line always carries (CreatureLine: "smashes up to N thick", "squeezes gaps of N+"), so every B2+
# creature read as smashing and squeezing: the A3_B2 "smashed with every wall standing" rows and saw_squeeze=true on canyon
# lanes it walked round were this. Only the job report is evidence.
REPORT_SMASH, REPORT_SQUEEZE = "smashing through", "squeezing through"


def observe_lane(s, lane, pid, timeout, goal_slack=1):
    """Generator: yields Wait until the creature reaches the goal, is lost, or the budget ends; fills lane.out with the samples.
    Re-issues the goto when the creature is idle far from the wall (a wild animal wanders; a held creature's goal is
    remembered unreachable for 600 ticks, UnreachableMemo.CooldownTicks, so a re-order every 600 asks the decider again).
    Inspect is read only where it can say something: in a canyon's rock span (squeezing), or near a wall while the creature
    stands still (a smash is one blow a second on the spot; a creature walking up to a wall already carries the job's report).
    smash_ticks sums the poll intervals in which it stood smashing: the blow count is smash_ticks / 60 + 1."""
    out = lane.out
    out.update(samples=[], saw_squeeze=False, saw_smash=False, smash_polls=0, smash_ticks=0, first_contact=None, wall_gone_tick=None,
               reached=False, lost=None, in_gap=False, t_enter=None, t_exit=None, polls=0, minx=None, ordered=0, inspects=0)
    t_start = s.now()
    wall_cells = sorted(set(lane.walls) | set(lane.rocks))
    wx = lane.meta.get("wx") or lane.meta.get("rx") or lane.x0 + LEAD
    xs = [c[0] for c in wall_cells] or [wx]
    wx0, wx1 = min(xs), max(xs)
    last_order = t_start
    prev = None          # (tick, x, z, stood_smashing)
    while True:
        t = s.now()
        if t - t_start > timeout:
            break
        p = s.pawns().get(str(pid))
        if p is None or p["cell"] is None:
            out["lost"] = "pawn not listed"
            break
        if p["dead"]:
            out["lost"] = "pawn dead"
            break
        x, z = p["cell"]
        out["polls"] += 1
        out["samples"].append((t - t_start, x, z))
        near = wx0 - 4 <= x <= wx1 + 3
        if near and out["first_contact"] is None and x >= wx0 - 2:
            out["first_contact"] = t - t_start
        in_span = lane.kind == "canyon" and wx0 <= x <= wx1
        if in_span:
            gz = lane.meta["gap_rows"]
            out["in_gap"] = out["in_gap"] or gz[0] <= z <= gz[1]
        still = prev is not None and (x, z) == (prev[1], prev[2])
        stood = False
        if (in_span if lane.kind == "canyon" else (near and still)):
            lines = " ".join(s.inspect(pid)).lower()
            out["inspects"] += 1
            if REPORT_SQUEEZE in lines:
                out["saw_squeeze"] = True
            if REPORT_SMASH in lines and still:
                stood = True
                out["saw_smash"] = True
                out["smash_polls"] += 1
                if prev[3]:
                    out["smash_ticks"] += t - prev[0]
                else:
                    out["smash_ticks"] += min(t - prev[0], BLOW_TICKS)   # the first still poll: at most one blow's worth
        prev = (t, x, z, stood)
        gx, gz_ = lane.goal
        if abs(x - gx) <= goal_slack + 1 and abs(z - gz_) <= 3:
            out["reached"] = True
            break
        if t - last_order >= 600 and not near:
            s.call("jawa/ordered_job", pawnId=pid, jobDef="Goto", targetAX=gx, targetAZ=gz_, waitTicks=1)
            out["ordered"] += 1
            last_order = t
        if in_span:
            nxt_poll = POLL_GAP
        elif near:
            nxt_poll = POLL_NEAR
        else:
            nxt_poll = int(min(POLL_FAR, max(POLL_NEAR, (wx0 - 6 - x) * 8))) if x < wx0 - 6 else POLL_FAR
        yield Wait(nxt_poll)
    out["ticks"] = s.now() - t_start
    # N blows land at 0, 60, .. (N-1) x 60 ticks into the smash and the job ends on the last: (N-1) x 60 ticks stood smashing
    out["blows_seen"] = int(round(out["smash_ticks"] / float(BLOW_TICKS))) + 1 if out["smash_ticks"] > 0 else 0
    if lane.kind == "canyon":
        out["t_enter"] = interp_cross(out["samples"], wx0 + 1)
        out["t_exit"] = interp_cross(out["samples"], wx1)


def interp_cross(samples, x_at):
    """Game tick (relative) at which x first reaches x_at, linearly interpolated between the two samples that straddle it;
    None when never. Poll granularity (10-15 ticks) would otherwise be a 15% error on a 90-tick crossing."""
    prev = None
    for t, x, _z in samples:
        if x >= x_at:
            if prev is None or prev[1] >= x_at:
                return float(t)
            t0, x0 = prev[0], prev[1]
            return t0 + (t - t0) * (x_at - x0) / float(x - x0)
        prev = (t, x)
    return None


def layout_notes(lane):
    """The plan's own seal check (pure, before any bridge call): a sealed lane whose start reaches its goal round the structure
    (or, for a canyon, other than through its gap) tests nothing."""
    if not lane.sealed or lane.start is None or lane.goal is None:
        return []
    if lane_leaks(lane, lane.meta.get("gap_cells") or ()):
        return ["layout leaks: the plan's flood fill reaches the goal without crossing the structure"]
    return []


def stage_and_spawn(s, lane, faction=None):
    """Stage the lane, read it back, spawn its creature; returns (pid or None, site_notes)."""
    notes = layout_notes(lane)
    s.clear(lane.zone)
    strays = s.kill_strays(lane.zone)
    if strays:
        lane.out["strays_killed"] = strays
    placed, rocks, moat_bad = s.build(lane)
    if moat_bad:
        notes.append("moat/floor: %d cells failed to paint" % moat_bad)
    want_w, want_r = len(lane.walls), len(lane.rocks)
    got_w = len([t for t in s.things(lane.zone, "Wall,Door") if t["cell"] in lane.walls])
    if want_w and got_w < want_w:
        notes.append("walls built %d of %d" % (got_w, want_w))
    if want_r:
        got_r = len([t for t in s.things(lane.zone, ROCK) if t["cell"] in lane.rocks])
        if got_r < want_r:
            notes.append("rock placed %d of %d" % (got_r, want_r))
    kind = CAST[lane.cast][0] if lane.cast else lane.meta.get("kind")
    r = s.call("jawa/spawn_pawn", kindDef=kind, x=lane.start[0], z=lane.start[1], faction=faction or lane.faction, count=1)
    pid = ((r.get("pawns") or [{}])[0]).get("id")
    if pid is None:
        notes.append("spawn_pawn failed: %s" % str(r.get("error") or r)[:120])
    return pid, notes


def read_creature(s, pid, slot):
    ok_b, b = s.static("Breadth", str(pid))
    ok_f, f = s.static("Footprint", str(pid))
    ok_p, pw = s.static("Passage", str(pid))
    try:
        info = dict(b=int(float(b)), f=int(float(f)), p=int(float(pw)))
    except (TypeError, ValueError):
        info = {}
    if info:
        s.cast.live.setdefault(slot, {}).update(info)
    return info


def lane_runner(s, lane, rowfn, timeout=None):
    """The generator body shared by wall, canyon and plug lanes: stage, spawn, order, observe, evaluate (rowfn writes rows).
    timeout None = the lane's own budget (set from its expectation when it was planned)."""
    pid, notes = stage_and_spawn(s, lane)
    lane.out["site_notes"] = notes
    if pid is None:
        rowfn(s, lane, None, None, notes)
        return
    info = read_creature(s, pid, lane.cast) if lane.cast else {}
    s.call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=1.0)
    s.call("jawa/ordered_job", pawnId=pid, jobDef="Goto", targetAX=lane.goal[0], targetAZ=lane.goal[1], waitTicks=1)
    yield Wait(1)
    for w in observe_lane(s, lane, pid, timeout if timeout is not None else lane.budget):
        yield w
    # what is left of the walls
    left = {t["cell"]: t for t in s.things(lane.zone, "Wall,Door")}
    lane.out["walls_left"] = len([c for c in lane.walls if c in left])
    lane.out["hp_lost"] = sum(max(0.0, (left[c]["maxhp"] or 0) - (left[c]["hp"] or 0)) for c in lane.walls if c in left)
    lane.out["rock_left"] = len([t for t in s.things(lane.zone, ROCK) if t["cell"] in lane.rocks]) if lane.rocks else 0
    if lane.cast and not lane.out.get("insp"):
        lane.out["insp"] = " | ".join(s.inspect(pid))[:400]
    rowfn(s, lane, pid, info, notes)
    s.kill_pawns([pid])


# ============================================================================ row writers
SMASH_MIN_TICKS = 90       # stood smashing at least this long = a smash (a break-through pauses half a step, never a second)


def classify_wall_lane(out, lane):
    """held | broke | smashed | partial | leaked | unreached from the samples and what is left. In a SEALED lane a creature at
    the goal with every wall standing walked round something: the seal leaked (SITE), never "around"."""
    n = len(lane.walls)
    gone = n - out.get("walls_left", n)
    if out.get("saw_smash") and (out.get("smash_ticks") or 0) >= SMASH_MIN_TICKS:
        return "smashed"
    if gone > 0:
        return "broke" if out.get("reached") else "partial"
    if out.get("reached"):
        return "leaked" if lane.sealed else "around"
    return "unreached"


def ladder_row(s, lane, pid, info, notes):
    rid = "A3_%s" % lane.id
    if pid is None or not info:
        s.row(rid, "A3", "UNMEASURED", "HARNESS", dict(why="creature not spawned or Breadth unreadable", notes=notes), "B3")
        return
    b, p = info["b"], info["p"]
    hp, roofed, t = lane.meta["hp"], lane.meta["roofed"], lane.meta["t"]
    knobs = s.knobs
    e = lane_expect(b, t, hp, roofed, **knobs)
    o = lane.out
    got = classify_wall_lane(o, lane)
    blows = o.get("blows_seen") or 0
    detail = dict(B=b, P=p, t=t, mat=lane.meta["mat"], roofed=roofed, expect=e["verdict"], got=got, blows_expect=e["blows"],
                  blows_seen=blows, smash_ticks=o.get("smash_ticks"), ticks=o.get("ticks"), budget=lane.budget,
                  walls_left=o.get("walls_left"), first_contact=o.get("first_contact"), ordered=o.get("ordered"), notes=notes)
    if notes:
        s.row(rid, "A3", "UNMEASURED", "SITE", detail, "B3")
        return
    if o.get("lost"):
        s.row(rid, "A3", "UNMEASURED", "HARNESS", dict(detail, lost=o["lost"]), "B3")
        return
    if got == "leaked":
        s.row(rid, "A3", "UNMEASURED", "SITE", dict(detail, why="goal reached with every wall standing in a sealed lane: the moat leaked"), "B3")
        return
    if e["verdict"] == "hold":
        ok = got == "unreached" and o.get("hp_lost", 0) == 0 and not o.get("saw_smash")
    elif e["verdict"] == "break":
        ok = got == "broke"
    else:
        ok = got == "smashed" and abs(blows - e["blows"]) <= max(2, int(0.2 * e["blows"]))
    if not ok and got == "unreached" and e["verdict"] != "hold":
        detail["why"] = "sealed lane, the goal unreachable, and the creature never broke in: the breach did not trigger"
    s.row(rid, "A3", "PASS" if ok else "FAIL", "MOD", detail, "B3")


def canyon_row(s, lane, pid, info, notes):
    rid = "A2_%s" % lane.id
    if pid is None or not info:
        s.row(rid, "A2", "UNMEASURED", "HARNESS", dict(why="creature not spawned or Breadth unreadable", notes=notes), "B2")
        return
    p, sl = info["p"], lane.meta["s"]
    band = gap_band(sl, p)
    o = lane.out
    detail = dict(P=p, S=sl, band=band, in_gap=o.get("in_gap"), t_enter=o.get("t_enter"), t_exit=o.get("t_exit"),
                  saw_squeeze=o.get("saw_squeeze"), rock_left=o.get("rock_left"), rock_want=len(lane.rocks), notes=notes,
                  reached=o.get("reached"), budget=lane.budget)
    if notes:
        s.row(rid, "A2", "UNMEASURED", "SITE", dict(detail, why="rock canyon not as staged (natural rock cannot be placed, the moat, or the wall/spawn failed)"), "B2")
        return
    if o.get("lost"):
        s.row(rid, "A2", "UNMEASURED", "HARNESS", dict(detail, lost=o.get("lost")), "B2")
        return
    if o.get("rock_left") != len(lane.rocks):
        s.row(rid, "A2", "FAIL", "MOD", dict(detail, why="rock HP/count changed: rock is never damaged"), "B2")
        return
    if band == "narrow":
        # sealed: the gap is the only way through, so a creature that ignores it never reaches the goal
        s.row(rid, "A2", "PASS" if not o.get("in_gap") and not o.get("reached") else "FAIL", "MOD",
              dict(detail, bar="S < 0.5P never used: the creature stays west of the sealed canyon"), "B2")
        return
    if not o.get("reached"):
        s.row(rid, "A2", "FAIL" if not o.get("in_gap") else "UNMEASURED", "MOD" if not o.get("in_gap") else "HARNESS",
              dict(detail, why="sealed canyon: the gap is the only way, and the creature never took it" if not o.get("in_gap")
                   else "in the gap but the goal not reached in the budget"), "B2")
        return
    dur = None
    if o.get("t_enter") is not None and o.get("t_exit") is not None:
        dur = o["t_exit"] - o["t_enter"]
    detail["crossing_ticks"] = dur
    s.canyon.setdefault(lane.cast, {})[sl] = dict(dur=dur, p=p, band=band, in_gap=o.get("in_gap"))
    s.row(rid, "A2", "PASS" if o.get("in_gap") else "UNMEASURED", "MOD" if o.get("in_gap") else "SITE",
          dict(detail, bar="the gap is used", why="" if o.get("in_gap") else "reached without a gap sample: the moat leaked"), "B2")


def canyon_cost_rows(s):
    """The time bar: per creature, the crossing time at S relative to S = P (the control), against squeeze_cost, +-15%."""
    for slot, by in sorted(s.canyon.items()):
        ctl = next((v for v in by.values() if v["band"] == "walk" and v["dur"]), None)
        for sl, v in sorted(by.items()):
            if v["band"] != "squeeze" or not v["dur"]:
                continue
            rid = "A2_cost_%s_S%d" % (slot, sl)
            if not ctl or not ctl["dur"]:
                s.row(rid, "A2", "UNMEASURED", "HARNESS", dict(why="no walk-speed control lane (S >= P) for this creature"), "B2")
                continue
            want = squeeze_cost(sl, v["p"], s.knobs.get("at_half", 2.0))
            ratio = float(v["dur"]) / ctl["dur"]
            ok = abs(ratio - want) <= 0.15 * want
            s.row(rid, "A2", "PASS" if ok else "FAIL", "MOD", dict(S=sl, P=v["p"], ratio=round(ratio, 2), want=round(want, 2),
                                                                  tol="15%", poll_ticks=POLL_GAP), "B2")
        for sl, v in sorted(by.items()):
            if v["band"] == "walk" and v is not ctl and v["dur"] and ctl and ctl["dur"]:
                r = float(v["dur"]) / ctl["dur"]
                s.row("A2_walk_%s_S%d" % (slot, sl), "A2", "PASS" if abs(r - 1) <= 0.10 else "FAIL", "MOD",
                      dict(S=sl, ratio=round(r, 2), bar="S >= P at x1 +-10%"), "B2")


# ============================================================================ blocks
def mk_knobs(s):
    """The settings the bars are computed from, read live (not assumed): the bars follow the build under test."""
    def g(f, d):
        v = s.sget(f)
        x = fnum(v)
        return x if x is not None else d
    b2 = str(s.sget("breadth2BreakingEnabled")).lower()
    s.knobs = dict(per=g("trampleBudgetPerBreadth", 100.0), blow=g("blowDamagePerBreadth", 20.0), hold_line=g("holdLineFactor", 1.0),
                   roof_hp=g("roofWallHpFactor", 1.5), roof_dmg=g("roofWallDamageFactor", 0.6667), at_half=g("squeezeSlowdownAtHalf", 2.0),
                   b2_breaks=(b2 != "false"))


def b0_preflight(s):
    s.left_over = s.restore_left_over()
    if s.left_over:
        s.notes.append("restored settings a killed run left changed: %s" % s.left_over)
    rm = s.call("jawa/running_mods", details=False)
    ids = [p.lower() for p in rm.get("packageIds") or []]
    s.env.update(running=len(ids), hugethings=MOD_ID in ids, largepawns=LARGEPAWNS_ID in ids,
                 flowworks="mandrake.rm.flowworks" in ids, config="hugethings-%d" % len(ids) if ids else "UNMEASURED")
    ok = bool(ids) and MOD_ID in ids and len(ids) <= 40
    s.row("B0_tier_truth", "-", "PASS" if ok else "UNMEASURED", "HARNESS",
          dict(running=len(ids), hugethings=MOD_ID in ids, largepawns=LARGEPAWNS_ID in ids,
               why="" if ok else "Huge Things not running, or a full-list load (>40 mods)"), "B0")
    s.row("B0_largepawns", "A2", "PASS" if LARGEPAWNS_ID in ids else "UNMEASURED", "HARNESS",
          dict(why="" if LARGEPAWNS_ID in ids else "Large Pawns absent: footprints are 1x1, P = B, the Large Pawns walkability "
                                                   "exception (design 6) is untested; run on the flowworks_hugethings tier"), "B0")
    s.call("jawa/kill_hostiles")
    s.call("jawa/weather_set", weather="Clear", lockWeather=True)
    s.call("jawa/incident_queue_clear")
    # no wild animal walks in while lanes stand (the stager also kills any stray inside a zone before it builds)
    wb = s.call("jawa/wild_spawner_block", action="block", minutes=120)
    s.env["wild_spawner_blocked"] = wb.get("blocked")
    mi = s.call("jawa/map_info")
    if mi.get("sizeX"):
        s.size = (int(mi["sizeX"]), int(mi.get("sizeZ") or mi["sizeX"]))
    mk_knobs(s)
    s.arena = plan_arena(s.size)
    s.arena_used = s.arena["region"]
    # the cast, read live on a throwaway lane in the arena (spawn, read, kill)
    x, z = s.arena["origin"]
    for slot, (kind, _why) in CAST.items():
        r = s.call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction="none", count=1)
        pid = ((r.get("pawns") or [{}])[0]).get("id")
        if pid is None:
            s.row("B0_cast_%s" % slot, "-", "UNMEASURED", "HARNESS", dict(kind=kind, why="spawn_pawn: %s" % str(r.get("error") or r)[:120]), "B0")
            continue
        info = read_creature(s, pid, slot)
        s.cast.live.setdefault(slot, {})["kind"] = kind
        ok_l, line = s.static("CreatureLine", str(pid))
        s.cast.live[slot]["line"] = line if ok_l else None
        good = bool(info) and info["b"] == PLANNED_B[slot]
        s.row("B0_cast_%s" % slot, "-", "PASS" if good else "UNMEASURED", "SITE" if info else "HARNESS",
              dict(kind=kind, live=info, planned_B=PLANNED_B[slot],
                   why="" if good else "live breadth differs from the slot: bars use the LIVE value (a juvenile spawn?)"), "B0")
        s.kill_pawns([pid])
        x += 6
    # can this bridge place natural rock? (1-cell probe)
    cx, cz = s.arena["origin"][0], s.arena["origin"][1] + 10
    s.call("jawa/spawn_batch", ops="%s:%d,%d" % (ROCK, cx, cz))
    got = [t for t in s.things((cx, cz, 1, 1), ROCK) if t["cell"] == (cx, cz)]
    s.rock_ok = bool(got)
    s.call("jawa/destroy_batch", rects=rect_str((cx, cz, 1, 1)), categories="All")
    s.row("B0_rock_placeable", "A2", "PASS" if s.rock_ok else "UNMEASURED", "HARNESS",
          dict(why="" if s.rock_ok else "spawn_batch of %s did not appear on the map: natural rock cannot be staged by this "
                                        "bridge, so A2 and the plug row (A4) need a map with a real rock outcrop" % ROCK), "B0")


def plan_arena(size):
    """ONE arena (cleared and reused by every block): origin at the south-west margin; lane footprints are packed per block."""
    m = 15
    return dict(origin=(m, m), region=(m, m, size[0] - 2 * m, size[1] - 2 * m))


def wave_zones(arena, n, w, h, gap=ZONE_GAP):
    sizes = [("z%d" % i, w, h) for i in range(n)]
    return [shelf_pack(sizes, arena["region"], gap)["z%d" % i] for i in range(n)]


def run_wave(s, lanes, rowfn, block, timeout=None):
    """Run lanes (already zoned inside the arena, non-overlapping) on ONE shared clock, wave by wave. timeout None = each
    lane's own budget, so a wave lasts as long as its slowest lane's expectation, not a flat worst case."""
    wave = max(1, s.args.wave)
    for batch in chunks(lanes, wave):
        gens = {ln.id: lane_runner(s, ln, rowfn, timeout) for ln in batch}
        res, spent = run_shared(gens, s.advance, s.now, log=s.say)
        s.timing["%s_ticks" % block] = s.timing.get("%s_ticks" % block, 0) + spent
        for name, r in res.items():
            if r != "done":
                s.row("%s_%s_crashed" % (block, name), "-", "UNMEASURED", "HARNESS", dict(result=r), block)
        for ln in batch:
            s.clear(ln.zone, floor=ln.sealed)
        s.call("jawa/kill_hostiles", destroyCorpses=True)


def set_full_rule(s, on=True):
    """temperamentEnabled off = the FULL rule always applies (WallsSlots.FullRule): lanes test the physics, not the mood."""
    s.sset("temperamentEnabled", "False" if on else "True")


# ---- B1 / A8 defaults and dialog
def b1_a8_defaults(s):
    bad = {}
    for f, want in DEFAULTS.items():
        got = s.sget(f)
        if isinstance(want, bool):
            ok = str(got).lower() == str(want).lower()
        else:
            g = fnum(got)
            ok = g is not None and abs(g - want) <= 1e-3 * max(1.0, abs(want))
        if not ok:
            bad[f] = dict(got=got, want=want)
    left = getattr(s, "left_over", {}) or {}
    s.row("A8_defaults", "A8", "PASS" if not bad else "FAIL", "MOD",
          dict(checked=len(DEFAULTS), differing=bad, restored_from_killed_run=left,
               note="a differing value may be the player's own (or a killed run's, restored in B0 and listed here): compare "
                    "with the snapshot before calling it a mod bug"), "B1")
    # the Mod Settings group: every label of the walls-and-slots group is found in the open dialog's UI text
    labels = keyed_labels()
    r = s.call("rimworld/open_mod_settings", modId=MOD_ID, replaceExisting=True)
    opened = r.get("success") is True
    lay = s.call("rimworld/get_ui_layout") if opened else {}
    txt = " | ".join(texts_of(lay, [])).lower()
    shot = s.call("jawa/take_screenshot", fileName="walls_slots_settings_%d" % int(time.time())).get("filePath") if opened else None
    s.call("jawa/window_list_close", action="close", typeName="ModSettings", closeAll=True)
    if not opened or not txt:
        s.row("A8_dialog_group", "A8", "UNMEASURED", "HARNESS", dict(opened=opened, textChars=len(txt), shot=shot,
              why="dialog not opened, or get_ui_layout returned no text; the screenshot is for his eye"), "B1", eyes=True)
        return
    missing = [k for k, lab in labels.items() if lab.lower() not in txt]
    # pass 2 (2026-10-19, HARNESS): the page is one scrolled column (screenshot: sections + scrollbar draw) and get_ui_layout
    # returns only the visible rows, so a label below the fold is not readable here: UNMEASURED for his eye, never FAIL.
    below_fold = bool(missing) and "reset this section" in txt
    st = "PASS" if not missing else ("UNMEASURED" if below_fold else "FAIL")
    s.row("A8_dialog_group", "A8", st, "HARNESS" if st == "UNMEASURED" else "MOD",
          dict(labels=len(labels), missing=missing[:12], shot=shot,
               note="a long settings page scrolls; a label below the fold may be missing from the layout text -> his eye"), "B1",
          eyes=bool(missing))


def keyed_labels():
    """The walls-and-slots group's visible labels from the Keyed file: keys between RM_HugeThings_WallsSlots and the first
    RM_WallsSlots_* mote key, without _Desc and without {0} templates (a slider label carries its value)."""
    out = {}
    try:
        root = ET.parse(KEYED).getroot()
    except (OSError, ET.ParseError):
        return out
    on = False
    for e in root:
        tag = e.tag
        if tag == "RM_HugeThings_WallsSlots":
            on = True
        elif tag.startswith("RM_WallsSlots_"):
            on = False
        if on and not tag.endswith("_Desc") and "{0}" not in (e.text or "") and tag != "RM_HugeThings_WallsSlotsNeeds":
            out[tag] = (e.text or "").strip()
    return out


def texts_of(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, str) and k.lower() in ("label", "text", "title", "tooltip", "content", "caption"):
                acc.append(v)
            else:
                texts_of(v, acc)
    elif isinstance(o, list):
        for v in o:
            texts_of(v, acc)
    return acc


# ---- B2 / A2
def canyon_budget(sl, p, at_half=2.0):
    band = gap_band(sl, p)
    if band == "narrow":
        return HOLD_BUDGET
    return WALK_BUDGET + int(CANYON_LEN * 30 * (squeeze_cost(sl, p, at_half) - 1.0))


def b2_canyons(s):
    if not s.rock_ok:
        s.row("A2_canyons", "A2", "UNMEASURED", "HARNESS", dict(why="natural rock could not be placed (B0_rock_placeable)"), "B2")
        return
    set_full_rule(s)
    lanes = []
    w = LEAD + CANYON_LEN + LEAD
    n = sum(min(6, s.cast.p(slot)) for slot in CAST)
    zones = wave_zones(s.arena, n, w, CANYON_H)
    i = 0
    for slot in CAST:
        p = s.cast.p(slot)
        for sl in range(1, min(6, p) + 1):
            lanes.append(build_canyon_lane("%s_S%d" % (slot, sl), slot, sl, zones[i],
                                           budget=canyon_budget(sl, p, s.knobs.get("at_half", 2.0))))
            i += 1
    s.canyon = {}
    run_wave(s, lanes, canyon_row, "B2")
    canyon_cost_rows(s)


# ---- B3 / A3 + A8 wall line
def ladder_budget(e):
    return HOLD_BUDGET if e["verdict"] == "hold" else smash_budget(e["blows"]) if e["verdict"] == "smash" else WALK_BUDGET


def b3_ladder(s):
    """Every ladder lane at once by default (--wave 64): a wave lasts as long as its slowest lane (B2 roofed granite, 20
    blows), so one wave of all lanes costs that one lane's ticks instead of waves x the flat 2,600 of pass 2."""
    set_full_rule(s)
    plan = []
    for slot in CAST:
        b = s.cast.b(slot)
        for mat, hp in (("wood", WOOD_HP), ("granite", GRANITE_HP)):
            for roofed in (False, True):
                for t in ladder_ts(b, hp, roofed, full=s.args.full_ladder, **s.knobs):
                    plan.append((slot, mat, hp, roofed, t))
    w = LEAD + 6 + LEAD
    zones = wave_zones(s.arena, max(1, min(len(plan), s.args.wave)), w, LANE_H)
    for batch in chunks(plan, s.args.wave):
        lanes = []
        for j, (slot, mat, hp, roofed, t) in enumerate(batch):
            e = lane_expect(s.cast.b(slot), t, hp, roofed, **s.knobs)
            lanes.append(build_ladder_lane("%s_%s_%s_t%d" % (slot, mat, "roof" if roofed else "open", t), slot, mat, roofed, t,
                                           zones[j], budget=ladder_budget(e)))
        run_wave(s, lanes, ladder_row, "B3")
    s.env["ladder_lanes"] = len(plan)


def wall_inspect_rows(s):
    """A8: the wall's inspect line on a staged run of wall (thickness 1..6), against StopsUpTo; the creature line against the
    kernel. Staged on one throwaway strip (no creature)."""
    zone = wave_zones(s.arena, 1, 14, 12)[0]
    ln = Lane("insp", "A8", None, "inspect", zone, sealed=False)
    # six separate runs: run k is k columns thick and 12 tall, side by side with a one-cell clear gap between them
    x = zone[0]
    runs = []
    for t in range(1, 7):
        for i in range(t):
            for z in range(zone[1], zone[1] + 12):
                ln.walls[(x + i, z)] = ("Wall", "WoodLog")
        runs.append((t, x))
        x += t + 1
    zone2 = (zone[0], zone[1], x - zone[0] + 1, 12)
    ln.zone = zone2
    s.clear(zone2)
    s.build(ln)
    for t, x0 in runs:
        thing = next((th for th in s.things(zone2, "Wall") if th["cell"] == (x0, zone[1] + 6)), None)
        if not thing:
            s.row("A8_wall_line_t%d" % t, "A8", "UNMEASURED", "SITE", dict(why="wall not built"), "B3")
            continue
        up = stops_up_to(t, s.knobs["hold_line"])
        lines = " ".join(s.inspect(thing["id"]))
        want = ("Holds big creatures up to breadth %d" % up) if up >= 2 else "Too thin to hold a big creature"
        s.row("A8_wall_line_t%d" % t, "A8", "PASS" if want in lines and ("(%d thick here)" % t) in lines else "FAIL", "MOD",
              dict(want=want, thick=t, got=lines[-160:]), "B3")
    s.clear(zone2)
    for slot in CAST:
        info = s.cast.live.get(slot) or {}
        line = info.get("line")
        if not line or "b" not in info:
            s.row("A8_creature_line_%s" % slot, "A8", "UNMEASURED", "HARNESS", dict(why="creature line or breadth unread in B0"), "B3")
            continue
        want = creature_line(info["b"], info["p"], s.knobs, str(s.sget("breadth2BreakingEnabled")).lower() != "false")
        s.row("A8_creature_line_%s" % slot, "A8", "PASS" if line.strip() == want else "FAIL", "MOD",
              dict(got=line, want=want, note="inspect_string of the pawn also carries it; static_call CreatureLine is the exact text"), "B3")


def creature_line(b, p, knobs, b2_breaks):
    """WallsSlotsUtility.CreatureLine in English (Keyed RM_WallsSlots_Part*): parts joined by ' · '."""
    parts = ["Breadth %d (needs %d-wide gaps)" % (b, p)]
    if p > 1:
        parts.append("squeezes gaps of %d+" % min_squeeze(p))
    hold = hold_thickness(b, knobs["hold_line"])
    if b >= 3 or (b == 2 and b2_breaks):
        parts.append("breaks walls up to %d HP" % round(trample_budget(b, knobs["per"])))
        if hold > 1:
            parts.append("smashes up to %d thick" % (hold - 1))
        parts.append("stopped by %d thick" % hold)
    else:
        parts.append("stopped by any built wall")
    return " · ".join(parts)


# ---- B4 / A4
def b4_sandwich_plug(s):
    """The three sandwich lanes and the plug on ONE clock (pass 2 ran the plug as a second wave)."""
    set_full_rule(s)
    slot = "B4"
    b = s.cast.b(slot)
    w = LEAD + 6 + LEAD
    zones = shelf_pack([("z%d" % i, w, LANE_H_TALL if i < 3 else LANE_H) for i in range(4)], s.arena["region"], ZONE_GAP)
    zones = [zones["z%d" % i] for i in range(4)]
    lanes = []

    def sandwich(lid, zone, diagonal, solid):
        ln = Lane(lid, "A4", slot, "sandwich", zone, cast=slot, hp=WOOD_HP, solid=solid, diagonal=diagonal)
        wx = zone[0] + LEAD
        cols = [wx, wx + 1, wx + 2, wx + 3, wx + 4] if solid else [wx, wx + 2, wx + 4]
        for x in cols:
            wall_across(ln, x, "WoodLog")
        set_ends(ln, wx + 4, DIAG_DZ if diagonal else 0)
        ln.meta.update(wx=wx, layers=len(cols))
        t = sandwich_t(ln, b)
        v = decide(b, max(t, len(cols)) if solid else t, len(cols) * WOOD_HP, False, s.knobs["b2_breaks"], s.knobs["hold_line"], s.knobs["per"])
        # a smash of L layers of wood: ceil(195 / 20B) blows a layer
        ln.budget = HOLD_BUDGET if v == "hold" else smash_budget(len(cols) * blows_for(WOOD_HP, b, False, s.knobs["blow"])) if v == "smash" else WALK_BUDGET
        return ln
    lanes.append(sandwich("sandwich_straight", zones[0], False, False))
    lanes.append(sandwich("sandwich_diagonal", zones[1], True, False))
    lanes.append(sandwich("five_solid", zones[2], False, True))
    gens = {ln.id: lane_runner(s, ln, sandwich_row) for ln in lanes}
    plug = None
    if s.rock_ok:
        # the plug: one wood wall between two rock outcrops, the outcrops spanning the rest of the sealed lane
        zone = zones[3]
        plug = Lane("plug", "A4", slot, "plug", zone, cast=slot, hp=WOOD_HP)
        wx = zone[0] + LEAD
        zc = plug.zc
        for z in range(plug.iz0, plug.iz0 + plug.ih):
            if abs(z - zc) <= 1 + max(0, b // 2):          # the plug is 3 + b//2 cells tall: the creature meets only the plug
                plug.walls[(wx, z)] = ("Wall", "WoodLog")
            else:
                for dx in range(-2, 3):
                    plug.rocks.add((wx + dx, z))
        set_ends(plug, wx + 2)
        plug.meta.update(wx=wx)
        gens["plug"] = lane_runner(s, plug, plug_row)
    res, spent = run_shared(gens, s.advance, s.now, log=s.say)
    s.timing["B4_ticks"] = s.timing.get("B4_ticks", 0) + spent
    for name, r in res.items():
        if r != "done":
            s.row("B4_%s_crashed" % name, "-", "UNMEASURED", "HARNESS", dict(result=r), "B4")
    for ln in lanes + ([plug] if plug else []):
        s.clear(ln.zone, floor=True)
    if not s.rock_ok:
        s.row("A4_plug", "A4", "UNMEASURED", "HARNESS", dict(why="natural rock could not be placed (B0_rock_placeable)"), "B4")


def sandwich_t(lane, b):
    """T = the densest B-deep stretch of wall columns: wood,air,wood,air,wood in a B 4 window -> 2; five solid -> 4."""
    cols = sorted(set(c[0] for c in lane.walls))
    t = 0
    for c0 in cols:
        t = max(t, len([c for c in cols if c0 <= c < c0 + b]))
    return t


def sandwich_row(s, lane, pid, info, notes):
    rid = "A4_%s" % lane.id
    if pid is None or not info:
        s.row(rid, "A4", "UNMEASURED", "HARNESS", dict(why="creature not spawned or Breadth unreadable", notes=notes), "B4")
        return
    o = lane.out
    b = info["b"]
    layers = lane.meta["layers"]
    t = sandwich_t(lane, b)
    hp_sum = layers * WOOD_HP
    verdict = decide(b, t if not lane.meta["solid"] else max(t, layers), hp_sum, False, s.knobs["b2_breaks"], s.knobs["hold_line"], s.knobs["per"])
    got = classify_wall_lane(o, lane)
    detail = dict(B=b, T=t, layers=layers, hp_sum=hp_sum, expect=verdict, got=got, walls_left=o.get("walls_left"),
                  smash_ticks=o.get("smash_ticks"), budget=lane.budget, notes=notes)
    if notes or o.get("lost"):
        s.row(rid, "A4", "UNMEASURED", "SITE" if notes else "HARNESS", dict(detail, lost=o.get("lost")), "B4")
        return
    if got == "leaked":
        s.row(rid, "A4", "UNMEASURED", "SITE", dict(detail, why="goal reached with every wall standing in a sealed lane: the moat leaked"), "B4")
        return
    if verdict == "hold":
        ok = got == "unreached" and o.get("hp_lost", 0) == 0
    elif verdict == "smash":
        ok = got == "smashed"
    else:
        ok = got == "broke"
    s.row(rid, "A4", "PASS" if ok else "FAIL", "MOD", detail, "B4")


def plug_row(s, lane, pid, info, notes):
    o = lane.out
    detail = dict(rock_left=o.get("rock_left"), rock_want=len(lane.rocks), walls_left=o.get("walls_left"), reached=o.get("reached"), notes=notes)
    if notes or pid is None or o.get("lost") or not info:
        s.row("A4_plug", "A4", "UNMEASURED", "SITE" if notes else "HARNESS", dict(detail, lost=o.get("lost")), "B4")
        return
    ok = o.get("rock_left") == len(lane.rocks) and o.get("walls_left", 1) < len(lane.walls) and o.get("reached")
    s.row("A4_plug", "A4", "PASS" if ok else "FAIL", "MOD", dict(detail, bar="broken like wood; the rock untouched"), "B4")


# ---- B5 / A6 scrape and roof pair
SCRAPE_W = 16          # a SHORT sealed lane: the ten crossings are ten walks of ~9 cells, not of 2 x LEAD + 3


def b5_scrape_roof(s):
    """The scrape lane and the roof pair on ONE clock (pass 2 ran them one after the other)."""
    set_full_rule(s)
    slot = "B4"
    b = s.cast.b(slot)
    sizes = [("scrape", SCRAPE_W, LANE_H), ("open", LEAD + 6 + LEAD, LANE_H), ("roofed", LEAD + 6 + LEAD, LANE_H)]
    zs = shelf_pack(sizes, s.arena["region"], ZONE_GAP)
    # scrape: a 2-wide built gap (wood sides 3 thick so it is a gap run, not a wall) across the sealed lane, ten crossings
    zone = zs["scrape"]
    ln = Lane("scrape", "A6", slot, "scrape", zone, cast=slot)
    wx = zone[0] + 6
    zc = ln.zc
    gap = (zc, zc + 1)
    for x in range(wx, wx + 3):
        for z in range(ln.iz0, ln.iz0 + ln.ih):
            if not (gap[0] <= z <= gap[1]):
                ln.walls[(x, z)] = ("Wall", "WoodLog")
    set_ends(ln, wx + 2)
    ln.meta.update(wx=wx, gap=gap, gap_cells=[(x, z) for x in range(wx, wx + 3) for z in gap])
    gens = {"scrape": scrape_runner(s, ln)}
    # roof pair: granite, free-standing vs roofed, B4
    pair = []
    for roofed in (False, True):
        e = lane_expect(b, 1, GRANITE_HP, roofed, **s.knobs)
        l2 = build_ladder_lane("roofpair_%s" % ("roofed" if roofed else "open"), slot, "granite", roofed, 1,
                               zs["roofed" if roofed else "open"], budget=ladder_budget(e))
        pair.append(l2)
        gens[l2.id] = lane_runner(s, l2, roof_row)
    res, spent = run_shared(gens, s.advance, s.now, log=s.say)
    s.timing["B5_ticks"] = s.timing.get("B5_ticks", 0) + spent
    for name, r in res.items():
        if r != "done":
            s.row("B5_%s_crashed" % name, "-", "UNMEASURED", "HARNESS", dict(result=r), "B5")
    for l3 in [ln] + pair:
        s.clear(l3.zone, floor=True)
    roof_compare(s, pair)


def scrape_runner(s, lane):
    pid, notes = stage_and_spawn(s, lane)
    if pid is None:
        s.row("A6_scrape", "A6", "UNMEASURED", "HARNESS", dict(notes=notes, why="spawn failed"), "B5")
        return
    info = read_creature(s, pid, lane.cast)
    if not info:
        s.row("A6_scrape", "A6", "UNMEASURED", "HARNESS", dict(why="Breadth unreadable"), "B5")
        s.kill_pawns([pid])
        return
    p = info["p"]
    gz = lane.meta["gap"]
    s_w = gz[1] - gz[0] + 1
    flank_cells = [c for c in lane.walls if c[1] in (gz[0] - 1, gz[1] + 1) and lane.meta["wx"] <= c[0] < lane.meta["wx"] + 3]
    hp_hist = {c: [] for c in flank_cells}
    crossings = 0
    west, east = lane.start, lane.goal
    t0 = s.now()
    dest = east
    gx0, gx1 = lane.meta["wx"] - 2, lane.meta["wx"] + 4      # at the gap (start and goal rest just outside this)
    while crossings < 10 and s.now() - t0 < 6000:
        s.call("jawa/ordered_job", pawnId=pid, jobDef="Goto", targetAX=dest[0], targetAZ=dest[1], waitTicks=1)
        arrived = False
        for _ in range(60):
            yield Wait(15)
            pw = s.pawns().get(str(pid))
            if pw is None or pw["dead"]:
                break
            if pw["cell"] and gx0 <= pw["cell"][0] <= gx1:
                # the flanks are read only while the creature is at the gap (no scrape can land elsewhere)
                th = {t["cell"]: t for t in s.things(lane.zone, "Wall")}
                for c in flank_cells:
                    hp_hist[c].append((s.now() - t0, th[c]["hp"] if c in th else 0.0))
            if pw["cell"] and abs(pw["cell"][0] - dest[0]) <= 2:
                arrived = True
                break
        if not arrived:
            break
        crossings += 1
        dest = west if dest == east else east
    steps = {}
    ok_amount, ok_rate = True, True
    for c, hist in hp_hist.items():
        prev = None
        last_drop_t = None
        for t, hp in hist:
            if prev is not None and hp < prev - 1e-6:
                d = prev - hp
                if hp > 0 and abs(d / 20.0 - round(d / 20.0)) > 0.05:      # the killing blow may be a remainder (cell gone: hp reads 0)
                    ok_amount = False
                if last_drop_t is not None and t - last_drop_t < 55:
                    ok_rate = False
                last_drop_t = t
            prev = hp
        steps['%d,%d' % c] = (round(hist[0][1] - hist[-1][1], 1) if hist else None)
    dead = [c for c, h in hp_hist.items() if h and h[-1][1] <= 0]
    detail = dict(P=p, S=s_w, crossings=crossings, flank_hp_lost=steps, flanks_dead=len(dead), drops_multiple_of_20=ok_amount,
                  at_most_once_per_second=ok_rate, note="poll 15 ticks; a drop is a 20-multiple, successive drops >= ~60 ticks apart")
    if crossings < 10:
        s.row("A6_scrape", "A6", "UNMEASURED", "HARNESS", dict(detail, why="fewer than ten crossings completed in the budget"), "B5")
    elif notes:
        s.row("A6_scrape", "A6", "UNMEASURED", "SITE", dict(detail, notes=notes), "B5")
    else:
        lost_any = any((v or 0) > 0 for v in steps.values())
        s.row("A6_scrape", "A6", "PASS" if (lost_any and ok_amount and ok_rate) else "FAIL", "MOD", detail, "B5")
    # widening: a dead flank widens the gap (S+1 where it died) -- read from the walls left
    left = [t["cell"] for t in s.things(lane.zone, "Wall")]
    widened = [c for c in dead if c not in left]
    s.row("A6_scrape_widens", "A6", "PASS" if (not dead or widened) else "FAIL", "MOD",
          dict(dead=len(dead), removed=len(widened), note="UNMEASURED-in-spirit when nothing died in ten crossings (wood 195 HP, 20 a step: the 10th hit)"),
          "B5")
    s.kill_pawns([pid])


def roof_row(s, lane, pid, info, notes):
    rid = "A6_%s" % lane.id
    if pid is None or not info:
        s.row(rid, "A6", "UNMEASURED", "HARNESS", dict(why="creature not spawned or Breadth unreadable", notes=notes), "B5")
        return
    o = lane.out
    wx = lane.meta["wx"]
    zc = lane.start[1]
    ok_r, txt = s.static("RoofedWall", "current|%d,%d|true" % (wx, zc))
    o["roofed_read_before"] = txt.strip().lower() == "true" if ok_r else None
    o["blows_seen"] = o.get("blows_seen") or 0           # observe_lane: stood-smashing ticks / 60 + 1
    s.roof_blows[lane.meta["roofed"]] = o["blows_seen"]
    want_roof = lane.meta["roofed"]
    detail = dict(B=info["b"], roofed_staged=want_roof, roofed_read=o["roofed_read_before"], blows_est=o["blows_seen"],
                  expect_blows=lane_expect(info["b"], 1, GRANITE_HP, want_roof, **s.knobs)["blows"], notes=notes)
    if notes or o.get("lost"):
        s.row(rid, "A6", "UNMEASURED", "SITE" if notes else "HARNESS", dict(detail, lost=o.get("lost")), "B5")
        return
    ok = (o["roofed_read_before"] == want_roof) and abs(o["blows_seen"] - detail["expect_blows"]) <= 2
    s.row(rid, "A6", "PASS" if ok else "FAIL", "MOD", detail, "B5")


def roof_compare(s, pair):
    a, b = s.roof_blows.get(False), s.roof_blows.get(True)
    if a is None or b is None:
        s.row("A6_roof_ratio", "A6", "UNMEASURED", "HARNESS", dict(why="a roof-pair lane did not complete"), "B5")
        return
    s.row("A6_roof_ratio", "A6", "PASS" if b > a else "FAIL", "MOD", dict(open_blows=a, roofed_blows=b, bar="roofed takes more blows (x1.5 counted HP, 2/3 damage)"), "B5")
    s.row("A6_roof_collapse_vanilla", "A6", "UNMEASURED", "OWED",
          dict(why="roof grid before/after the breach is recorded in the lanes' roof reads, but 'vanilla's collapse' needs vanilla's support radius "
                   "applied to the after-grid: his eye on the collapse (no state read can say a roof SHOULD have fallen)"), "B5", eyes=True)


# ---- B6 / A7
CONC_H = 15            # the concurrency lane holds two creatures side by side (B2 at zc-3, B4 at zc+3)


def b6_door_concurrency_saves(s):
    """Door lanes, concurrency and the wall destroyed en route, all on ONE clock (pass 2: three runs in a row)."""
    set_full_rule(s)
    w = LEAD + 3 + LEAD
    sizes = [("d%d" % j, w, LANE_H) for j in range(4)] + [("conc", w, CONC_H), ("gone", LEAD + 5 + LEAD, LANE_H)]
    zs = shelf_pack(sizes, s.arena["region"], ZONE_GAP)
    gens, lanes = {}, []
    # the door: a granite wall (1 thick) across the sealed lane with one door cell; wild vs tamed, B3 and B2
    plan = [("B3", "none"), ("B3", "player"), ("B2", "none"), ("B2", "player")]
    for j, (slot, fac) in enumerate(plan):
        zone = zs["d%d" % j]
        ln = Lane("door_%s_%s" % (slot, "tamed" if fac == "player" else "wild"), "A7", slot, "door", zone, cast=slot, faction=fac,
                  budget=smash_budget(blows_for(GRANITE_HP, 2, False, s.knobs["blow"])) if fac == "none" else 900)
        wx = zone[0] + LEAD
        wall_across(ln, wx, "BlocksGranite", door_at=ln.zc)
        set_ends(ln, wx)
        ln.meta.update(wx=wx, door=(wx, ln.zc))
        lanes.append(ln)
        gens[ln.id] = lane_runner(s, ln, door_row)
    # concurrency: two creatures of different B past the same wall in the same tick (shared spawn tick, one wall of 3 wood)
    gens["conc"] = concurrency_runner(s, zs["conc"])
    # a wall destroyed (by "a colonist": destroy_batch, no instigator) while a titan is held at it
    gens["gone"] = wall_gone_runner(s, zs["gone"])
    res, spent = run_shared(gens, s.advance, s.now, log=s.say)
    s.timing["B6_ticks"] = s.timing.get("B6_ticks", 0) + spent
    for name, r in res.items():
        if r != "done":
            s.row("B6_%s_crashed" % name, "-", "UNMEASURED", "HARNESS", dict(result=r), "B6")
    for zone in list(zs.values()):
        s.clear(zone, floor=True)
    # save + reload mid-squeeze / mid-smash: the bridge cannot hand us a save without ending the shared world; OWED
    s.row("A7_save_reload", "A7", "UNMEASURED", "OWED",
          dict(why="save/load mid-squeeze and mid-smash needs a held mid-job state across a load; the FlowWorks session's B7 does one "
                   "save+reload: when the two sessions run on one load, stage a squeeze (B2 canyon) and a smash (B3 lane) in that "
                   "session's tick window and read RM_TitanSqueeze / the clearing job after the load. Filed as owed, not guessed."),
          "B6", eyes=False)


def door_row(s, lane, pid, info, notes):
    rid = "A7_%s" % lane.id
    if pid is None or not info:
        s.row(rid, "A7", "UNMEASURED", "HARNESS", dict(why="creature not spawned or Breadth unreadable", notes=notes), "B6")
        return
    o = lane.out
    p = info["p"]
    door_cell = lane.meta["door"]
    th = {t["cell"]: t for t in s.things(lane.zone, "Door")}
    door_alive = door_cell in th
    door_hp = th[door_cell]["hp"] if door_alive else 0.0
    tamed = lane.faction == "player"
    sq = gap_band(1, p) == "squeeze"
    detail = dict(B=info["b"], P=p, tamed=tamed, door_alive=door_alive, door_hp=door_hp, saw_squeeze=o.get("saw_squeeze"),
                  saw_smash=o.get("saw_smash"), reached=o.get("reached"), kernel_door_band=gap_band(1, p), notes=notes)
    if notes or o.get("lost"):
        s.row(rid, "A7", "UNMEASURED", "SITE" if notes else "HARNESS", dict(detail, lost=o.get("lost")), "B6")
        return
    if tamed:
        # a tame creature never breaks the player's door; it squeezes it only where a 1-wide gap is >= half P (P <= 2)
        ok = door_alive and (o.get("saw_squeeze") or o.get("reached")) if sq else (door_alive and not o.get("saw_smash"))
        detail["bar"] = "tamed: squeezes the 1-wide door when P <= 2 (door intact), else leaves it alone (kernel: a 1-wide gap is below half width from P = 3)"
    else:
        ok = (not door_alive) and not o.get("saw_squeeze")
        detail["bar"] = "wild: the door is WALL cell with door HP: it breaks it, never squeezes it"
    s.row(rid, "A7", "PASS" if ok else "FAIL", "MOD", detail, "B6")


def concurrency_runner(s, zone):
    """Two creatures (B2 and B4) spawned in the same tick at the same wall (3 wood thick, across a sealed lane), both ordered
    in one tick."""
    ln = Lane("conc", "A7", None, "conc", zone)
    wx = zone[0] + LEAD
    for i in range(3):
        wall_across(ln, wx + i, "WoodLog")
    zc = ln.zc
    goal = (wx + 2 + GOAL_PAST, zc)
    s.clear(zone)
    s.kill_strays(zone)
    s.build(ln)
    pids = {}
    for slot, dz in (("B2", -3), ("B4", 3)):
        r = s.call("jawa/spawn_pawn", kindDef=CAST[slot][0], x=zone[0] + START_OFF, z=zc + dz, faction="none", count=1)
        pids[slot] = ((r.get("pawns") or [{}])[0]).get("id")
    if not all(pids.values()):
        s.row("A7_concurrency", "A7", "UNMEASURED", "HARNESS", dict(why="spawn failed", pids=pids), "B6")
        return
    infos = {sl: read_creature(s, pid, sl) for sl, pid in pids.items()}
    exp = {sl: decide(infos[sl].get("b", 1), 3, 3 * WOOD_HP, False, s.knobs["b2_breaks"], s.knobs["hold_line"], s.knobs["per"])
           for sl in pids if infos[sl]}
    for sl, pid in pids.items():
        s.call("jawa/ordered_job", pawnId=pid, jobDef="Goto", targetAX=goal[0], targetAZ=zc + (-3 if sl == "B2" else 3), waitTicks=1)
    t0 = s.now()
    done = {}
    # B4 smashes 3 layers of wood (ceil(195 / 80) = 3 blows a layer); B2 holds at once
    budget = smash_budget(3 * blows_for(WOOD_HP, infos.get("B4", {}).get("b", 4), False, s.knobs["blow"]))
    breakers = [sl for sl in exp if exp[sl] in ("break", "smash")]
    while s.now() - t0 < budget:
        yield Wait(30)
        pw = s.pawns()
        for sl, pid in pids.items():
            c = (pw.get(str(pid)) or {}).get("cell")
            if c and c[0] >= wx + 3 and sl not in done:
                done[sl] = s.now() - t0
        if breakers and all(sl in done for sl in breakers) and s.now() - t0 >= HOLD_BUDGET:
            break           # every breaker is through, and a holder has had a held lane's whole budget to (wrongly) cross
    left = len([t for t in s.things(zone, "Wall")])
    crossed = {sl: sl in done for sl in pids}
    # a creature whose rule forbids the crossing (hold) must not have crossed where the wall stands; one whose rule allows it must
    ok = bool(exp) and all(not (exp[sl] == "hold" and crossed[sl] and left == len(ln.walls)) and
                           (crossed[sl] if exp[sl] in ("break", "smash") else True) for sl in exp)
    s.row("A7_concurrency", "A7", "PASS" if ok else "FAIL", "MOD",
          dict(expect=exp, crossed=crossed, ticks=done, walls_left=left, budget=budget,
               note="B2 holds a 3-thick wall (hold at 2); B4 smashes it (3 x 195 = 585 > its 400 budget, thickness 3 < 4)"),
          "B6")
    s.kill_pawns(list(pids.values()))


REJUDGE_BAR = 450      # ticks from the cut to the far side: the walk past (~8 cells at <= 30) + two break-through pauses


def wall_gone_runner(s, zone):
    """A B4 starts right at a 5-thick wood wall across a sealed lane (held: >= 4 thick), so it is held at once. Then we destroy
    the middle three columns (leaving columns wx and wx+4: two 1-thick layers, T 1 in a B 4 window, 390 HP <= 400: broken
    through) and re-order the goto: the held crossing must be forgotten when its walls go (WallsSlotsUtility.NotifyDespawned)
    so the creature re-judges and goes through. Pass 2's version waited for an approach that a held (sealed) creature never
    makes. rejudge_ticks is the lag from the cut to the far side."""
    ln = Lane("gone", "A7", "B4", "gone", zone, cast="B4")
    wx = zone[0] + LEAD
    for i in range(5):
        wall_across(ln, wx + i, "WoodLog")     # five solid: B4 holds (>= 4 thick)
    set_ends(ln, wx + 4)
    ln.start = (wx - 3, ln.zc)
    pid, notes = stage_and_spawn(s, ln)
    if pid is None or notes:
        s.row("A7_wall_destroyed_en_route", "A7", "UNMEASURED", "HARNESS" if pid is None else "SITE", dict(notes=notes), "B6")
        if pid is not None:
            s.kill_pawns([pid])
        return
    read_creature(s, pid, "B4")
    s.call("jawa/ordered_job", pawnId=pid, jobDef="Goto", targetAX=ln.goal[0], targetAZ=ln.goal[1], waitTicks=1)
    yield Wait(240)                              # the decision is taken at the path start: held by now
    held_before = len([t for t in s.things(zone, "Wall") if t["cell"] in ln.walls])
    c = (s.pawns().get(str(pid)) or {}).get("cell")
    early = bool(c and c[0] > wx + 4)
    s.call("jawa/destroy_batch", rects=rect_str((wx + 1, ln.iz0, 3, ln.ih)), categories="Building")
    t_cut = s.now()
    s.call("jawa/ordered_job", pawnId=pid, jobDef="Goto", targetAX=ln.goal[0], targetAZ=ln.goal[1], waitTicks=1)
    reached = False
    last_order = t_cut
    while s.now() - t_cut < 1500:
        yield Wait(30)
        c = (s.pawns().get(str(pid)) or {}).get("cell")
        if c and c[0] >= ln.goal[0] - 2:
            reached = True
            break
        if s.now() - last_order >= 300:          # a wild animal drops a failed goto: ask again (a lag here is the finding)
            s.call("jawa/ordered_job", pawnId=pid, jobDef="Goto", targetAX=ln.goal[0], targetAZ=ln.goal[1], waitTicks=1)
            last_order = s.now()
    lag = s.now() - t_cut if reached else None
    held_ok = held_before == len(ln.walls) and not early
    detail = dict(walls_before=held_before, walls_planned=len(ln.walls), crossed_before_cut=early, reached_after_cut=reached,
                  rejudge_ticks=lag, bar_ticks=REJUDGE_BAR,
                  bar="held at 5 thick; after the cut to two 1-thick layers the re-order at the cut is judged afresh: through in "
                      "< %d ticks (~8 cells and two break-throughs). A lag past ~600 is the decider's stale unreachable cooldown "
                      "(UnreachableMemo), fixed 2026-10-19 by forgetting it with the held crossing" % REJUDGE_BAR)
    if not held_ok:
        s.row("A7_wall_destroyed_en_route", "A7", "FAIL", "MOD", dict(detail, why="not held by 5 thick wood before the cut"), "B6")
    else:
        s.row("A7_wall_destroyed_en_route", "A7", "PASS" if reached and lag <= REJUDGE_BAR else "FAIL", "MOD", detail, "B6")
    s.kill_pawns([pid])


# ---- B7 / A5
def b7_pen(s):
    """Wild B3 in a ring of single wood walls. Calm and fed: stays. Hungry: restlessness rises (rate measured, breakout
    inferred unless --long-restless). Shot: breaks out within 30 s. Inside a 3-thick granite ring: never, no wall dies."""
    set_full_rule(s, on=False)           # temperament ON: this is the one block that tests the mood
    slot = "B3"
    p = s.cast.p(slot)
    inner = int(math.ceil(math.sqrt(6 * p * p))) + 1           # inner side so area >= 6 P^2 (not confined)
    small = max(p, 3)                                           # a confining ring: area < 6 P^2
    zones = wave_zones(s.arena, 4, max(inner, 8) + 14, max(inner, 8) + 14, gap=8)   # pens are not moated: room between them
    gens = {
        "fed_roomy": pen_runner(s, "fed_roomy", zones[0], inner, 1, fed=True, shot=False),
        "hungry_small": pen_runner(s, "hungry_small", zones[1], small, 1, fed=False, shot=False),
        "shot": pen_runner(s, "shot", zones[2], inner, 1, fed=True, shot=True),
        "granite3": pen_runner(s, "granite3", zones[3], small, 3, fed=False, shot=True, granite=True),
    }
    res, spent = run_shared(gens, s.advance, s.now, log=s.say)
    s.timing["B7_ticks"] = spent
    for name, r in res.items():
        if r != "done":
            s.row("A5_%s_crashed" % name, "A5", "UNMEASURED", "HARNESS", dict(result=r), "B7")


def pen_runner(s, name, zone, inner, thick, fed, shot, granite=False):
    stuff = "BlocksGranite" if granite else "WoodLog"
    ln = Lane("pen_" + name, "A5", "B3", "pen", zone, cast="B3", sealed=False)     # the ring IS the seal
    x0, z0 = zone[0] + 6, zone[1] + 6
    for t in range(thick):
        for i in range(-t - 1, inner + t + 1):
            for c in ((x0 + i, z0 - t - 1), (x0 + i, z0 + inner + t), (x0 - t - 1, z0 + i), (x0 + inner + t, z0 + i)):
                ln.walls[c] = ("Wall", stuff)
    s.clear(zone)
    s.kill_strays(zone)
    s.build(ln)
    cx, cz = x0 + inner // 2, z0 + inner // 2
    r = s.call("jawa/spawn_pawn", kindDef=CAST["B3"][0], x=cx, z=cz, faction="none", count=1)
    pid = ((r.get("pawns") or [{}])[0]).get("id")
    if pid is None:
        s.row("A5_%s" % name, "A5", "UNMEASURED", "HARNESS", dict(why="spawn failed"), "B7")
        return
    info = read_creature(s, pid, "B3")
    food_ok = s.call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=1.0 if fed else 0.0).get("success") is True
    pen_cells = (inner + 2 * thick) ** 2
    walls_n = len(ln.walls)
    area_cells = inner * inner
    confined = area_cells < 6 * info.get("p", 3) ** 2
    rest0 = restless_of(s, pid)
    t0 = s.now()
    if shot:
        yield Wait(300)
        s.call("jawa/damage", damageDef="Bullet", amount=5, thingId=pid, allowColonists=False)
    out_t = None
    steps = 0
    budget = 2400 if not (s.args.long_restless and not fed) else 120000
    rest_hist = []
    while s.now() - t0 < budget:
        yield Wait(300)
        steps += 1
        pw = s.pawns().get(str(pid))
        if pw is None or pw["dead"]:
            break
        c = pw["cell"]
        if c and not (x0 - 1 <= c[0] <= x0 + inner and z0 - 1 <= c[1] <= z0 + inner):
            out_t = s.now() - t0
            break
        rest_hist.append((s.now() - t0, restless_of(s, pid)))
        if not fed and not s.args.long_restless and s.now() - t0 >= 2400:
            break
    left = len([t for t in s.things(zone, "Wall")])
    rest = restless_of(s, pid)
    rate = None
    if len(rest_hist) >= 2 and rest_hist[-1][0] > rest_hist[0][0]:
        rate = (rest_hist[-1][1] - rest_hist[0][1]) / float(rest_hist[-1][0] - rest_hist[0][0])
    detail = dict(P=info.get("p"), area=area_cells, six_p2=6 * info.get("p", 3) ** 2, confined=confined, fed_set=food_ok,
                  restless_start=rest0, restless_end=rest, rate_per_tick=rate, out_tick=out_t, walls_left=left, walls=walls_n)
    rid = "A5_%s" % name
    if name == "fed_roomy":
        ok = out_t is None and left == walls_n
        s.row(rid, "A5", "PASS" if ok else "FAIL", "MOD", dict(detail, bar="calm, fed, unconfined: stays; no wall dies"), "B7")
    elif name == "hungry_small":
        if rate is None or rest0 is None:
            s.row(rid, "A5", "UNMEASURED", "HARNESS", dict(detail, why="Restless line unreadable (inspect 'Restless N%')"), "B7")
        else:
            day = 60000.0
            expect_rate = (1 if confined else 0) + (1 if not fed else 0)
            ok = rate * day > 0.5 * expect_rate
            ticks_full = ((1.0 - (rest or 0.0)) / rate) if rate > 0 else None
            s.row(rid, "A5", "PASS" if ok else "FAIL", "MOD",
                  dict(detail, causes=expect_rate, bar="rises ~1.0/day per cause (rate x 60000 > 0.5 x causes)", inferred_ticks_to_100pct=ticks_full,
                       breakout_at_100="INFERRED, not observed (pass --long-restless to wait)"), "B7")
        if s.args.long_restless:
            s.row("A5_breakout_at_100", "A5", "PASS" if out_t is not None else "FAIL", "MOD", dict(out_tick=out_t, restless_end=rest), "B7")
        else:
            s.row("A5_breakout_at_100", "A5", "UNMEASURED", "OWED",
                  dict(why="a full meter is %s ticks at the measured rate; the rate row above is the evidence, the breakout itself waits for --long-restless "
                           "or a quiet half hour" % (int((1.0 - (rest or 0.0)) / rate) if rate else "?")), "B7")
    elif name == "shot":
        ok = out_t is not None and out_t <= 300 + 1800
        s.row(rid, "A5", "PASS" if ok else "FAIL", "MOD", dict(detail, bar="shot, it breaks out within 30 s (1800 ticks) of the shot"), "B7")
    else:
        ok = out_t is None and left == walls_n
        s.row(rid, "A5", "PASS" if ok else "FAIL", "MOD", dict(detail, bar="3-thick granite ring: never breaks out, no wall dies (hold at B 3)"), "B7")
    s.kill_pawns([pid])
    s.clear(zone)


def restless_of(s, pid):
    ok, txt = s.static("Restless", str(pid))
    v = fnum(txt) if ok else None
    if v is not None:
        return v
    m = re.search(r"Restless\s+(\d+)%", " ".join(s.inspect(pid)))
    return int(m.group(1)) / 100.0 if m else None


# ============================================================================ catalog, plan, verify lines
CRITERIA = [
    # (criterion, block, text, ticks, wall s): ESTIMATED from the pass-3 mock (bridge calls x CALL_S + ticks / TPS_STEP), with
    # each block's ticks taken as its longest lane BUDGET (the mock walks faster than a live creature)
    ("A2", "B2", "canyon lanes: open-sky rock gaps 1..P wide per creature; S>=P x1 +-10%, 0.5P<=S<P at squeeze cost +-15%, S<0.5P never used, rock unchanged", 1200, 100),
    ("A3", "B3", "thickness ladder: wood/granite, open/roofed, 1..B thick (compressed); broke through / smashed (blow count) / held per design section 3", 2300, 340),
    ("A4", "B4", "sandwich straight+diagonal (smashed), five solid (held), plug between rock outcrops (wood broken, rock untouched)", 1800, 55),
    ("A6", "B5", "scrape: 10 crossings of a 2-wide built gap; roof pair granite open vs roofed blow counts", 2500, 85),
    ("A7", "B6", "door wild vs tamed, concurrency, wall destroyed en route; save/reload mid-job owed", 2300, 70),
    ("A5", "B7", "pen: calm fed stays, hungry restlessness rate, shot breaks out in 30 s, 3-thick granite never", 2700, 60),
    ("A8", "B1", "defaults read back, settings dialog group labels, wall and creature inspect lines", 0, 10),
]
BLOCKS = [
    dict(id="B0", title="preflight: tier truth, cast read live, rock probe, bars from live settings"),
    dict(id="B1", title="A8 defaults + settings dialog (zero tick)"),
    dict(id="B2", title="A2 canyon lanes (natural rock)"),
    dict(id="B3", title="A3 thickness ladder + A8 wall/creature inspect lines"),
    dict(id="B4", title="A4 sandwich, five solid, plug"),
    dict(id="B5", title="A6 scrape, roof pair"),
    dict(id="B6", title="A7 door, concurrency, wall destroyed en route"),
    dict(id="B7", title="A5 pen, restlessness, shot, granite ring"),
]
ORDER = tuple(b["id"] for b in BLOCKS)


def verdicts(rows):
    by = {}
    for r in rows:
        if r["criterion"] in ("-", None) or r["cls"] == "OWED" or r["status"] == "SKIP":
            continue
        by.setdefault(r["criterion"], []).append(r)
    out = {}
    for k, rs in by.items():
        sts = [r["status"] for r in rs]
        if "FAIL" in sts:
            res = "fail"
        elif all(x == "PASS" for x in sts):
            res = "pass"
        elif "PASS" in sts:
            res = "partial"
        else:
            continue
        out[k] = (res, [r["id"] for r in rs])
    return out


def write_verify_lines(s):
    p = os.path.join(s.out_dir, "verify_lines.txt")
    ev = os.path.relpath(os.path.join(s.out_dir, "session.json"), REPO)
    lines = []
    if s.mock or s.env.get("partial"):
        # A mock proves the script's paths, never the game; a partial run is never recordable. No ledger-ready line for either.
        with open(p, "w", encoding="utf-8") as f:
            f.write("# no verify lines: %s run\n" % ("mock" if s.mock else "partial (--only/--skip)"))
        return p, 0
    for cid, (res, ids) in sorted(verdicts(s.rows).items()):
        lines.append('python3 src/RimMandrake/rimflow/cli.py verify %s --criterion %s --result %s --config %s --level L2 --evidence %s '
                     '--why "walls_slots_live rows %s"' % (ITEM, cid, res, s.env.get("config", "UNMEASURED"), ev, ",".join(ids)[:200]))
    with open(p, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return p, len(lines)


def print_plan(s, sel):
    s.say("WALLS-AND-SLOTS LIVE SESSION PLAN  arena on %dx%d (one region, cleared and reused by every block):" % s.size)
    s.say("  cast (planned breadth, read live in B0): " + ", ".join("%s=%s(B%d)" % (k, v[0], PLANNED_B[k]) for k, v in CAST.items()))
    total = 0.0
    for b in BLOCKS:
        if b["id"] not in sel:
            continue
        crit = [c for c in CRITERIA if c[1] == b["id"]]
        t = sum(c[3] for c in crit)
        w = sum(c[4] for c in crit)
        total += w
        s.say("%-3s %-70s ~%5d ticks ~%4.0f s (ESTIMATED)" % (b["id"], b["title"][:70], t, w))
        for c in crit:
            s.say("      %-3s %s" % (c[0], c[2][:110]))
    s.say("ESTIMATED wall for the selected blocks: %.0f s (+ one cold load of the flowworks_hugethings tier, ESTIMATED 60-120 s, + one quicktest map)" % total)
    return total


# ============================================================================ the fake game (offline; the script's own paths)
class FakeHugeGame(object):
    """Offline stand-in: a grid world, creatures that cross a lane by the kernel mirror, the tools this script calls. A mock run
    proves the script's PATHS, never the game (the rows say so). --mock-fault flips one behaviour so the matching rows FAIL:
    hold (nothing holds), squeeze (no slowdown), roof (roof does nothing), rock (rock is damaged), scrape (no scrape),
    defaults (a setting differs); unsealed (the stager paints no moat: pass 2's open lanes, walked round, rows must be SITE).
    The fake's Reachability is a 1-cell flood fill (reach_around): a goal it can reach is walked round, as the real decider
    does when the detour is under titanClearingDetourFactor."""

    TPC = 15      # base ticks per cell

    def __init__(self, fault=None, size=(250, 250)):
        self.fault, self.size = fault, size
        self.tick = 0
        self.things = {}          # cell -> dict(id, def, stuff, hp, maxhp, faction)
        self.roof = set()
        self.pawns = {}
        self.next_id = 1
        self.settings = {k: str(v) for k, v in DEFAULTS.items()}
        if fault == "defaults":
            self.settings["blowDamagePerBreadth"] = "30.0"
        self.rock_placeable = fault != "norock"
        self.last_scrape = {}
        self.water = set()        # Impassable terrain cells (the lanes' moats)

    # ---- tool dispatch
    def call(self, tool, **kw):
        fn = getattr(self, "t_" + tool.replace("jawa/", "j_").replace("rimworld/", "r_"), None)
        if fn is None:
            return {"success": True}
        return fn(**kw)

    def ticks(self, n):
        self.advance(n)
        return {"success": True}

    def new_id(self, pre):
        self.next_id += 1
        return "%s%d" % (pre, self.next_id)

    def t_j_running_mods(self, **kw):
        return {"success": True, "packageIds": ["brrainz.harmony", "ludeon.rimworld", MOD_ID, LARGEPAWNS_ID, "mandrake.rm.flowworks", "brrainz.rimbridgeserver", "mandrake.rm.biomes"]}

    def t_j_map_info(self, **kw):
        return {"success": True, "sizeX": self.size[0], "sizeZ": self.size[1], "ticksGame": self.tick}

    def t_j_mod_settings_field(self, typeName=None, action="get", field=None, value=None, **kw):
        if action == "get":
            return {"success": field in self.settings, "value": self.settings.get(field)}
        self.settings[field] = str(value)
        return {"success": True}

    def t_j_spawn_batch(self, ops="", **kw):
        n = 0
        for op in str(ops).split(";"):
            d, rest = op.split(":")
            x, z = (int(v) for v in rest.split(",")[:2])
            if d == ROCK and not self.rock_placeable:
                continue
            self.things[(x, z)] = dict(id=self.new_id("T"), d=d, stuff=None, hp=1e9, maxhp=1e9, faction=None)
            n += 1
        return {"success": True, "count": n}

    def t_j_build_batch(self, ops="", stuff="WoodLog", **kw):
        n = 0
        for op in str(ops).split(";"):
            d, rest = op.split(":")
            x, z = (int(v) for v in rest.split(",")[:2])
            hp = {"Wall": {"WoodLog": WOOD_HP, "BlocksGranite": GRANITE_HP}.get(stuff, WOOD_HP), "Door": 130.0}.get(d, WOOD_HP)
            self.things[(x, z)] = dict(id=self.new_id("T"), d=d, stuff=stuff, hp=hp, maxhp=hp, faction="Colony")
            n += 1
        return {"success": True, "placed": n}

    def t_j_set_terrain_batch(self, ops="", **kw):
        n = 0
        for op in str(ops).split(";"):
            d, rest = op.split(":")
            x, z, w, h = (int(v) for v in rest.split(","))
            for i in range(x, x + w):
                for j in range(z, z + h):
                    (self.water.add if d == MOAT else self.water.discard)((i, j))
                    n += 1
        return {"success": True, "cellsChanged": n, "cellsFailedVerify": 0}

    def t_j_set_roof_batch(self, ops="", **kw):
        d, rest = str(ops).split(":")
        x, z, w, h = (int(v) for v in rest.split(","))
        for i in range(x, x + w):
            for j in range(z, z + h):
                (self.roof.add if d != "None" else self.roof.discard)((i, j))
        return {"success": True}

    def t_j_destroy_batch(self, rects="", categories="All", **kw):
        x, z, w, h = (int(v) for v in str(rects).split(",")[:4])
        for c in [c for c in self.things if x <= c[0] < x + w and z <= c[1] < z + h]:
            if categories == "Building" and self.things[c]["d"] == ROCK:
                continue
            del self.things[c]
        return {"success": True}

    def t_j_list_things(self, rect=None, defName=None, **kw):
        x, z, w, h = (int(v) for v in str(rect).split(",")[:4])
        want = set(str(defName).split(",")) if defName else None
        out = []
        for c, t in self.things.items():
            if x <= c[0] < x + w and z <= c[1] < z + h and (want is None or t["d"] in want):
                # the live shape (probed 2026-10-19): x/z at the thing's top level, no "position"
                out.append(dict(id=t["id"], **{"def": t["d"]}, x=c[0], z=c[1], hitPoints=t["hp"], maxHitPoints=t["maxhp"],
                                stuff=t["stuff"], faction=t["faction"]))
        return {"success": True, "things": out, "countMatched": len(out)}

    def t_j_spawn_pawn(self, kindDef=None, x=0, z=0, faction="hostile", **kw):
        bs = {"Elephant": 4.0, "RM_Hwelgrue": 8.0, "RM_Totchak": 14.0, "RM_Oommok": 36.0}.get(kindDef, 1.0)
        pid = self.new_id("P")
        b = breadth_of(bs)
        f = 2 if bs >= 2.5 else 1
        f = 3 if bs >= 4.5 else f
        f = 4 if bs >= 10 else f
        self.pawns[pid] = dict(id=pid, kind=kindDef, x=x, z=z, faction=faction, b=b, f=f, goal=None, state="walk", ticks=0, dead=False,
                               prog=0.0, restless=0.0, fed=True, blow_t=0, job="", cross=None, fled=False)
        return {"success": True, "pawns": [{"id": pid}]}

    def t_j_list_pawns(self, rect=None, faction=None, **kw):
        box = [int(v) for v in str(rect).split(",")[:4]] if rect else None
        out = []
        for p in self.pawns.values():
            if box and not (box[0] <= p["x"] < box[0] + box[2] and box[1] <= p["z"] < box[1] + box[3]):
                continue
            if faction == "nonplayer" and p["faction"] == "player":
                continue
            out.append(dict(id=p["id"], kind=p["kind"], faction=p["faction"], dead=p["dead"], downed=False,
                            position={"x": p["x"], "z": p["z"]}))
        return {"success": True, "pawns": out}

    def t_j_pawn_need(self, pawn=None, need=None, level=1.0, **kw):
        if pawn in self.pawns and need == "Food":
            self.pawns[pawn]["fed"] = level > 0.5
        return {"success": True}

    def t_j_damage(self, thingId=None, **kw):
        if thingId in self.pawns:
            if kw.get("damageDef") == "Bomb":
                self.pawns[thingId]["dead"] = True
            else:
                self.pawns[thingId]["fled"] = True
        return {"success": True}

    def t_j_kill_hostiles(self, **kw):
        return {"success": True}

    def t_j_ordered_job(self, pawnId=None, targetAX=None, targetAZ=None, **kw):
        p = self.pawns.get(pawnId)
        if p:
            p["goal"] = (targetAX, targetAZ)
            if p["state"] in ("done", "walk", "hold"):
                p["state"] = "walk"
        return {"success": True}

    def t_j_inspect_string(self, thingIds=None, **kw):
        p = self.pawns.get(str(thingIds))
        if p:
            lines = []
            if p["state"] == "squeeze":
                lines.append("squeezing through a gap.")
            if p["state"] == "smash":
                lines.append("smashing through Wall.")
            lines.append("Restless %d%%" % int(p["restless"] * 100))
            return {"success": True, "things": [{"id": p["id"], "inspect": lines}]}
        for c, t in self.things.items():
            if t["id"] == str(thingIds):
                run = 1
                x = c[0]
                while (x + run, c[1]) in self.things and self.things[(x + run, c[1])]["d"] == "Wall":
                    run += 1
                run_l = 0
                while (x - run_l - 1, c[1]) in self.things and self.things[(x - run_l - 1, c[1])]["d"] == "Wall":
                    run_l += 1
                th = run + run_l
                up = stops_up_to(th)
                line = ("Holds big creatures up to breadth %d (%d thick here)" % (up, th)) if up >= 2 else "Too thin to hold a big creature (%d thick here)" % th
                return {"success": True, "things": [{"id": t["id"], "inspect": [line]}]}
        return {"success": True, "things": []}

    def t_j_static_call(self, type=None, method=None, args="", **kw):
        if method in ("Breadth", "Footprint", "Passage"):
            p = self.pawns.get(str(args))
            if not p:
                return {"success": False, "error": "no pawn"}
            v = {"Breadth": p["b"], "Footprint": p["f"], "Passage": passage(p["b"], p["f"])}[method]
            return {"success": True, "result": str(v)}
        if method == "Restless":
            p = self.pawns.get(str(args))
            return {"success": bool(p), "result": "%.4f" % p["restless"] if p else "error"}
        if method == "CreatureLine":
            p = self.pawns.get(str(args))
            knobs = dict(hold_line=1.0, per=100.0)
            return {"success": True, "result": creature_line(p["b"], passage(p["b"], p["f"]), knobs, True)}
        if method == "RoofedWall":
            parts = str(args).split("|")
            x, z = (int(v) for v in parts[1].split(","))
            ra = ta = rb = tb = 0
            for d in (1, 2):
                for lat in range(-2, 3):
                    ta += 1; tb += 1
                    ra += (x - d, z + lat) in self.roof
                    rb += (x + d, z + lat) in self.roof
            ok = (ta and 2 * ra >= ta) or (tb and 2 * rb >= tb)
            if self.fault == "roof":
                ok = not ok
            return {"success": True, "result": "True" if ok else "False"}
        return {"success": False, "error": "unknown"}

    def t_r_open_mod_settings(self, **kw):
        return {"success": True}

    def t_r_get_ui_layout(self, **kw):
        labels = list(keyed_labels().values())
        if self.fault == "label":
            labels = labels[1:]
        return {"success": True, "elements": [{"label": l} for l in labels]}

    def t_j_take_screenshot(self, **kw):
        return {"success": True, "filePath": "mock.png"}

    # ---- the simulation
    def knobs(self):
        g = lambda f: float(self.settings[f])
        return dict(per=g("trampleBudgetPerBreadth"), blow=g("blowDamagePerBreadth"), hold_line=g("holdLineFactor"),
                    roof_hp=g("roofWallHpFactor"), roof_dmg=g("roofWallDamageFactor"), at_half=g("squeezeSlowdownAtHalf"),
                    b2_breaks=self.settings["breadth2BreakingEnabled"].lower() != "false")

    def advance(self, n):
        for _ in range(int(n)):
            self.tick += 1
            for p in self.pawns.values():
                if not p["dead"]:
                    self.step(p)
        return {"success": True}

    def roofed(self, c):
        return self.t_j_static_call(method="RoofedWall", args="current|%d,%d|true" % c).get("result") == "True"

    def free(self, c):
        return c not in self.things and c not in self.water

    def reach_around(self, p, also_blocked=()):
        """BFS (1-cell, 4-way) from the creature to its goal over cells free of things and water, within 40 cells: the fake's
        Reachability. A reachable goal is walked round, as the real decider does when the detour is under 2.5x (pass 2)."""
        start, goal = (p["x"], p["z"]), tuple(p["goal"])
        blocked = set(also_blocked)
        seen, todo = {start}, [start]
        while todo:
            c = todo.pop()
            if c == goal:
                return True
            for n in ((c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)):
                if (n not in seen and abs(n[0] - start[0]) <= 40 and abs(n[1] - start[1]) <= 40 and self.free(n)
                        and n not in blocked):
                    seen.add(n)
                    todo.append(n)
        return False

    def go_round(self, p):
        p["x"], p["z"] = p["goal"]
        p["state"] = "done"

    def step(self, p):
        kn = self.knobs()
        # restlessness (pen creatures only: a creature with a ring)
        if p["state"] == "hold" or p.get("pen"):
            pass
        if p["goal"] is None:
            self.pen_step(p, kn)
            return
        gx, gz = p["goal"]
        if p["state"] == "done":
            return
        if p["state"] == "smash":
            p["ticks"] += 1
            if p["ticks"] % 60 == 0:
                self.smash_blow(p, kn)
            return
        pw = passage(p["b"], p["f"])
        dx = 1 if gx > p["x"] else -1 if gx < p["x"] else 0
        if p["state"] == "squeeze":
            p["prog"] += 1.0 / (self.TPC * p["sq_cost"])
            if p["prog"] >= 1.0:
                p["prog"] = 0.0
                p["x"] += dx
                if self.fault != "scrape":
                    self.scrape(p)
                nx = (p["x"] + dx, p["z"])
                if self.free(nx) and self.span(nx, pw) >= pw:
                    p["state"] = "walk"
            return
        if p["state"] == "hold":
            return
        if dx == 0:
            p["state"] = "done" if abs(gz - p["z"]) <= 1 else "walk"
            if abs(gz - p["z"]) > 1:
                p["z"] += 1 if gz > p["z"] else -1
            return
        nxt = (p["x"] + dx, p["z"])
        if self.free(nxt):
            sp = self.span(nxt, pw)
            if sp < pw:
                band = gap_band(sp, pw)
                if self.fault == "rock":       # the broken mod: it chews a rock cell beside its gap
                    for dz in (1, -1, 2, -2):
                        if self.things.get((nxt[0], nxt[1] + dz), {}).get("d") == ROCK:
                            del self.things[(nxt[0], nxt[1] + dz)]
                            break
                if band == "squeeze" and self.settings["squeezeEnabled"].lower() != "false":
                    cost = squeeze_cost(sp, pw, kn["at_half"]) if self.fault != "squeeze" else 1.0
                    p["state"], p["sq_cost"], p["prog"] = "squeeze", cost, 0.0
                    return
                if band == "narrow" and self.reach_around(p, [(nxt[0], z) for z in range(p["z"] - pw, p["z"] + pw + 1)]):
                    self.go_round(p)       # an open way round the too-narrow gap (an unsealed lane)
                    return
                if band == "narrow":
                    p["state"] = "hold"    # sealed: the too-narrow gap was the only way, and it is never used
                    return
                if band == "squeeze":
                    x = nxt[0]
                    while (x, p["z"]) not in self.things and self.span((x, p["z"]), pw) < pw and abs(x - p["x"]) < 40:
                        x += dx
                    while self.span((x, p["z"]), pw) < pw and abs(x - p["x"]) < 60:
                        x += dx
                    p["x"] = x
                    p["prog"] = -float(CANYON_H * self.TPC)
                    return
            p["prog"] += 1.0
            if p["prog"] >= self.TPC:
                p["prog"] = 0.0
                p["x"] += dx
            return
        self.contact(p, dx, kn)

    def span(self, c, cap):
        """Free cells across z around c, counted up to cap (the gap's clear width S)."""
        s = 1
        for sign in (1, -1):
            k = 1
            while s < cap and self.free((c[0], c[1] + sign * k)):
                s += 1
                k += 1
        return s

    def scrape(self, p):
        for dz in (-1, 1):
            for off in range(0, p["f"] + 1):
                c = (p["x"], p["z"] + dz * (off + 1))
                t = self.things.get(c)
                if t and t["d"] == "Wall" and self.tick - self.last_scrape.get(c, -999) >= 60:
                    self.last_scrape[c] = self.tick
                    t["hp"] -= 20.0
                    if t["hp"] <= 0:
                        del self.things[c]

    def contact(self, p, dx, kn):
        b, pw = p["b"], passage(p["b"], p["f"])
        if p["state"] != "hold" and self.reach_around(p):
            self.go_round(p)
            return
        cells = []
        x = p["x"] + dx
        gapless = 0
        while gapless < 3 and len(cells) < 40:
            if (x, p["z"]) in self.things:
                cells.append((x, p["z"]))
                gapless = 0
            else:
                gapless += 1
            x += dx
        rock = [c for c in cells if self.things[c]["d"] == ROCK]
        if rock and self.fault == "rock":
            for c in rock:
                self.things[c]["hp"] -= 1.0
                if True:
                    del self.things[c]
            return
        if rock:
            self.canyon(p, dx, kn, pw, rock)
            return
        layers = sorted(set(c[0] for c in cells), key=lambda v: abs(v - p["x"]))
        wood_like = [self.things[c] for c in cells]
        roofed = any(self.roofed(c) for c in cells[:1])
        if self.fault == "roof":
            roofed = False
        thick = 0
        for c0 in layers:
            thick = max(thick, len([v for v in layers if c0 <= v < c0 + b]) if dx > 0 else len([v for v in layers if c0 - b < v <= c0]))
        hp_layers = {}
        for c in cells:
            hp_layers[c[0]] = max(hp_layers.get(c[0], 0.0), counted_hp(self.things[c]["maxhp"], roofed, kn["roof_hp"]))
        hp_sum = sum(hp_layers.values())
        door_wild = any(self.things[c]["d"] == "Door" for c in cells)
        if self.fault == "hold":
            verdict = "smash"
        else:
            verdict = decide(b, thick, hp_sum, False, kn["b2_breaks"], kn["hold_line"], kn["per"])
        if p["faction"] == "player":
            verdict = "protected"
        if len(cells) == 1 and self.things[cells[0]]["d"] == "Door" and p["faction"] == "player" and gap_band(1, pw) == "squeeze":
            p["state"], p["sq_cost"], p["sq_end"], p["sq_z_exit"], p["prog"] = "squeeze", squeeze_cost(1, pw, kn["at_half"]), cells[0][0] + 1, p["z"], 0.0
            return
        if verdict in ("hold", "protected", "forbidden", "open"):
            p["state"] = "hold"
            if verdict == "hold" and False:
                pass
            return
        p["cross"] = dict(cells=cells, roofed=roofed, verdict=verdict)
        if verdict == "break":
            p["state"] = "smash_break"
            for c in cells:
                self.things.pop(c, None)
            p["x"] = cells[-1][0] + dx
            p["state"] = "walk"
            return
        p["state"] = "smash"
        p["ticks"] = 0

    def smash_blow(self, p, kn):
        cr = p["cross"]
        cells = [c for c in cr["cells"] if c in self.things]
        if not cells:
            p["state"] = "walk"
            p["x"] = max(c[0] for c in cr["cells"]) + 1 if p["goal"] and p["goal"][0] > p["x"] else p["x"]
            return
        near = min(cells, key=lambda c: abs(c[0] - p["x"]))
        dmg = blow_damage(p["b"], cr["roofed"], kn["blow"], kn["roof_dmg"])
        t = self.things[near]
        t["hp"] -= dmg
        if t["hp"] <= 0:
            del self.things[near]
        if not [c for c in cr["cells"] if c in self.things]:
            p["state"] = "walk"
            p["x"] = max(c[0] for c in cr["cells"]) + (1 if p["goal"][0] > p["x"] else -1)

    def canyon(self, p, dx, kn, pw, rock):
        # find the gap in this rock block: the run of rows free across the block's x range nearest the creature (the moat
        # rows are not free, so a sealed lane's only run is its gap)
        xs = sorted(set(c[0] for c in rock))
        rows = [z for z in range(p["z"] - 12, p["z"] + 13) if all(self.free((x, z)) for x in xs)]
        runs, cur = [], []
        for z in rows:
            if cur and z != cur[-1] + 1:
                runs.append(cur)
                cur = []
            cur.append(z)
        if cur:
            runs.append(cur)
        s, gz = 0, p["z"]
        if runs:
            run = min(runs, key=lambda r: min(abs(z - p["z"]) for z in r))
            s, gz = len(run), run[len(run) // 2]
            rows = run
        band = gap_band(s, pw) if s else "narrow"
        if band == "walk" or (band == "squeeze" and self.settings["squeezeEnabled"].lower() != "false"):
            cost = 1.0 if band == "walk" else squeeze_cost(s, pw, kn["at_half"]) if self.fault != "squeeze" else 1.0
            p["z"] = gz
            p["state"] = "squeeze"
            p["sq_cost"] = cost
            p["sq_end"] = xs[-1] + 1
            p["sq_z_exit"] = gz
            p["prog"] = 0.0
            p["x"] = xs[0] - 1 if dx > 0 else p["x"]
            return
        # too narrow: round the block if anything is open (an unsealed lane), else it stays put (the sealed lane's verdict)
        gap = [(x, z) for x in xs for z in rows] if rows else []
        if self.reach_around(p, gap):
            self.go_round(p)
        else:
            p["state"] = "hold"

    def pen_step(self, p, kn):
        # restlessness for creatures spawned in a ring: confined (reachable area small) and/or hungry
        ring = [c for c, t in self.things.items() if abs(c[0] - p["x"]) < 20 and abs(c[1] - p["z"]) < 20 and t["d"] == "Wall"]
        if not ring:
            return
        xs = [c[0] for c in ring]
        zs = [c[1] for c in ring]
        inner = (max(xs) - min(xs) - 1) * (max(zs) - min(zs) - 1)
        confined = inner < 6 * passage(p["b"], p["f"]) ** 2
        causes = (1 if confined else 0) + (0 if p["fed"] else 1)
        if causes:
            p["restless"] = min(1.0, p["restless"] + causes / 60000.0)
        else:
            p["restless"] = max(0.0, p["restless"] - 0.5 / 60000.0)
        full = p["restless"] >= 1.0 or p["fled"]
        thick_walls = [c for c in ring if self.things[c]["stuff"] == "BlocksGranite"]
        if full and not thick_walls and self.tick % 60 == 0:
            # break out through the nearest wall on the east side
            east = [c for c in ring if c[0] == max(xs)]
            if east:
                tgt = min(east, key=lambda c: abs(c[1] - p["z"]))
                self.things.pop(tgt, None)
                p["x"] = tgt[0] + 1


# ============================================================================ driver
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--mock-fault", default=None, choices=[None, "hold", "squeeze", "roof", "rock", "scrape", "defaults", "label", "norock",
                                                           "unsealed"])
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--table", action="store_true", help="print design section 3 from the kernel mirror and exit")
    ap.add_argument("--only", default="")
    ap.add_argument("--skip", default="")
    ap.add_argument("--full-ladder", action="store_true")
    ap.add_argument("--wave", type=int, default=64)
    ap.add_argument("--long-restless", action="store_true")
    ap.add_argument("--frame-budget-ms", type=float, default=150.0)
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args(argv)
    bad = selftest()
    if bad:
        print("KERNEL MIRROR SELFTEST FAILED (the script's bars disagree with design section 3/4): " + "; ".join(bad))
        return 3
    if a.table:
        print("B   lone wood  roofed wood  lone granite  roofed granite   holds at")
        for b in (2, 3, 4, 5, 6, 10):
            cells = []
            for hp, rf in ((WOOD_HP, False), (WOOD_HP, True), (GRANITE_HP, False), (GRANITE_HP, True)):
                e = lane_expect(b, 1, hp, rf)
                cells.append("%s%s" % (e["verdict"], (" %d" % e["blows"]) if e["blows"] else ""))
            print("%-3d %-11s %-12s %-13s %-15s %d" % (b, *cells, hold_thickness(b)))
        return 0
    if a.list:
        print(json.dumps(dict(blocks=BLOCKS, criteria=CRITERIA, cast=CAST), indent=1))
        return 0
    sel = [b for b in ORDER if (not a.only or b in a.only.split(",") or any(c[1] == b and c[0] in a.only.split(",") for c in CRITERIA))
           and b not in a.skip.split(",")]
    if "B0" not in sel and not a.dry_run:
        sel.insert(0, "B0")
    stamp = time.strftime("%Y%m%dT%H%M%S")
    out_dir = a.out_dir or os.path.join(REPO, "Transient", "walls_slots_live", ("mock_" if a.mock else "dry_" if a.dry_run else "") + stamp)
    os.makedirs(out_dir, exist_ok=True)
    s = Session(a, out_dir)
    s.knobs = dict(per=100.0, blow=20.0, hold_line=1.0, roof_hp=1.5, roof_dmg=0.6667, at_half=2.0, b2_breaks=True)
    s.canyon, s.roof_blows = {}, {}
    s.arena = plan_arena(s.size)
    s.env["partial"] = bool(a.only or a.skip)
    print_plan(s, sel)
    if a.dry_run:
        s.say("DRY RUN: no bridge touched. Kernel mirror selftest: clean (section 3 table and section 4 costs).")
        return 0
    if a.mock:
        s.B = FakeHugeGame(fault=a.mock_fault)
    else:
        import validation_core as V
        s.B = V.Bridge()
        try:
            V.log_revive(s.B)
            V.tap_start(s.B)
        except Exception as ex:  # noqa: BLE001
            s.notes.append("log_revive/tap_start: %s" % ex)
    steps = dict(B0=b0_preflight, B1=b1_a8_defaults, B2=b2_canyons, B3=lambda s_: (b3_ladder(s_), wall_inspect_rows(s_)),
                 B4=b4_sandwich_plug, B5=b5_scrape_roof, B6=b6_door_concurrency_saves, B7=b7_pen)
    t_start = time.time()
    try:
        for bid in sel:
            s.say("=== %s %s  (t+%.0fs, tick %s)" % (bid, next(b["title"] for b in BLOCKS if b["id"] == bid), time.time() - t_start, s.now()))
            w0, c0 = time.time(), s.calls
            try:
                steps[bid](s)
            except Exception as ex:  # noqa: BLE001 - recorded, the session goes on
                s.say(traceback.format_exc())
                s.row("%s_crashed" % bid, "-", "UNMEASURED", "HARNESS", dict(error=str(ex)), bid)
            s.timing[bid] = round(time.time() - w0, 1)
            s.timing["%s_calls" % bid] = s.calls - c0
    finally:
        s.restore_settings()
        s.call("jawa/wild_spawner_block", action="release")
    s.timing["total_s"] = round(time.time() - t_start, 1)
    s.timing["bridge_calls"] = s.calls
    s.timing["ticks_total"] = sum(v for k, v in s.timing.items() if k.endswith("_ticks"))
    s.save()
    p, n = write_verify_lines(s)
    counts = {}
    for r in s.rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    s.say("DONE %s rows %s  verify lines %d -> %s  session %s" % (len(s.rows), counts, n, os.path.relpath(p, REPO),
                                                                  os.path.relpath(os.path.join(out_dir, "session.json"), REPO)))
    eyes = sorted({r["id"] for r in s.rows if r.get("eyes")})
    s.say("OWNER EYES (%d): %s" % (len(eyes), "; ".join(eyes)))
    s.say("A mock verdict proves the script's paths, never the game." if a.mock else "Partial run: not recordable." if s.env["partial"] else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
