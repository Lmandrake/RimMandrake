"""scene_pawn_land_on_pawn_sizes.py - Explosive Knockback 0.2.0, the landing half of bar collision_bruise_by_size: a thrown
colonist that comes down on a pawn which walked onto its landing cell mid-flight bruises both, each by the other's size
(scene library 0.3.0). Items RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN, RIMMANDRAKE_COVER_KNOCKBACK_BAR_HALVES_NO_LIVE_CHECK_SEES.

scene_pawn_arc_bruise_sizes reads the other half (a throw stopped mid-path by a standing pawn: RM_KnockbackPlan.Collide).
Its bruises never come from a landing, so the blind challenge's planted C_LANDING_BRUISE_SWAPPED (the amounts of
RM_PawnFlyerPatches.Landed swapped) passed it 11/11 (visit 1, 2026-11-25). This scene reads the landing.

Kind A. The stage save RM_Stage_ExplosiveKnockback on ArchSmall; four lanes, 10 cells apart, all of the player's faction:
  lane      blast at (7, z)   thrower colonist at (8, z)   walker at (10, z + 1), ordered onto (10, z)
  small     Squirrel (Mass 60 x 0.2 = 12 kg)      large  Muffalo (60 x 2.4 = 144 kg)
  colonist  Colonist (about 60 kg)                empty  no walker
The blast is jawa/explosion_at (Bomb, radius 2.9, damage 1) with "Bigger blasts throw harder" (blastPowerFromDamage) off and
the throw cap maxThrowCells at 2. One cell from a force-1 Bomb a colonist plans 3 cells or more (sc_mortar_throw), so the cap
makes every landing cell (10, z), on the lane's line, with no wall or pawn on the path at the blast. The walker stands one cell
off that line, 3.16 cells from the blast (outside 2.9), and is ordered onto (10, z) 2 ticks before the blast. A pawn's
position moves when its step ends (12 to 14 ticks for these three at 4.4 to 4.8 cells/s), and a flight of 2 cells lasts the
flyer's minimum, 0.3 s = 18 ticks (RM_PawnFlyer_Knockback flightDurationMin). So the walker is off the path when the throw is
planned and on the cell when the colonist lands: the case "a pawn that walks onto the landing cell mid-flight".

The checks (each prints PASS, FAIL or INVALID with what it read):
  V_LAND_REC <lane>  small, large, colonist: one `land_on_pawn` record names the thrower and the walker (INVALID when the
                     walker was not on the cell: the opportunity was missed, the mod is not judged)
  V_SMALL      the squirrel takes the larger hit: otherAmount > amount, and its new Bruise+Crush is larger (or it died)
  V_LARGE      the colonist takes the larger hit: amount > otherAmount, and its new Bruise+Crush is larger than the muffalo's
  V_ALIKE      two colonists: the split follows the masses (amount / otherAmount = otherMass / mass within 0.05) and each
               hit is at most 4.45 (a like pair's two cells of wall impact, 1.25 / 2.25 x 2 x 4 per cell)
  V_NOT_DOWNED colonist lane: neither colonist is downed
  V_HEDIFF <lane>  the walker gained a Bruise or Crush hediff
  V_EMPTY      empty lane: the colonist launched, and no `land_on_pawn` record names it

    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_pawn_land_on_pawn_sizes.py
    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_pawn_land_on_pawn_sizes.py --plant no_bruise

The plant no_bruise turns impactDamageEnabled off: V_SMALL, V_LARGE and V_HEDIFF must FAIL. The build plant
C_LANDING_BRUISE_SWAPPED (design/concepts/ExplosiveKnockback/version/in_game/visit_1/plants/) must make V_SMALL and V_LARGE
FAIL. The 0.05 and 4.45 are the same rule as scene_pawn_arc_bruise_sizes.
"""
import json

import scene
from scene import cond as c

GAME = "ArchSmall"
STAGE = "RM_Stage_ExplosiveKnockback"
SETTINGS = "RimMandrake.ExplosiveKnockback.RimMandrakeExplosiveKnockbackSettings"
JOURNAL = "RimMandrake.ExplosiveKnockback.RM_KnockbackJournal"
STATION = (20, 20, 30, 44)
RADIUS = 2.9
CAP = 2                          # maxThrowCells for the scene: every landing cell is (10, z)
LANES = {"small": ("Squirrel", 6), "large": ("Muffalo", 16), "colonist": ("Colonist", 26), "empty": (None, 36)}
ORDER = ["small", "large", "colonist", "empty"]
LEAD = 2                         # ticks between the walkers' order and the blasts
SETTLE = 240
HURT = ("Bruise", "Crush")


def put(s, field, value, strict=True):
    """Set one static settings field as the session's driver, and read the write back (a driverless write is refused)."""
    r = s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field, value=value, driver=s.id) or {}
    if strict and (r.get("success") is not True or str(r.get("valueAfter")) != str(value)):
        raise RuntimeError("SETTING_REFUSED: %s=%s was not written (%s)" % (field, value, {k: r.get(k) for k in ("success", "valueAfter", "error", "message")}))
    return r


land_sizes = scene.contract(
    claim="a thrown colonist that lands on a pawn which walked onto its landing cell bruises both, the lighter one harder, and downs nobody",
    kind="A",
    exposure=c.value("thrower_empty", "positionInt.x") > STATION[0] + 8,
    success=[c.played(SETTLE)],
    forbidden=[],
    end=SETTLE, limit=SETTLE + LEAD + 900)


def at(x, z):
    return STATION[0] + x, STATION[1] + z


_MARK = []


def mark_journal(s):
    v = s.read("static:" + JOURNAL, "lines")
    lines = list(v.v) if v.state == "ok" and isinstance(v.v, (list, tuple)) else []
    _MARK[:] = [lines[-1] if lines else None, len(lines)]


def since_mark(raw):
    raw = list(raw)
    if not _MARK or _MARK[0] is None:
        return raw
    last, n = _MARK
    if 0 < n <= len(raw) and raw[n - 1] == last:
        return raw[n:]
    for i in range(min(n, len(raw)) - 1, -1, -1):
        if raw[i] == last:
            return raw[i + 1:]
    return raw


def journal(s):
    v = s.read("static:" + JOURNAL, "lines")
    if v.state != "ok":
        return [], "journal %s" % v.state
    recs = []
    for line in since_mark(v.v if isinstance(v.v, (list, tuple)) else str(v.v).splitlines()):
        line = str(line).strip()
        if line.startswith("{"):
            try:
                recs.append(json.loads(line))
            except ValueError:
                pass
    return recs, None


def thing_id(s, alias):
    d, n = s.read(alias, "def.defName"), s.read(alias, "thingIDNumber")
    return ("%s%d" % (d.v, int(float(n.v))), int(float(n.v))) if d.state == "ok" and n.state == "ok" else (None, None)


def hurt(s, alias):
    """-> (Bruise+Crush severity, hediff count, dead) or None when the pawn cannot be read (a dead animal reads gone)."""
    n = s.read(alias, "health.hediffSet.hediffs._size")
    dead = s.read(alias, "Dead")
    if n.state != "ok":
        return None
    reads = []
    for i in range(int(n.v)):
        reads += [(alias, "health.hediffSet.hediffs[%d].def.defName" % i), (alias, "health.hediffSet.hediffs[%d].severityInt" % i)]
    vals = s.read_many(reads=reads) if reads else []
    sev = 0.0
    for i in range(0, len(vals), 2):
        if vals[i].state == "ok" and str(vals[i].v) in HURT and vals[i + 1].state == "ok":
            sev += float(vals[i + 1].v)
    return sev, int(n.v), dead.state == "ok" and str(dead.v) == "True"


cast = {}
for name in ORDER:
    kind, z = LANES[name]
    cast["thrower_" + name] = dict(kind="Colonist", at=(8, z), faction="player")
    if kind:
        cast["walker_" + name] = dict(kind=kind, at=(10, z + 1), faction="player")

rows = {}
with scene.open(GAME, contract=land_sizes, needs={"mods": ["ExplosiveKnockback"], "map": STAGE, "calm": "standard"}) as s:
    mark_journal(s)
    s.stage(station=STATION, cast=cast)
    fields = ["blastPowerFromDamage", "maxThrowCells"] + (["impactDamageEnabled"] if scene.plant() == "no_bruise" else [])
    prior = {f: (s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=f) or {}).get("value") for f in fields}
    try:
        put(s, "blastPowerFromDamage", "False")
        put(s, "maxThrowCells", str(CAP))
        if scene.plant() == "no_bruise":
            put(s, "impactDamageEnabled", "False")
        for name in ORDER:
            kind, z = LANES[name]
            t, w = "thrower_" + name, ("walker_" + name if kind else None)
            rows[name] = dict(thrower=t, walker=w, ids={"thrower": thing_id(s, t), "walker": thing_id(s, w) if w else (None, None)},
                              before={"thrower": hurt(s, t), "walker": hurt(s, w) if w else None},
                              start=s.read(t, "positionInt").v, land=at(8 + CAP, z))
        for name in ORDER:              # every walker ordered on one tick, every blast on one tick LEAD ticks later
            w = rows[name]["walker"]
            if w:
                lx, lz = rows[name]["land"]
                # a Goto reads its cell from targetA; the library's job verb puts a cell in targetB, so the order goes raw
                got = s.raw("jawa/ordered_job", pawnId=rows[name]["ids"]["walker"][0], jobDef="Goto", targetAX=lx, targetAZ=lz, waitTicks=0) or {}
                rows[name]["order"] = {k: got.get(k) for k in ("success", "accepted", "afterJobDef", "nowRunningRequested", "error", "message") if k in got}
        s.run(until=LEAD, limit=LEAD + 60)
        for name in ORDER:
            _k, z = LANES[name]
            rows[name]["walker_at_blast"] = s.read(rows[name]["walker"], "positionInt").v if rows[name]["walker"] else None
            bx, bz = at(7, z)
            s.raw("jawa/explosion_at", at="%d,%d" % (bx, bz), radius=RADIUS, damType="Bomb", damAmount=1)
        s.run(until=SETTLE, limit=SETTLE + 120)
        recs, err = journal(s)
        for name in ORDER:
            r = rows[name]
            tid = r["ids"]["thrower"][0]
            r["recs"] = [x for x in recs if x.get("thing") == tid and x.get("type") in ("launch", "land_on_pawn", "bruise", "land", "redirect")]
            r["err"] = err
            r["after"] = {"thrower": hurt(s, r["thrower"]), "walker": hurt(s, r["walker"]) if r["walker"] else None}
            r["walker_end"] = s.read(r["walker"], "positionInt").v if r["walker"] else None
            r["downed"] = {k: (lambda v: v.state == "ok" and str(v.v) == "True")(s.read(a, "Downed")) for k, a in
                           (("thrower", r["thrower"]), ("walker", r["walker"])) if a}
        s.shot((STATION[0] + 4, STATION[1] + 2, 10, 38), name="lanes_after")
    finally:
        for f, v in prior.items():
            if v is not None:
                put(s, f, str(v), strict=False)
    folder = s.run_dir

fails = invalid = 0


def row(verdict, ident, text):
    global fails, invalid
    fails += verdict == "FAIL"
    invalid += verdict == "INVALID"
    print("%s %s: %s" % (verdict, ident, text))


def rec_of(name, kind):
    return [x for x in rows[name]["recs"] if x.get("type") == kind]


def num(rec, key):
    try:
        return float(rec.get(key))
    except (TypeError, ValueError, AttributeError):
        return None


def gain(name, who):
    b, a = rows[name]["before"][who], rows[name]["after"][who]
    return None if a is None or b is None else a[0] - b[0]


land = {}
for name in ("small", "large", "colonist"):
    r = rows[name]
    wid = r["ids"]["walker"][1]
    hits = [x for x in rec_of(name, "land_on_pawn") if x.get("pawnId") == wid]
    launch = rec_of(name, "launch")
    to = launch[0].get("to") if launch else None
    on_cell = to is not None and list(to) == list(r["land"])
    if hits:
        land[name] = hits[0]
        row("PASS", "V_LAND_REC " + name, "land_on_pawn %s" % {k: hits[0].get(k) for k in ("pawn", "mass", "otherMass", "amount", "otherAmount")})
    elif not on_cell or r["walker_at_blast"] is None:
        row("INVALID", "V_LAND_REC " + name, "no opportunity: launch to %s (want %s), walker at the blast %s, at the end %s, order %s" % (
            to, r["land"], r["walker_at_blast"], r["walker_end"], r.get("order")))
    else:
        row("FAIL", "V_LAND_REC " + name, "the colonist landed on %s with the walker there at the end (%s) and no land_on_pawn record; "
            "walker at the blast %s; records %s%s" % (to, r["walker_end"], r["walker_at_blast"], [x.get("type") for x in r["recs"]],
                                                       ", " + r["err"] if r["err"] else ""))
    if name in land:
        g = gain(name, "walker")
        dead = r["after"]["walker"] is None or r["after"]["walker"][2]
        row("PASS" if (g is not None and g > 0) or dead else "FAIL", "V_HEDIFF " + name,
            "walker's new Bruise+Crush %s (before %s, after %s)" % (g, r["before"]["walker"], r["after"]["walker"]))


def pair(name):
    rec = land.get(name)
    return (num(rec, "amount"), num(rec, "otherAmount")) if rec else (None, None)


a, o = pair("small")
if "small" in land:
    gs, gw = gain("small", "thrower"), gain("small", "walker")
    dead = rows["small"]["after"]["walker"] is None or rows["small"]["after"]["walker"][2]
    row("PASS" if a is not None and o is not None and o > a and (dead or (gs is not None and gw is not None and gw > gs)) else "FAIL", "V_SMALL",
        "colonist %s vs squirrel %s; hediffs colonist +%s vs squirrel +%s (squirrel dead %s)" % (a, o, gs, gw, dead))
a, o = pair("large")
if "large" in land:
    gl, gw = gain("large", "thrower"), gain("large", "walker")
    row("PASS" if a is not None and o is not None and a > o and gl is not None and gw is not None and gl > gw else "FAIL", "V_LARGE",
        "colonist %s vs muffalo %s; hediffs colonist +%s vs muffalo +%s" % (a, o, gl, gw))
a, o = pair("colonist")
if "colonist" in land:
    m, om = num(land["colonist"], "mass"), num(land["colonist"], "otherMass")
    ratio = a / o if a and o else None
    follows = ratio is not None and m and om and abs(ratio - om / m) <= 0.05
    light = a is not None and o is not None and max(a, o) <= 4.45
    row("PASS" if follows and light else "FAIL", "V_ALIKE", "amount %s / otherAmount %s = %s; masses %s, %s -> %s (limit +-0.05); both at most 4.45: %s" % (
        a, o, ratio, m, om, (om / m) if m and om else None, light))
    d = rows["colonist"]["downed"]
    row("PASS" if not d.get("thrower") and not d.get("walker") else "FAIL", "V_NOT_DOWNED", "thrower downed %s, walker downed %s" % (
        d.get("thrower"), d.get("walker")))
el, eh = rec_of("empty", "launch"), rec_of("empty", "land_on_pawn")
row("PASS" if len(el) == 1 and not eh else "FAIL", "V_EMPTY", "%d launch record(s) to %s, %d land_on_pawn record(s)" % (
    len(el), [x.get("to") for x in el], len(eh)))
print("%s sc_pawn_land_on_pawn_sizes: %d failing, %d invalid row(s); pictures in %s" % (
    "PASS" if fails == 0 and invalid == 0 else ("FAIL" if fails else "INVALID"), fails, invalid, folder))
print(scene.judge(folder))
