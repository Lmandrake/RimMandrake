#!/usr/bin/env python3
"""Offline acceptance of the colony station holds (src/RimMandrake/Utils/colony_holds.py), item
RIMMANDRAKE_BUILD_COLONY_STATION_HOLDS_BYSTANDERS_BY_AREA. A fake game that keeps areas, pawn areas and forbidden
state; no bridge. A fake proves what this Python does, never what the game does: the live reading is prove_colony_holds."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)

import colony_holds as C  # noqa: E402
import scene  # noqa: E402
import scene_fake as F  # noqa: E402
import scene_stations as ST  # noqa: E402

MAP = (60, 50)


class Game:
    def __init__(self, pawns):
        self.pawns = {p["id"]: dict(p, area=p.get("area")) for p in pawns}
        self.areas, self.forbid = {}, {}
        self.refuse_area = set()

    def __call__(self, tool, **a):
        if tool == C.LIST_PAWNS:
            return {"success": True, "pawns": [{k: v for k, v in p.items() if k != "area"} for p in self.pawns.values()]}
        if tool == C.NEW_AREA:
            self.areas.setdefault(a["label"], set())
            return {"success": True, "label": a["label"]}
        if tool == C.PAINT:
            cells = self.areas[a["area"]]
            if a.get("clearAreaFirst"):
                cells.clear()
            for r in a["ops"].split(";"):
                x, z, w, h = map(int, r.split(","))
                for i in range(x, x + w):
                    for j in range(z, z + h):
                        (cells.add if a["value"] else cells.discard)((i, j))
            return {"success": True, "failedVerify": 0, "outOfBounds": 0}
        if tool == C.SETTINGS:
            p = self.pawns[a["pawnId"]]
            if "area" in a and a["pawnId"] not in self.refuse_area:
                p["area"] = None if a["area"] in ("none", "clear") else a["area"]
            return {"success": True, "area": p["area"]}
        if tool == C.FORBID:
            self.forbid[a["rect"]] = a["forbidden"]
            return {"success": True, "changed": 3}
        raise AssertionError(tool)


PAWNS = [dict(id="c1", faction="player"), dict(id="c2", faction="player", area="Farm"), dict(id="goat", faction="player", kind="animal"),
         dict(id="cast1", faction="player")]
RECT, MARGIN = (20, 20, 10, 8), 3


def hold(g, **kw):
    return C.hold(g, MAP, RECT, MARGIN, cast=kw.get("cast", ("cast1",)))


def the_area_excludes_the_station_and_its_margin_and_covers_the_rest():
    g = Game(PAWNS)
    h = hold(g)
    cells = g.areas[h["area"]]
    gx0, gz0, gx1, gz1 = RECT[0] - MARGIN, RECT[1] - MARGIN, RECT[0] + RECT[2] + MARGIN, RECT[1] + RECT[3] + MARGIN
    inside = {(x, z) for x in range(gx0, gx1) for z in range(gz0, gz1)}
    assert not (cells & inside), "the area holds %d cell(s) of the station plus margin" % len(cells & inside)
    assert len(cells) == MAP[0] * MAP[1] - len(inside), (len(cells), MAP, len(inside))


def every_colony_pawn_and_animal_is_held_but_not_the_cast():
    g = Game(PAWNS)
    h = hold(g)
    assert sorted(p["id"] for p in h["held"]) == ["c1", "c2", "goat"], h
    assert all(g.pawns[i]["area"] == h["area"] for i in ("c1", "c2", "goat")) and g.pawns["cast1"]["area"] is None, g.pawns


def a_station_on_the_map_edge_still_leaves_a_free_area():
    rs = C.free_rects(MAP, (0, 0, 10, 10), 3)
    cells = {(x, z) for r in rs for x in range(r[0], r[0] + r[2]) for z in range(r[1], r[1] + r[3])}
    assert len(cells) == MAP[0] * MAP[1] - 13 * 13 and (12, 12) not in cells and (13, 13) in cells
    try:
        C.hold(Game(PAWNS), (10, 10), (0, 0, 10, 10), 0)
    except C.HoldFault as e:
        assert e.name == "NO_FREE_CELLS", e
    else:
        raise AssertionError("a station that fills the map was not refused")


def close_gives_each_pawn_its_own_area_back_and_the_things_theirs():
    g = Game(PAWNS)
    h = hold(g)
    lines = C.release(g, h, RECT)
    assert lines == [], lines
    assert g.pawns["c1"]["area"] is None and g.pawns["c2"]["area"] == "Farm" and g.pawns["goat"]["area"] is None, g.pawns
    assert g.forbid["20,20,10,8"] is False and not g.areas[h["area"]], (g.forbid, len(g.areas[h["area"]]))


def the_things_of_the_station_are_set_forbidden():
    g = Game(PAWNS)
    h = hold(g)
    assert g.forbid == {"20,20,10,8": True} and h["forbidden"] == 3, (g.forbid, h)


def a_pawn_the_area_cannot_bind_is_named_not_counted():
    g = Game(PAWNS + [dict(id="draftee", drafted=True), dict(id="mad", mentalState="Wander_Sad"), dict(id="stubborn")])
    g.refuse_area.add("stubborn")
    h = hold(g)
    un = {u["id"]: u["why"] for u in h["unbound"]}
    assert set(un) == {"draftee", "mad", "stubborn"}, un
    assert "drafted" in un["draftee"] and "mental" in un["mad"] and "did not take" in un["stubborn"], un
    assert "draftee" not in [p["id"] for p in h["held"]]
    line = C.receipt_line("st1", h)
    assert "NOT HELD" in line and "draftee (drafted)" in line, line


def a_failed_restore_is_named():
    g = Game(PAWNS)
    h = hold(g)
    g.refuse_area.add("c2")
    lines = C.release(g, h, RECT)
    assert len(lines) == 1 and "c2" in lines[0] and "Farm" in lines[0], lines


def an_unreadable_map_is_could_not_look_and_makes_nothing():
    g = Game(PAWNS)
    made = []

    def call(tool, **a):
        made.append(tool)
        return {"success": False, "message": "no map"} if tool == C.LIST_PAWNS else g(tool, **a)
    try:
        C.hold(call, MAP, RECT, MARGIN)
    except C.HoldFault as e:
        assert e.name == "COULD_NOT_LOOK" and made == [C.LIST_PAWNS], (e, made)
    else:
        raise AssertionError("an unreadable map was held")


def the_scene_takes_the_hold_on_a_colony_station_and_the_receipt_says_so():
    scene.LAUNCH.update(mode="script", commit=None, script=None, plant=None)
    gm = F.FakeGame(run_until=True)
    gm.saves.append("RM_Stage_colony")
    gm.map_size = MAP
    gm.pawns_on = {None: [dict(id="c1"), dict(id="c2")]}
    W = F.FakeWorld(gm)
    W.stage_made("RM_Stage_colony", ST.Stage("RM_Stage_colony", "colony", MAP).to_json())
    scene.WORLD = W
    with scene.open("ArchSmall", needs={"map": "RM_Stage_colony"}) as s:
        c = s.stage(things={"lamp": dict(thing="WallLamp", at=(0, 0))}, station=dict(size=(10, 8), margin=2))
        line = [x for x in c.receipt.could_not_look if x.startswith("shared map")]
        assert line and "held 2 pawn(s)" in line[0], c.receipt.could_not_look
    tools = [t for t, _ in gm.log]
    assert tools.count(C.FORBID) == 2 and tools.count(C.NEW_AREA) == 1, tools     # forbidden at the take, released at the close


def main():
    tests = [v for k, v in sorted(globals().items()) if callable(v) and k.startswith(("the_", "every_", "a_", "an_", "close_"))
             and getattr(v, "__module__", "") == __name__]
    bad = 0
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001
            bad += 1
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, e))
    print("%d/%d passed" % (len(tests) - bad, len(tests)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
