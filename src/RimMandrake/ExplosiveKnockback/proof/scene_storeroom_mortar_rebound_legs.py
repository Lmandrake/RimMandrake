"""scene_storeroom_mortar_rebound_legs.py - Explosive Knockback 0.2.0, sc_storeroom_mortar_rebound_legs: a mortar shell goes
off in a walled storeroom of loose goods, and each rebound leg of a thrown good is shorter than the leg before, until it
rests (scene library 0.3.0).

Bar (design/concepts/ExplosiveKnockback/record.json): rebound_goes_shorter, "each time a thrown good rebounds off a wall or
a closed door, the player sees it carry on a clearly shorter way than the flight before, until it comes to rest". The
kernel's rule is offline (RM_KnockbackMath.ReboundCells: a rebound keeps goodsReboundKeepPercent of the cells left at the
hit, rounded down). This scene reads what the player sees: the cells each leg really flew in the game, from the journal.

Kind A. A fresh quicktest map on ArchSmall; one clean station; three granite-walled storerooms (Wall, stuff BlocksGranite,
as RM_KnockbackProof builds them), each set off alone. Each room is 5 cells deep (inner z 0..4) and W cells wide:
  narrow  W=2   a rebound crosses 1 cell before the far wall
  mid     W=3   a rebound crosses 2 cells
  wide    W=5   a rebound crosses 4 cells (a rebound of 3 or fewer cells rests inside the room)
In each room: a Shell_HighExplosive (Bomb, radius 2.9) at inner (1, 2), and loose goods (stack 1) against the west wall at
inner (0, 1) Steel, (0, 2) ComponentIndustrial, (0, 3) Plasteel, 1 and 1.41 cells from the shell. (Goods 2.83 cells out
round to 0 cells and skip too_weak, RM_KnockbackProof_StoreroomBombPit.cs visit 3, so the goods sit close.) Each good is
pushed into its wall, takes the hit where it lies (wallFirst) and bounces back across the room. The shell is set off by
damage (s.act.damage Crush, its hit points + 60), as scene_blast_show does. Rooms are 8 or more cells apart: no blast
reaches the next room. No colonist, no raid, no hostile pawn.

The range (what the game varies for this bar, and what this scene covers):
  - the room's width against the rebound's reach: covered by the three widths (cut by the far wall at 1, 2 cells; rests
    inside at 4). The cells a throw gets (distance to the shell, the good's mass): covered at 1 and 1.41 cells, three masses.
  - left out: a closed door as the face (the kernel treats it as a wall, offline case); diagonal-only rooms; shelves and
    crates (containers do not rebound); goodsRebound off (no rebound at all: nothing to compare).

Leg lengths. For each thrown good the journal gives item_move (from, the first leg's planned dest, wallFirst), item_rebound
(at, hit, left, cells, to, bounce; the wallFirst bounce is written at the start cell with bounce 1) and item_land (dest =
the cell the carrier flew to, to = where it was placed). The turning points are: the start cell, each in-flight rebound's
`at` in bounce order, the land's `dest`. A leg is the straight (Euclidean) distance between two turning points, in cells.
For a wallFirst good the "flight before" the first rebound leg is the hit in place (0 cells), so its pairs begin with the
second leg; a good thrown clear of a wall compares its first rebound leg with its blast flight.

The checks (each prints PASS or FAIL with what it read):
  V_THROWN <room>   at least one good of the room has an item_move; prints each good's planned cells and flight ticks
  V_TRACE           every thrown good has one item_land, and its item_rebound count equals the land's `bounces`
  V_RESTS           every thrown good came to rest within MaxBounces = 6 (RM_ThingFlyer_Knockback.cs:26)
  V_SHORTER <room>  every pair of consecutive legs has leg[i+1] / leg[i] < 1 (limit 1, from the bar's "shorter"); prints the
                    worst ratio, its good, the pairs and legs read; a room with no pair says why (UNLAID: no rebound, or the
                    rebound rested inside the room)
  V_SHORTER all     the same over every room; UNLAID when no pair was read anywhere
  INFO budgets      each leg's planned cells (the kernel's budget) beside the cells flown
  SHOTS             <room>_after, SETTLE ticks after each blast

    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_storeroom_mortar_rebound_legs.py
    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_storeroom_mortar_rebound_legs.py --plant keep_all

UNRUN until Stage 6: written 2026-11-24 by RIMMANDRAKE_AUTOBUILD_EXPLOSIVEKNOCKBACK_SIX_BARS_LEFT and never run live.
The plant `keep_all` sets goodsReboundKeepPercent to 100 (inside a try whose finally puts back the value read before): a
rebound then loses no cells, a good crossing a narrow room flies the same width again and again until MaxBounces, and
V_SHORTER must FAIL with a worst ratio of 1. That shows the check can see legs that do not shrink.
Open points for the first run:
  - the settings reads and the plant are s.raw jawa/mod_settings_field (`tune` is NOT_BUILT): the run is EXPLORED.
  - a wall-cut leg: in the narrow room a rebound that reaches the far wall flies 1 cell, and the next rebound, if any, can
    fly 1 cell too (rounded-down cells: 5 planned -> 3 kept -> 1 flown, 2 left -> 1 kept -> 1 flown). Then V_SHORTER narrow
    FAILS on the real build: the bar's "clearly shorter way" and the room's walls disagree. That is a question for the
    Conductor with the shot narrow_after, never a check to relax here.
  - the planned cells at 1 and 1.41 cells from a 50-Bomb shell are not measured; if every good plans 3 or fewer, the mid
    and wide rooms read no pair, and only the narrow room speaks.
  - the goods may be destroyed by the blast or the wall hit (destroyedAtWall / destroyedInFlight): they are printed and
    leave the pairs.
"""
import json
import math

import scene
from scene import cond as c

GAME = "ArchSmall"
# a stage save (stage_map.py make ArchSmall --kind settlement --save RM_Stage_ExplosiveKnockback): every roof and
# destroyable thing cleared. A fixed station on a fresh quicktest map can lie under mountain roof: on 2026-11-24 the
# colonist was gone by tick 3 under collapsed rocks and the stack buried (APPARATUS FAULT of the first run).
STAGE = "RM_Stage_ExplosiveKnockback"
SETTINGS = "RimMandrake.ExplosiveKnockback.RimMandrakeExplosiveKnockbackSettings"
JOURNAL = "RimMandrake.ExplosiveKnockback.RM_KnockbackJournal"
STATION = (20, 20, 28, 10)
SHELL = "Shell_HighExplosive"   # Bomb, explosiveRadius 2.9 (Items_Resource_Shell.xml)
DEPTH = 5                       # inner z 0..4
# room -> (inner west x, inner south z, inner width)
ROOMS = {"narrow": (2, 2, 2), "mid": (10, 2, 3), "wide": (19, 2, 5)}
ORDER = ["narrow", "mid", "wide"]
GOODS = [((0, 1), "Steel"), ((0, 2), "ComponentIndustrial"), ((0, 3), "Plasteel")]
SHELL_AT = (1, 2)
MAX_BOUNCES = 6                 # RM_ThingFlyer_Knockback.MaxBounces
SETTLE = 360                    # ticks after each blast; at keep 100 a 6-bounce chain of short legs must also have landed
LIMIT_RATIO = 1.0               # the bar: each leg shorter than the one before (strictly)

legs_bar = scene.contract(
    claim="a good thrown in a walled storeroom rebounds a shorter way each time, until it rests",
    kind="A",
    exposure=c.state("wall_narrow[0]", "positionInt") == "ok",   # the storeroom really stood
    success=[c.played(SETTLE)],                                  # the judged run is the last: the last room's settle
    forbidden=[],
    end=SETTLE, limit=len(ORDER) * SETTLE + 900)


def ring(room):
    """The wall cells around a room's inner rectangle, station-relative."""
    ox, oz, w = ROOMS[room]
    cells = []
    for x in range(ox - 1, ox + w + 1):
        cells += [(x, oz - 1), (x, oz + DEPTH)]
    for z in range(oz, oz + DEPTH):
        cells += [(ox - 1, z), (ox + w, z)]
    return cells


def inner(room, xz):
    ox, oz, _ = ROOMS[room]
    return ox + xz[0], oz + xz[1]


def journal(s):
    v = s.read("static:" + JOURNAL, "lines")
    if v.state != "ok":
        return None, "journal %s" % v.state
    raw = v.v if isinstance(v.v, (list, tuple)) else str(v.v).splitlines()
    recs = []
    for line in raw:
        line = str(line).strip()
        if line.startswith("{"):
            try:
                recs.append(json.loads(line))
            except ValueError:
                pass
    return recs, None


def thing_id(s, alias):
    d, n = s.read(alias, "def.defName"), s.read(alias, "thingIDNumber")
    return "%s%s" % (d.v, n.v) if d.state == "ok" and n.state == "ok" else None


def setting(s, field):
    return (s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field) or {}).get("value")


def blast(s, room, rows):
    ids = {}
    for i in range(len(GOODS)):
        tid = thing_id(s, "good%d_%s" % (i, room))
        if tid:
            ids[tid] = GOODS[i][1]
    alias = "shell_" + room
    hp = s.read(alias, "hitPointsInt")
    s.act.damage(alias, (hp.v if hp.state == "ok" else 100) + 60, kind="Crush", name="blast_" + room)
    s.run(until=SETTLE, limit=SETTLE + 120)
    ox, oz, w = ROOMS[room]
    s.shot((STATION[0] + ox - 3, STATION[1] + oz - 3, w + 6, DEPTH + 6), name=room + "_after")
    recs, err = journal(s)
    mine = [r for r in (recs or []) if isinstance(r.get("tick"), (int, float)) and r["tick"] >= (hp.tick or 0)
            and r.get("thing") in ids and r.get("type") in ("item_move", "item_rebound", "item_land", "blocked", "skip")]
    rows[room] = dict(ids=ids, recs=mine, err=err)


planted = scene.plant() == "keep_all"
staged = {}
for room in ORDER:
    staged["wall_" + room] = dict(thing="Wall", at=ring(room), stuff="BlocksGranite")   # a group: wall_<room>[0], [1], ...
    staged["shell_" + room] = dict(thing=SHELL, at=inner(room, SHELL_AT))
    for i, (xz, d) in enumerate(GOODS):    # each good its own alias: the goods differ by def
        staged["good%d_%s" % (i, room)] = dict(thing=d, at=inner(room, xz))

with scene.open(GAME, contract=legs_bar, needs={"mods": ["ExplosiveKnockback"], "map": STAGE, "calm": "standard"}) as s:
    s.stage(station=STATION, things=staged)
    rebound_on = setting(s, "goodsRebound")
    prior = {f: setting(s, f) for f in ["goodsReboundKeepPercent"]}
    rows = {}
    try:
        if planted:
            s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="goodsReboundKeepPercent", value="100")
        keep_now = setting(s, "goodsReboundKeepPercent")
        for room in ORDER:
            blast(s, room, rows)
    finally:
        for f, v in prior.items():   # back to what it read before, on every exit path
            if v is not None:
                s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=f, value=str(v))
    folder = s.run_dir

fails = 0


def row(ok, ident, text):
    global fails
    fails += not ok
    print("%s %s: %s" % ("PASS" if ok else "FAIL", ident, text))


def cell(v):
    if isinstance(v, (list, tuple)) and len(v) >= 2:
        try:
            return float(v[0]), float(v[-1])
        except (TypeError, ValueError):
            return None
    return None


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def good_legs(recs, tid):
    """-> dict for one good: the move, its rebounds in bounce order, its land, the legs flown and their budgets."""
    mine = [r for r in recs if r.get("thing") == tid]
    moves = [r for r in mine if r.get("type") == "item_move"]
    lands = [r for r in mine if r.get("type") == "item_land"]
    rebs = sorted([r for r in mine if r.get("type") == "item_rebound"], key=lambda r: (r.get("tick") or 0, r.get("bounce") or 0))
    g = dict(moves=moves, lands=lands, rebs=rebs, legs=[], budgets=[], wallFirst=None, note="",
             other=[{k: r.get(k) for k in ("type", "stop", "reason", "planned", "destroyedAtWall")} for r in mine
                    if r.get("type") in ("blocked", "skip")])
    if len(moves) != 1:
        g["note"] = "%d item_move" % len(moves)
        return g
    m = moves[0]
    wf = str(m.get("wallFirst")).lower() == "true"
    g["wallFirst"] = wf
    start = cell(m.get("from"))
    in_flight = rebs[1:] if wf and rebs and cell(rebs[0].get("at")) == start else rebs
    points = [start] + [cell(r.get("at")) for r in in_flight]
    budgets = ([rebs[0].get("cells")] if wf and rebs else [m.get("planned")]) + [r.get("cells") for r in in_flight]
    if len(lands) == 1:
        land = lands[0]
        points.append(cell(land.get("dest")) or cell(land.get("to")))
        if str(land.get("destroyedInFlight")).lower() == "true":
            g["note"] = "destroyed in flight"
    else:
        g["note"] = "%d item_land" % len(lands)
    if any(p is None for p in points):
        g["note"] += " unreadable cell"
        return g
    g["legs"] = [dist(points[i], points[i + 1]) for i in range(len(points) - 1)]
    g["budgets"] = budgets[:len(g["legs"])]
    return g


print("INFO goodsRebound = %s; goodsReboundKeepPercent = %s during the blasts (default 70; plant %s)" % (
    rebound_on, keep_now, "keep_all" if planted else "none"))
all_pairs, all_worst = 0, None
for room in ORDER:
    r = rows[room]
    goods = {tid: good_legs(r["recs"], tid) for tid in r["ids"]}
    thrown = [t for t, g in goods.items() if g["moves"]]
    row(len(thrown) > 0, "V_THROWN " + room, "%d of %d goods moved%s; %s" % (
        len(thrown), len(goods), ", " + r["err"] if r["err"] else "",
        [(r["ids"][t], {k: (g["moves"][0].get(k) if g["moves"] else None) for k in ("planned", "cells", "stop", "wallFirst", "flightTicks")},
          g["other"]) for t, g in goods.items()]))
    pairs, worst, worst_of, nlegs, why = 0, None, None, 0, []
    for t in thrown:
        g = goods[t]
        legs = g["legs"]
        nlegs += len(legs)
        first = 1 if g["wallFirst"] else 0    # a wallFirst good's flight before its first rebound leg is the hit in place
        for i in range(first, len(legs) - 1):
            if legs[i] <= 0:
                continue
            ratio = legs[i + 1] / legs[i]
            pairs += 1
            if worst is None or ratio > worst:
                worst, worst_of = ratio, "%s leg %d->%d" % (r["ids"][t], i, i + 1)
        if len(legs) - first < 2:
            why.append("%s %s" % (r["ids"][t], "no rebound in flight" if len(g["rebs"]) <= first else "one leg"))
        print("INFO budgets %s %s: legs flown %s, planned cells %s, bounces %d%s" % (
            room, r["ids"][t], ["%.2f" % x for x in legs], g["budgets"], len(g["rebs"]), " (" + g["note"] + ")" if g["note"] else ""))
    if pairs:
        row(worst < LIMIT_RATIO, "V_SHORTER " + room, "worst ratio %.3f (%s), limit < %.1f, %d pair(s) of %d leg(s) read" % (
            worst, worst_of, LIMIT_RATIO, pairs, nlegs))
    else:
        print("INFO V_SHORTER %s: no pair read, %d leg(s): %s (UNLAID in this room)" % (room, nlegs, why))
    all_pairs += pairs
    if worst is not None and (all_worst is None or worst > all_worst):
        all_worst = worst
    bad_trace = [(r["ids"][t], len(goods[t]["lands"]), len(goods[t]["rebs"]), [x.get("bounces") for x in goods[t]["lands"]])
                 for t in thrown if len(goods[t]["lands"]) != 1 or str(goods[t]["lands"][0].get("bounces")) != str(len(goods[t]["rebs"]))]
    row(not bad_trace, "V_TRACE " + room, "%d thrown good(s) read; mismatched (good, lands, rebounds, land bounces): %s" % (
        len(thrown), bad_trace))
    over = [(r["ids"][t], len(goods[t]["rebs"])) for t in thrown if len(goods[t]["rebs"]) > MAX_BOUNCES or not goods[t]["lands"]]
    row(not over, "V_RESTS " + room, "worst bounce count %s, limit %d, %d good(s) read; over or never landed: %s" % (
        max([len(goods[t]["rebs"]) for t in thrown] or [None]), MAX_BOUNCES, len(thrown), over))
if all_pairs:
    row(all_worst < LIMIT_RATIO, "V_SHORTER all", "worst ratio %.3f, limit < %.1f, %d pair(s) read over %d room(s)" % (
        all_worst, LIMIT_RATIO, all_pairs, len(ORDER)))
else:
    row(False, "V_SHORTER all", "no pair of legs read in any room: UNLAID (the scene made no rebound to compare)")
print("%s sc_storeroom_mortar_rebound_legs: %d failing row(s); pictures in %s" % ("PASS" if fails == 0 else "FAIL", fails, folder))
print(scene.judge(folder))
