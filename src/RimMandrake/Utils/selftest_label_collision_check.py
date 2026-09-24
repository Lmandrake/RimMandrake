#!/usr/bin/env python3
"""selftest_label_collision_check.py — proves label_collision_check.py's
verdict logic, independent of whatever the live dump currently looks like.

Same two-halves shape as this repo's other db-backed selftests
(selftest_ecosystem_pyramid_check.py):

  1. PURE LOGIC on synthetic (defName -> label) / (defName -> biomes) maps —
     runs anywhere, no game, no dump, no network. This is the half that
     protects the DUPLICATE_CANON_DEFNAME_PAIRS_1 fix from being silently
     reintroduced.
  2. A LIVE SMOKE RUN against the real defs.sqlite, structure-only. Prints
     the project's UNMEASURED phrase and exits non-zero-but-not-FAIL when the
     dump is unreachable (e.g. from the Mac, where DUMP_ROOT is a Windows
     path) — run_selftests.py reads that phrase, not a bare failure.

Run: bare `python3 selftest_label_collision_check.py`, from anywhere.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import label_collision_check as lcc                    # noqa: E402

UNMEASURED_PHRASE = "UNMEASURED, not a pass or a fail"


def t_no_collision_when_every_cast_defname_has_a_unique_label():
    labels = {"RSW_Gizka": "gizka", "RSW_Kreetle": "kreetle"}
    cast = {"RSW_Gizka": ["RUT_Desert"], "RSW_Kreetle": ["RUT_Desert"]}
    out = lcc.find_collisions(labels, cast)
    assert out == [], out


def t_donor_and_port_cast_under_the_same_label_is_a_collision():
    # The actual DUPLICATE_CANON_DEFNAME_PAIRS_1 shape: two defNames, one
    # label, both cast in different biomes.
    labels = {"Gizka": "gizka", "RSW_Gizka": "gizka"}
    cast = {"Gizka": ["RUT_AridShrubland", "RUT_Greentide"],
            "RSW_Gizka": ["RUT_Desert", "RUT_ExtremeDesert"]}
    out = lcc.find_collisions(labels, cast)
    assert len(out) == 1, out
    c = out[0]
    assert c.label == "gizka", c
    assert c.defnames == ["Gizka", "RSW_Gizka"], c
    assert c.cast_in["Gizka"] == ["RUT_AridShrubland", "RUT_Greentide"], c
    assert c.cast_in["RSW_Gizka"] == ["RUT_Desert", "RUT_ExtremeDesert"], c


def t_installed_but_uncast_donor_def_is_not_a_collision():
    # The donor def exists in the dump (label present) but is not in `cast`
    # at all (nothing wires it into any BiomeDef any more) — this is exactly
    # the post-fix state DUPLICATE_CANON_DEFNAME_PAIRS_1 leaves behind
    # ("Mlie's mod stays installed; its defs simply stop being cast by us").
    labels = {"Gizka": "gizka", "RSW_Gizka": "gizka"}
    cast = {"RSW_Gizka": ["RUT_Desert", "RUT_AridShrubland"]}
    out = lcc.find_collisions(labels, cast)
    assert out == [], out


def t_unresolved_defname_excluded_not_guessed():
    # A cast defName with no known label (ghost / unresolved ThingDef) must
    # not be silently grouped with anything — same "never guess" posture as
    # ecosystem_pyramid_check.py's unresolved handling.
    labels = {"RSW_Gizka": "gizka"}
    cast = {"RSW_Gizka": ["RUT_Desert"], "Ghost_Thing": ["RUT_Desert"]}
    out = lcc.find_collisions(labels, cast)
    assert out == [], out


def t_three_way_collision_reports_all_three_defnames():
    labels = {"A": "shared", "B": "shared", "C": "shared", "D": "other"}
    cast = {"A": ["Biome1"], "B": ["Biome2"], "C": ["Biome3"], "D": ["Biome1"]}
    out = lcc.find_collisions(labels, cast)
    assert len(out) == 1, out
    assert out[0].defnames == ["A", "B", "C"], out


def t_same_defname_two_biomes_is_not_itself_a_collision():
    # One defName cast in multiple biomes is normal and not the defect this
    # checker exists for (that's what wildAnimals is for).
    labels = {"RSW_Gizka": "gizka"}
    cast = {"RSW_Gizka": ["RUT_Desert", "RUT_ExtremeDesert", "RUT_AridShrubland"]}
    out = lcc.find_collisions(labels, cast)
    assert out == [], out


UNIT_TESTS = [
    t_no_collision_when_every_cast_defname_has_a_unique_label,
    t_donor_and_port_cast_under_the_same_label_is_a_collision,
    t_installed_but_uncast_donor_def_is_not_a_collision,
    t_unresolved_defname_excluded_not_guessed,
    t_three_way_collision_reports_all_three_defnames,
    t_same_defname_two_biomes_is_not_itself_a_collision,
]


def main():
    broken = []
    for fn in UNIT_TESTS:
        try:
            fn()
        except AssertionError as exc:
            broken.append("%s: %s" % (fn.__name__, exc))
        except Exception as exc:                       # noqa: BLE001
            broken.append("%s: %r (unexpected exception type)" % (fn.__name__, exc))

    if broken:
        print("%d of %d unit check(s) FAILED:" % (len(broken), len(UNIT_TESTS)))
        for line in broken:
            print("  FAIL " + line)
        return 1

    print("%d/%d pure-logic unit checks passed." % (len(UNIT_TESTS), len(UNIT_TESTS)))

    # Live smoke run — structure only, never a pinned collision list (rosters
    # legitimately change; this only proves the plumbing runs end to end).
    try:
        collisions = lcc.run()
    except RuntimeError as exc:
        msg = str(exc)
        if msg.startswith("UNMEASURED"):
            print(msg)
            print(UNMEASURED_PHRASE)
            return 2
        print("FAIL live run raised an unexpected error: %s" % msg)
        return 1

    print("live smoke run OK: %d label collision(s) found against the "
          "current dump." % len(collisions))
    for c in collisions:
        print("  %s: %s" % (c.label, ", ".join(c.defnames)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
