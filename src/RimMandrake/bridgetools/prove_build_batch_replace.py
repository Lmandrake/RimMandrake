"""Live proof of BUILDBATCH_FIX_REPLACE_LEAVES_OLD_THING (clause A1): jawa/build_batch replacing a same-def thing at
the same cell leaves ONE thing there, not two, and reports the destruction only when it happened.

    python.exe src/RimMandrake/bridgetools/prove_build_batch_replace.py < /dev/null

Needs a quicktest (or any throwaway) map on a list holding FlowWorks (RM_Ladder, isEdifice=false: the def the bug
was caught on, because GenSpawn.SpawningWipes never wipes one non-edifice with another) and the companion built at or
after this item. Steps:
  1. clear a small rect near the map centre and place an UNOWNED RM_Ladder (faction none);
  2. build_batch RM_Ladder on the same cell, faction player, wipeExisting=true: displaced[] must name it with
     sameDefReplacedInPlace=true, failed[] must be empty, and list_things on that cell must hold exactly ONE
     RM_Ladder, owned by the player, whose id is not the old one;
  3. build_batch RM_Ladder there again with wipeExisting=false: it must be REFUSED (failed[] non-empty, survived 0)
     and the cell must still hold exactly one RM_Ladder, the same id as after step 2.
  The rect is cleared afterwards. Exit 0 = every clause held, 1 = a clause failed, 2 = no verdict (no bridge, no map,
  no RM_Ladder def, the first ladder could not be placed).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
import rimbridge_client as rb  # noqa: E402

LADDER = "RM_Ladder"


def ladders_at(c, x, z):
    r = c.call("jawa/list_things", {"defName": LADDER, "rect": "%d,%d,1,1" % (x, z)}, check=False)
    r = r if isinstance(r, dict) else {}
    return [t for t in (r.get("things") or []) if isinstance(t, dict)], r


def main():
    h, p, t = rb.resolve_endpoint()
    c = rb.RimBridge(host=h, port=p, token=t, timeout=120)
    c.connect()
    mi = c.call("jawa/map_info", {}, check=False)
    mi = mi if isinstance(mi, dict) else {}
    sx, sz = int(mi.get("sizeX") or 0), int(mi.get("sizeZ") or mi.get("sizeY") or 0)
    if sx <= 20 or sz <= 20:
        print("NO VERDICT: map_info gave no map: %s" % str(mi)[:200])
        return 2
    x, z = sx // 2 + 7, sz // 2 + 7
    rect = "%d,%d,3,3" % (x - 1, z - 1)
    c.call("jawa/destroy_batch", {"rects": rect, "categories": "Plant,Item,Filth,Building"}, check=False)
    fails = []
    try:
        a = c.call("jawa/build_batch", {"ops": "%s:%d,%d" % (LADDER, x, z), "faction": "none"}, check=False)
        a = a if isinstance(a, dict) else {}
        before, _ = ladders_at(c, x, z)
        if int(a.get("survived") or 0) != 1 or len(before) != 1:
            print("NO VERDICT: could not place the unowned %s at %d,%d: %s / %s" % (LADDER, x, z, str(a)[:300], before))
            return 2
        old_id = before[0].get("id")
        b = c.call("jawa/build_batch", {"ops": "%s:%d,%d" % (LADDER, x, z), "faction": "player", "wipeExisting": True},
                   check=False)
        b = b if isinstance(b, dict) else {}
        disp = b.get("displaced") or []
        print("replace: survived=%s failed=%s displaced=%s" % (b.get("survived"), b.get("failed"), disp))
        if b.get("failed"):
            fails.append("the replace reported failed[]: %s" % b.get("failed"))
        if not any(d.get("destroyed") == LADDER and d.get("sameDefReplacedInPlace") for d in disp if isinstance(d, dict)):
            fails.append("displaced[] does not name the replaced %s" % LADDER)
        after, raw = ladders_at(c, x, z)
        print("after replace: %s" % [(t.get("id"), t.get("faction")) for t in after])
        if len(after) != 1:
            fails.append("cell %d,%d holds %d %s after the replace (want 1): %s" % (x, z, len(after), LADDER, after))
        else:
            if after[0].get("id") == old_id:
                fails.append("the surviving ladder is the OLD one %s" % old_id)
            if not after[0].get("faction"):
                fails.append("the surviving ladder is unowned: %s" % after[0])
        new_id = after[0].get("id") if len(after) == 1 else None
        r = c.call("jawa/build_batch", {"ops": "%s:%d,%d" % (LADDER, x, z), "faction": "player", "wipeExisting": False},
                   check=False)
        r = r if isinstance(r, dict) else {}
        print("wipeExisting=false: survived=%s failed=%s" % (r.get("survived"), r.get("failed")))
        if not r.get("failed") or int(r.get("survived") or 0) != 0:
            fails.append("wipeExisting=false over a same-def ladder was not refused: %s" % str(r)[:300])
        last, _ = ladders_at(c, x, z)
        if len(last) != 1 or last[0].get("id") != new_id:
            fails.append("after the refused op the cell holds %s (want only %s)" % ([t.get("id") for t in last], new_id))
    finally:
        c.call("jawa/destroy_batch", {"rects": rect, "categories": "Building"}, check=False)
    if fails:
        print("FAIL A1:\n  " + "\n  ".join(fails))
        return 1
    print("PASS A1: replacing %s %s at %d,%d left one ladder (%s, player), and wipeExisting=false refused a second"
          % (LADDER, old_id, x, z, new_id))
    return 0


if __name__ == "__main__":
    sys.exit(main())
