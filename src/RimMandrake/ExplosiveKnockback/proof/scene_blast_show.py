"""scene_blast_show.py - Explosive Knockback 0.2.0, sc_blast_show: the blast show in the game (scene library 0.3.0).

Bars (design/concepts/ExplosiveKnockback/record.json): blast_show_fire_and_flash, blast_show_screen_shake,
blast_show_air_ripple, blast_show_crater_scar and blast_show_scales_with_damage; the smoke and soot bars join when their
parts are built. The kernel's sizes are decided offline (T_BLAST_SHOW_OFFLINE). This scene reads what only the game can
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
  V_SCAR_KIND   he_soil, ied_soil, anti_soil -> RM_KnockbackBlastCrater_*; he_rough, he_tile, fire_soil ->
                RM_KnockbackBlastScorch_*; he_water and emp_soil -> no scar of ours
  V_NO_VANILLA  no Filth_BlastMark on any pad
  V_SCAR_SIZE   drawn widths on soil rise: he_soil < ied_soil < anti_soil (RM_KnockbackShowPlan: 7, 10, 20)
  V_SHAKE       RM_KnockbackShow.lastShakeTick moves to the blast's tick for each harmful blast in view, and its kick rises
                he_soil < anti_soil
  SHOTS         <pad>_fire right after each blast, <pad>_scar after 300 ticks

    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_blast_show.py
    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_blast_show.py --plant show_off

UNRUN until Stage 6: written 2026-11-24 by RIMMANDRAKE_AUTOBUILD_EXPLOSIVEKNOCKBACK_FOURTEEN_BARS_LEFT and never run live.
The plant `show_off` turns the four built show switches off: V_SCAR_KIND, V_NO_VANILLA and V_SHAKE must then FAIL
(vanilla's mark returns, no kick of ours), which shows that the checks can see. Open points for the first run: whether
jawa/mod_settings_field get stamps the run EXPLORED (if so, V_SHAKE supports and the shots decide the shake), and whether
the off-screen capture draws flecks (if not, the _fire shots are taken on screen with rimworld/jump_camera_to_cell).
"""
import scene
from scene import cond as c

GAME = "ArchSmall"
SETTINGS = "RimMandrake.ExplosiveKnockback.RimMandrakeExplosiveKnockbackSettings"
SHOW = "RimMandrake.ExplosiveKnockback.RM_KnockbackShow"
SWITCHES = ("showFireAndFlash", "showScreenShake", "showAirRipple", "showCraterScars")
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
ORDER = ["he_soil", "he_rough", "he_tile", "he_water", "ied_soil", "fire_soil", "emp_soil", "anti_soil"]
WANT = {"he_soil": "Crater", "ied_soil": "Crater", "anti_soil": "Crater", "he_rough": "Scorch", "he_tile": "Scorch",
        "fire_soil": "Scorch", "he_water": None, "emp_soil": None}
HARMFUL = [p for p in ORDER if p != "emp_soil"]
SETTLE = 300            # ticks after each blast: every fleck of the show is gone in under 2 s (120 ticks)
HALF = 4                # a pad's reading rect is its centre +-4 cells; the antigrain's reaches +-12 (its 20-cell scar)

show = scene.contract(
    claim="a harmful blast shows our own fire, flash, shake, ripple and scar, sized by its power, never vanilla's mark",
    kind="A",
    exposure=c.state("he_soil_x", "positionInt") == "gone",
    success=[c.played(len(ORDER) * SETTLE)],
    forbidden=[],
    end=len(ORDER) * SETTLE, limit=len(ORDER) * SETTLE + 900)


def rect(pad):
    x, z = PADS[pad][2]
    h = 12 if pad == "anti_soil" else HALF
    return (STATION[0] + x - h, STATION[1] + z - h, 2 * h + 1, 2 * h + 1)


def scars_on(s, pad):
    """-> ([(kind, width)] of our scar filth on a pad, the count of vanilla blast marks there)."""
    names = [str(v.v) for v in s.read_many(rect=rect(pad), path="def.defName") if v.state == "ok"]
    ours = []
    for n in names:
        for kind in ("Crater", "Scorch"):
            if n.startswith("RM_KnockbackBlast%s_" % kind):
                ours.append((kind, int(n.rsplit("_", 1)[1])))
    return ours, names.count("Filth_BlastMark")


def static(s, field):
    r = s.raw("jawa/mod_settings_field", typeName=SHOW, action="get", field=field)
    try:
        return float((r or {}).get("value"))
    except (TypeError, ValueError, AttributeError):
        return None


with scene.open(GAME, contract=show, needs={"mods": ["ExplosiveKnockback"], "map": "fresh:quicktest", "calm": "standard"}) as s:
    s.stage(station=STATION,
            terrain={p: dict(rect=(x - HALF, z - HALF, 2 * HALF + 1, 2 * HALF + 1), terrain=t) for p, (_d, t, (x, z)) in PADS.items()},
            things={p + "_x": dict(thing=d, at=(x, z)) for p, (d, _t, (x, z)) in PADS.items()})
    if scene.plant() == "show_off":
        for f in SWITCHES:
            s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=f, value="False")
    rows = {}
    for pad in ORDER:
        t0 = static(s, "lastShakeTick")
        hp = s.read(pad + "_x", "hitPointsInt")
        s.act.damage(pad + "_x", (hp.v if hp.state == "ok" else 100) + 60, kind="Crush", name=pad)
        s.shot(rect(pad), name=pad + "_fire")
        t1, kick = static(s, "lastShakeTick"), static(s, "lastShakeKick")
        s.run(until=SETTLE, limit=SETTLE + 120)
        s.shot(rect(pad), name=pad + "_scar")
        ours, vanilla = scars_on(s, pad)
        rows[pad] = dict(scars=ours, vanilla=vanilla, shook=(t0 is not None and t1 is not None and t1 > t0), kick=kick)
    folder = s.run_dir

fails = 0


def row(ok, ident, text):
    global fails
    fails += not ok
    print("%s %s: %s" % ("PASS" if ok else "FAIL", ident, text))


for pad in ORDER:
    r, want = rows[pad], WANT[pad]
    kinds = sorted({k for k, _w in r["scars"]})
    row(kinds == ([want] if want else []), "V_SCAR_KIND " + pad, "scars %s, want %s" % (r["scars"], want or "none"))
    row(r["vanilla"] == 0, "V_NO_VANILLA " + pad, "%d Filth_BlastMark" % r["vanilla"])
    if pad in HARMFUL:
        row(r["shook"], "V_SHAKE " + pad, "the show's kick tick moved: %s (kick %s)" % (r["shook"], r["kick"]))
ws = [max((w for _k, w in rows[p]["scars"]), default=0) for p in ("he_soil", "ied_soil", "anti_soil")]
row(ws[0] < ws[1] < ws[2], "V_SCAR_SIZE", "drawn widths he_soil, ied_soil, anti_soil = %s, strictly rising" % ws)
ka, kb = rows["he_soil"]["kick"], rows["anti_soil"]["kick"]
row(ka is not None and kb is not None and kb > ka, "V_SHAKE_SIZE", "kick he_soil %s < anti_soil %s" % (ka, kb))
print("%s sc_blast_show: %d failing row(s); the pictures in %s go to the art judge" % ("PASS" if fails == 0 else "FAIL", fails, folder))
print(scene.judge(folder))
