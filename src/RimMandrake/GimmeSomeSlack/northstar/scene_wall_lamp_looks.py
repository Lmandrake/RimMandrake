"""Gimme Some Slack, scene `sc_wall_lamp_looks`, bar `wall_lamp_takes_looks`, on the scene library 0.3.0.

Row converted: SC_wall_lamp_draws_each_look, "each of the four wall lamps, one per look, takes its look". A fresh agent wrote the
first version from `scene.py help` and the old claim only (design/specs/2026-11-23-bridge-v2/12_conversion_readings.md); its
guesses were then replaced by the facts below, each read from the mod's source. The old row (scene_rows.py `wall_lamp_looks`)
stays the deciding row until this scene was seen to FAIL on its planted fault and PASS on the real build in one sitting.

What the row reads: the style that each lamp stores (CompStyleable.styleDef, a public field), which the mod's own pick sets. What
the lamp DRAWS is computed by methods (Graphic.MatAt) and no value path reaches it: the picture goes to the art judge, and a
reader of the drawn texture is a hands ticket. The lamps are given their looks by the build menu's own pick through the mod's
proof probe (AerialProbe, `cplace`), which no generic hand does: so every run of this scene is EXPLORED and counts for no bar
until a `style=` hand exists (the hands ticket of the conversion).

    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\GimmeSomeSlack\\northstar\\scene_wall_lamp_looks.py
    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\GimmeSomeSlack\\northstar\\scene_wall_lamp_looks.py --plant master_switch_off
"""
import scene
from scene import cond as c

GAME, MOD, MAP = "ArchSmall", "GimmeSomeSlack", "fresh:quicktest"
STATION = (60, 60, 30, 12)                    # scene_rows.py SC0 site: a 30 x 12 rectangle of the quicktest map
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
STYLE = {look: "WallLamp_" + look for look in LOOKS}          # Defs/Aerial/RM_ConduitStyles.xml: one ThingStyleDef per look
WALL_Z, LAMP_Z = 8, 7                          # the lamps stand in front of the wall, on its south face
LAMP_CELLS = [(3 + 4 * i, LAMP_Z) for i in range(len(LOOKS))]  # scene_rows.py: (x + 3 + 4 i, z + 7), relative to the station
PROBE = "RimMandrake.GimmeSomeSlack.Aerial.AerialProbe"       # the mod's proof probe: static request, result, serial
SETTINGS = "RimMandrake.GimmeSomeSlack.GimmeSomeSlackSettings"  # the master switch: static field `enabled`
LAMPS = ["lamps[%d]" % i for i in range(len(LOOKS))]
TICKS = 60

looks = scene.contract(
    claim="each of the four wall lamps, one per look, takes its look", kind="A",
    exposure=[c.state(lamp, "positionInt") == "ok" for lamp in LAMPS],
    success=[c.played(TICKS)] + [c.value(lamp, "comp<CompStyleable>.styleDef") == STYLE[look] for lamp, look in zip(LAMPS, LOOKS)],
    forbidden=[c.state(lamp, "positionInt") == "gone" for lamp in LAMPS],
    end=TICKS, limit=TICKS + 60)


def ask_probe(s, cmd):
    """Post one command to the mod's probe and let one tick pass, so that a frame services it. -> its result text."""
    s.raw("jawa/mod_settings_field", typeName=PROBE, action="set", field="request", value=cmd)
    s.run(until=1, limit=10)
    r = s.read("static:" + PROBE, "result")
    if r.state != "ok":
        raise scene.Fault("COULD_NOT_LOOK", detail="the probe's answer to %s: %r" % (cmd, r))
    return r.v


with scene.open(GAME, contract=looks, needs={"mods": [MOD], "map": MAP, "calm": "standard"}) as s:
    x0, z0 = STATION[0], STATION[1]
    s.stage(station=STATION, things={"wall": dict(thing="Wall", stuff="Steel", at=[(x, WALL_Z) for x in range(2, 25)]),
                                     "cord": dict(thing="PowerConduit", at=[(x, 6) for x in range(2, 25)])})
    planted = scene.plant() == "master_switch_off"
    prior = (s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="get", field="enabled") or {}).get("value") if planted else None
    try:
        if planted:
            s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="enabled", value="False")
        for (x, z), look in zip(LAMP_CELLS, LOOKS):
            ask_probe(s, "cplace:WallLamp:%s:%d,%d:god" % (look, x0 + x, z0 + z))
        at = {}
        for v in s.read_many(rect=(x0, z0 + LAMP_Z, STATION[2], 1), path="def.defName"):
            if v.state == "ok" and v.v == "WallLamp":
                at[v.of] = None
        found = s.read_many(rect=(x0, z0 + LAMP_Z, STATION[2], 1), path="positionInt")
        by_cell = {}
        for v in found:
            if v.of in at and v.state == "ok":
                x, *_y, z = (int(n) for n in str(v.v).split(","))
                by_cell[(x - x0, z - z0)] = v.of[6:]
        missing = [cl for cl in LAMP_CELLS if cl not in by_cell]
        if missing:
            raise scene.Fault("STAGING_FAULT", detail="no wall lamp stands at %s after the picks" % missing)
        s.stage(cast={"lamps": dict(take=[by_cell[cl] for cl in LAMP_CELLS])})
        run = s.run(until=looks.end, limit=looks.limit)
        shot = s.shot(rect=("lamps", 3), name="wall_lamps_all_looks")
        print(run, run.receipt, shot)
    finally:
        if planted:   # the setting back to what it read before the plant, on every exit path
            s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="enabled", value=str(prior) if prior is not None else "True")
    folder = s.run_dir
print(scene.judge(folder))
