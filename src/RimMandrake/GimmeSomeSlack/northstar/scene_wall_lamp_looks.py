"""Gimme Some Slack, scene `sc_wall_lamp_looks`, bar `wall_lamp_takes_looks`, on the scene library 0.3.0.

Row converted: SC_wall_lamp_draws_each_look, "each of the four wall lamps, one per look, takes its look". A fresh agent wrote the
first version from `scene.py help` and the old claim only (design/specs/2026-11-23-bridge-v2/12_conversion_readings.md); its
guesses were then replaced by the facts below, each read from the mod's source. The old row (scene_rows.py `wall_lamp_looks`)
stays the deciding row until this scene was seen to FAIL on its planted fault and PASS on the real build in one sitting.

What the row reads, for each lamp: the look that it DRAWS (DRAWN_PATH: the path step `drawn` of the hands gives the texture path
of the graphic that Thing.Graphic returns, the mod's patches included), and the style that it stores (CompStyleable.styleDef).
With the master switch off the mod draws the vanilla art and keeps the stored style, so only the drawn look can turn the row
red on that plant. The lamps get their looks from s.stage things style=: jawa/build_batch sets the style after the spawn, as
the build menu's god-mode pick does (Designator_Build.DesignateSingleCell; the mod's pick, ConduitStylePicker.Pick, sets only
that style and a menu memory). No mod probe is called, so a run can count for the bar.

    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\GimmeSomeSlack\\northstar\\scene_wall_lamp_looks.py
    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\GimmeSomeSlack\\northstar\\scene_wall_lamp_looks.py --plant master_switch_off
"""
import scene
from scene import cond as c

GAME, MOD, MAP = "ArchSmall", "GimmeSomeSlack", "fresh:quicktest"
STATION = (60, 60, 30, 12)                    # scene_rows.py SC0 site: a 30 x 12 rectangle of the quicktest map
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
STYLE = {look: "WallLamp_" + look for look in LOOKS}          # Defs/Aerial/RM_ConduitStyles.xml: one ThingStyleDef per look
ART = {look: "RimMandrake/GimmeSomeSlack/Styles/%s/WallLamp" % look for look in LOOKS}   # the same file: each style's texPath
DRAWN_PATH = "drawn.path"                      # what the lamp draws (hands boundary, THE PATH GRAMMAR: the reader `drawn`)
WALL_Z, LAMP_Z = 8, 7                          # the lamps stand in front of the wall, on its south face
LAMP_CELLS = [(3 + 4 * i, LAMP_Z) for i in range(len(LOOKS))]  # scene_rows.py: (x + 3 + 4 i, z + 7), relative to the station
ROT = 0                                        # a wall lamp's rotation names the side its wall is on: north
SETTINGS = "RimMandrake.GimmeSomeSlack.GimmeSomeSlackSettings"  # the master switch: static field `enabled`
LAMPS = ["lamp_" + look.lower() for look in LOOKS]
TICKS = 60

looks = scene.contract(
    claim="each of the four wall lamps, one per look, takes its look", kind="A",
    exposure=[c.state(lamp, "positionInt") == "ok" for lamp in LAMPS],
    success=[c.played(TICKS)]
            + [c.value(lamp, "comp<CompStyleable>.styleDef") == STYLE[look] for lamp, look in zip(LAMPS, LOOKS)]
            + [c.value(lamp, DRAWN_PATH) == ART[look] for lamp, look in zip(LAMPS, LOOKS)],
    forbidden=[c.state(lamp, "positionInt") == "gone" for lamp in LAMPS],
    end=TICKS, limit=TICKS + 60)


with scene.open(GAME, contract=looks, needs={"mods": [MOD], "map": MAP, "calm": "standard"}) as s:
    planted = scene.plant() == "master_switch_off"
    prior = (s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="get", field="enabled") or {}).get("value") if planted else None
    try:
        if planted:
            s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="enabled", value="False")
        things = {"wall": dict(thing="Wall", stuff="Steel", at=[(x, WALL_Z) for x in range(2, 25)]),
                  "cord": dict(thing="PowerConduit", at=[(x, 6) for x in range(2, 25)])}
        things.update({lamp: dict(thing="WallLamp", at=cell, rot=ROT, style=STYLE[look]) for lamp, cell, look in zip(LAMPS, LAMP_CELLS, LOOKS)})
        s.stage(station=STATION, things=things)
        run = s.run(until=looks.end, limit=looks.limit)
        shot = s.shot(rect=STATION, name="wall_lamps_all_looks")
        print(run, run.receipt, shot)
    finally:
        if planted:   # the setting back to what it read before the plant, on every exit path
            s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="enabled", value=str(prior) if prior is not None else "True")
    folder = s.run_dir
print(scene.judge(folder))
