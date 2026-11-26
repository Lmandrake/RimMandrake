"""scene_walk_under_cover.py - FlowWorks: a colonist ordered along a pit floor walks under each pit cover kind, the cover fades
over her, and she comes out the far end. Kind A.

RIMMANDRAKE_REBUILD_FLOWWORKS_WALK_MAP_OLD_CODED_AND_STRANGE (owner, 2026-11-25: "Please set up proper testing for walking under
covered pits and plank-covered pits"). The offline rule is CoverUnder_* (SelfTest/CoverUnderFadeChecks.cs, ba94149031); the only
live row, validation_v2 X8b, proves that a colonist already under a woven scrap cover stays below. No live check ordered a
colonist to walk under any cover kind. This scene does, on every kind.

The opportunity is the walk save that walk_map.py stages (stations 43-45): three 3 m pits 3 x 9, each with one cover kind over
its middle 3 x 3 (woven scrap, planks, reinforced frame), one colonist already under the cover and one walker in the open south
end. The pit is 3 wide and the cover spans it, so a walker who reaches the open north end has walked under the cover.
On a first walk to the middle of each cover, each walker's cell is read by state (RM_PromotionProofs.ProofBeneath:
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

    def order(cell_of, what):
        # one act each, not one batch: a batch stops at the first act that is not done, and with walking under switched off
        # the first walker cannot start her walk, so the others were never ordered (planted run, 2026-11-25)
        effects = [s.act.job(w, "Goto", cell=cell_of(x0), name=what) for w, x0 in zip(W, PITS)]
        for e in effects:
            reply = (e.observed or {}).get("reply") or {}
            # the game refused the order itself (bad arguments: live 2026-11-25, a cell sent as a second target): apparatus.
            # The game took the order and the colonist could not start it (reply accepted=True, no path under a cover with
            # walking under switched off): a fact about the mod, judged by where she ends.
            if not getattr(e, "accepted", False) and reply.get("accepted") is not True:
                raise scene.Fault("ACT_NOT_DONE", detail="a walk order was not taken: %r %s" % (e, str(e.observed)[:300]))

    # 1. each walker to the middle of its cover, and the cover over her read by state (not judged: the judge reads the last run)
    order(lambda x0: (x0, OZ + 4), "walk under")    # the west column: the colonist already under stands in the middle one
    s.run(until=c.all_(*[z_of(w) == OZ + 4 for w in W]), limit=TICKS)
    fades = []
    for w, x0 in zip(W, PITS):
        v = s.read(w, "positionInt")
        x, *_y, z = (int(n) for n in str(v.v).split(",")) if v.state == "ok" else (None, None)
        if z == OZ + 4:
            r = s.raw("jawa/static_call", type="RimMandrake.FlowWorks.RM_PromotionProofs", method="ProofBeneath", args="%d,%d" % (x, z)) or {}
            txt = str(r.get("result") or r.get("message") or r)
            ok = ("pawn=%s " % WALKERS[W.index(w)] in txt and ("band=True" in txt or "beneath=True" in txt) and "faded=True" in txt)
        else:
            txt, ok = "not under its cover: at %s" % (v.v,), False
        fades.append((ok, "%s: %s" % (w, txt[:200])))
    # 2. back to the open south end, then 3. the judged walk: south end, under the cover, out the north end
    order(lambda x0: (x0 + 1, OZ + 1), "back south")
    s.run(until=c.all_(*[z_of(w) == OZ + 1 for w in W]), limit=TICKS)
    order(lambda x0: (x0 + 1, OZ + 7), "walk north")
    run = s.run(until=walk.end, limit=TICKS)
    print(run, run.receipt)
    folder = s.run_dir
print("FADE READS (want band=True or beneath=True, faded=True for each walker under its cover):")
for ok, f in fades:
    print("  %s %s" % ("ok  " if ok else "NOT", f))
print("FADE: %d of %d walkers read under a faded cover" % (sum(1 for ok, _f in fades if ok), len(fades)))
print(scene.judge(folder))
