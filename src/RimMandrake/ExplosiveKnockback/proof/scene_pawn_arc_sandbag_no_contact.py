"""scene_pawn_arc_sandbag_no_contact.py - Explosive Knockback 0.2.0, sc_pawn_arc_sandbag_no_contact: a colonist thrown
toward a pawn behind a sandbag is stopped by the sandbag and touches nobody (scene library 0.3.0).

Bar (design/concepts/ExplosiveKnockback/record.json): no_impact_without_contact. The kernel's rule is decided offline
(RM_KnockbackMath: nothing comes to rest on a sandbag cell, so the thrower goes back to the last free cell, and a stop on
the pawn beyond becomes PawnBeyondCover with hitOther false; 0.1.0 reported a bruise on a pawn it never touched). This
scene reads what only the game can show: on a real throw the standing pawn shows no impact and gains no injury.

Kind A. A fresh quicktest map on ArchSmall; one clean station; three lanes, 12 cells apart, each set off alone. Along +x:
  near     blast (6, z) | colonist (7, z) | Sandbags (8, z) | standing colonist (9, z)
  far      blast (6, z) | colonist (7, z) | free (8, z) | Sandbags (9, z) | standing colonist (10, z)
  control  blast (6, z) | colonist (7, z) | free (8, z) | standing colonist (9, z)       (the near lane, no sandbag)
Sandbags is Core's (Buildings_Security.xml, stuff Fabric/Leathery: Cloth), the player's. The standing colonist is 3 or
more cells from the blast, outside its 2.9 radius: only contact can touch it. The blast is jawa/explosion_at (Bomb,
radius 2.9, damage 1) with the player's setting "Bigger blasts throw harder" (blastPowerFromDamage) off, so it pushes at
the Bomb's plain force and harms by 1 (a real shell is 50 Bomb and would down the thrown colonist; the C# proofs staged
the same way, RM_KnockbackProof.Boom realPower false). sandbagsStopThrow stays at the player's value (read and printed;
the bar is read at its default, false). No raid, no hostile pawn.

The checks (each prints PASS or FAIL with what it read):
  V_STOP <lane>      near, far: the thrower's `blocked` or `launch` record reads stop PawnBeyondCover; a `launch` reads
                     hitOther false; otherImpact (where written) is 0
  V_NO_BRUISE <lane> near, far: no `bruise` record names the thrower
  V_UNTOUCHED <lane> near, far: the standing colonist's hediff count is unchanged and its Bruise+Crush severity did not rise
  V_CONTROL          control: stop Pawn, a `bruise` record naming the standing colonist, and its Bruise+Crush rose
  V_REACH far        the far throw was planned for at least 3 cells (else the lane is UNLAID: it never reached the sandbag)
  SHOTS              <lane>_after, 120 ticks after each blast

    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_pawn_arc_sandbag_no_contact.py
    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_pawn_arc_sandbag_no_contact.py --plant no_sandbag

UNRUN until Stage 6: written 2026-11-24 by RIMMANDRAKE_AUTOBUILD_EXPLOSIVEKNOCKBACK_SIX_BARS_LEFT and never run live.
The plant `no_sandbag` stages the near and far lanes without their sandbag: V_STOP, V_NO_BRUISE and V_UNTOUCHED must then
FAIL (the thrower reaches the pawn), which shows that the checks can see a contact.
Open points for the first run:
  - `explode` is NOT_BUILT: the blast is s.raw jawa/explosion_at, the settings write is s.raw jawa/mod_settings_field;
    both stamp the run EXPLORED, so it counts for no bar until those verbs are built.
  - the colonists are not drafted (`order` is NOT_BUILT): one that steps off its cell before the blast lands spoils its
    lane; each lane prints where its thrower stood.
  - whether a 1-cell-from-centre Bomb throw plans 3 or more cells (V_REACH far); if not, move the far lane's colonist.
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
STATION = (20, 20, 24, 40)
RADIUS = 2.9                    # Shell_HighExplosive's explosiveRadius (Items_Resource_Shell.xml)
# lane -> (z, sandbag x or None, standing colonist x)
LANES = {"near": (6, 8, 9), "far": (18, 9, 10), "control": (30, None, 9)}
ORDER = ["near", "far", "control"]
SETTLE = 240
HURT = ("Bruise", "Crush")      # Blunt's hediffSkin and hediff (Damages_MeleeWeapon.xml)

no_contact = scene.contract(
    claim="a colonist thrown at a pawn behind a sandbag is stopped by the sandbag and touches nobody",
    kind="A",
    exposure=c.state("bag_near", "positionInt") == "ok",       # the cover really stood in the line
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
    last, n = _MARK
    # by position while the list has not trimmed (the line before the cut is still the mark); a run on the same save
    # writes lines identical to the last run's, so the mark's text alone can cut inside this run's own lines
    if 0 < n <= len(raw) and raw[n - 1] == last:
        return raw[n:]
    for i in range(min(n, len(raw)) - 1, -1, -1):   # trimmed: the mark moved toward the front, never past position n
        if raw[i] == last:
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
    """-> (Bruise+Crush severity, hediff count) or None when the pawn cannot be read."""
    n = s.read(alias, "health.hediffSet.hediffs._size")
    if n.state != "ok":
        return None
    reads = []
    for i in range(int(n.v)):
        reads += [(alias, "health.hediffSet.hediffs[%d].def.defName" % i), (alias, "health.hediffSet.hediffs[%d].severityInt" % i)]
    vals = s.read_many(reads=reads) if reads else []
    sev = sum(float(vals[i + 1].v) for i in range(0, len(vals), 2)
              if vals[i].state == "ok" and str(vals[i].v) in HURT and vals[i + 1].state == "ok")
    return sev, int(n.v)


def lane_fire(s, name, rows):
    """Read a lane and set off its blast, on the paused tick that every lane shares."""
    z = LANES[name][0]
    thrower, other = "thrower_" + name, "other_" + name
    ids = {"thrower": thing_id(s, thrower), "other": thing_id(s, other)}
    start = s.read(thrower, "positionInt")
    bx, bz = at(6, z)
    rows[name] = dict(ids=ids, before=hurt(s, other), start=start.v, t0=start.tick, blast=(bx, bz))
    s.raw("jawa/explosion_at", at="%d,%d" % (bx, bz), radius=RADIUS, damType="Bomb", damAmount=1)


def lane_read(s, name, rows):
    r = rows[name]
    bx, bz = r.pop("blast")
    s.shot((bx - 2, bz - 3, 12, 7), name=name + "_after")
    recs, err = journal(s)
    mine = [x for x in (recs or []) if isinstance(x.get("tick"), (int, float)) and x["tick"] >= (r["t0"] or 0)
            and x.get("thing") == r["ids"]["thrower"] and x.get("type") in ("bruise", "launch", "blocked")]
    r.update(after=hurt(s, "other_" + name), recs=mine, err=err)

planted = scene.plant() == "no_sandbag"
cast, things = {}, {}
for name in ORDER:
    z, bag, ox = LANES[name]
    cast["thrower_" + name] = dict(kind="Colonist", at=(7, z), faction="player")
    cast["other_" + name] = dict(kind="Colonist", at=(ox, z), faction="player")
    if bag is not None and not planted:
        things["bag_" + name] = dict(thing="Sandbags", at=(bag, z), stuff="Cloth")

with scene.open(GAME, contract=no_contact, needs={"mods": ["ExplosiveKnockback"], "map": STAGE, "calm": "standard"}) as s:
    mark_journal(s)
    s.stage(station=STATION, cast=cast, things=things or None)
    stops = (s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="get", field="sandbagsStopThrow") or {}).get("value")
    prior = {f: (s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=f) or {}).get("value") for f in ["blastPowerFromDamage"]}
    rows = {}
    try:
        s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="blastPowerFromDamage", value="False")
        # every lane's blast on one paused tick, then one settle: the cast is not drafted, and with a settle per lane the
        # later lanes' pawns walked off their cells (2026-11-24 ArchSmall: the far lane's thrower 1 cell off, its throw
        # never reached the sandbag; APPARATUS FAULT). The lanes lie 12 cells apart; a blast reaches 2.9
        for name in ORDER:
            lane_fire(s, name, rows)
        s.run(until=SETTLE, limit=SETTLE + 120)
        for name in ORDER:
            lane_read(s, name, rows)
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


def of(name, kind):
    return [r for r in rows[name]["recs"] if r.get("type") == kind]


def num(rec, key):
    try:
        return float(rec.get(key))
    except (TypeError, ValueError, AttributeError):
        return None


print("INFO sandbagsStopThrow = %s (the bar is read at its default, False)" % stops)
for name in ("near", "far"):
    r = rows[name]
    moves = of(name, "blocked") + of(name, "launch")
    m = moves[0] if len(moves) == 1 else None
    other_imp = num(m, "otherImpact") if m else None
    ok = (m is not None and m.get("stop") == "PawnBeyondCover"
          and (m.get("type") != "launch" or str(m.get("hitOther")).lower() == "false")
          and (other_imp is None or other_imp == 0))
    row(ok, "V_STOP " + name, "%d move record(s) %s (thrower at %s%s)" % (
        len(moves), [{k: x.get(k) for k in ("type", "stop", "hitOther", "planned", "cells", "impact", "otherImpact")} for x in moves],
        r["start"], ", " + r["err"] if r["err"] else ""))
    row(not of(name, "bruise"), "V_NO_BRUISE " + name, "%d bruise record(s): %s" % (len(of(name, "bruise")), of(name, "bruise")))
    b, a = r["before"], r["after"]
    row(b is not None and a is not None and a[1] == b[1] and a[0] <= b[0], "V_UNTOUCHED " + name,
        "standing colonist (Bruise+Crush severity, hediff count) before %s, after %s" % (b, a))
    if name == "far":
        planned = num(m, "planned") if m else None
        row(planned is not None and planned >= 3, "V_REACH far", "planned %s cells, needs >= 3 to reach the sandbag%s" % (
            planned, "" if planned is not None and planned >= 3 else ": UNLAID"))
r = rows["control"]
moves = of("control", "blocked") + of("control", "launch")
br = of("control", "bruise")
b, a = r["before"], r["after"]
row(len(moves) == 1 and moves[0].get("stop") == "Pawn" and len(br) == 1 and br[0].get("other") == r["ids"]["other"]
    and b is not None and a is not None and a[0] > b[0], "V_CONTROL",
    "moves %s; bruise %s; standing colonist before %s, after %s" % (
        [{k: x.get(k) for k in ("type", "stop", "hitOther", "cells")} for x in moves],
        [{k: x.get(k) for k in ("other", "amount", "otherAmount")} for x in br], b, a))
print("%s sc_pawn_arc_sandbag_no_contact: %d failing row(s); pictures in %s" % ("PASS" if fails == 0 else "FAIL", fails, folder))
print(scene.judge(folder))
