"""scene_pawn_arc_bruise_sizes.py - Explosive Knockback 0.2.0, sc_pawn_arc_bruise_sizes: a thrown colonist that meets a
standing pawn bruises both, and the lighter one takes the larger hit (scene library 0.3.0).

Bar (design/concepts/ExplosiveKnockback/record.json): collision_bruise_by_size. The kernel's split is decided offline
(CollisionBruise(own, other) = 2 x impactDamagePerCell x impactFactor x other / (own + other)); this scene reads what only
the game can show: on a real throw the hit lands on the right body, in hediffs, and nobody is downed by a bruise.
Masses (Races_Animal_Base Mass 60 x baseBodySize, StatPart_BodySize): Squirrel 0.2 -> 12 kg, Elephant 4.0 -> 240 kg, a
human about 60 kg. Expected: into a squirrel the colonist takes ~1.3 and the squirrel ~6.7 (it may die of it); into an
elephant the colonist takes ~6.4 and the elephant ~1.6; into a colonist ~4 each.

Kind A. A fresh quicktest map on ArchSmall; one clean station; four lanes, 10 cells apart, each set off alone:
  lane     blast at (6, z)   thrower colonist at (8, z)   standing in its path at (9, z), all of the player's faction
  small    Squirrel          large    Elephant            colonist  Colonist            empty     nothing
The standing pawn is 3 cells from the blast, outside its 2.9 radius: only the bruise can touch it. The blast is
jawa/explosion_at (Bomb, radius 2.9, damage 1) with the player's setting "Bigger blasts throw harder"
(blastPowerFromDamage) off, so it pushes at the Bomb's plain force and harms by 1: a real shell is 50 Bomb (Damages_Misc
defaultDamage 50; the shell's comp has no override) and would down or kill the thrown colonist, which hides the bar.
The C# proofs staged their pawn throws the same way (RM_KnockbackProof.Boom, realPower false). No raid, no hostile pawn.

The checks (each prints PASS or FAIL with what it read):
  V_BRUISE_REC <lane>  small, large, colonist: one `bruise` record names the thrower and the standing pawn
  V_SMALL       the squirrel takes the larger hit: journal otherAmount > amount, and its new Bruise+Crush severity is
                larger than the colonist's (a dead squirrel counts as the larger hit)
  V_LARGE       the colonist takes the larger hit: amount > otherAmount, and its new Bruise+Crush is larger than the
                elephant's
  V_ALIKE       two colonists: amount / otherAmount within [0.8, 1.25] and the split follows the masses
                (amount / otherAmount = otherMass / mass within 0.05, the kernel's identity)
  V_NOT_DOWNED  colonist lane: neither colonist is Downed after the bruise
  V_HEDIFF <lane>  the standing pawn gained a Bruise or Crush hediff (the journal's bruise is a real one)
  V_EMPTY       empty lane: no `bruise` record, and the launch reads hitOther false
  SHOTS         <lane>_after, 120 ticks after each blast

    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_pawn_arc_bruise_sizes.py
    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_pawn_arc_bruise_sizes.py --plant no_bruise

UNRUN until Stage 6: written 2026-11-24 by RIMMANDRAKE_AUTOBUILD_EXPLOSIVEKNOCKBACK_SIX_BARS_LEFT and never run live.
The plant `no_bruise` turns impactDamageEnabled off: V_SMALL, V_LARGE and V_HEDIFF must then FAIL. The tolerances
0.8/1.25 and 0.05 are our own rule (the bar says "alike", no number; 0.05 covers the journal's 0.### rounding).
Open points for the first run:
  - `explode` is NOT_BUILT: the blast is s.raw jawa/explosion_at, and the settings write is s.raw jawa/mod_settings_field;
    both stamp the run EXPLORED, so it counts for no bar until `explode` (and a settings verb) is built.
  - the colonists are not drafted (`order` is NOT_BUILT): a colonist that steps off its cell in the one tick before the
    blast lands is read as a wrong lane (V_BRUISE_REC fails and says where it stood).
  - the landing-on case (a colonist thrown onto a pawn at the end of its flight: `land_on_pawn`) is not staged: where a
    throw ends depends on the cells a 6-cell flight clears, and no lane here stages it reliably. Open, not claimed.
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
LANES = {"small": ("Squirrel", 6), "large": ("Elephant", 16), "colonist": ("Colonist", 26), "empty": (None, 36)}
ORDER = ["small", "large", "colonist", "empty"]
SETTLE = 240                    # ticks after each blast: a 6-cell throw lands well inside it
HURT = ("Bruise", "Crush")      # Blunt's hediffSkin and hediff (Damages_MeleeWeapon.xml); the blast's Bomb gives Shredded/Crack

bruise_sizes = scene.contract(
    claim="a thrown colonist that meets a standing pawn bruises both, the lighter one harder, and downs nobody",
    kind="A",
    exposure=c.value("thrower_empty", "positionInt.x") > STATION[0] + 8,     # a blast of this staging really throws
    success=[c.played(SETTLE)],                              # the judged run is the last: the last lane's settle
    forbidden=[],
    end=SETTLE, limit=len(ORDER) * SETTLE + 900)


def at(x, z):
    return STATION[0] + x, STATION[1] + z



# The journal is a static list: it outlives a load. Every run of a scene loads the same stage save, so its thing ids and
# ticks repeat, and a filter on tick or id cannot tell this run's records from the last run's. mark_journal keeps the
# last line already there when the session opens; since_mark keeps only the lines after it (the list trims its oldest
# 1000 lines at 4000, so the mark is a line's text, not a position; a mark trimmed away means every line is this run's).
_MARK = []


def mark_journal(s):
    v = s.read("static:" + JOURNAL, "lines")
    lines = list(v.v) if v.state == "ok" and isinstance(v.v, (list, tuple)) else []
    _MARK[:] = [lines[-1] if lines else None, len(lines)]
    print("INFO journal mark: %d line(s) before this run" % len(lines))


def since_mark(raw):
    raw = list(raw)
    if not _MARK or _MARK[0] is None:
        return raw
    for i in range(len(raw) - 1, -1, -1):
        if raw[i] == _MARK[0]:
            return raw[i + 1:]
    return raw


def journal(s):
    v = s.read("static:" + JOURNAL, "lines")
    if v.state != "ok":
        return None, "journal %s" % v.state
    raw = since_mark(v.v if isinstance(v.v, (list, tuple)) else str(v.v).splitlines())
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
    return "%s%d" % (d.v, int(float(n.v))) if d.state == "ok" and n.state == "ok" else None   # an id reads back as a float


def hurt(s, alias):
    """-> (new-injury severity of Bruise+Crush, hediff count, dead) or None when the pawn cannot be read."""
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


def lane(s, name, rows):
    _kind, z = LANES[name]
    thrower, other = "thrower_" + name, ("other_" + name if LANES[name][0] else None)
    ids = {"thrower": thing_id(s, thrower), "other": thing_id(s, other) if other else None}
    before = {"thrower": hurt(s, thrower), "other": hurt(s, other) if other else None}
    start = s.read(thrower, "positionInt")
    t0 = start.tick
    bx, bz = at(6, z)
    s.raw("jawa/explosion_at", at="%d,%d" % (bx, bz), radius=RADIUS, damType="Bomb", damAmount=1)
    s.run(until=SETTLE, limit=SETTLE + 120)
    s.shot((bx - 2, bz - 3, 14, 7), name=name + "_after")
    recs, err = journal(s)
    mine = [r for r in (recs or []) if isinstance(r.get("tick"), (int, float)) and r["tick"] >= (t0 or 0)
            and r.get("def") == "Human" and r.get("type") in ("bruise", "launch", "blocked")]
    after = {"thrower": hurt(s, thrower), "other": hurt(s, other) if other else None}
    downed = {k: s.read(a, "Downed") for k, a in (("thrower", thrower), ("other", other)) if a}
    rows[name] = dict(ids=ids, before=before, after=after, recs=mine, err=err, start=start.v,
                      downed={k: (v.state == "ok" and str(v.v) == "True") for k, v in downed.items()})


cast = {}
for name in ORDER:
    kind, z = LANES[name]
    cast["thrower_" + name] = dict(kind="Colonist", at=(8, z), faction="player")
    if kind:
        cast["other_" + name] = dict(kind=kind, at=(9, z), faction="player")

with scene.open(GAME, contract=bruise_sizes, needs={"mods": ["ExplosiveKnockback"], "map": STAGE, "calm": "standard"}) as s:
    mark_journal(s)
    s.stage(station=STATION, cast=cast)
    fields = ["blastPowerFromDamage"] + (["impactDamageEnabled"] if scene.plant() == "no_bruise" else [])
    prior = {f: (s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=f) or {}).get("value") for f in fields}
    rows = {}
    try:
        s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="blastPowerFromDamage", value="False")
        if scene.plant() == "no_bruise":
            s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="impactDamageEnabled", value="False")
        for name in ORDER:
            lane(s, name, rows)
    finally:
        for f, v in prior.items():   # each setting back to what it read before, on every exit path
            if v is not None:
                s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=f, value=str(v))
    folder = s.run_dir

fails = 0


def row(ok, ident, text):
    global fails
    fails += not ok
    print("%s %s: %s" % ("PASS" if ok else "FAIL", ident, text))


def bruise_of(name):
    r = rows[name]
    tid = r["ids"]["thrower"]
    for rec in r["recs"]:
        if rec.get("type") == "bruise" and rec.get("thing") == tid:
            return rec
    return None


def gain(name, who):
    b, a = rows[name]["before"][who], rows[name]["after"][who]
    if a is None or b is None:
        return None
    return a[0] - b[0]


def num(rec, key):
    try:
        return float(rec.get(key))
    except (TypeError, ValueError, AttributeError):
        return None


for name in ("small", "large", "colonist"):
    b = bruise_of(name)
    r = rows[name]
    row(b is not None and b.get("other") == r["ids"]["other"], "V_BRUISE_REC " + name,
        "bruise %s (thrower %s, standing %s, thrower started at %s, %d record(s) read%s)" % (
            None if b is None else {k: b.get(k) for k in ("other", "mass", "otherMass", "amount", "otherAmount")},
            r["ids"]["thrower"], r["ids"]["other"], r["start"], len(r["recs"]), ", " + r["err"] if r["err"] else ""))
    g = gain(name, "other")
    row(g is not None and g > 0, "V_HEDIFF " + name, "standing pawn's new Bruise+Crush severity %s (before %s, after %s)" % (
        g, r["before"]["other"], r["after"]["other"]))

bs, bl, bc = bruise_of("small"), bruise_of("large"), bruise_of("colonist")
amt = {n: (num(b, "amount"), num(b, "otherAmount")) if b else (None, None) for n, b in (("small", bs), ("large", bl), ("colonist", bc))}
gs, gso = gain("small", "thrower"), gain("small", "other")
squirrel_dead = rows["small"]["after"]["other"] is None or rows["small"]["after"]["other"][2]   # unreadable: dead and gone
a, o = amt["small"]
row(a is not None and o is not None and o > a and (squirrel_dead or (gs is not None and gso is not None and gso > gs)), "V_SMALL",
    "journal colonist %s vs squirrel %s; hediffs colonist +%s vs squirrel +%s (squirrel dead %s)" % (a, o, gs, gso, squirrel_dead))
a, o = amt["large"]
gl, glo = gain("large", "thrower"), gain("large", "other")
row(a is not None and o is not None and a > o and gl is not None and glo is not None and gl > glo, "V_LARGE",
    "journal colonist %s vs elephant %s; hediffs colonist +%s vs elephant +%s" % (a, o, gl, glo))
a, o = amt["colonist"]
m, om = (num(bc, "mass"), num(bc, "otherMass")) if bc else (None, None)
ratio = a / o if a and o else None
follows = ratio is not None and m and om and abs(ratio - om / m) <= 0.05
row(ratio is not None and 0.8 <= ratio <= 1.25 and bool(follows), "V_ALIKE",
    "amount %s / otherAmount %s = %s (limit 0.8..1.25); masses %s, %s -> otherMass/mass %s (limit +-0.05)" % (
        a, o, ratio, m, om, (om / m) if m and om else None))
d = rows["colonist"]["downed"]
row(not d.get("thrower") and not d.get("other"), "V_NOT_DOWNED", "thrower downed %s, standing colonist downed %s" % (
    d.get("thrower"), d.get("other")))
er = rows["empty"]
tid = er["ids"]["thrower"]
eb = [x for x in er["recs"] if x.get("type") == "bruise" and x.get("thing") == tid]
el = [x for x in er["recs"] if x.get("type") == "launch" and x.get("thing") == tid]
row(not eb and len(el) == 1 and str(el[0].get("hitOther")).lower() == "false", "V_EMPTY",
    "%d bruise record(s), launch %s" % (len(eb), [{k: x.get(k) for k in ("stop", "hitOther", "cells")} for x in el]))
print("%s sc_pawn_arc_bruise_sizes: %d failing row(s); pictures in %s" % ("PASS" if fails == 0 else "FAIL", fails, folder))
print(scene.judge(folder))
