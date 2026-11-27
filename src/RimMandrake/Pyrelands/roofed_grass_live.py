"""sc_roofed_grass_declines (bar roofed_grass_declines_visibly): one chain of the Pyrelands suite (validation.py registers it
through register()). Kind A. The owner, 2026-11-26: "the grass just suddenly all dies at the same time ... it doesn't turn
into dead grass, just... barren nothing". Claim: grass under a roof declines visibly, each plant at its own pace, and leaves
dead grass that a colonist can cut and that crumbles on its own clock, again not all at once.

  roofed_grass_declines   A fresh load of the registered site. Room A: a 12 x 16 patch of grown ember grass inside a steel
                          wall ring with a door on its west wall, lit by four refuelled TorchLamps, roofed once the patch
                          stands. Patch B: a 5 x 5 walled, unroofed control 4 cells east. One plant of A (the subject) is
                          damaged to 1 HP before the roof goes on. Weather locked Clear, fire put out.
                            wither    hourly until A is empty or the death deadline is past: per plant its hit points and
                                      inspect line; A's dead grass; the roof on A and B; fire. Every roofed plant shows a
                                      line, reads wilting then withered, loses HP and never gains it, and leaves dead grass
                                      on its cell; no hour takes more than SHARE_MAX of the patch; the deaths spread over at
                                      least WINDOW_MIN_TICKS; none dies before its earliest time; all are dead by the
                                      deadline. B shows no line, loses no HP and no plant.
                            subject   the 1-HP plant is gone, dead grass on its cell, at the first read.
                            cut       a colonist (spawned outside the door) is ordered to cut three dead grass: they go, the
                                      rest stay.
                            crumble   every 4 h until the crumble deadline: no dead grass gone before its earliest time,
                                      HP never rises, all gone by the deadline.
                            captures  play-zoom captures of A at the roofing, mid-wilt, the first deaths, the end of the
                                      wither, after the cut and mid-crumble, each with the room's light read (a dark capture
                                      is UNMEASURED; the look itself is judged by a person on these pictures, Stage 6).

Ranges (the owner's 2026-11-16 rule: the bar's whole range before any code, offline):
  The game varies: witherTicks and crumbleTicks (defs; read here from the defs, not assumed), the plant's id and cell (its
  own death time, RM_RoofWitherKernel.DeathTicks), the long-tick phase of each plant (id hash), the plant's hit points when
  roofed (full: regime "roofed fresh"; low: regime "roofed damaged", the subject), roofed or not (A vs B), the gate.
  Regimes read live here: roofed fresh, roofed damaged, never roofed, dead grass roofed, dead grass cut. Left out live:
  roofed then unroofed, intermittent roof, the gate off and the roster toggle off (T_ROOF_WITHER_OFFLINE and the fuzz
  family wither read them over the kernel; roof_withers reads the gate off and the roster toggle live), quickgrass (the
  same comp and kernel with its own numbers: offline), fire (other bars).
  TorchLamps heat the room: the kernel reads no temperature (roofed and the gate only), so the heat cannot move what this
  chain reads; vanilla plant growth does read it, and growth is not read here.

Run (the pyrelands tier, a free game, python.exe, the bridge env of that game; about 6 game days at speed):
    python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains roofed_grass_declines
Offline: python3 src/RimMandrake/Pyrelands/selftest_pyrelands_roofed_grass_live.py
"""
import datetime
import json
import math
import os
import re
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
GRASS = "RM_FE_Plant_EmberGrass"
DEAD = "RM_FE_DeadGrass"
EMBER_XML = os.path.join(HERE, "Defs", "ThingDefs_Plants", "EmberGrass.xml")
DEAD_XML = os.path.join(HERE, "Defs", "ThingDefs_Plants", "DeadGrass.xml")
COMP_CS = os.path.join(HERE, "Source", "CompWithersUnderRoof.cs")
KEYED_XML = os.path.join(HERE, "Languages", "English", "Keyed", "Pyrelands.xml")
COMP_CLASS = "RimMandrake.Pyrelands.CompProperties_WithersUnderRoof"
CRUMBLE_CLASS = "RimMandrake.Pyrelands.RM_DeadGrassExtension"

LONG = 2000                    # GenTicks.TickLongInterval (vanilla 1.6 decompile); RM_RoofWitherKernel.LongTickTicks
HOUR = 2500                    # one game hour (validation.TEN_HOUR)
SPREAD_LO, SPREAD_HI = 0.6, 1.4    # RM_RoofWitherKernel.SpreadLo / SpreadHi: a plant's death time over witherTicks
SHARE_MAX = 0.15               # selftest_pyrelands_roof_wither.py SHARE_MAX (our reading of the bar), there per long tick;
#                                here per hour (2500 >= one long tick), so an hour's share is at least a long tick's: stricter
WINDOW_MIN_TICKS = 30000       # selftest_pyrelands_roof_wither.py WINDOW_MIN_TICKS: deaths' 5th..95th percentile span
MIN_PATCH = 150                # the selftest's Monte Carlo (printed): the smallest patch whose hourly share stays <= SHARE_MAX
#                                in every trial of a fair kernel is 143 at its seeds; 150 with room. A holds 188 plant cells.
B_MIN = 20                     # our own rule: the control holds at least 20 of its 25 cells
LIT = 0.3                      # GlowGrid.cs:201 GameGlowLitThreshold (0.3): a cell reads Lit above it
NOROOF_B = True                # B and its ring go in the map's no-roof area before the walls rise: B's doorless ring closes a
#                                room, vanilla AutoBuildRoofAreaSetter puts a closed room in the build-roof area unless NoRoof,
#                                and the colonists roof it (ArchSmall 2026-11-27: 16 of B's 25 cells roofed by tick 7500, B
#                                wilting, withers_unevenly UNMEASURED on its own "B cells roofed" guard)
CAL_CELLS = 6                  # our own rule: the first capture's zoom probe, a rect this small at A's middle.
#                                play_zoom.shoot probes its first rect at the zoom the last call left and refuses when that
#                                rect does not fit the screen (ArchSmall 2026-11-27, smoke_weather_live's 50 x 50 sky:
#                                'Requested cell rectangle does not fit in the viewport'); a 6 x 6 rect fit there
LIT_SHARE = 0.9                # our own rule: a capture counts when 90% of A's cells are lit
CUT_TARGETS = 3                # dead grass the colonist is ordered to cut (the rest are the control)
CUT_WAIT = HOUR                # ticks for three cuts: harvestWork 40 each (DeadGrass.xml) and a ~15-cell walk
CRUMBLE_READ = 4 * HOUR        # crumble reads every 4 h (not a spread check: the share there is noted, not judged)
A_W, A_H = 12, 16              # A's interior: every cell within 6 of a wall (vanilla roof support reaches 6.9)
B_S = 5                        # B's interior (roof_withers' 5 x 5)
GAP = 4                        # cells between A's ring and B's ring
LAMPS = ((2, 3), (9, 3), (2, 12), (9, 12))   # TorchLamps in A (offsets from A's corner): precedent TheSump/prove_glasswalk_speed
SUBJECT = (5, 7)               # the 1-HP subject's offset in A: off every lamp
SHOT_AT = {"roofed": 0, "wilting": 12, "first_deaths": 16, "half_dead": 24}   # hour of the wither phase at each capture
PLANT_ENV = "PYRE_PLANT_RGD"   # planted scene faults for the live twin: mass_kill (A's grass destroyed at once, no remains)
OUT_ENV = "RM_RGD_DIR"


# ---- the shipped numbers, read from the defs (never assumed)
def _class_default(field, src=COMP_CS):
    m = re.search(r"public\s+int\s+%s\s*=\s*(\d+)\s*;" % field, open(src, encoding="utf-8").read())
    return int(m.group(1)) if m else None


def shipped_numbers(ember=EMBER_XML, dead=DEAD_XML, comp_cs=COMP_CS):
    """Pure (reads files). -> {witherTicks, grassHp, crumbleTicks, deadHp, remainsDef, sources}. A def's field wins over the
    class default (CompWithersUnderRoof.cs), as the game's XML loader does."""
    out, src = {}, {}
    e = ET.parse(ember).getroot()
    g = [d for d in e.iter("ThingDef") if (d.findtext("defName") or "") == GRASS][0]
    comp = [li for li in g.iter("li") if li.get("Class") == COMP_CLASS][0]
    wt = comp.findtext("witherTicks")
    out["witherTicks"] = int(wt) if wt else _class_default("witherTicks", comp_cs)
    src["witherTicks"] = "EmberGrass.xml" if wt else "CompWithersUnderRoof.cs class default"
    out["remainsDef"] = comp.findtext("remainsDef")
    out["grassHp"] = int(g.find("statBases").findtext("MaxHitPoints"))
    d = ET.parse(dead).getroot()
    base = [x for x in d.iter("ThingDef") if x.get("Name") == "RM_FE_DeadGrassBase"][0]
    ext = [li for li in base.iter("li") if li.get("Class") == CRUMBLE_CLASS]
    ct = ext[0].findtext("crumbleTicks") if ext else None
    out["crumbleTicks"] = int(ct) if ct else _class_default("crumbleTicks", comp_cs)
    src["crumbleTicks"] = "DeadGrass.xml" if ct else "CompWithersUnderRoof.cs class default"
    out["deadHp"] = int(base.find("statBases").findtext("MaxHitPoints"))
    out["sources"] = src
    return out


def keyed_lines(path=KEYED_XML):
    """Pure (reads a file). -> (the wilting line, the withered line), the comp's inspect lines (RM_WithersUnderRoof,
    RM_WitheredUnderRoof)."""
    r = ET.parse(path).getroot()
    return r.findtext("RM_WithersUnderRoof"), r.findtext("RM_WitheredUnderRoof")


def stage_of_lines(lines, keyed):
    """Pure. A plant's inspect lines -> 2 withered, 1 wilting (or roofed), 0 no line."""
    wilt, withered = keyed
    text = "\n".join(str(x) for x in lines or [])
    if withered and withered in text:
        return 2
    if wilt and wilt in text:
        return 1
    return 0


# ---- the scene's geometry
def cells_of(rect):
    x, z, w, h = rect
    return [(x + i, z + j) for j in range(h) for i in range(w)]


def ring_of(rect):
    """Pure. The wall ring one cell outside `rect`."""
    x, z, w, h = rect
    return [(cx, z - 1) for cx in range(x - 1, x + w + 1)] + [(cx, z + h) for cx in range(x - 1, x + w + 1)] \
        + [(x - 1, cz) for cz in range(z, z + h)] + [(x + w, cz) for cz in range(z, z + h)]


def geometry(anchor):
    """Pure. The pad's anchor -> A, B (interiors), their rings, A's door (west wall, in the ring), the lamps, A's plant
    cells, the subject's cell, the colonist's spawn and exit cells (outside the door) and the scene rect to clear."""
    ax, az = anchor
    a = (ax - A_W - 2, az - A_H // 2, A_W, A_H)
    ring_a = ring_of(a)
    b = (a[0] + A_W + 1 + GAP + 1, az - B_S // 2, B_S, B_S)
    ring_b = ring_of(b)
    door = (a[0] - 1, a[1] + A_H // 2)
    lamps = [(a[0] + dx, a[1] + dz) for dx, dz in LAMPS]
    plant_cells = [c for c in cells_of(a) if c not in lamps]
    spawn = (door[0] - 3, door[1])
    exit_ = (door[0] - 5, door[1])
    x0 = min(exit_[0], a[0] - 1) - 1
    x1 = b[0] + B_S + 1
    z0, z1 = min(a[1], b[1]) - 1, max(a[1] + A_H, b[1] + B_S) + 1
    return {"A": a, "B": b, "ringA": [c for c in ring_a if c != door], "ringB": ring_b, "door": door, "lamps": lamps,
            "plantCells": plant_cells, "subject": (a[0] + SUBJECT[0], a[1] + SUBJECT[1]), "spawn": spawn, "exit": exit_,
            "scene": (x0, z0, x1 - x0 + 1, z1 - z0 + 1)}


# ---- the phases' clock (ticks after the roof goes on)
def plan(wither, crumble):
    """Pure. -> the phases' bounds, each from the kernel's rule:
      a plant's death time d lies in [SPREAD_LO, SPREAD_HI] x witherTicks; its lethal long tick falls in (d - LONG, d + LONG]
      (its first roofed long tick comes within LONG of the roof) and the map kills it on the next tick (+1);
      dead grass is gone in (spawn + dc - LONG, spawn + dc + LONG] for dc in [SPREAD_LO, SPREAD_HI] x crumbleTicks.
    cutBeforeCrumble: the cut ends before the first dead grass can crumble, so the uncut dead grass is a control."""
    earliest_death = int(math.floor(SPREAD_LO * wither)) - LONG
    deadline = int(math.ceil(SPREAD_HI * wither)) + LONG + 1
    reads = int(math.ceil(deadline / float(HOUR))) + 2
    earliest_crumble = earliest_death + int(math.floor(SPREAD_LO * crumble)) - LONG
    cut_end = reads * HOUR + CUT_WAIT
    span = int(math.ceil(SPREAD_HI * crumble)) + LONG + 1
    return {"earliestDeath": earliest_death, "deathDeadline": deadline, "witherReads": reads,
            "earliestCrumble": earliest_crumble, "cutEnd": cut_end, "cutBeforeCrumble": cut_end < earliest_crumble,
            "crumbleSpan": span, "crumbleReads": int(math.ceil((span + HOUR) / float(CRUMBLE_READ))) + 1,
            "crumbleMinAge": int(math.floor(SPREAD_LO * crumble)) - LONG - HOUR}


def _row(rows, name, ok, worst, limit, cases):
    rows.append({"check": name, "ok": bool(ok), "worst": worst, "limit": limit, "cases": cases})


def percentile(xs, p):
    """Pure. Nearest-rank on the sorted values (index round(p x (n - 1)))."""
    s = sorted(xs)
    return s[int(round(p * (len(s) - 1)))] if s else None


def deaths_of(start_ids, reads):
    """Pure. -> {id: tick of the first read it is missing from}."""
    out = {}
    for r in reads:
        for i in start_ids:
            if i not in out and i not in r["A"]:
                out[i] = r["tick"]
    return out


def judge_wither(start, reads, numbers, subject_id, gate, area_a):
    """Pure. start {"A": {id: [x, z, hp]}, "B": {...}}; reads [{"tick", "A": {id: [x, z, hp, stage]}, "deadA": [[x, z]],
    "B": {...}, "deadB": n, "roofA": n, "roofB": n, "fire": n}] -> (opportunity rows, verdict rows, deaths {id: tick}).
    The subject is left out of every patch row (its own rows: judge_subject)."""
    p = plan(numbers["witherTicks"], numbers["crumbleTicks"])
    hp_max = numbers["grassHp"]
    ids = [i for i in start["A"] if i != subject_id]
    n = len(ids)
    opp, ver = [], []
    _row(opp, "PyrelandsMechanicsGate on", gate is True, gate, "True", 1)
    _row(opp, "A's patch (grown ember grass, the subject apart)", n >= MIN_PATCH, n, ">= %d" % MIN_PATCH, 1)
    full = sum(1 for i in ids if start["A"][i][2] == hp_max)
    _row(opp, "A's plants at full HP when roofed", full == n, n - full, "== 0 below %d" % hp_max, n)
    _row(opp, "B's control plants", len(start["B"]) >= B_MIN, len(start["B"]), ">= %d" % B_MIN, 1)
    _row(opp, "reads", len(reads) > 0, len(reads), "> 0", 1)
    _row(opp, "A cells roofed at every read", all(r["roofA"] == area_a for r in reads),
         min([r["roofA"] for r in reads] or [None]), "== %d" % area_a, len(reads))
    _row(opp, "B cells roofed at any read", all(r["roofB"] == 0 for r in reads), max([r["roofB"] for r in reads] or [0]),
         "== 0", len(reads))
    _row(opp, "fires in the scene at any read", all(r["fire"] == 0 for r in reads), max([r["fire"] for r in reads] or [0]),
         "== 0", len(reads))
    deaths = deaths_of(ids, reads)
    # per plant: its stages and hit points read while it stood
    seen = dict((i, []) for i in ids)
    for r in reads:
        for i in ids:
            if i in r["A"]:
                seen[i].append((r["tick"], r["A"][i][2], r["A"][i][3]))
    rise = 0
    fall = 0
    unlined = 0
    for i in ids:
        hps = [start["A"][i][2]] + [s[1] for s in seen[i]]
        rise = max([rise] + [b - a for a, b in zip(hps, hps[1:])])
        st = [s[2] for s in seen[i]]
        fall = max([fall] + [a - b for a, b in zip(st, st[1:])])
        unlined += sum(1 for s in st if s < 1)
    cases = sum(len(v) for v in seen.values())
    _row(ver, "A's HP rise between reads (HP never comes back under a roof)", rise == 0, rise, "== 0", cases)
    _row(ver, "A's look falls back between reads (wilting, then withered)", fall == 0, fall, "== 0", cases)
    _row(ver, "A plant reads without a wither line under the roof", unlined == 0, unlined, "== 0", cases)
    dead = sorted(deaths)
    no_wilt = [i for i in dead if 1 not in [s[2] for s in seen[i]]]
    no_withered = [i for i in dead if 2 not in [s[2] for s in seen[i]]]
    no_decline = [i for i in dead if not any(s[1] < hp_max for s in seen[i])]
    _row(ver, "deaths never read wilting before", not no_wilt, len(no_wilt), "== 0", len(dead))
    _row(ver, "deaths never read withered before", not no_withered, len(no_withered), "== 0", len(dead))
    _row(ver, "deaths that never lost HP before", not no_decline, len(no_decline), "== 0", len(dead))
    remains = dict((tuple(c), 0) for r in reads for c in r["deadA"])
    left = 0
    for i in dead:
        r = [x for x in reads if x["tick"] == deaths[i]][0]
        if (start["A"][i][0], start["A"][i][1]) not in set(tuple(c) for c in r["deadA"]):
            left += 1
    _row(ver, "deaths with no dead grass on their cell at the read they vanish", left == 0, left, "== 0", len(dead))
    per = {}
    for i in dead:
        per[deaths[i]] = per.get(deaths[i], 0) + 1
    worst = max(per.values()) / float(n) if per and n else 0.0
    _row(ver, "share of the patch dead in one hour", worst <= SHARE_MAX, round(worst, 3), "<= %.2f" % SHARE_MAX, len(reads))
    ts = [deaths[i] for i in dead]
    window = (percentile(ts, 0.95) - percentile(ts, 0.05)) if len(ts) >= 2 else None
    _row(ver, "the deaths' 5th..95th percentile span (ticks)", window is not None and window >= WINDOW_MIN_TICKS, window,
         ">= %d" % WINDOW_MIN_TICKS, len(ts))
    early = [deaths[i] for i in dead if deaths[i] <= p["earliestDeath"]]
    _row(ver, "deaths read at or before the earliest death time", not early, min(ts) if ts else None,
         "> %d" % p["earliestDeath"], len(ts))
    past = [r for r in reads if r["tick"] >= p["deathDeadline"]]
    if past:
        alive = len([i for i in ids if i in past[0]["A"]])
        _row(ver, "A's plants alive at the first read past the deadline", alive == 0, alive,
             "== 0 at tick >= %d" % p["deathDeadline"], n)
    elif len(dead) < n:
        _row(opp, "a read at or past the death deadline", False, reads[-1]["tick"] if reads else None,
             ">= %d" % p["deathDeadline"], 1)
    b_ids = list(start["B"])
    b_line = sum(1 for r in reads for i in b_ids if i in r["B"] and r["B"][i][3] > 0)
    b_lost = max([0] + [sum(1 for i in b_ids if i not in r["B"]) for r in reads])
    b_hp = max([0] + [start["B"][i][2] - r["B"][i][2] for r in reads for i in b_ids if i in r["B"]])
    b_dead = max([0] + [r.get("deadB", 0) for r in reads])
    bc = len(reads) * len(b_ids)
    _row(ver, "B plant reads with a wither line (never roofed)", b_line == 0, b_line, "== 0", bc)
    _row(ver, "B's plants lost", b_lost == 0, b_lost, "== 0", len(b_ids))
    _row(ver, "B's HP lost (worst plant)", b_hp <= 0, b_hp, "<= 0", bc)
    _row(ver, "dead grass in B", b_dead == 0, b_dead, "== 0", len(reads))
    return opp, ver, deaths


def judge_subject(subject, hp_at_roof, first_read, dead_cells_first):
    """Pure. The 1-HP subject: gone at the first read (at least LONG + 1 ticks after the roof), dead grass on its cell."""
    opp, ver = [], []
    sid, cell = subject
    _row(opp, "the subject's HP when roofed", hp_at_roof == 1, hp_at_roof, "== 1", 1)
    tick = first_read["tick"] if first_read else None
    _row(opp, "the first read's tick after the roof", tick is not None and tick >= LONG + 1, tick, ">= %d" % (LONG + 1), 1)
    alive = bool(first_read) and sid in first_read["A"]
    _row(ver, "the 1-HP subject standing at the first read", not alive, alive, "False", 1)
    has = tuple(cell) in set(tuple(c) for c in dead_cells_first or [])
    _row(ver, "dead grass on the subject's cell at the first read", has, has, "True", 1)
    return opp, ver


def pick_targets(dead_rows, door, k=CUT_TARGETS):
    """Pure. A's dead grass rows -> the k nearest the door (ties by id), the cut's targets."""
    rows = [r for r in dead_rows if r.get("id") is not None]
    rows.sort(key=lambda r: ((r["x"] - door[0]) ** 2 + (r["z"] - door[1]) ** 2, str(r["id"])))
    return rows[:k]


def judge_cut(targets, others, after_ids, accepted):
    """Pure. -> (opportunity rows, verdict rows). accepted: TryTakeOrderedJob's own bool for the first order."""
    opp, ver = [], []
    _row(opp, "cut targets", len(targets) == CUT_TARGETS, len(targets), "== %d" % CUT_TARGETS, 1)
    _row(opp, "the first cut order accepted", accepted is True, accepted, "True", 1)
    _row(opp, "uncut dead grass left as the control", len(others) > 0, len(others), "> 0", 1)
    left = [i for i in targets if i in after_ids]
    lost = [i for i in others if i not in after_ids]
    _row(ver, "ordered cuts still standing after the wait", not left, len(left), "== 0", len(targets))
    _row(ver, "uncut dead grass gone during the cut (none can crumble yet)", not lost, len(lost), "== 0", len(others))
    return opp, ver


def judge_crumble(first_seen, reads, last_death, numbers, fire):
    """Pure. first_seen {id: tick}; reads [{"tick", "dead": {id: hp}}] (ticks after the roof) -> (opp, verdict, noted)."""
    p = plan(numbers["witherTicks"], numbers["crumbleTicks"])
    opp, ver = [], []
    ids = list(first_seen)
    _row(opp, "dead grass at the crumble's start", len(ids) > 0, len(ids), "> 0", 1)
    _row(opp, "fires in the scene at any crumble read", fire == 0, fire, "== 0", len(reads))
    gone = {}
    rise = 0
    last = dict((i, None) for i in ids)
    for r in reads:
        for i in ids:
            if i in r["dead"]:
                if last[i] is not None:
                    rise = max(rise, r["dead"][i] - last[i])
                last[i] = r["dead"][i]
            elif i not in gone:
                gone[i] = r["tick"]
    early = [gone[i] - first_seen[i] for i in gone if gone[i] - first_seen[i] <= p["crumbleMinAge"]]
    _row(ver, "dead grass gone before its earliest crumble (ticks after first seen)", not early,
         min(early) if early else (min([gone[i] - first_seen[i] for i in gone]) if gone else None),
         "> %d" % p["crumbleMinAge"], len(gone))
    _row(ver, "dead grass HP rise between reads", rise <= 0, rise, "<= 0", sum(len(r["dead"]) for r in reads))
    deadline = (last_death or 0) + p["crumbleSpan"]
    past = [r for r in reads if r["tick"] >= deadline]
    if past:
        n = len([i for i in ids if i in past[0]["dead"]])
        _row(ver, "dead grass left at the first read past the crumble deadline", n == 0, n, "== 0 at tick >= %d" % deadline,
             len(ids))
    else:
        _row(opp, "a read at or past the crumble deadline", False, reads[-1]["tick"] if reads else None,
             ">= %d" % deadline, 1)
    per = {}
    for i in gone:
        per[gone[i]] = per.get(gone[i], 0) + 1
    noted = {"crumbleReadShareMax": round(max(per.values()) / float(len(ids)), 3) if per and ids else None,
             "gone": len(gone), "of": len(ids), "readEvery": CRUMBLE_READ}
    return opp, ver, noted


def calibration_rect(rect, cells=None):
    """Pure. The zoom probe's rect: `cells` (CAL_CELLS) square at the middle of `rect`."""
    c = cells or CAL_CELLS
    return (rect[0] + (rect[2] - c) // 2, rect[1] + (rect[3] - c) // 2, c, c)


def judge_captures(shots):
    """Pure. shots [{"label", "path", "lit", "cells"}] -> opportunity rows (a dark or missing capture is no picture)."""
    opp = []
    _row(opp, "captures taken", all(s.get("path") for s in shots) and shots, sum(1 for s in shots if s.get("path")),
         "== %d" % len(shots), len(shots))
    lit = [s.get("lit") if s.get("lit") is not None else 0.0 for s in shots]
    _row(opp, "A's lit share at the darkest capture", bool(lit) and min(lit) >= LIT_SHARE,
         round(min(lit), 3) if lit else None, ">= %.2f at groundGlow >= %.1f" % (LIT_SHARE, LIT), len(shots))
    return opp


def lit_share(glow, cells):
    """Pure. jawa/glow_at cells[] -> the share of `cells` whose groundGlow reads >= LIT (unread cells are dark)."""
    g = dict(((int(c["x"]), int(c["z"])), float(c.get("groundGlow") or 0.0)) for c in (glow or {}).get("cells") or [])
    return sum(1 for c in cells if g.get(tuple(c), 0.0) >= LIT) / float(len(cells)) if cells else 0.0


def error_lines(lines):
    """Pure. _log_since lines -> the error and exception lines (the contract: a new error line in Player.log)."""
    return [str(m.get("text", ""))[:240] for m in lines or []
            if str(m.get("type") or m.get("level") or "").lower() in ("error", "exception")]


def out_dir(stamp=None):
    """Where the manifest goes: $RM_RGD_DIR, else D:\\ClaudeWork\\rimmandrake\\roofed_grass\\<stamp>."""
    base = os.environ.get(OUT_ENV)
    if not base:
        root = r"D:\ClaudeWork\rimmandrake\roofed_grass" if os.name == "nt" else "/mnt/d/ClaudeWork/rimmandrake/roofed_grass"
        base = os.path.join(root, stamp or datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    return base


def write_manifest(path_dir, data):
    os.makedirs(path_dir, exist_ok=True)
    p = os.path.join(path_dir, "manifest.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, default=str)
    return p


def print_rows(tag, rows):
    for r in rows:
        print("[rgd-check] %s: %s: %s worst=%r limit=%s cases=%d" % (tag, r["check"], "ok" if r["ok"] else "NOT", r["worst"],
                                                                     r["limit"], r["cases"]), flush=True)


def register(suite, V):
    """Adds roofed_grass_declines to the Pyrelands suite. V is validation.py's namespace (its helpers and constants)."""
    state = {}
    keyed = keyed_lines()

    def ticks(t):
        return t.session._ticks() - state["t0"] if V._live(t) else None

    def plants_of(t, rect):
        """-> {id: [x, z, hp, stage]} of the ember grass in `rect` (hit points from list_things, the line from inspect)."""
        rows = V._things(t, GRASS, V._rs(rect), limit=600)
        ins = t.bridge_call("jawa/inspect_string", rect=V._rs(rect), limit=1200)
        if not V._live(t):
            return {}
        things = (ins or {}).get("things")
        if not isinstance(things, list):
            V._unmeasured(t, "inspect_string over %s unreadable: %r" % (V._rs(rect), str(ins)[:200]))
        st = dict((r.get("id"), stage_of_lines(r.get("inspect"), keyed)) for r in things if r.get("defName") == GRASS)
        return dict((r["id"], [int(r["x"]), int(r["z"]), int(r.get("hitPoints") or 0), st.get(r["id"], 0)]) for r in rows)

    def roofed_cells(t, rect, want):
        ops = str((t.bridge_call("jawa/get_roof_batch", rects=V._rs(rect)) or {}).get("ops") or "")
        rc = V._r6_ops_cells(ops)
        if want:
            return sum(1 for c in cells_of(rect) if rc.get(c) == "RoofConstructed")
        return sum(1 for c in cells_of(rect) if rc.get(c) not in (None, "", "None"))

    def shot(t, label):
        g = state["geo"]
        if CAL_CELLS and not state.get("zoomProbe"):   # learns the zoom on a rect that fits; never judged, never listed
            state["zoomProbe"] = t.screenshot(name="rgd_zoomprobe", rect=calibration_rect(g["A"]), ppc=V.R6_PLAY_PPC)
        glow = t.bridge_call("jawa/glow_at", rect=V._rs(g["A"]))
        path = V._r6_shot(t, g["A"], "rgd_%s" % label)
        state["shots"].append({"label": label, "path": path, "lit": lit_share(glow, g["plantCells"]) if V._live(t) else None,
                               "tick": ticks(t), "hour": (glow or {}).get("hour") if isinstance(glow, dict) else None})

    def read(t):
        g = state["geo"]
        dead = V._things(t, DEAD, V._rs(g["A"]), limit=600)
        r = {"tick": ticks(t), "A": plants_of(t, g["A"]), "deadA": [[int(d["x"]), int(d["z"])] for d in dead],
             "B": plants_of(t, g["B"]), "deadB": V._count(t, DEAD, V._rs(g["B"])),
             "roofA": roofed_cells(t, g["A"], True), "roofB": roofed_cells(t, g["B"], False),
             "fire": V._count(t, "Fire", V._rs(g["scene"]))}
        return r, dead

    def save():
        state["manifest"] = write_manifest(state["dir"], dict(
            (k, state.get(k)) for k in ("scene", "geo", "numbers", "plan", "start", "subject", "reads", "cut", "crumble",
                                        "shots", "plantedFault")))

    def judged(t, tag, opp, ver):
        print_rows(tag, opp + ver)
        save()
        bad_o, bad_v = [r for r in opp if not r["ok"]], [r for r in ver if not r["ok"]]
        V._note(t, "%s: the checks" % tag, {"manifest": state.get("manifest"), "not": [r["check"] for r in bad_o + bad_v]})
        if bad_o:
            V._unmeasured(t, "%s: %s" % (tag, "; ".join("%s %r (limit %s)" % (r["check"], r["worst"], r["limit"])
                                                        for r in bad_o)))
        if bad_v:
            V._fail("%s: %s" % (tag, "; ".join("%s %r (limit %s, %d cases)" % (r["check"], r["worst"], r["limit"],
                                                                               r["cases"]) for r in bad_v)))

    @suite.chain("roofed_grass_declines")
    @V._teardown(fire=True, weather=True)
    def roofed_grass_declines(t):
        state.clear()
        state.update(dir=out_dir(), scene="sc_roofed_grass_declines", shots=[], reads=[],
                     plantedFault=os.environ.get(PLANT_ENV) or None)
        nums = shipped_numbers()
        pl = plan(nums["witherTicks"], nums["crumbleTicks"])
        state.update(numbers=nums, plan=pl)
        with V._comp(t, "roofed_grass_stage"):
            if V._live(t):
                mid, why = V._load_registered_site(t)   # the contract: a fresh map
                if mid is None:
                    V._unmeasured(t, "SITE: %s" % why)
            V._pad(t, V.R6_PAD_WITHER)
            g = geometry(t.anchor)
            state["geo"] = g
            if state["plantedFault"]:
                V._note(t, "PLANTED FAULT", "%s=%s" % (PLANT_ENV, state["plantedFault"]))
            print("[rgd-check] plan: cut ends %d, earliest crumble %d (limit cut < crumble), witherTicks %d (%s), "
                  "crumbleTicks %d (%s)" % (pl["cutEnd"], pl["earliestCrumble"], nums["witherTicks"],
                                            nums["sources"]["witherTicks"], nums["crumbleTicks"],
                                            nums["sources"]["crumbleTicks"]), flush=True)
            if not pl["cutBeforeCrumble"] or nums["remainsDef"] != DEAD:
                V._unmeasured(t, "the scene's clock does not fit the shipped numbers: %r, remainsDef %r" % (pl, nums["remainsDef"]))
            state["gate"] = V._ten_gate_on(t)
            t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
            V._extinguish(t)
            V._open_ground(t, g["scene"], margin=2)
            if NOROOF_B:   # before the ring closes the room: the auto-roof reads the area when the room forms
                b_ring = (g["B"][0] - 1, g["B"][1] - 1, B_S + 2, B_S + 2)
                t.bridge_call("jawa/paint_area", area="roof", ops=V._rs(b_ring), value=False)
                t.bridge_call("jawa/paint_area", area="noroof", ops=V._rs(b_ring))
            t.bridge_call("jawa/build_batch", ops=";".join("Wall:%d,%d" % c for c in g["ringA"] + g["ringB"]), stuff="Steel",
                          faction="player")
            t.bridge_call("jawa/build_batch", ops="Door:%d,%d" % g["door"], stuff="Steel", faction="player")
            t.bridge_call("jawa/spawn_batch", ops=";".join("TorchLamp:%d,%d" % c for c in g["lamps"]))
            lamps = V._things(t, "TorchLamp", V._rs(g["A"]), limit=20)
            for lamp in lamps:
                t.bridge_call("jawa/thing_refuel", thingId=lamp["id"], amount=100)
            V._plants(t, GRASS, g["A"], growth=1.0)
            V._plants(t, GRASS, g["B"], growth=1.0)
            a0, b0 = V._things(t, GRASS, V._rs(g["A"]), limit=600), V._things(t, GRASS, V._rs(g["B"]), limit=100)
            sub = [r for r in a0 if (int(r["x"]), int(r["z"])) == g["subject"]]
            hp_sub = None
            if sub:
                t.bridge_call("jawa/damage", damageDef="Rotting", amount=float(int(sub[0]["hitPoints"]) - 1),
                              thingId=sub[0]["id"])
                hp_sub = dict((r["id"], r.get("hitPoints")) for r in V._things(t, GRASS, "%d,%d,1,1" % g["subject"],
                                                                                 limit=5)).get(sub[0]["id"])
            t.bridge_call("jawa/set_roof_batch", ops="RoofConstructed:%s" % V._rs(g["A"]))
            state["t0"] = t.session._ticks() if V._live(t) else 0
            state["mark"] = V._log_mark(t)
            state["start"] = {"A": dict((r["id"], [int(r["x"]), int(r["z"]), int(r.get("hitPoints") or 0)]) for r in a0),
                              "B": dict((r["id"], [int(r["x"]), int(r["z"]), int(r.get("hitPoints") or 0)]) for r in b0)}
            state["subject"] = {"id": sub[0]["id"] if sub else None, "cell": list(g["subject"]), "hpAtRoof": hp_sub}
            if V._live(t):
                print("[rgd-check] stage: A plants %d of %d cells (limit >= %d), B %d of %d (limit >= %d), lamps %d "
                      "(limit %d), subject HP %r (limit 1)" % (len(a0), len(g["plantCells"]), MIN_PATCH + 1, len(b0),
                                                                B_S * B_S, B_MIN, len(lamps), len(LAMPS), hp_sub), flush=True)
                save()
                if len(lamps) != len(LAMPS) or not sub:
                    V._unmeasured(t, "the room is not staged: %d lamps of %d, subject %r" % (len(lamps), len(LAMPS),
                                                                                             bool(sub)))
            shot(t, "roofed")
        V._independent(t)
        with V._comp(t, "roofed_grass_withers_unevenly"):
            if "start" not in state:
                V._unmeasured(t, "the stage did not finish")
            plant = state["plantedFault"] or ""
            for h in range(1, pl["witherReads"] + 1):
                V._wait(t, HOUR)
                if plant == "mass_kill" and h == SHOT_AT["first_deaths"] and V._live(t):
                    t.bridge_call("jawa/destroy_batch", rects=V._rs(state["geo"]["A"]), categories="Plant")
                r, _dead = read(t)
                if not V._live(t):
                    break
                state["reads"].append(r)
                for label, at in SHOT_AT.items():
                    if at == h:
                        shot(t, label)
                if not r["A"] and r["tick"] >= HOUR:
                    break
            shot(t, "wither_end")
            if V._live(t):
                opp, ver, deaths = judge_wither(state["start"], state["reads"], state["numbers"], state["subject"]["id"],
                                                state["gate"], A_W * A_H)
                state["deaths"] = deaths
                judged(t, "wither", opp, ver)
        V._independent(t)
        with V._comp(t, "roofed_grass_one_hp_dies_next_long_tick"):
            if V._live(t):
                first = state["reads"][0] if state["reads"] else None
                opp, ver = judge_subject((state["subject"]["id"], state["subject"]["cell"]), state["subject"]["hpAtRoof"],
                                         first, first["deadA"] if first else [])
                judged(t, "subject", opp, ver)
        V._independent(t)
        with V._comp(t, "dead_grass_can_be_cut"):
            g = state.get("geo")
            if not g:
                V._unmeasured(t, "the stage did not finish")
            dead = V._things(t, DEAD, V._rs(g["A"]), limit=600)
            targets = pick_targets(dead, g["door"])
            tids = [r["id"] for r in targets]
            others = [r["id"] for r in dead if r["id"] not in tids]
            cid = t.spawn_pawn("Colonist", beyond=[g["spawn"], g["spawn"]])
            accepted = None
            for i, r in enumerate(targets):
                t.bridge_call("jawa/designate_batch", action="add", designation="CutPlant", rect="%d,%d,1,1" % (r["x"], r["z"]))
                o = t.bridge_call("jawa/ordered_job", pawnId=cid, jobDef="CutPlant", targetAId=r["id"], queue=i > 0,
                                  waitTicks=0)
                if i == 0:
                    accepted = (o or {}).get("accepted") if isinstance(o, dict) else None
            V._wait(t, CUT_WAIT)
            after = set(r["id"] for r in V._things(t, DEAD, V._rs(g["A"]), limit=600))
            t.bridge_call("jawa/ordered_job", pawnId=cid, jobDef="Goto", targetAX=g["exit"][0], targetAZ=g["exit"][1],
                          queue=False, waitTicks=0)
            state["cut"] = {"colonist": cid, "targets": tids, "others": len(others), "accepted": accepted,
                            "after": len(after), "tick": ticks(t)}
            shot(t, "after_cut")
            if V._live(t):
                if not cid:
                    V._unmeasured(t, "no colonist could be spawned outside the door")
                opp, ver = judge_cut(tids, others, after, accepted)
                judged(t, "cut", opp, ver)
        V._independent(t)
        with V._comp(t, "dead_grass_crumbles_unevenly"):
            g = state.get("geo")
            if not g or not state.get("reads"):
                V._unmeasured(t, "the wither phase left no reads")
            first_seen = {}
            dead_now = V._things(t, DEAD, V._rs(g["A"]), limit=600)
            # first seen: the wither read where its cell first held dead grass (the remains of that cell's plant)
            cell_first = {}
            for r in state["reads"]:
                for c in r["deadA"]:
                    cell_first.setdefault(tuple(c), r["tick"])
            for d in dead_now:
                first_seen[d["id"]] = cell_first.get((int(d["x"]), int(d["z"])), ticks(t))
            last_death = max(list((state.get("deaths") or {}).values()) + [0])
            creads, fire, half = [], 0, False
            for _k in range(pl["crumbleReads"]):
                V._wait(t, CRUMBLE_READ)
                rows = V._things(t, DEAD, V._rs(g["A"]), limit=600)
                if not V._live(t):
                    break
                fire = max(fire, V._count(t, "Fire", V._rs(g["scene"])))
                creads.append({"tick": ticks(t), "dead": dict((r["id"], int(r.get("hitPoints") or 0)) for r in rows)})
                if not half and first_seen and len(rows) <= len(first_seen) // 2:
                    half = True
                    shot(t, "crumble_half")
                if not rows and creads[-1]["tick"] >= last_death + pl["crumbleSpan"]:
                    break
            state["crumble"] = {"firstSeen": len(first_seen), "reads": creads, "lastDeath": last_death}
            if V._live(t):
                opp, ver, noted = judge_crumble(first_seen, creads, last_death, state["numbers"], fire)
                state["crumble"]["noted"] = noted
                print("[rgd-check] crumble noted (not judged): %r" % noted, flush=True)
                judged(t, "crumble", opp, ver)
        V._independent(t)
        with V._comp(t, "roofed_grass_captures_lit"):
            if V._live(t):
                judged(t, "captures", judge_captures(state["shots"]), [])
        V._independent(t)
        with V._comp(t, "roofed_grass_no_error_line"):
            lines = V._log_since(t, state.get("mark"))
            if V._live(t):
                errs = error_lines(lines)
                print("[rgd-check] error lines since the mark: %d (limit 0) of %d lines read" % (len(errs), len(lines)),
                      flush=True)
                V._note(t, "error lines since the scene's mark", {"errors": errs[:5], "lines": len(lines)})
                if errs:
                    V._fail("%d new error line(s) in the log: %r" % (len(errs), errs[:2]))
        # housekeeping (owner 2026-11-17): the roof off A; the next chain loads a fresh site anyway
        if state.get("geo"):
            t.bridge_call("jawa/set_roof_batch", ops="None:%s" % V._rs(state["geo"]["A"]))
