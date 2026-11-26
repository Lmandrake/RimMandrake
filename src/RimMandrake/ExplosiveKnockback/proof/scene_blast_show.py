"""scene_blast_show.py - Explosive Knockback 0.2.0, sc_blast_show: the blast show in the game (scene library 0.3.0).

Bars (design/concepts/ExplosiveKnockback/record.json): blast_show_fire_and_flash, blast_show_screen_shake,
blast_show_air_ripple, blast_show_crater_scar, blast_show_smoke, blast_show_soot_on_things, blast_show_soot_on_pawns and
blast_show_scales_with_damage. The kernel's sizes are decided offline (T_BLAST_SHOW_OFFLINE). This scene reads what only the game can
show: a real blast lays OUR scar and never vanilla's mark, of the kind its ground calls for and of the width its power
calls for; the show kicked the camera; and a picture of each blast right after it goes off (fire, flash, sparks, thrown
bits, ripple) and once it has settled (the scar), for the art judge (design/RimMandrake/art_judge_brief.md), whose keep
is part of this verdict.

Kind A. A fresh quicktest map on ArchSmall; one clean station with seven pads, each a vanilla explosive set off by damage
(as scene_storeroom_pit.py sets off its shells: the path every vanilla explosive takes, CompExplosive -> GenExplosion):
  he_soil, he_rough, he_tile, he_water   Shell_HighExplosive (Bomb, radius 2.9) on Soil, Granite_Rough, TileGranite, WaterShallow
  ied_soil                               TrapIED_HighExplosive (Bomb, radius 3.9) on Soil
  fire_soil                              Shell_Incendiary (Flame, radius 2.9) on Soil: fire, no thrown dirt, a scorch, no crater
  emp_soil                               Shell_EMP (EMP harms nobody): the vanilla look, no scar of ours
  anti_soil                              Shell_AntigrainWarhead (BombSuper, radius 14.9) on Soil, set off last, far from the rest
Radii and types are read from Core's Items_Resource_Shell.xml and Buildings_Security.xml (2026-11-24). No raid, no hostile pawn.

The checks (each prints PASS or FAIL with what it read):
  V_SCAR_KIND   he_soil, ied_soil, anti_soil -> RM_KnockbackBlastCrater_<n>Wide; he_rough, he_tile, fire_soil ->
                RM_KnockbackBlastScorch_<n>Wide; he_water and emp_soil -> no scar of ours
  V_NO_VANILLA  no Filth_BlastMark on any pad
  V_SCAR_SIZE   drawn widths on soil rise: he_soil < ied_soil < anti_soil (RM_KnockbackShowPlan: 7, 10, 20)
  V_SHAKE       RM_KnockbackShow.lastShakeTick moves to the blast's tick for each harmful blast in view, and its kick rises
                he_soil < anti_soil
  V_SOOT_THING  the granite wall two cells from he_tile's centre wears the charred paint RM_FE_Charred after its blast
  V_SOOT_PAWN   the muffalo three cells from ied_soil's centre carries hediff RM_KnockbackSoot after its blast (it is
                thrown, as any pawn in a blast is; the muffalo's size keeps it alive at that distance [guess ~80%])
  SHOTS         <pad>_fire right after each blast (fire, flash, sparks, bits, ripple, the smoke column rising), <pad>_scar
                after 300 ticks (the scar; the smoke has thinned)

    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_blast_show.py
    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_blast_show.py --plant show_off

UNRUN until Stage 6: written 2026-11-24 by RIMMANDRAKE_AUTOBUILD_EXPLOSIVEKNOCKBACK_FOURTEEN_BARS_LEFT and never run live.
The plant `show_off` turns the seven show switches off: V_SCAR_KIND, V_NO_VANILLA, V_SHAKE, V_SOOT_THING and V_SOOT_PAWN
must then FAIL (vanilla's mark returns, no kick of ours, no soot), which shows that the checks can see. Smoke and soot
checks were added 2026-11-24 by RIMMANDRAKE_GREEN_EXPLOSIVEKNOCKBACK_T_BLAST_SHOW_RED_DECIDER, also unrun; open point: the
read paths PaintColorDef.defName (a Building property) and health.hediffSet.hediffs[i].def.defName. Open points for the first run: whether
jawa/mod_settings_field get stamps the run EXPLORED (if so, V_SHAKE supports and the shots decide the shake), and whether
the off-screen capture draws flecks (if not, the _fire shots are taken on screen with rimworld/jump_camera_to_cell).
"""
import json
import re

import scene
from scene import cond as c

GAME = "ArchSmall"
SETTINGS = "RimMandrake.ExplosiveKnockback.RimMandrakeExplosiveKnockbackSettings"
SHOW = "RimMandrake.ExplosiveKnockback.RM_KnockbackShow"
SWITCHES = ("showFireAndFlash", "showScreenShake", "showAirRipple", "showCraterScars", "showSmoke", "showSootOnThings",
            "showSootOnPawns")
STATION = (20, 20, 100, 40)
# pad -> (explosive, terrain, centre relative to the station's corner); a pad is 9 x 9 cells around its centre
PADS = {
    "he_soil": ("Shell_HighExplosive", "Soil", (6, 6)),
    "he_rough": ("Shell_HighExplosive", "Granite_Rough", (18, 6)),
    "he_tile": ("Shell_HighExplosive", "TileGranite", (30, 6)),
    "he_water": ("Shell_HighExplosive", "WaterShallow", (42, 6)),
    "ied_soil": ("TrapIED_HighExplosive", "Soil", (54, 6)),
    "fire_soil": ("Shell_Incendiary", "Soil", (6, 24)),
    "emp_soil": ("Shell_EMP", "Soil", (24, 24)),
    "anti_soil": ("Shell_AntigrainWarhead", "Soil", (80, 20)),      # last: its 14.9-cell blast reaches no other pad
}
# ied_soil goes first: its muffalo is staged at the start and, after four earlier pads' settles (1,200+ ticks), had walked
# out of the soot reach in the first live run (visit 1 of 0.2.0: V_SOOT_PAWN read no soot, no muffalo in ied_soil's frame)
ORDER = ["ied_soil", "he_soil", "he_rough", "he_tile", "he_water", "fire_soil", "emp_soil", "anti_soil"]
WANT = {"he_soil": "Crater", "ied_soil": "Crater", "anti_soil": "Crater", "he_rough": "Scorch", "he_tile": "Scorch",
        "fire_soil": "Scorch", "he_water": None, "emp_soil": None}
HARMFUL = [p for p in ORDER if p != "emp_soil"]
SETTLE = 300            # ticks after each blast: every fleck of the show is gone in under 2 s (120 ticks)
# the soot watchers: a granite wall on he_tile (a built floor pad) and a muffalo on ied_soil, inside each blast's soot
# reach (0.8 x the effective radius: about 2.3 cells for the 2.9-cell shell, 3.1 for the 3.9-cell IED)
WALL_AT = (32, 6)
BEAST_AT = (57, 6)
JOURNAL = "RimMandrake.ExplosiveKnockback.RM_KnockbackJournal"
# The Rot's living ground digests every outdoor filth (EnvironmentalHazards RM_MapComponent_AcceleratedRot.ThinOutdoorFilth:
# a 15% chance of one thinning each 250 ticks), our scars included. A fresh quicktest map can be that biome: there a scar
# laid at the blast was gone at 300 ticks in 8 of 24 IED blasts, each removal named by the journal's scar_gone record
# (RIMMANDRAKE_FIND_KNOCKBACK_IED_SCAR_MISSING_ONE_RUN_IN_THREE). The scene holds that other mod's mechanic still for
# its run, so each row judges this mod alone; the setting is put back on every exit.
ROT = ("RimMandrake.EnvironmentalHazards.RM_EnvironmentalHazardsSettings", "acceleratedRotEnabled")
SCAR_NAME = re.compile(r"RM_KnockbackBlast(Crater|Scorch)_(\d+)Wide$")   # RM_KnockbackShow.ScarDefName
HALF = 4                # a pad's reading rect is its centre +-4 cells; the antigrain's reaches +-12 (its 20-cell scar)

show = scene.contract(
    claim="a harmful blast shows our own fire, flash, shake, ripple and scar, sized by its power, never vanilla's mark",
    kind="A",
    exposure=c.state("he_soil_x", "positionInt") == "gone",
    success=[c.played(SETTLE)],                   # c.played counts the judged run only: the last pad's settle
    forbidden=[],
    end=SETTLE, limit=len(ORDER) * SETTLE + 900)


def rect(pad):
    x, z = PADS[pad][2]
    h = 12 if pad == "anti_soil" else HALF
    return (STATION[0] + x - h, STATION[1] + z - h, 2 * h + 1, 2 * h + 1)


def scars_on(s, pad):
    """-> ([(kind, width)] of our scar filth on a pad, the count of vanilla blast marks there)."""
    names = [str(v.v) for v in s.read_many(rect=rect(pad), path="def.defName") if v.state == "ok"]
    ours = []
    for n in names:
        m = SCAR_NAME.match(n)
        if m:
            ours.append((m.group(1), int(m.group(2))))
    return ours, names.count("Filth_BlastMark")


def journal_lines(s):
    v = s.read("static:" + JOURNAL, "lines")
    return [str(x) for x in v.v] if v.state == "ok" and isinstance(v.v, (list, tuple)) else None


def scar_log(before, after):
    """-> the journal's scar and scar_gone records written between two reads (LayScar: laid, or why the cell refused;
    RM_Patch_Filth_ScarGone: who removed it), or a could-not-look line."""
    if before is None or after is None:
        return ["journal unread"]
    new = after[len(before):] if after[:len(before)] == before else [x for x in after if x not in set(before)]
    out = []
    for line in new:
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("type") in ("scar", "scar_gone"):
            out.append({k: r[k] for k in ("type", "at", "def", "laid", "why", "cell", "mode", "by") if k in r})
    return out


def static(s, field):
    r = s.raw("jawa/mod_settings_field", typeName=SHOW, action="get", field=field)
    try:
        return float((r or {}).get("value"))
    except (TypeError, ValueError, AttributeError):
        return None


def blasts(s, rows):
    """Set off each pad in turn, and read its scars, marks and shake into rows[pad]."""
    for pad in ORDER:
        # the show's kick falls with the blast's distance from the centre of the view (RM_KnockbackShowPlan.ShakeMag): the
        # contract reads "each harmful blast in view", so the view is put on the pad first (visit 1 of 0.2.0: with the
        # view elsewhere only the antigrain's kick was above the one-pixel floor)
        cx, cz = PADS[pad][2]
        s.raw("rimworld/jump_camera_to_cell", x=cx, z=cz)
        t0 = static(s, "lastShakeTick")
        j0 = journal_lines(s)
        hp = s.read(pad + "_x", "hitPointsInt")
        s.act.damage(pad + "_x", (hp.v if hp.state == "ok" else 100) + 60, kind="Crush", name=pad)
        s.shot(rect(pad), name=pad + "_fire")
        t1, kick = static(s, "lastShakeTick"), static(s, "lastShakeKick")
        # the kick tick is a static: it outlives a map, so the first pad's t0 can be a later tick of the last map (visit 1 of
        # 0.2.0: ied_soil first read "not moved"). A shake of this blast writes the tick now, so a change is the reading.
        shook = t0 is not None and t1 is not None and t1 >= 0 and t1 != t0
        if not shook:
            kick = None             # a kick read with no shake of this blast is an earlier blast's: never compare it
        s.run(until=SETTLE, limit=SETTLE + 120)
        s.shot(rect(pad), name=pad + "_scar")
        ours, vanilla = scars_on(s, pad)
        rows[pad] = dict(scars=ours, vanilla=vanilla, shook=shook, kick=kick, log=scar_log(j0, journal_lines(s)))
        if pad == "he_tile":
            paint = s.read("soot_wall", "PaintColorDef.defName")
            rows[pad]["paint"] = str(paint.v) if paint.state == "ok" else "unread (%s)" % paint.state
        if pad == "ied_soil":
            rows[pad]["sooted"] = sooted(s, "soot_beast")


def sooted(s, alias):
    """-> True/False: the pawn carries RM_KnockbackSoot; None when its hediffs cannot be read."""
    n = s.read(alias, "health.hediffSet.hediffs._size")
    if n.state != "ok":
        return None
    vals = s.read_many(reads=[(alias, "health.hediffSet.hediffs[%d].def.defName" % i) for i in range(int(n.v))]) if int(n.v) else []
    return any(v.state == "ok" and str(v.v) == "RM_KnockbackSoot" for v in vals)


with scene.open(GAME, contract=show, needs={"mods": ["ExplosiveKnockback"], "map": "fresh:quicktest", "calm": "standard"}) as s:
    s.stage(station=STATION,
            terrain={p: dict(rect=(x - HALF, z - HALF, 2 * HALF + 1, 2 * HALF + 1), terrain=t) for p, (_d, t, (x, z)) in PADS.items()},
            things=dict({p + "_x": dict(thing=d, at=(x, z)) for p, (d, _t, (x, z)) in PADS.items()},
                        soot_wall=dict(thing="Wall", stuff="BlocksGranite", at=WALL_AT)),
            cast={"soot_beast": dict(kind="Muffalo", at=BEAST_AT)})
    planted = scene.plant() == "show_off"
    rows = {}
    prior = {f: (s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=f) or {}).get("value") for f in SWITCHES} if planted else {}
    rot = s.raw("jawa/mod_settings_field", typeName=ROT[0], action="get", field=ROT[1]) or {}
    rot_prior = rot.get("value") if rot.get("success") is True else None
    print("INFO rot hold: %s" % ("The Rot's filth digestion was %s, held off for the run" % rot_prior if rot_prior is not None
                                 else "not held, its setting could not be read (%s)" % rot.get("message")))
    try:
        if rot_prior is not None:
            r = s.raw("jawa/mod_settings_field", typeName=ROT[0], action="set", field=ROT[1], value="False", driver=s.id) or {}
            if r.get("success") is not True:
                raise RuntimeError("SETTING_REFUSED: %s=False was not written (%s)" % (ROT[1], r.get("message")))
        if planted:
            for f in SWITCHES:
                r = s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=f, value="False", driver=s.id) or {}
                if r.get("success") is not True:   # inside a session a set names its driver; a refused plant plants nothing
                    raise RuntimeError("SETTING_REFUSED: %s=False was not written (%s)" % (f, r.get("message")))
        blasts(s, rows)
    finally:
        for f, v in prior.items():   # each switch back to what it read before the plant, on every exit path
            s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=f, value=str(v) if v is not None else "True", driver=s.id)
        if rot_prior is not None:
            s.raw("jawa/mod_settings_field", typeName=ROT[0], action="set", field=ROT[1], value=str(rot_prior), driver=s.id)
    folder = s.run_dir

fails = 0


def row(ok, ident, text):
    global fails
    fails += not ok
    print("%s %s: %s" % ("PASS" if ok else "FAIL", ident, text))


for pad in ORDER:
    r, want = rows[pad], WANT[pad]
    kinds = sorted({k for k, _w in r["scars"]})
    row(kinds == ([want] if want else []), "V_SCAR_KIND " + pad, "scars %s, want %s; journal %s" % (r["scars"], want or "none", r.get("log")))
    row(r["vanilla"] == 0, "V_NO_VANILLA " + pad, "%d Filth_BlastMark" % r["vanilla"])
    if pad in HARMFUL:
        row(r["shook"], "V_SHAKE " + pad, "the show's kick tick moved: %s (kick %s)" % (r["shook"], r["kick"]))
ws = [max((w for _k, w in rows[p]["scars"]), default=0) for p in ("he_soil", "ied_soil", "anti_soil")]
row(ws[0] < ws[1] < ws[2], "V_SCAR_SIZE", "drawn widths he_soil, ied_soil, anti_soil = %s, strictly rising" % ws)
ka, kb = rows["he_soil"]["kick"], rows["anti_soil"]["kick"]
row(ka is not None and kb is not None and kb > ka, "V_SHAKE_SIZE", "kick he_soil %s < anti_soil %s" % (ka, kb))
paint = rows["he_tile"].get("paint")
row(paint == "RM_FE_Charred", "V_SOOT_THING", "the wall by he_tile wears %s, want RM_FE_Charred" % paint)
soot = rows["ied_soil"].get("sooted")
row(soot is True, "V_SOOT_PAWN", "the muffalo by ied_soil carries RM_KnockbackSoot: %s" % soot)
print("%s sc_blast_show: %d failing row(s); the pictures in %s go to the art judge" % ("PASS" if fails == 0 else "FAIL", fails, folder))
print(scene.judge(folder))
