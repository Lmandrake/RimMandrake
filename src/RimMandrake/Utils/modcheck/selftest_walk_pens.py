#!/usr/bin/env python3
"""Selftest for modcheck/walk_pens.py (offline: XML in a temp tree, the real Pyrelands defs, pure layout and site math).

Page: design/specs/2026-11-24-walk-pens/boundary.md. Each check names the promise it tests."""
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_walk_pens_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modcheck import walk_pens as WP  # noqa: E402

fails = []
n_checks = [0]


def check(cond, promise, msg=""):
    n_checks[0] += 1
    if not cond:
        fails.append("%s: %s" % (promise, msg))


def tree(files):
    root = tempfile.mkdtemp()
    for rel, text in files.items():
        p = os.path.join(root, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(text)
    return root


BIOME = """<?xml version="1.0" encoding="utf-8"?>
<Defs>
  <BiomeDef>
    <defName>RM_Testlands</defName>
    <wildAnimals>
      <!-- <RM_Ghost>0.5</RM_Ghost> -->
      <RM_A>0.5</RM_A>
      <RM_B>0.2</RM_B>
      <RM_C>0.1</RM_C>
    </wildAnimals>
  </BiomeDef>
  <BiomeDef>
    <defName>RM_Listlands</defName>
    <wildAnimals>
      <li><animal>RM_L1</animal><commonality>1</commonality></li>
      <li><animal>RM_L2</animal><commonality>1</commonality></li>
    </wildAnimals>
  </BiomeDef>
</Defs>
"""
PATCH = """<?xml version="1.0" encoding="utf-8"?>
<Patch>
  <Operation Class="PatchOperationFindMod">
    <mods><li>Some Mod</li></mods>
    <match Class="PatchOperationAdd">
      <xpath>Defs/BiomeDef[defName="RM_Testlands"]/wildAnimals</xpath>
      <value><RSW_X>0.2</RSW_X><RSW_Y>0.1</RSW_Y></value>
    </match>
  </Operation>
  <Operation Class="PatchOperationRemove">
    <xpath>Defs/BiomeDef[defName="RM_Testlands"]/wildAnimals/RM_C</xpath>
  </Operation>
  <Operation Class="PatchOperationAdd">
    <xpath>Defs/BiomeDef[defName="SomeOtherBiome"]/wildAnimals</xpath>
    <value><RSW_Z>1</RSW_Z></value>
  </Operation>
</Patch>
"""
REPLACE = """<Patch><Operation Class="PatchOperationReplace">
  <xpath>Defs/BiomeDef[defName="RM_Listlands"]/wildAnimals</xpath>
  <value><wildAnimals><RM_R1>1</RM_R1></wildAnimals></value>
</Operation></Patch>"""

_ran = []


def _checks():
    """Every check, once; each records the promise it tests."""
    if _ran:
        return
    _ran.append(True)
    # --- the-roster-is-read-as-elements / patches-add-remove-and-replace
    root = tree({"src/RimMandrake/Testlands/Defs/BiomeDefs/T.xml": BIOME,
                 "src/RimUtinni/UtinniPatches/Patches/WildAnimals_Testlands.xml": PATCH})
    r = WP.roster("Testlands", root=root)
    check(r["from"] == "biome", "the-roster-is-read-as-elements", "from %r" % r.get("from"))
    check("RM_Ghost" not in r["kinds"], "the-roster-is-read-as-elements", "a commented kind is on the roster: %r" % r["kinds"])
    check(set(WP.biome_cast(root, "RM_Listlands")) == {"RM_L1", "RM_L2"}, "the-roster-is-read-as-elements",
          "li form: %r" % WP.biome_cast(root, "RM_Listlands"))
    check("RSW_X" in r["kinds"] and "RSW_Y" in r["kinds"], "patches-add-remove-and-replace", "add (inside FindMod) lost: %r" % r["kinds"])
    check("RM_C" not in r["kinds"], "patches-add-remove-and-replace", "remove ignored: %r" % r["kinds"])
    check("RSW_Z" not in r["kinds"], "patches-add-remove-and-replace", "another biome's patch leaked in: %r" % r["kinds"])
    check("li" not in r["kinds"] and "value" not in r["kinds"], "the-roster-is-read-as-elements", "a tag name is on the roster")
    check(sorted(r["kinds"]) == ["RM_A", "RM_B", "RM_L1", "RM_L2", "RSW_X", "RSW_Y"] and r["biomes"] == ["RM_Listlands", "RM_Testlands"],
          "patches-add-remove-and-replace", "both biomes of the mod, patched: %r" % r)
    root2 = tree({"src/RimMandrake/Listlands/Defs/B.xml": BIOME.replace("RM_Testlands", "RM_Other"),
                  "src/RimUtinni/UtinniPatches/Patches/R.xml": REPLACE})
    check(WP.biome_cast(root2, "RM_Listlands") == ["RM_R1"], "patches-add-remove-and-replace",
          "replace: %r" % WP.biome_cast(root2, "RM_Listlands"))

    # --- a-mod-with-no-biome-uses-its-animal-kinds
    KINDS = """<Defs>
      <ThingDef><defName>RM_Beast</defName><race><intelligence>Animal</intelligence><baseBodySize>1</baseBodySize></race></ThingDef>
      <ThingDef><defName>RM_Person</defName><race><intelligence>Humanlike</intelligence></race></ThingDef>
      <PawnKindDef Abstract="True" Name="RM_BaseKind"><race>RM_Beast</race></PawnKindDef>
      <PawnKindDef><defName>RM_BeastKind</defName><race>RM_Beast</race></PawnKindDef>
      <PawnKindDef><defName>RM_PersonKind</defName><race>RM_Person</race></PawnKindDef>
    </Defs>"""
    root3 = tree({"src/RimStarWars/Beasty/Defs/K.xml": KINDS})
    r3 = WP.roster("Beasty", root=root3)
    check(r3["from"] == "pawnkinds" and r3["kinds"] == ["RM_BeastKind"], "a-mod-with-no-biome-uses-its-animal-kinds", "%r" % r3)
    check(WP.roster("NoSuchMod", root=root3)["kinds"] == [] and WP.roster("NoSuchMod", root=root3)["from"] == "no mod folder",
          "a-mod-with-no-biome-uses-its-animal-kinds", "an absent mod must read 'no mod folder', never a roster")

    # --- the-pyrelands-roster-is-sixteen (the real defs of this repo)
    SIXTEEN = {"RM_FireHawk", "RM_FurnaceBeast", "RM_Ullai", "RM_Emberscythe", "RM_Sytheclaw", "RM_Barbslinger", "RM_FireWasp",
               "RM_Flamefang", "RM_Ashwallow", "RSW_Anooba", "RSW_Iriaz", "RSW_Nuna", "RSW_Orray", "RSW_Zeer", "RSW_Dalgo", "RSW_Gizka"}
    rp = WP.roster("Pyrelands")
    check(set(rp["kinds"]) == SIXTEEN and len(rp["kinds"]) == 16, "the-pyrelands-roster-is-sixteen",
          "got %d: extra %r missing %r" % (len(rp["kinds"]), sorted(set(rp["kinds"]) - SIXTEEN), sorted(SIXTEEN - set(rp["kinds"]))))

    # --- a-pen-is-sized-by-body-size / pens-do-not-overlap / a-pen-has-walls-and-one-door / six-spawn-cells-inside
    sizes = {"RSW_Gizka": 0.18, "RM_FireWasp": 0.79, "RM_Ullai": 1.8, "RM_Barbslinger": 2.5, "RSW_Zeer": 4.5, "RM_FurnaceBeast": 9.0}
    sizes.update({"K%02d" % i: 0.3 + i * 0.4 for i in range(12)})
    pens, W, H = WP.layout(sizes)
    check(len(pens) == len(sizes), "pens-do-not-overlap", "a kind has no pen")
    ordered = sorted(pens, key=lambda p: sizes[p["kind"]])
    check(all(a["w"] <= b["w"] for a, b in zip(ordered, ordered[1:])), "a-pen-is-sized-by-body-size", "a bigger body got a smaller pen")
    for a in pens:
        check(a["x"] >= 0 and a["z"] >= 0 and a["x"] + a["w"] <= W and a["z"] + a["h"] <= H, "pens-do-not-overlap", "pen outside block %r" % a)
        for b in pens:
            if a is b:
                continue
            apart = a["x"] + a["w"] + 2 <= b["x"] or b["x"] + b["w"] + 2 <= a["x"] or \
                a["z"] + a["h"] + 2 <= b["z"] or b["z"] + b["h"] + 2 <= a["z"]
            check(apart, "pens-do-not-overlap", "%s and %s touch or overlap" % (a["kind"], b["kind"]))
    for p in pens:
        walls, door = WP.wall_cells(p), WP.door_cell(p)
        ring = {(x, z) for x in range(p["x"], p["x"] + p["w"]) for z in range(p["z"], p["z"] + p["h"])
                if x in (p["x"], p["x"] + p["w"] - 1) or z in (p["z"], p["z"] + p["h"] - 1)}
        check(door in ring and door not in walls and walls | {door} == ring, "a-pen-has-walls-and-one-door", "pen %s" % p["kind"])
        check(door[0] not in (p["x"], p["x"] + p["w"] - 1), "a-pen-has-walls-and-one-door", "door in a corner %r" % (door,))
        cells = WP.spawn_cells(p)
        inside = all(p["x"] < x < p["x"] + p["w"] - 1 and p["z"] < z < p["z"] + p["h"] - 1 for x, z in cells)
        check(len(set(cells)) == 6 and inside, "six-spawn-cells-inside", "pen %s cells %r" % (p["kind"], cells))

    # --- the-site-never-covers-a-station / no-free-site-is-said
    N = 120
    stations = [(30, 40), (90, 20)]
    blocked = WP.station_cells(stations, radius=12, size=(N, N))
    blocked |= {(x, 100) for x in range(N)}                    # a river across the top
    cost = {(x, z): 1 for x in range(60, 70) for z in range(0, N)}  # poor ground, allowed but dearer
    site = WP.pick_site((N, N), blocked, cost, 40, 20, margin=3)
    check(site is not None, "the-site-never-covers-a-station", "no site on an open map")
    if site:
        ox, oz = site
        cover = {(x, z) for x in range(ox - 3, ox + 40 + 3) for z in range(oz - 3, oz + 20 + 3)}
        check(not (cover & blocked), "the-site-never-covers-a-station", "site %r covers %d blocked cells" % (site, len(cover & blocked)))
        check(all(abs(x - sx) > 12 or abs(z - sz) > 12 for x, z in cover for sx, sz in stations), "the-site-never-covers-a-station",
              "site %r within a station's radius" % (site,))
        check(not (cover & set(cost)), "the-site-never-covers-a-station", "a clean site existed but poor ground was chosen")
    full = {(x, z) for x in range(N) for z in range(N) if (x + z) % 7 == 0}
    check(WP.pick_site((N, N), full, {}, 40, 20, margin=3) is None, "no-free-site-is-said", "a site over blocked cells was returned")
    check(WP.pick_site((30, 30), set(), {}, 40, 20, margin=3) is None, "no-free-site-is-said", "a block larger than the map was placed")

    # --- the-age-plan-is-three-and-three
    three = [(0.0, "AnimalBaby"), (0.2, "AnimalJuvenile"), (0.45, "AnimalAdult")]
    plan = WP.age_plan(three)
    check([g for g, _, _ in plan] == ["Male"] * 3 + ["Female"] * 3, "the-age-plan-is-three-and-three", "genders %r" % plan)
    st = [s for _, s, _ in plan]
    check(st.count("AnimalJuvenile") == 1 and st.count("AnimalBaby") == 1 and st.count("AnimalAdult") == 4,
          "the-age-plan-is-three-and-three", "stages %r" % st)
    for g, s, age in plan:
        check(WP.stage_at(three, age) == s, "the-age-plan-is-three-and-three", "age %s reads %s, planned %s" % (age, WP.stage_at(three, age), s))
    two = WP.age_plan([(0.0, "AnimalBaby"), (0.3, "AnimalAdult")])
    check([s for _, s, _ in two].count("AnimalBaby") == 2, "the-age-plan-is-three-and-three", "two stages: %r" % two)
    one = WP.age_plan([(0.0, "AnimalAdult")])
    check(all(s == "AnimalAdult" for _, s, _ in one), "the-age-plan-is-three-and-three", "one stage: %r" % one)

    # --- the-live-check-reads-state
    good = [{"kindDef": "RM_A", "dead": False, "hostile": False, "inMentalState": False}] * 6
    check(WP.judge_pen("RM_A", good)["verdict"] == "PASS", "the-live-check-reads-state", "six good read %r" % WP.judge_pen("RM_A", good))
    check(WP.judge_pen("RM_A", good[:5])["verdict"] == "FAIL", "the-live-check-reads-state", "five read PASS")
    bad = good[:5] + [{"kindDef": "RM_A", "dead": False, "hostile": True, "inMentalState": False}]
    check(WP.judge_pen("RM_A", bad)["verdict"] == "FAIL", "the-live-check-reads-state", "a hostile read PASS")
    mad = good[:5] + [{"kindDef": "RM_A", "dead": False, "hostile": False, "inMentalState": True}]
    check(WP.judge_pen("RM_A", mad)["verdict"] == "FAIL", "the-live-check-reads-state", "a mental state read PASS")
    other = good[:5] + [{"kindDef": "RM_B", "dead": False, "hostile": False, "inMentalState": False}]
    check(WP.judge_pen("RM_A", other)["verdict"] == "FAIL", "the-live-check-reads-state", "a wrong kind read PASS")
    check(WP.judge_pen("RM_A", None)["verdict"] == "COULD NOT LOOK", "the-live-check-reads-state", "no reading read as a verdict")
    check(WP.exit_code([{"verdict": "PASS"}] * 3) == 0 and WP.exit_code([{"verdict": "PASS"}, {"verdict": "FAIL"}]) == 1 and
          WP.exit_code([{"verdict": "PASS"}, {"verdict": "COULD NOT LOOK"}]) == 2 and WP.exit_code([]) == 2,
          "the-live-check-reads-state", "exit codes")


def _promise(name):
    _checks()
    bad = [f for f in fails if f.startswith(name + ":")]
    assert not bad, "; ".join(bad)


def t_the_roster_is_read_as_elements():
    _promise("the-roster-is-read-as-elements")


def t_patches_add_remove_and_replace():
    _promise("patches-add-remove-and-replace")


def t_the_pyrelands_roster_is_sixteen():
    _promise("the-pyrelands-roster-is-sixteen")


def t_a_mod_with_no_biome_uses_its_animal_kinds():
    _promise("a-mod-with-no-biome-uses-its-animal-kinds")


def t_a_pen_is_sized_by_body_size():
    _promise("a-pen-is-sized-by-body-size")


def t_pens_do_not_overlap():
    _promise("pens-do-not-overlap")


def t_the_site_never_covers_a_station():
    _promise("the-site-never-covers-a-station")


def t_no_free_site_is_said():
    _promise("no-free-site-is-said")


def t_a_pen_has_walls_and_one_door():
    _promise("a-pen-has-walls-and-one-door")


def t_six_spawn_cells_inside():
    _promise("six-spawn-cells-inside")


def t_the_age_plan_is_three_and_three():
    _promise("the-age-plan-is-three-and-three")


def t_the_live_check_reads_state():
    _promise("the-live-check-reads-state")




def main():
    TESTS = [t_the_roster_is_read_as_elements, t_patches_add_remove_and_replace, t_the_pyrelands_roster_is_sixteen, t_a_mod_with_no_biome_uses_its_animal_kinds, t_a_pen_is_sized_by_body_size, t_pens_do_not_overlap, t_the_site_never_covers_a_station, t_no_free_site_is_said, t_a_pen_has_walls_and_one_door, t_six_spawn_cells_inside, t_the_age_plan_is_three_and_three, t_the_live_check_reads_state]
    bad = []
    for t in TESTS:
        try:
            t()
        except AssertionError as e:
            bad.append("%s: %s" % (t.__name__, e))
    if bad:
        print("FAIL selftest_walk_pens: %d of %d promises (%d of %d checks)" % (len(bad), len(TESTS), len(fails), n_checks[0]))
        for b in bad:
            print("  - " + b)
        return 1
    print("PASS selftest_walk_pens: %d of %d promises, %d of %d checks" % (len(TESTS), len(TESTS), n_checks[0], n_checks[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
