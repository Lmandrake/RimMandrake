"""scene_moat_rim_wardens.py - FlowWorks sc_moat_raid, row MOAT_rim_wardens_not_stabbed, written again on the scene library 0.3.0.

The old row is concept_scenes.py `_moat_raid` / `_moat_rows`. It stays the deciding row of the test table until this scene was
seen to FAIL on its planted fault and PASS on the real build in one sitting (RIMMANDRAKE_CONVERT_THREE_SCENES_SHOW_IF_TEN_NAMES_HELP).

The opportunity is the state that the test pilot sitting of 2026-11-23 saved on ArchBig: two raiders held in the drained moat of the
sc_moat_raid geometry (save TP_MOAT_HELD_A). Two wardens are staged on the lip of the plot, one beside each raider, and each is
given the capture job. Melee from the pit to the rim is denied by the mod (setting pitLipMeleeDeniedEnabled, shipped on).
A warden that a raider swings at gets mindState.lastMeleeThreatHarmTick, which the game sets on every melee swing at a pawn, hit
or miss (Verb_MeleeAttack.TryCastShot). A freshly staged warden holds -99999.

    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\FlowWorks\\northstar\\scene_moat_rim_wardens.py
    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\FlowWorks\\northstar\\scene_moat_rim_wardens.py --plant melee_rule_off
"""
import scene
from scene import cond as c

GAME, SAVE = "ArchBig", "TP_MOAT_HELD_A"            # the fixture is in ArchBig's Saves folder
X0, Z0, W, N = 60, 60, 4, 16                        # concept_scenes._moat_geom: O, MOAT_W, MOAT_PLOT + 2 * MOAT_W
PX, PZ, PN = X0 + W, Z0 + W, N - 2 * W              # the undug plot inside the ring
RAIDERS = ["Human21181", "Human21233"]              # held in the drained moat in that save
RAIDER, WARDEN = ["raiders[0]", "raiders[1]"], ["wardens[0]", "wardens[1]"]
CAPTURE, TICKS = "RM_CaptureDown", 900              # MOAT_CAPTURE_TICKS of the old scene
SETTINGS = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"


def inside(of, x0, z0, n):
    return c.value(of, "positionInt.x").in_(x0, x0 + n - 1) & c.value(of, "positionInt.z").in_(z0, z0 + n - 1)


def in_ring(of):
    return inside(of, X0, Z0, N) & ~inside(of, PX, PZ, PN)


moat = scene.contract(
    claim="raiders held in the drained moat do not stab the rim wardens", kind="A",
    exposure=c.any_(*[in_ring(r) for r in RAIDER]),
    success=[c.played(TICKS)] + [c.value(w, "health.healthState") == "Mobile" for w in WARDEN],
    forbidden=[c.value(w, "mindState.lastMeleeThreatHarmTick") >= 0 for w in WARDEN],
    end=TICKS, limit=TICKS + 100)


def lip(cell):
    """The plot square nearest a raider's cell: a warden there stands on the rim, beside the raider."""
    plot = [(PX + i, PZ + j) for i in range(PN) for j in range(PN)]
    return min(plot, key=lambda p: (p[0] - cell[0]) ** 2 + (p[1] - cell[1]) ** 2)


def cell_of(v):
    if v.state != "ok":
        raise scene.Fault("STAGING_FAULT", detail="the fixture does not hold the raider: %r" % (v,))
    x, *_y, z = (int(n) for n in str(v.v).split(","))
    return x, z


with scene.open(GAME, contract=moat, needs={"mods": ["FlowWorks"], "map": SAVE, "calm": "standard"}) as s:
    s.stage(cast={"raiders": dict(take=RAIDERS)})
    at = [cell_of(v) for v in s.read_many(reads=[(r, "positionInt") for r in RAIDER])]
    s.stage(cast={"wardens": dict(kind="Colonist", at=[lip(a) for a in at])})
    planted = scene.plant() == "melee_rule_off"
    prior = (s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="get", field="pitLipMeleeDeniedEnabled") or {}).get("value") if planted else None
    try:
        if planted:
            s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="pitLipMeleeDeniedEnabled", value="False")
        with s.act.batch() as b:                        # both orders on one tick
            for w, r, a in zip(WARDEN, RAIDER, at):
                b.job(w, CAPTURE, target=r, cell=lip(a), name="capture")
        run = s.run(until=moat.end, limit=moat.limit)
        print(run, run.receipt)
    finally:
        if planted:   # the setting back to what it read before the plant, on every exit path
            s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="pitLipMeleeDeniedEnabled", value=str(prior) if prior is not None else "True")
    folder = s.run_dir
print(scene.judge(folder))
