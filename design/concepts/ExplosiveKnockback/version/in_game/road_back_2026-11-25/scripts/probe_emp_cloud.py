"""probe_emp_cloud.py - explain step for RIMMANDRAKE_EXPLAIN_KNOCKBACK_PALE_CLOUD_OVER_EMP_PAD (EXPLORED).

Seen: in sc_blast_show (visit 1, runs 1 and 3) a large pale cloud covers the emp_soil pad 300 ticks after its Shell_EMP.
Candidates: (a) our show draws smoke on an EMP blast, (b) smoke from another pad drifts in (fire_soil's incendiary sits 18
cells west and goes off just before it), (c) a vanilla EMP effect.
Here an EMP shell goes off alone on soil, on a fresh map with no other blast: pad A with every show switch as it is (all on),
then pad B, 40 cells away, with every show switch and the knockback master switch (enabled) off. Pictures at 0, 100 and 300 ticks of each, and the defs of every thing
on the pad at 300 (filth, gas-like things, fire).
What the answer changes: a cloud on A and not B is ours (a, a mod fault); no cloud on either is (b), a staging fault of the
scene; a cloud on both is vanilla's (c).

    python.exe design\\concepts\\ExplosiveKnockback\\version\\in_game\\road_back_2026-11-25\\scripts\\probe_emp_cloud.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import scene  # noqa: E402
from scene import cond as c  # noqa: E402

GAME = "ArchSmall"
SETTINGS = "RimMandrake.ExplosiveKnockback.RimMandrakeExplosiveKnockbackSettings"
SWITCHES = ["enabled", "showFireAndFlash", "showSmoke", "showSootOnThings", "showSootOnPawns", "showScreenShake", "showAirRipple", "showCraterScars"]
STATION = (20, 20, 70, 20)
PADS = {"emp_on": (10, 10), "emp_off": (50, 10)}
HALF = 6
probe = scene.contract(claim="an EMP shell alone on soil: is there a cloud 300 ticks later, with the show on and off", kind="C",
                       exposure=c.state("emp_on_x", "positionInt") == "gone", success=[c.played(300)], forbidden=[], end=300, limit=900)


def rect(pad):
    x, z = PADS[pad]
    return (STATION[0] + x - HALF, STATION[1] + z - HALF, 2 * HALF + 1, 2 * HALF + 1)


def snow(s, pad, when):
    """Snow depth on five cells of the pad (centre and four corners), the weather and the outdoor temperature."""
    x, z = PADS[pad]
    size = s.read("map", "info.sizeInt")
    w = int(str(size.v).split(",")[0]) if size.state == "ok" else None
    cells = [(x, z), (x - 4, z - 4), (x + 4, z - 4), (x - 4, z + 4), (x + 4, z + 4)]
    reads = [("map", "snowGrid.depthGrid[%d]" % ((STATION[1] + cz) * w + STATION[0] + cx)) for cx, cz in cells] if w else []
    reads += [("map", "weatherManager.curWeather.defName"), ("map", "mapTemperature.outdoorTemp") if False else ("map", "weatherManager.lastWeather.defName")]
    vals = s.read_many(reads=reads)
    print("%s %s: snow %s; weather %s" % (pad, when, [(v.v if v.state == "ok" else "%s %s" % (v.state, v.detail)) for v in vals[:-2]],
                                         [(v.v if v.state == "ok" else v.state) for v in vals[-2:]]))


with scene.open(GAME, contract=probe, needs={"mods": ["ExplosiveKnockback"], "map": "fresh:quicktest", "calm": "standard"}) as s:
    s.stage(station=STATION,
            terrain={p: dict(rect=(x - HALF, z - HALF, 2 * HALF + 1, 2 * HALF + 1), terrain="Soil") for p, (x, z) in PADS.items()},
            things={p + "_x": dict(thing="Shell_EMP", at=xz) for p, xz in PADS.items()})
    prior = {f: (s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=f) or {}).get("value") for f in SWITCHES}
    print("show switches before:", prior)
    try:
        for pad in ("emp_on", "emp_off"):
            if pad == "emp_off":
                for f in SWITCHES:
                    r = s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=f, value="False", driver=s.id) or {}
                    if r.get("success") is not True:
                        raise RuntimeError("SETTING_REFUSED %s: %s" % (f, r))
            x, z = PADS[pad]
            s.raw("rimworld/jump_camera_to_cell", x=STATION[0] + x, z=STATION[1] + z)
            hp = s.read(pad + "_x", "hitPointsInt")
            s.act.damage(pad + "_x", (hp.v if hp.state == "ok" else 100) + 60, kind="Crush", name=pad)
            s.shot(rect(pad), name=pad + "_t0")
            snow(s, pad, "t0")
            s.run(until=100, limit=300)
            s.shot(rect(pad), name=pad + "_t100")
            snow(s, pad, "t100")
            s.run(until=200, limit=400)
            s.shot(rect(pad), name=pad + "_t300")
            snow(s, pad, "t300")
            defs = sorted(set(str(v.v) for v in s.read_many(rect=rect(pad), path="def.defName") if v.state == "ok"))
            x0, z0, w, h = rect(pad)
            for gas in ("BlindSmoke", "ToxGas", "RotStink", "DeadlifeDust"):    # which gas the cloud is: a clear reports the cells it changed
                g = s.raw("jawa/set_gas", action="clear", rect="%d,%d,%d,%d" % (x0, z0, w, h), gasType=gas) or {}
                print("%s: clear %s -> %s" % (pad, gas, {k: g.get(k) for k in ("success", "cellsChanged", "error", "message") if k in g}))
            s.run(until=5, limit=60)
            s.shot(rect(pad), name=pad + "_cleared")
            print("%s: defs on the pad at 300 ticks: %s" % (pad, defs))
    finally:
        for f, v in prior.items():
            s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=f, value=str(v) if v is not None else "True", driver=s.id)
    print("pictures in", s.run_dir)
