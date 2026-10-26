"""V2_FILLIN_SCENE_STAGE_FILL_MATERIAL: put RM_Gravel on the ground beside a fill-in job pawn.

Since fill costs spoil (DIG_SPOIL_BUILD_GRAVEL_PAYS_ITS_WAY) RM_FillInCanalWorkGiver offers a fill of an unpaid pit only when
gravel, crushed ice or a stone chunk lies free on the map ("No gravel, crushed ice or stone chunks to fill with."). The
validation_v2 E7a/E7b scenes predate the rule, so J_workgiver_selection failed on them. The material must be a thing on the
ground (RM_DigSpoil.FindFillMaterial searches the map, not the pack), so it is spawned with rimworld/spawn_thing, like
gravel_live.py does.

`call` is the runner's bridge call (`B.call`). -> (ok, detail); not ok when any spawn is refused, never silently fine.
"""

GRAVEL = "RM_Gravel"
STACK = 2           # a notch costs 1 gravel; one spare so a merged or half-used stack still pays


def spawn_fill_material(call, spots, stack=STACK):
    """One gravel stack on each (x, z) in `spots`."""
    bad = []
    for x, z in spots:
        r = call("rimworld/spawn_thing", defName=GRAVEL, stackCount=stack, x=x, z=z) or {}
        if r.get("success") is False or r.get("error"):
            bad.append("(%s,%s): %s" % (x, z, str(r.get("error") or r)[:120]))
    return (not bad), ("gravel staged at %d spots" % len(spots) if not bad else "spawn_thing refused: " + "; ".join(bad))
