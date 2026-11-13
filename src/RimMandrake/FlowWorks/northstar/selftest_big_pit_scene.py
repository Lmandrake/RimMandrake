#!/usr/bin/env python3
"""Offline test of big_pit_scene.py's pure half: no bridge, no game. Written first and run against the first-series layout
(the 2026-11-12 BP0-BP6 builder: boxes on a 4-cell pitch, singles on the east column x=15, 2x2 things centred on row z=14),
which it must flag; then against pack_layout."""
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import big_pit_scene as S  # noqa: E402

# Core sizes read from the 1.6 Defs XML; the three RM sizes the harness reads live are taken as 2x2 here (worst plausible)
SIZES = {"SculptureGrand": (2, 2), "DoubleBed": (2, 2), "RM_GlowTank": (2, 2), "RM_HoseReel": (2, 2), "Table2x2c": (2, 2),
         "TableButcher": (3, 1), "HandTailoringBench": (3, 1), "SculptureLarge": (1, 1), "Bed": (1, 2), "Shelf": (2, 1),
         "Dresser": (2, 1), "RM_ResinSealingJarShelf": (2, 1), "Bedroll": (1, 2), "Battery": (1, 2), "PlantPot": (1, 1),
         "SculptureSmall": (1, 1), "DiningChair": (1, 1), "Stool": (1, 1), "Armchair": (1, 1), "EndTable": (1, 1),
         "StandingLamp": (1, 1), "TorchLamp": (1, 1), "Cooler": (1, 1), "RM_BrineCrock": (1, 1), "RM_EvaporativeCrock": (1, 1),
         "RM_AncientStasisLocker_Refurbished": (2, 2)}
# the first series: (def, centre i, centre j); the north row j=14 and the east column i=15 sat on the wall
OLD_FURN = [("SculptureGrand", 1, 14), ("DoubleBed", 5, 14), ("RM_GlowTank", 9, 14), ("RM_HoseReel", 13, 14),
            ("DiningChair", 15, 1), ("Stool", 15, 3), ("Armchair", 15, 5), ("EndTable", 15, 7), ("Cooler", 15, 13),
            ("Bed", 1, 6), ("Bedroll", 1, 2)]


class FakeBridge:
    """A bridge answering only what plan and verify read: a flat map with a geyser, the def rows, one dry-built scene."""
    def __init__(self, geysers, built=None, hp_drift=False, wild=()):
        self.geysers, self.built, self.hp_drift, self.wild = geysers, built or [], hp_drift, wild

    def ticks(self, n):
        pass

    def call(self, tool, **kw):
        if tool == "jawa/map_info":
            return {"sizeX": 250, "sizeZ": 250}
        if tool == "jawa/list_things" and kw.get("defName") == "SteamGeyser":
            return {"things": [{"def": "SteamGeyser", "x": x, "z": z} for x, z in self.geysers]}
        if tool == "jawa/get_defs":
            rows = []
            for ref in kw["defs"].split(";"):
                dn = ref.split("/")[1]
                rows.append({"defName": dn, "fields": {"size": "(%d,%d)" % SIZES.get(dn, (1, 1)),
                                                        "stuffCategories": ["Woody"] if dn in ("Bed", "Armchair") else [],
                                                        "stackLimit": 75}})
            return {"defs": rows}
        if tool == "jawa/list_things":
            x0, z0, w, h = [int(v) for v in kw["rect"].split(",")]
            return {"things": [t for t in self.built if x0 <= t["x"] < x0 + w and z0 <= t["z"] < z0 + h]}
        if tool == "jawa/flowworks_excavation_rect":
            return {"rows": [{"x": kw["x"] + i, "z": kw["z"] + j, "d": S.DEPTH, "f": self.fill_of(kw["x"], kw["z"])}
                             for i in range(kw["w"]) for j in range(kw["h"])]}
        if tool == "jawa/list_pawns":
            return {"pawns": [{"id": "Thing_W", "kind": k, "x": 1, "z": 1} for k in self.wild]}
        return {"success": True}

    def fill_of(self, x, z):
        return {(cx, cz): f for _k, cx, cz, f, _fl in S.copies_for(self.origin)}[(x, z)]


def fake_things(plan, origin, hp=100):
    out = []
    for k, x0, z0, f, fl in S.copies_for(origin):
        for kind, _k2, dn, _src, (i, j), n in plan["things"]:
            d = "MinifiedThing" if kind == "mini" else "Corpse_" + dn if kind == "corpse" else dn
            out.append({"def": d, "x": x0 + i, "z": z0 + j, "stackCount": n, "hitPoints": hp, "maxHitPoints": 100,
                        "stuff": "WoodLog" if dn in plan["stuff"] else None, "rotation": 0})
    return out


def live_half(fails_check):
    import json
    import tempfile
    out = tempfile.mkdtemp()
    S.OUT, S.STEP = out, "plan"
    S.B = FakeBridge([(50, 100)])
    S.B.origin = S.DEFAULT_ORIGIN
    S.ROWS[:] = []
    ok = S.do_plan(None)
    plan = json.load(open(os.path.join(out, "scene_plan.json")))
    fails_check(ok and plan["origin"] != list(S.DEFAULT_ORIGIN), "plan moves off the geyser at (50,100): origin %s" % plan["origin"])
    fails_check(plan["stuff"] == {"Bed": "WoodLog", "Armchair": "WoodLog"}, "plan reads stuff only for stuffable defs: %s" % plan["stuff"])
    fails_check(len(json.load(open(os.path.join(out, "capture_list.json")))) == 9, "capture_list.json: deepest + 7 copies + overview")
    return plan, out


def main():
    fails, count = [], [0]

    def check(ok, msg):
        count[0] += 1
        if not ok:
            fails.append(msg)

    # --- the old layout is caught (planted fault: must read red)
    bad = [d for d, i, j in OLD_FURN if not S.inside(S.footprint(i, j, *SIZES[d], 0))]
    check(len(bad) >= 6, "the first series' outer ring is flagged outside the margin (got %s)" % bad)

    # --- footprint: every rotation and size, even sides never shrink, E/W swap
    for w, h, rot in itertools.product(range(1, 5), range(1, 5), range(4)):
        fp = S.footprint(5, 5, w, h, rot)
        ww, hh = (h, w) if rot % 2 else (w, h)
        check(len(fp) >= ww * hh, "footprint %dx%d rot %d covers at least its %d cells (%d)" % (w, h, rot, ww * hh, len(fp)))
        check((5, 5) in fp, "footprint %dx%d rot %d holds its centre" % (w, h, rot))
    check(S.footprint(5, 5, 2, 1, 1) == S.footprint(5, 5, 1, 2, 0), "rot 1 swaps width and height")

    # --- pack_layout: the real scene, every footprint cell inside the dug rect with the margin kept, no overlap
    rows = S.scene_things(SIZES)
    check(len(rows) == len(S.FURN) + len(S.ITEMS) + len(S.MINI) + len(S.CORPSES), "every planned thing has a row")
    used = {}
    for kind, key, dn, _src, (i, j), _n in rows:
        w, h = SIZES[dn] if kind == "furn" else (1, 1)
        for rot in range(4):    # the layout is rot 0, but a thing turned in place must still sit inside the pit (rot-safe box)
            cells = S.footprint(i, j, w, h, rot) if w == h else S.footprint(i, j, w, h, 0)
            check(all(0 <= x < S.PW and 0 <= z < S.PW for x, z in cells), "%s rot %d: a footprint cell is outside the dug rect" % (key, rot))
        cells = S.footprint(i, j, w, h, 0)
        check(S.inside(cells), "%s: footprint %s leaves the margin-%d interior" % (key, sorted(cells)[:2], S.MARGIN))
        for c in cells:
            check(c not in used, "%s overlaps %s at %s" % (key, used.get(c), c))
            used[c] = key
    check(all(S.MARGIN <= x < S.PW - S.MARGIN and S.MARGIN <= z < S.PW - S.MARGIN for x, z in used), "no used cell touches a wall")
    # planted fault: a margin-0 layout puts something on the wall ring, which the margin-1 check must see
    wall = S.pack_layout({"a": (1, 1)}, margin=0)["a"]
    check(not S.inside(S.footprint(wall[0], wall[1], 1, 1, 0)), "margin-0 layout lands on the wall ring and is flagged")
    # a thing too big to fit is a refusal, never a spill
    try:
        S.pack_layout({"huge": (15, 15)})
        check(False, "a 15x15 thing in a 14x14 interior must raise LayoutError")
    except S.LayoutError:
        check(True, "")
    try:
        S.scene_things({k: v for k, v in SIZES.items() if k != "Bed"})
        check(False, "a missing size must raise, never be guessed")
    except S.LayoutError:
        check(True, "")
    # the layout also fits when every furniture piece is a 3x3 (a worse-than-real case)
    try:
        S.scene_things({k: (3, 3) for k in SIZES})
        check(False, "26 pieces of 3x3 cannot fit in 14x14: must raise")
    except S.LayoutError:
        check(True, "")
    check(len(S.FURN) == 26 and len(S.ITEMS) == 35, "scene content counts are the first series' (26 furniture, 35 items)")

    # --- stuff: a stuffable def always gets a stuff from its own categories; a stuffless one none
    check(S.pick_stuff(None) is None and S.pick_stuff([]) is None, "no categories -> no stuff")
    check(S.pick_stuff(["Metallic", "Woody"]) == "Steel", "metal first")
    check(S.pick_stuff(["Woody", "Stony"]) == "WoodLog", "wood when no metal")
    check(S.pick_stuff(["Stony"]) == "BlocksGranite", "stone for sculptures")
    check(S.pick_stuff("Fabric") == "Cloth", "a bare string is one category")
    check(S.pick_stuff(["Fabric", "Leathery"]) == "Cloth", "apparel gets cloth")
    try:
        S.pick_stuff(["Gaseous"])
        check(False, "an unknown category must raise")
    except S.LayoutError:
        check(True, "")

    # --- parse
    check(S.parse_size("(2,3)") == (2, 3) and S.parse_size([2, 3]) == (2, 3) and S.parse_size({"x": 2, "z": 3}) == (2, 3), "size shapes")
    check(S.parse_size(None) is None and S.parse_size("") is None and S.parse_size("(0,2)") is None, "unreadable size is None")
    got = S.parse_def_rows({"defs": [{"defName": "A", "fields": {"size": "(1,2)", "stuffCategories": ["Woody"]}}]}, ("size", "stuffCategories"))
    check(got == {"A": {"size": "(1,2)", "stuffCategories": ["Woody"]}}, "get_defs rows parse")

    # --- origin: avoid geysers
    check(S.choose_origin(250, []) == S.DEFAULT_ORIGIN, "no geyser: the preferred origin")
    ox, oz = S.DEFAULT_ORIGIN
    o = S.choose_origin(250, [(ox + 13, oz + 8 + 0)])
    check(o is not None and o != S.DEFAULT_ORIGIN, "a geyser inside the site moves the origin")
    x0, z0, w, h = S.site_rect(o)
    check(not (x0 - S.GEYSER_CLEAR <= ox + 13 < x0 + w + S.GEYSER_CLEAR and z0 - S.GEYSER_CLEAR <= oz + 8 < z0 + h + S.GEYSER_CLEAR),
          "the new site keeps the geyser clear")
    check(S.choose_origin(250, [(ox - S.GEYSER_CLEAR + 1, oz + 5)]) != S.DEFAULT_ORIGIN, "a geyser just outside the rect but inside the clearance moves it")
    check(S.choose_origin(250, [(ox - S.GEYSER_CLEAR - 1, oz + 5)]) == S.DEFAULT_ORIGIN, "a geyser beyond the clearance does not")
    check(S.choose_origin(100, [(x, z) for x in range(0, 100, 6) for z in range(0, 100, 6)]) is None, "geysers everywhere: None, not a bad site")
    for o in (S.DEFAULT_ORIGIN, (60, 30)):
        for k, x, z, f, fl in S.copies_for(o):
            check(S.site_rect(o)[0] <= x and x + S.PW <= S.site_rect(o)[0] + S.SITE_W and z + S.PW <= S.site_rect(o)[1] + S.SITE_H,
                  "copy %s lies inside the site rect for origin %s" % (k, o))

    # --- copies don't overlap, fills as in the first series
    cps = S.copies_for(S.DEFAULT_ORIGIN)
    for (a, ax, az, *_), (b, bx, bz, *_) in itertools.combinations(cps, 2):
        check(abs(ax - bx) >= S.PW or abs(az - bz) >= S.PW, "copies %s and %s do not overlap" % (a, b))
    check(cps[0][:3] == ("BP0_dry", 42, 111) and cps[6][3:] == (3, "RM_Fluid_Tar"), "the first series' coordinates and fills are kept")

    # --- labels, HP baseline, capture list
    check(S.expected_label(8, 0, "water") == "Pit, 4.0 m deep", "dry label")
    check(S.expected_label(8, 3, "tar") == "Pit, 1.5 m tar in 4.0 m", "tar label")
    check(S.expected_label(5, 2, "water") == "Pit, 1.0 m water in 2.5 m", "wet label, exact depth not a band")
    check(S.expected_label(0, 0, "water") is None, "an undug cell has no pit label")
    check("or more" not in S.expected_label(8, 8, "water") and "Canal" not in S.expected_label(2, 0, "water"), "never a band or 'Canal'")
    check(S.judge_hp(36, 36) == "PASS" and S.judge_hp(35, 36) == "FAIL" and S.judge_hp(36, None) == "UNMEASURED",
          "HP is judged against the spawn baseline; a knife born at 36/100 PASSes at 36")
    caps = S.capture_list(S.DEFAULT_ORIGIN)
    check(caps[0]["name"] == "deepest_BP5_brim", "the deepest water copy is first: %s" % caps[0]["name"])
    check([c["name"] for c in caps[1:8]] == [c[0] for c in cps] and caps[-1]["name"] == "overview", "each copy then the overview")
    check(all(c["rect"][2] > 0 and c["rootSize"] > 0 for c in caps), "every capture has a rect and a zoom")
    t = {"def": "Dresser", "x": 50, "z": 99, "rotation": 0}
    v, det = S.judge_thing(t, 42, 99, 4, ("Dresser", 8, 0), SIZES)
    check(v == "FAIL" and not det["inPit"], "a thing on the wall row reads FAIL, not in pit")
    v, det = S.judge_thing({"def": "Dresser", "x": 50, "z": 114, "rotation": 0}, 42, 111, 4, ("Dresser", 8, 3), SIZES)
    check(v == "PASS" and det["liquidOverM"] == 2.0, "an inside thing at its cell reads PASS with 2.0 m over it")

    plan0 = {"origin": list(S.DEFAULT_ORIGIN), "site": list(S.site_rect(S.DEFAULT_ORIGIN)), "copies": S.copies_for(S.DEFAULT_ORIGIN),
             "things": S.scene_things(SIZES), "stuff": {"Bed": "WoodLog"}}
    md = S.key_markdown(plan0, provisional=True)
    check(all(c[0] in md for c in plan0["copies"]) and all(f[0] in md for f in S.FURN) and "PROVISIONAL" in md, "the key names every copy and every furniture def")
    check(md.count("| item |") == len(S.ITEMS) and md.count("| corpse |") == 2 and "Muffalo" in md, "the key lists items and corpses")

    # --- the live half against a fake bridge: plan, then verify (catches wiring errors; nothing here touches a game)
    plan, out = live_half(check)
    origin = tuple(plan["origin"])
    S.sky_gate = lambda *a, **k: None

    def run_verify(things, wild=(), baseline_hp=100):
        import json
        S.B = FakeBridge([], things, wild=wild)
        S.B.origin = origin
        S.ROWS[:] = []
        base = {}
        for k, x0, z0, f, fl in S.copies_for(origin):
            base[k] = {"%s@%d,%d" % (t["def"], t["x"] - x0, t["z"] - z0): baseline_hp for t in things
                       if x0 <= t["x"] < x0 + S.PW and z0 <= t["z"] < z0 + S.PW}
        json.dump(base, open(os.path.join(out, "spawn_baseline.json"), "w"))
        S.verify(plan)
        return {r["row"]: r["verdict"] for r in S.ROWS}

    v = run_verify(fake_things(plan, origin))
    bad = {k: x for k, x in v.items() if x != "PASS"}
    check(set(bad) == {"label_onscreen_text"}, "a clean fake scene PASSes every row but the on-screen label read (UNMEASURED): %s" % list(bad.items())[:6])
    check(any(k.endswith("_furn_Bed") for k in v) and any("_corpse_Villager" in k for k in v), "one row per building kind and per corpse")
    check(sum(1 for k in v if "_furn_" in k) == 7 * len(S.FURN), "a furniture row per kind per copy")
    t = fake_things(plan, origin)
    t[5]["hitPoints"] = 50       # a spawned HP of 50/100 is fine when the baseline was 50; here the baseline says 100
    v = run_verify(t)
    check(any(x == "FAIL" for k, x in v.items() if "_furn_" in k or "_item_" in k), "HP changed since spawn reads FAIL")
    t = fake_things(plan, origin)
    for x in t:
        x["hitPoints"] = 36
    v = run_verify(t, baseline_hp=36)
    check(all(x == "PASS" for k, x in v.items() if "_furn_" in k or "_item_" in k), "every thing born at 36 HP and still 36 PASSes (the knife lesson)")
    t = fake_things(plan, origin)
    k0 = next(i for i, x in enumerate(t) if x["def"] == "Bed")
    t[k0]["x"] = origin[0] + 2 + 0      # onto the wall column of copy BP0
    t[k0]["z"] = origin[1] + 22
    v = run_verify(t)
    check(v.get("BP0_dry_furn_Bed") == "FAIL" and v.get("BP0_dry_inside_margin") == "FAIL", "a bed on the wall ring reads FAIL")
    t = fake_things(plan, origin)
    for x in t:
        if x["def"] in plan["stuff"]:
            x["stuff"] = None
    v = run_verify(t)
    check(v.get("BP0_dry_furn_Bed") == "FAIL", "a stuffable thing made with no stuff reads FAIL")
    v = run_verify(fake_things(plan, origin), wild=("Segnosaurus",))
    check(v.get("wildlife_none_on_map") == "FAIL", "a wild animal on the map reads FAIL")
    t = fake_things(plan, origin)
    t.append({"def": "SteamGeyser", "x": origin[0] + 21, "z": origin[1] + 2, "stackCount": 1})
    v = run_verify(t)
    check(v.get("BP5_brim_nothing_unplanned") == "FAIL", "an unplanned thing in a copy reads FAIL")

    n = count[0]
    for f in fails:
        print("FAIL", f)
    print("%s %d/%d" % ("PASS" if not fails else "FAIL", n - len(fails), n))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
