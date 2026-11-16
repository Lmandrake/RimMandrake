"""Extra station X for the owner look 2026-11-16 (free area, east of the power pad): the kinds the 31 stations lack.

Run from the repo root:  python.exe <this file> | tr -d '\\r'
  room  : a 3x3 steel room; one run crosses the west and east walls, one the south and north walls, meeting
          in a 4-way junction inside (cords into a wall from every face)
  joints: a T, a plus and an L corner on one row, lamps set off-axis so cords leave at varied angles
  door  : a wall line with a steel door and an open gap, a run under each; an in-wall run ends inside the wall
"""
import os, sys
REPO = os.getcwd()
GSS = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack")
for p in (GSS, os.path.join(GSS, "northstar_matrix")):
    sys.path.insert(0, p)
import human_review as h  # noqa: E402
import run_live as RL  # noqa: E402

PL, RM = h.PL, h.RM
TAG = "GSSX"


def ring(x0, z0, x1, z1):
    return [(x, z) for x in range(x0, x1 + 1) for z in range(z0, z1 + 1) if x in (x0, x1) or z in (z0, z1)]


walls = ring(35, 230, 39, 234) + [(x, 238) for x in range(44, 57) if x not in (47, 53)]
conduit = sorted(set([(x, 232) for x in range(33, 42)] + [(37, z) for z in range(228, 237)] +
                     [(x, 229) for x in range(45, 54)] + [(47, 230), (47, 231), (50, 228), (50, 230), (50, 231),
                                                          (53, 230), (53, 231)] +
                     [(47, z) for z in range(235, 242)] + [(53, z) for z in range(235, 242)] +
                     [(x, 235) for x in range(48, 53)] + [(54, 238), (55, 238)]))
batteries = [(32, 232), (44, 229), (50, 236)]
lamps = [(42, 233), (36, 237), (38, 228), (46, 232), (51, 232), (50, 227), (54, 232), (47, 242), (53, 242)]
CELLS = set(walls) | set(conduit) | set(batteries) | set(lamps) | {(47, 238)}
RECT = (31, 226, 27, 18)

if __name__ == "__main__":
    R = h.Review(RL.LiveBridge(), None)
    out = {}
    for d, cells, stuff, rot in (("Wall", walls, "Steel", None), ("Door", [(47, 238)], "Steel", None),
                                 ("PowerConduit", conduit, None, None), ("Battery", batteries, None, 0),
                                 ("StandingLamp", lamps, None, None)):
        kw = {"ops": PL._ops(d, cells, rot), "wipeExisting": False}
        if stuff:
            kw["stuff"] = stuff
        r = R.call("jawa/build_batch", **kw)
        out[d] = "%s/%d %s" % (r.get("survived"), len(cells), (r.get("failed") or [])[:3])
    print("built:", out)
    lt = R.B.call("jawa/list_things", defName="Battery", rect="%d,%d,%d,%d" % RECT, limit=50)
    for t in lt.get("things") or []:
        R.call("jawa/battery_set", thing=t.get("id") or t.get("thingId"), mode="setPct", value=1.0)
    print("batteries charged:", len(lt.get("things") or []))
    R.call("jawa/map_commit")
    lab = "\n".join([
        RM.label_line(44, 225, "X  EXTRA: WALL FACES, JUNCTIONS, DOORWAY", "added for the owner look 2026-11-16: "
                      "cords into every wall face + a 4-way inside the room; T, plus and L corner; a door, an open gap, "
                      "an in-wall run ending in the wall", h.RUST, "medium", TAG),
        RM.label_line(37, 239, "every face", "west/east/south/north wall entries", h.RUST, "small", TAG),
        RM.label_line(49, 233, "T / plus / L", "lamps off-axis: varied cord angles", h.RUST, "small", TAG),
        RM.label_line(50, 243, "door / gap / in-wall", "", h.RUST, "small", TAG)])
    R.B.call("jawa/review_label", action="clear", tag=TAG)
    r = R.B.call("jawa/review_label", action="add", ops=lab, tag=TAG)
    print("labels:", {k: r.get(k) for k in ("success", "added", "refused")})
