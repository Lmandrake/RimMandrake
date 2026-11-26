"""scene_walk_under_cover.py - FlowWorks: a colonist ordered along a pit floor walks under each pit cover kind, the cover fades
over her, and she comes out the far end. Kind A.

RIMMANDRAKE_REBUILD_FLOWWORKS_WALK_MAP_OLD_CODED_AND_STRANGE (owner, 2026-11-25: "Please set up proper testing for walking under
covered pits and plank-covered pits"). The offline rule is CoverUnder_* (SelfTest/CoverUnderFadeChecks.cs, ba94149031); the only
live row, validation_v2 X8b, proves that a colonist already under a woven scrap cover stays below. No live check ordered a
colonist to walk under any cover kind. This scene does, on every kind.

The opportunity is the walk save that walk_map.py stages (stations 43-45): three 3 m pits 3 x 9, each with one cover kind over
its middle 3 x 3 (woven scrap, planks, reinforced frame), one colonist already under the cover and one walker in the open south
end. The pit is 3 wide and the cover spans it, so a walker who reaches the open north end has walked under the cover.
Between the order and the far end, each walker's cell under the cover is read by state (RM_PromotionProofs.ProofBeneath:
band or beneath True, faded True), never by picture.

    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\FlowWorks\\northstar\\scene_walk_under_cover.py
    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\FlowWorks\\northstar\\scene_walk_under_cover.py --plant walk_under_off
The planted fault switches the walk-under setting off (RM_SuspensionSettings.suspensionWalkUnder, shipped on): no walker may
then pass under a cover, and the scene must read MOD FAILURE or no success.
"""
import scene
from scene import cond as c

GAME, SAVE = "ArchBig", "FLOWWORKS_WALK_MAP_20261125"
OZ = 100                                            # walk_map.ROWS "covers": the pits' south row; covers on OZ+3..OZ+5
PITS = (14, 19, 24)                                 # the pits' west columns (woven scrap, planks, reinforced frame)
WALKERS = ["Human21371", "Human21386", "Human21401"]  # in the open south end (x0+1, OZ+1) of each pit in that save
W = ["walkers[0]", "walkers[1]", "walkers[2]"]
NORTH = OZ + 6                                      # the open north end: rows OZ+6..OZ+8
SUSP = "RimMandrake.FlowWorks.Pits.RM_SuspensionSettings"
TICKS = 3000                                        # hang guard: a 7-square walk takes a few hundred ticks; 10x and more


def z_of(w):
    return c.value(w, "positionInt.z")


walk = scene.contract(
    claim="a colonist ordered along a covered pit floor walks under each pit cover kind and out the far end", kind="A",
    exposure=c.all_(*[z_of(w) < OZ + 3 for w in W]),
    success=[z_of(w) >= NORTH for w in W],
    forbidden=[c.value(w, "health.Downed") == True for w in W],   # noqa: E712 - a condition, not a bool test
    end=c.all_(*[z_of(w) >= NORTH for w in W]), limit=TICKS)

planted = scene.plant() == "walk_under_off"
overlay = {"name": "walk_under_off", "entries": [{"typeName": SUSP, "field": "suspensionWalkUnder", "value": "False"}]} if planted else "none"

with scene.open(GAME, contract=walk, needs={"mods": ["FlowWorks"], "map": SAVE, "calm": "standard", "overlay": overlay}) as s:
    s.stage(cast={"walkers": dict(take=WALKERS)})
    with s.act.batch() as b:
        for w, x0 in zip(W, PITS):
            b.job(w, "Goto", cell=(x0 + 1, OZ + 7), name="walk north")
    under = s.run(until=c.any_(*[z_of(w).in_(OZ + 3, OZ + 5) for w in W]), limit=TICKS)
    fades = []
    for w, x0 in zip(W, PITS):
        v = s.read(w, "positionInt")
        x, *_y, z = (int(n) for n in str(v.v).split(",")) if v.state == "ok" else (None, None)
        if z is not None and OZ + 3 <= z <= OZ + 5:
            r = s.raw("jawa/static_call", type="RimMandrake.FlowWorks.RM_PromotionProofs", method="ProofBeneath", args="%d,%d" % (x, z)) or {}
            txt = str(r.get("result") or r.get("message") or r)
            fades.append("%s at %d,%d: %s" % (w, x, z, txt[:200]))
    run = s.run(until=walk.end, limit=TICKS)
    print(run, run.receipt)
    folder = s.run_dir
print("FADE READS (want band=True or beneath=True, faded=True for each walker under its cover):")
for f in fades:
    print("  " + f)
print(scene.judge(folder))
