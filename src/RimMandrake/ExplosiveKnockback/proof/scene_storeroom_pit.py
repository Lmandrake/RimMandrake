"""scene_storeroom_pit.py - Explosive Knockback, the storeroom bomb pit (arm A of storeroom_pit_proof.py), on the scene library 0.3.0.

The owner's flagship sentence (2026-11-12): "Just put a bomb into a storeroom with people in it beside a pit. Shows some items
falling into the pit and some people as well." The old proof stages and judges through RM_KnockbackProof, a C# helper compiled
into a PROOF build. Here the verdict is made outside the game, from the kept trace; the mod's own build is used.

The fixture is the saved sitting EK_SITTING_STATION1_STOREROOM_PIT_20261112: a stack of shells at the room's middle, five drafted
colonists, goods, and a FlowWorks superdeep pit on the open east side. The bomb is set off by damage, as the old proof does.
The old row stays the deciding row until this scene was seen to FAIL on its planted fault and PASS on the real build in one sitting.

    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_storeroom_pit.py
    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_storeroom_pit.py --plant knockback_off
"""
import scene
from scene import cond as c

GAME, SAVE = "ArchBig", "EK_SITTING_STATION1_STOREROOM_PIT_20261112"
SITE, PIT = (114, 117, 22, 15), (128, 122, 4, 5)    # storeroom_pit_proof.py defaults: the census rect, the pit cells
RADIUS, PEOPLE, GOODS, TICKS = 6.0, 5, 6, 300       # the blast radius; 5 colonists (the old START row); the 6 goods stacks nearest
                                                    # the bomb (the old row reads 12: one condition holds at most 64 nodes)
SETTINGS = "RimMandrake.ExplosiveKnockback.RimMandrakeExplosiveKnockbackSettings"
WHO = ["people[%d]" % i for i in range(PEOPLE)]
WHAT = ["goods[%d]" % i for i in range(GOODS)]


def in_pit(of):
    x, z, w, h = PIT
    return c.value(of, "positionInt.x").in_(x, x + w - 1) & c.value(of, "positionInt.z").in_(z, z + h - 1)


pit = scene.contract(
    claim="a bomb in a storeroom beside a pit throws goods and people into the pit, and kills nobody", kind="A",
    exposure=c.state("bomb", "positionInt") == "gone",
    success=[c.played(TICKS), c.any_(*[in_pit(p) for p in WHO]), c.any_(*[in_pit(g) for g in WHAT])],
    forbidden=[c.state(p, "positionInt") == "gone" for p in WHO] + [c.state(g, "positionInt") == "gone" for g in WHAT],
    end=TICKS, limit=TICKS + 100)


def far(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def cell(v):
    x, *_y, z = (int(n) for n in str(v).split(","))
    return x, z


with scene.open(GAME, contract=pit, needs={"mods": ["ExplosiveKnockback", "FlowWorks"], "map": SAVE, "calm": "standard"}) as s:
    kinds = {v.of: v.v for v in s.read_many(rect=SITE, path="def.category") if v.state == "ok"}
    defs = {v.of: v.v for v in s.read_many(rect=SITE, path="def.defName") if v.state == "ok"}
    cells = {v.of: cell(v.v) for v in s.read_many(rect=SITE, path="positionInt") if v.state == "ok"}
    shells = sorted(t for t, d in defs.items() if str(d).startswith("Shell_"))
    if not shells:
        raise scene.Fault("STAGING_FAULT", detail="no Shell_ thing in %s of %s" % (SITE, SAVE))
    bx, bz = cells[shells[0]]
    near = sorted((t for t in cells if t != shells[0] and far(cells[t], (bx, bz)) <= RADIUS),
                  key=lambda t: far(cells[t], (bx, bz)))
    people = [t for t in near if kinds.get(t) == "Pawn" and defs.get(t) == "Human"][:PEOPLE]
    goods = [t for t in near if kinds.get(t) == "Item" and t not in shells][:GOODS]
    if len(people) < PEOPLE or len(goods) < GOODS:
        raise scene.Fault("STAGING_FAULT", detail="the fixture holds %d colonists and %d goods stacks within %s of the bomb" % (
            len(people), len(goods), RADIUS))
    s.stage(cast={"bomb": dict(take=shells[0][6:]), "people": dict(take=[p[6:] for p in people]),
                  "goods": dict(take=[g[6:] for g in goods])})
    off = scene.plant() == "knockback_off"          # arm C of the old proof: the master switch off, so nothing is thrown
    prior = (s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="get", field="enabled") or {}).get("value") if off else None
    try:
        if off:
            s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="enabled", value="False")
        hp = s.read("bomb", "hitPointsInt")
        s.act.damage("bomb", (hp.v if hp.state == "ok" else 60) + 40, kind="Crush", name="bomb")
        run = s.run(until=pit.end, limit=pit.limit)
    finally:
        if off:   # the master switch back to what it read before the plant, on every exit path
            s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="enabled", value=str(prior) if prior is not None else "True")
    print(run, run.receipt)
    folder = s.run_dir
print(scene.judge(folder))
