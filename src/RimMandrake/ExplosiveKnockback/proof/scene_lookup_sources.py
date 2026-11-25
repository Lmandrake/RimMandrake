"""scene_lookup_sources.py - Explosive Knockback 0.2.0, the game-side wiring of the tuning lookup (bars per_weapon_tuning and
inv_weapon_ext_fields): which def on a real explosion the hook reads its tuning from (scene library 0.3.0). Item
RIMMANDRAKE_COVER_KNOCKBACK_BAR_HALVES_NO_LIVE_CHECK_SEES, part (3).

sc_lookup's proof entry lookup_projectile runs one lane: a projectile's own extension. The lookup order itself
(projectile, weapon, damage type, unpatched) is pure kernel (KbLookup.Resolve, K-13 offline). What only the game shows is
that RM_Patch_DamageWorker_ExplosionKnockback.ConfigOf reads Explosion.weapon and the DamageDef of a live blast. This scene
reads those two sources, and the projectile over a weapon.

Kind A. The stage save RM_Stage_ExplosiveKnockback on ArchSmall; four lanes, 6 cells apart, one colonist per lane at (8, z),
the blast at (7, z): jawa/explosion_at radius 2.9, damage 1. "Bigger blasts throw harder" (blastPowerFromDamage) is off, so
each request's force is its source's own force (damage ratio 1), and the global cap maxThrowCells is 12, above every lane's
throw. The extensions are added for the session with jawa/def_mod_extension (the session's release puts the defs back):
  lane       explosion                                         its tuning                          want source  force
  weapon     Bomb, weapon Gun_Revolver                         Gun_Revolver: force 2.5             weapon       2.5
  projectile Bomb, weapon Gun_Revolver, projectile Bullet_Revolver  Bullet_Revolver: force 1.6   projectile   1.6
  bomb       Bomb                                              Bomb's XML extension, force 1.0     damageDef    1.0
  flame      Flame                                             Flame's XML extension, force 0.5    damageDef    0.5

The checks (each prints PASS, FAIL or INVALID with what it read):
  V_SOURCE <lane>  exactly one request line names the lane's colonist; its source and force are the lane's
  V_ORDER          the launches' planned cells fall in force order: weapon > projectile > bomb > flame (a lane with no
                   launch counts 0). The kernel's rounding of 4 x force x falloff puts them 7, 4, 3, 1 at one cell.

    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_lookup_sources.py
    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_lookup_sources.py --plant no_weapon_ext
    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_lookup_sources.py --plant fire_off

Plant no_weapon_ext: Gun_Revolver gets no extension, the same reading as a ConfigOf that ignores Explosion.weapon. V_SOURCE
weapon and V_ORDER must FAIL. Plant fire_off: "fire at half" (fireAtHalf) off sets a fire damage type's force to 0, so the
Flame blast requests nothing: V_SOURCE flame must FAIL.
"""
import json

import scene
from scene import cond as c

GAME = "ArchSmall"
STAGE = "RM_Stage_ExplosiveKnockback"
SETTINGS = "RimMandrake.ExplosiveKnockback.RimMandrakeExplosiveKnockbackSettings"
JOURNAL = "RimMandrake.ExplosiveKnockback.RM_KnockbackJournal"
EXT = "RimMandrake.ExplosiveKnockback.RM_KnockbackExtension"
STATION = (20, 20, 30, 44)
RADIUS = 2.9
CAP = 12
SETTLE = 240
WEAPON, PROJECTILE = "Gun_Revolver", "Bullet_Revolver"
WEAPON_FORCE, PROJECTILE_FORCE = 2.5, 1.6
# lane -> (z, damType, weapon, projectile, want source, want force)
LANES = {
    "weapon": (4, "Bomb", WEAPON, None, "weapon", WEAPON_FORCE),
    "projectile": (10, "Bomb", WEAPON, PROJECTILE, "projectile", PROJECTILE_FORCE),
    "bomb": (16, "Bomb", None, None, "damageDef", 1.0),
    "flame": (22, "Flame", None, None, "damageDef", 0.5),
}
ORDER = ["weapon", "projectile", "bomb", "flame"]


def put(s, field, value, strict=True):
    """Set one static settings field as the session's driver, and read the write back (a driverless write is refused)."""
    r = s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field, value=value, driver=s.id) or {}
    if strict and (r.get("success") is not True or str(r.get("valueAfter")) != str(value)):
        raise RuntimeError("SETTING_REFUSED: %s=%s was not written (%s)" % (field, value, {k: r.get(k) for k in ("success", "valueAfter", "error", "message")}))
    return r


def add_ext(s, def_name, force):
    """Give a ThingDef a scene-only knockback extension and read it back first in the def's list."""
    r = s.raw("jawa/def_mod_extension", defType="ThingDef", defName=def_name, action="add", typeName=EXT,
              fields=json.dumps({"force": force}), driver=s.id) or {}
    after = r.get("extensionsAfter") or []
    head = after[0] if after else {}
    got = (head.get("fields") or {}).get("force")
    if r.get("success") is not True or head.get("type") != EXT or got is None or abs(float(got) - force) > 1e-4:
        raise RuntimeError("EXTENSION_REFUSED: %s force %s was not added (%s)" % (def_name, force, {k: r.get(k) for k in ("success", "error", "message", "extensionsAfter")}))
    return r


lookup = scene.contract(
    claim="a live blast takes its knockback tuning from its weapon, from its projectile over its weapon, and from its damage type, each force read from that def",
    kind="A",
    exposure=c.value("p_weapon", "positionInt.x") > STATION[0] + 8,
    success=[c.played(SETTLE)],
    forbidden=[],
    end=SETTLE, limit=SETTLE + 900)


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
    return "%s%d" % (d.v, int(float(n.v))) if d.state == "ok" and n.state == "ok" else None


cast = {"p_" + name: dict(kind="Colonist", at=(8, LANES[name][0]), faction="player") for name in ORDER}
rows, setup = {}, {}
with scene.open(GAME, contract=lookup, needs={"mods": ["ExplosiveKnockback"], "map": STAGE, "calm": "standard"}) as s:
    mark_journal(s)
    s.stage(station=STATION, cast=cast)
    fields = ["blastPowerFromDamage", "maxThrowCells"] + (["fireAtHalf"] if scene.plant() == "fire_off" else [])
    prior = {f: (s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=f) or {}).get("value") for f in fields}
    try:
        put(s, "blastPowerFromDamage", "False")
        put(s, "maxThrowCells", str(CAP))
        if scene.plant() == "fire_off":
            put(s, "fireAtHalf", "False")
        if scene.plant() != "no_weapon_ext":
            setup["weapon_ext"] = add_ext(s, WEAPON, WEAPON_FORCE).get("extensionsAfter")
        setup["projectile_ext"] = add_ext(s, PROJECTILE, PROJECTILE_FORCE).get("extensionsAfter")
        for name in ORDER:
            rows[name] = dict(id=thing_id(s, "p_" + name), start=s.read("p_" + name, "positionInt").v)
        for name in ORDER:
            z, dam, weapon, projectile, _src, _f = LANES[name]
            bx, bz = at(7, z)
            args = dict(at="%d,%d" % (bx, bz), radius=RADIUS, damType=dam, damAmount=1)
            if weapon:
                args["weapon"] = weapon
            if projectile:
                args["projectile"] = projectile
            got = s.raw("jawa/explosion_at", **args) or {}
            rows[name]["boom"] = {k: got.get(k) for k in ("success", "damType", "weapon", "projectile", "error", "message") if k in got}
            rows[name]["centre"] = [bx, bz]
        s.run(until=SETTLE, limit=SETTLE + 120)
        recs, err = journal(s)
        for name in ORDER:
            r = rows[name]
            mine = [x for x in recs if x.get("thing") == r["id"]]
            r["requests"] = [x for x in mine if x.get("type") == "request"]
            r["launches"] = [x for x in mine if x.get("type") == "launch"]
            r["err"] = err
            r["end"] = s.read("p_" + name, "positionInt").v
        s.shot((STATION[0] + 4, STATION[1] + 1, 18, 26), name="lanes_after")
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


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


for name in ORDER:
    r = rows[name]
    _z, _dam, weapon, projectile, want_src, want_force = LANES[name]
    if r["boom"].get("success") is not True or r["boom"].get("weapon") != weapon or r["boom"].get("projectile") != projectile:
        row("INVALID", "V_SOURCE " + name, "the blast was not fired as staged: %s" % r["boom"])
        continue
    req = r["requests"]
    src = req[0].get("source") if len(req) == 1 else None
    force = num(req[0].get("force")) if len(req) == 1 else None
    ok = len(req) == 1 and src == want_src and force is not None and abs(force - want_force) <= 1e-3
    row("PASS" if ok else "FAIL", "V_SOURCE " + name, "%d request line(s); source %s (want %s), force %s (want %s)%s%s" % (
        len(req), src, want_src, force, want_force,
        "; " + json.dumps({k: req[0].get(k) for k in ("damType", "typeForce", "damage", "damageRatio")}) if req else "",
        ", " + r["err"] if r["err"] else ""))


def planned(name):
    ls = rows[name]["launches"]
    return int(num(ls[0].get("planned")) or 0) if ls else 0


cells = [planned(n) for n in ORDER]
row("PASS" if all(cells[i] > cells[i + 1] for i in range(len(cells) - 1)) else "FAIL", "V_ORDER",
    "planned cells %s for %s (want strictly falling); ends %s" % (cells, ORDER, [rows[n]["end"] for n in ORDER]))
print("%s sc_lookup_sources: %d failing, %d invalid row(s); extensions %s; pictures in %s" % (
    "PASS" if fails == 0 and invalid == 0 else ("FAIL" if fails else "INVALID"), fails, invalid, json.dumps(setup), folder))
print(scene.judge(folder))
