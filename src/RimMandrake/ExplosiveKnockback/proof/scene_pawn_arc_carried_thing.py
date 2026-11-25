"""scene_pawn_arc_carried_thing.py - Explosive Knockback 0.2.0, sc_pawn_arc_carried_thing: what a thrown colonist carries
leaves its hands at the blast and flies on an arc of its own (scene library 0.3.0).

Bar (design/concepts/ExplosiveKnockback/record.json): carried_thing_own_arc. The plan is decided offline (KbPlanner.Carried
and CarriedRest; ThrowCarried in RM_MapComponent_Knockback moves the stack straight from the hands into its own
RM_ThingFlyer_Knockback, or drops it on the start cell when the plan skips it). This scene reads what only the game can
show: on a real throw the colonist's hands are empty from the launch tick, the stack flies in its own flyer and comes down
whole on its own planned cell, and the colonist comes down empty-handed on its.

Kind A. A fresh quicktest map on ArchSmall; one clean station; three lanes, 14 cells apart, each set off alone:
  light   a colonist at (8, z) on a stack of 20 Steel (10 kg, under lightMassLimit 75), ordered to haul it to (8, z+6)
  heavy   a colonist at (8, z) beside a player's Muffalo at (9, z) that dies where it stands (Corpse_Muffalo: the
          Muffalo's own mass, baseBodySize 2.4 in Races_Animal_CowGroup.xml, over lightMassLimit), ordered to haul the
          corpse to (8, z+6)
  empty   a colonist at (8, z) with nothing in its hands (the control: it flies as before)
Once the colonist holds its load, the blast goes off on the cell beside it (-x): jawa/explosion_at (Bomb, radius 2.9,
damage 1) with "Bigger blasts throw harder" (blastPowerFromDamage) off, so it pushes at the Bomb's plain force and harms
by 1 (a real shell is 50 Bomb and would down the colonist; the C# proofs staged the same way, RM_KnockbackProof.Boom
realPower false). No raid, no hostile pawn. The haul is the player's own order (HaulToCell, the job the C# pawn_arc
proof gave, with Job.count = the stack).

The checks (each prints PASS or FAIL with what it read):
  V_HANDS light       on the tick the `carried_throw` record appears: act thrown; the colonist's hands hold nothing; its
                      PawnFlyer's carriedThing is empty; the stack (same id, count 20) is the one thing inside the goods
                      flyer named by the record
  V_APART light       on at least one mid-flight tick, the stack's ground position (the goods flyer's groundPos) and the
                      colonist's (the PawnFlyer's startVec -> destCell at ticksFlying / ticksFlightTime) are >= 0.5 cell
                      apart; prints the widest gap and the count of ticks read
  V_STACK_LAND light  the stack's `item_land` lands it on the record's `to` with count 20; Steel on the station totals 20
                      before and after, in one stack
  V_PAWN_LAND <lane>  light, empty: the colonist's `land` record is on its `launch` record's `to`, and its hands are empty
  V_HEAVY heavy       carried_throw act dropped, reason too_heavy, mass > lightMassLimit (read), and the corpse lies on the
                      record's `from` cell, not carried
  V_CONTROL empty     the empty colonist's `launch` reads carried none, cells >= 1, and no carried_throw names it
  SHOTS               <lane>_air on the first mid-flight tick, <lane>_after once all is down

    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_pawn_arc_carried_thing.py
    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_pawn_arc_carried_thing.py --plant light_limit_5

UNRUN until Stage 6: written 2026-11-24 by RIMMANDRAKE_AUTOBUILD_EXPLOSIVEKNOCKBACK_SIX_BARS_LEFT and never run live.
The plant `light_limit_5` sets lightMassLimit to 5 kg (the slider's floor) for the scene: the 10 kg Steel is then too
heavy, so V_HANDS, V_APART and V_STACK_LAND must FAIL (the stack drops on the start cell), which shows the checks can see.
Open points for the first run:
  - `explode` is NOT_BUILT: the blast is s.raw jawa/explosion_at; the settings write is s.raw jawa/mod_settings_field;
    the 20-stack is s.raw jawa/spawn_batch (s.stage makes stacks of 1); the haul is s.raw jawa/ordered_job (s.act.job
    passes no Job.count; waitTicks=0 so the tool plays no ticks); the Muffalo's death is s.raw jawa/pawn_health (add
    MissingBodyPart on Brain: the game's own death check kills it). All stamp the run EXPLORED.
  - HaulToCell is given with haulMode Undefined (ordered_job has no haulMode) and no stockpile: the blast comes at the
    pickup, before the place toil reads the mode. If the job refuses, add a stockpile at (8, z+6) with jawa/map_zones.
  - the read paths of the vanilla PawnFlyer (startVec, destCell, ticksFlying, ticksFlightTime, carriedThing,
    innerContainer) are read from the RimWorld 1.6 class, not yet read live; an `error` state names the step.
  - the colonists are not drafted (`order` is NOT_BUILT); a lane prints where its colonist stood at the blast.
"""
import json

import scene
from scene import cond as c

GAME = "ArchSmall"
# a stage save (stage_map.py make ArchSmall --kind settlement --save RM_Stage_ExplosiveKnockback): every roof and
# destroyable thing cleared. A fixed station on a fresh quicktest map can lie under mountain roof: on 2026-11-24 the
# colonist was gone by tick 3 under collapsed rocks and the stack buried (APPARATUS FAULT of the first run).
STAGE = "RM_Stage_ExplosiveKnockback"
SETTINGS = "RimMandrake.ExplosiveKnockback.RimMandrakeExplosiveKnockbackSettings"
JOURNAL = "RimMandrake.ExplosiveKnockback.RM_KnockbackJournal"
STATION = (20, 20, 30, 44)
RADIUS = 2.9                    # Shell_HighExplosive's explosiveRadius (Items_Resource_Shell.xml)
STEEL = 20                      # the C# pawn_arc proof's stack (RM_KnockbackProof pawn_arc: Steel 20)
LANES = {"light": 6, "heavy": 20, "empty": 34}
ORDER = ["light", "heavy", "empty"]
PICKUP = 600                    # ticks a colonist may take to pick its load up
FIRE = 30                       # ticks the blast may take to throw (an Explosion spreads over a few ticks)
FLIGHT = 120                    # ticks stepped one by one while anything of the lane is in the air
SETTLE = 120
APART = 0.5                     # cells: under half a cell the two are drawn as one

carried = scene.contract(
    claim="a thrown colonist's load leaves its hands and flies whole on its own arc to its own cell",
    kind="A",
    exposure=c.value("colonist_empty", "positionInt.x") != STATION[0] + 8,      # the control colonist really flew
    success=[c.played(SETTLE)],                              # the judged run is the last: the empty lane's settle
    forbidden=[],
    end=SETTLE, limit=len(ORDER) * (PICKUP + FIRE + FLIGHT + SETTLE) + 900)


def at(x, z):
    return STATION[0] + x, STATION[1] + z


def journal(s, since):
    v = s.read("static:" + JOURNAL, "lines")
    if v.state != "ok":
        return []
    raw = v.v if isinstance(v.v, (list, tuple)) else str(v.v).splitlines()
    recs = []
    for line in raw:
        line = str(line).strip()
        if line.startswith("{"):
            try:
                r = json.loads(line)        # a carried_throw line names "thing" twice: json keeps the held thing's
            except ValueError:
                continue
            if isinstance(r.get("tick"), (int, float)) and r["tick"] >= since:
                recs.append(r)
    return recs


def thing_id(s, alias):
    d, n = s.read(alias, "def.defName"), s.read(alias, "thingIDNumber")
    return "%s%s" % (d.v, n.v) if d.state == "ok" and n.state == "ok" else None


def things_of(s, rect, defname):
    """-> {thing id: stackCount} of every thing of a def in a rect (the ids come from the read's .of)."""
    names = s.read_many(rect=rect, path="def.defName")
    counts = {v.of: v for v in s.read_many(rect=rect, path="stackCount")}
    out = {}
    for v in names:
        if v.state == "ok" and str(v.v) == defname:
            n = counts.get(v.of)
            out[v.of[len("thing:"):]] = int(n.v) if n is not None and n.state == "ok" else None
    return out


def num(v):
    try:
        return float(v.v) if v.state == "ok" else None
    except (TypeError, ValueError):
        return None


def empty(v):
    return v.state == "ok" and v.v in (None, "", "null", "None", 0)


def step(s):
    s.run(until=1, limit=5)


def lane_rect(z):
    x, zz = at(0, z)
    return (x, zz - 4, 22, 11)


def stage_loads(s):
    """The light lane's 20 Steel on its colonist's cell; the heavy lane's Muffalo dies where it stands."""
    lx, lz = at(8, LANES["light"])
    s.raw("jawa/spawn_batch", ops="Steel:%d,%d,%d" % (lx, lz, STEEL))
    muff = thing_id(s, "muffalo_heavy")
    s.raw("jawa/pawn_health", pawn=muff, action="add", hediff="MissingBodyPart", bodyPart="Brain")
    s.run(until=2, limit=10)


def lane(s, name, rows):
    z = LANES[name]
    col = "colonist_" + name
    cid = thing_id(s, col)
    rect = lane_rect(z)
    row = dict(cid=cid, load=None, load_def=None, before={}, hands=None, apart=None, after={}, recs=[], shots=[])
    if name in ("light", "heavy"):
        row["load_def"] = "Steel" if name == "light" else "Corpse_Muffalo"
        row["before"] = things_of(s, rect, row["load_def"])
        row["load"] = sorted(row["before"])[0] if row["before"] else None
        if row["load"] is None:
            row["err"] = "no %s on the lane before the haul" % row["load_def"]
            rows[name] = row
            return
        hx, hz = at(8, z + 6)
        s.raw("jawa/ordered_job", pawnId=cid, jobDef="HaulToCell", targetAId=row["load"], targetBX=hx, targetBZ=hz,
              count=(STEEL if name == "light" else 1), waitTicks=0)
        held = s.run(until=c.value(col, "carryTracker.innerContainer.innerList._size") > 0, limit=PICKUP)
        row["picked"] = (held.why, held.tick)
    px, pz = num(s.read(col, "positionInt.x")), num(s.read(col, "positionInt.z"))
    row["stood"] = (px, pz)
    t0 = s.read(col, "positionInt").tick or 0
    if px is None:
        row["err"] = "the colonist's cell could not be read before the blast"
        rows[name] = row
        return
    s.raw("jawa/explosion_at", at="%d,%d" % (px - 1, pz), radius=RADIUS, damType="Bomb", damAmount=1)
    launched = False
    for _ in range(FIRE):                       # find the launch tick: the first tick with this colonist's launch record
        step(s)
        recs = journal(s, t0)
        if any(r.get("type") == "launch" and r.get("thing") == cid for r in recs):
            launched = True
            break
    row["launched"] = launched
    pflyer = [v.of for v in s.read_many(rect=rect, path="def.defName") if v.state == "ok" and str(v.v) == "RM_PawnFlyer_Knockback"]
    pf = pflyer[0] if pflyer else None
    ct = [r for r in journal(s, t0) if r.get("type") == "carried_throw" and row["load"] and r.get("thing") == row["load"]]
    gf = ("thing:RM_ThingFlyer_Knockback%s" % ct[0].get("flyer")) if ct and int(ct[0].get("flyer") or -1) >= 0 else None
    if name == "light":
        reads = []
        if pf:
            reads += [(pf, "carriedThing"), (pf, "innerContainer.innerList[0].carryTracker.innerContainer.innerList._size")]
        if gf:
            reads += [(gf, "innerContainer.innerList._size"), (gf, "innerContainer.innerList[0].thingIDNumber"),
                      (gf, "innerContainer.innerList[0].stackCount")]
        vals = s.read_many(reads=reads) if reads else []
        row["hands"] = dict(pawn_flyer=pf, goods_flyer=gf, values=[(p, v.state, v.v if v.state == "ok" else None) for (_t, p), v in zip(reads, vals)])
        row["hands_ok"] = (pf is not None and gf is not None and len(vals) == 5 and empty(vals[0]) and num(vals[1]) == 0
                           and num(vals[2]) == 1 and "Steel%d" % int(num(vals[3]) or -1) == row["load"] and num(vals[4]) == STEEL)
        widest, ticks, shot = None, 0, False
        for _ in range(FLIGHT):                 # step the flight; compare the two ground positions on every tick
            if not (pf and gf):
                break
            v = s.read_many(reads=[(gf, "groundPos.x"), (gf, "groundPos.z"), (pf, "startVec.x"), (pf, "startVec.z"),
                                   (pf, "destCell.x"), (pf, "destCell.z"), (pf, "ticksFlying"), (pf, "ticksFlightTime")])
            if any(x.state != "ok" for x in v):
                break
            g = [num(x) for x in v]
            f = min(1.0, g[6] / g[7]) if g[7] else 1.0
            pxw, pzw = g[2] + (g[4] + 0.5 - g[2]) * f, g[3] + (g[5] + 0.5 - g[3]) * f
            gap = ((g[0] - pxw) ** 2 + (g[1] - pzw) ** 2) ** 0.5
            ticks += 1
            widest = gap if widest is None else max(widest, gap)
            if not shot and 0 < f < 1:
                s.shot((rect[0], rect[1], rect[2], rect[3]), name=name + "_air")
                shot = True
            step(s)
        row["apart"] = (widest, ticks)
    s.run(until=FLIGHT if name != "light" else 1, limit=FLIGHT + 10)
    s.run(until=SETTLE, limit=SETTLE + 60)
    s.shot(rect, name=name + "_after")
    row["recs"] = journal(s, t0)
    row["after"] = things_of(s, rect, row["load_def"]) if row["load_def"] else {}
    row["hands_after"] = s.read(col, "carryTracker.innerContainer.innerList._size")
    row["pos_after"] = (num(s.read(col, "positionInt.x")), num(s.read(col, "positionInt.z")))
    if row["load"]:
        row["load_pos"] = s.read_many(reads=[("thing:" + row["load"], "positionInt.x"), ("thing:" + row["load"], "positionInt.z"),
                                             ("thing:" + row["load"], "Spawned")])
    rows[name] = row


cast = {"colonist_" + n: dict(kind="Colonist", at=(8, z), faction="player") for n, z in LANES.items()}
cast["muffalo_heavy"] = dict(kind="Muffalo", at=(9, LANES["heavy"]), faction="player")
planted = scene.plant() == "light_limit_5"

with scene.open(GAME, contract=carried, needs={"mods": ["ExplosiveKnockback"], "map": STAGE, "calm": "standard"}) as s:
    s.stage(station=STATION, cast=cast)
    fields = ["blastPowerFromDamage", "lightMassLimit"]
    prior = {f: (s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=f) or {}).get("value") for f in fields}
    limit = prior.get("lightMassLimit")
    rows = {}
    try:
        s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="blastPowerFromDamage", value="False")
        if planted:
            s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="lightMassLimit", value="5")
        stage_loads(s)
        for name in ORDER:
            lane(s, name, rows)
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


def recs(name, kind, thing=None):
    return [r for r in rows[name]["recs"] if r.get("type") == kind and (thing is None or r.get("thing") == thing)]


def cell(rec, key):
    v = (rec or {}).get(key)
    return tuple(v) if isinstance(v, list) and len(v) == 2 else None


try:
    lim = float(limit)
except (TypeError, ValueError):
    lim = None
print("INFO lightMassLimit read %s kg before the scene (the bar is read at its default, 75)" % limit)

L = rows["light"]
ct = recs("light", "carried_throw", L["load"]) if L.get("load") else []
c0 = ct[0] if len(ct) == 1 else {}
row(bool(L.get("hands_ok")) and c0.get("act") == "thrown", "V_HANDS light",
    "carried_throw %s; on the launch tick %s (picked up: %s; stood %s%s)" % (
        {k: c0.get(k) for k in ("act", "reason", "count", "mass", "flyer", "to", "flightTicks")}, L.get("hands"),
        L.get("picked"), L.get("stood"), "; " + L["err"] if L.get("err") else ""))
widest, nt = L.get("apart") or (None, 0)
row(widest is not None and widest >= APART, "V_APART light",
    "widest ground gap %s cells over %d mid-flight tick(s) read, needs >= %s" % (None if widest is None else round(widest, 3), nt, APART))
land = recs("light", "item_land", L.get("load"))
l0 = land[0] if len(land) == 1 else {}
tb, ta = sum(v or 0 for v in L["before"].values()), sum(v or 0 for v in L["after"].values())
row(bool(l0) and cell(l0, "to") == cell(c0, "to") and l0.get("count") == STEEL and tb == ta == STEEL and len(L["after"]) == 1,
    "V_STACK_LAND light", "item_land %s vs planned %s; Steel before %s = %d, after %s = %d" % (
        {k: l0.get(k) for k in ("to", "dest", "count", "bounces", "place", "spawnFallback")}, cell(c0, "to"),
        L["before"], tb, L["after"], ta))
for name in ("light", "empty"):
    r = rows[name]
    la = recs(name, "launch", r["cid"])
    ld = recs(name, "land", r["cid"])
    a0, d0 = (la[0] if len(la) == 1 else {}), (ld[0] if len(ld) == 1 else {})
    h = r.get("hands_after")
    row(bool(a0) and bool(d0) and cell(d0, "at") == cell(a0, "to") and h is not None and h.state == "ok" and int(h.v) == 0,
        "V_PAWN_LAND " + name, "launch to %s, land at %s (downed %s), hands after %s, cell after %s" % (
            cell(a0, "to"), cell(d0, "at"), d0.get("downed"), (h.state, h.v if h.state == "ok" else None) if h is not None else None, r.get("pos_after")))
H = rows["heavy"]
hc = recs("heavy", "carried_throw", H.get("load")) if H.get("load") else []
h0 = hc[0] if len(hc) == 1 else {}
lp = H.get("load_pos") or []
lpos = (num(lp[0]), num(lp[1])) if len(lp) == 3 else None
frm = cell(h0, "from")
try:
    hm = float(h0.get("mass"))
except (TypeError, ValueError):
    hm = None
row(h0.get("act") == "dropped" and h0.get("reason") == "too_heavy" and hm is not None and lim is not None and hm > lim
    and frm is not None and lpos == (float(frm[0]), float(frm[1])), "V_HEAVY heavy",
    "carried_throw %s; the corpse lies at %s (picked up: %s%s)" % (
        {k: h0.get(k) for k in ("act", "reason", "mass", "from", "flyer")}, lpos, H.get("picked"), "; " + H["err"] if H.get("err") else ""))
E = rows["empty"]
ea = recs("empty", "launch", E["cid"])
e0 = ea[0] if len(ea) == 1 else {}
ec = [r for r in E["recs"] if r.get("type") == "carried_throw" and r.get("thingId") is not None and r.get("from") == e0.get("from")]
row(bool(e0) and e0.get("carried") == "none" and (e0.get("cells") or 0) >= 1 and not ec, "V_CONTROL empty",
    "launch %s; carried_throw at its cell: %d" % ({k: e0.get(k) for k in ("carried", "cells", "to", "stop")}, len(ec)))
print("%s sc_pawn_arc_carried_thing: %d failing row(s); pictures in %s" % ("PASS" if fails == 0 else "FAIL", fails, folder))
print(scene.judge(folder))
