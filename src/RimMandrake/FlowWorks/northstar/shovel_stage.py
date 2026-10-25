"""SHOVELS_BUILD_NO_DIGGING_BARE_HANDED: put one RM_Shovel in a test pawn's pack.

Since shovels v1 a colonist (or a raider) without a shovel in the pack gets no dig or fill job: the WorkGiver hands out
a fetch first, or nothing when none lies free. Live runners whose rows are NOT about shovels (gravel, deep stone, quarry
finds, the toggle chains, the raider trench rows) stage one here so their dig rows keep measuring what they measured.
Machine-dig rows stage none: machines dig bare-handed, and that is a row of its own (SH_machine_digs_bare).

`call` is the runner's bridge call (`B.call` or `t.bridge_call`). jawa/pawn_gear action=inventory makes the thing and
TryAddOrTransfers it, and FAILS on 0 moved, so success here is the shovel really in the pack.
"""

SHOVEL = "RM_Shovel"


def give_shovel(call, pawn, stuff="WoodLog"):
    """-> (ok, detail). One shovel into `pawn`'s pack; a FlowWorks without RM_Shovel reads not ok, never silently fine."""
    r = call("jawa/pawn_gear", **{"pawn": str(pawn), "action": "inventory", "def": SHOVEL, "stuff": stuff, "count": 1}) or {}
    ok = bool(r.get("success"))
    return ok, ("shovel in pack" if ok else "pawn_gear refused: %s" % str(r.get("error") or r)[:200])
