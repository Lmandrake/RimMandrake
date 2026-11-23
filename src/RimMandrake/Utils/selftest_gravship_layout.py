#!/usr/bin/env python3
"""Tests of gravship_layout.py. Page: design/specs/2026-11-23-gravship-layout-library/boundary.md. Each test has the
name of its promise."""
import os
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gravship_layout as G                                             # noqa: E402

RING = os.path.join(HERE, "..", "..", "..", "design", "Jawa", "worldbuilding", "ship_build", "exported",
                    "Gravship_v2_ring_2026-09-12.xml")                  # a real export: no GravEngine thing


def square(engine_thing=None):
    lay = G.Layout(5, 5, gravEngineX=2, gravEngineZ=2)
    for z in range(1, 4):
        for x in range(1, 4):
            lay.floor(x, z, "MetalTile")
    if engine_thing:
        lay.put(engine_thing[0], engine_thing[1], "GravEngine")
    return lay


def settings(path):
    """Canonical text of each storage/comp block in the file, in file order."""
    out = []
    for t in ET.parse(path).getroot().iterfind("rows/li/li/things/li"):
        for tag in ("exportedStorageSettings", "compSettings"):
            e = t.find(tag)
            if e is not None and e.get("IsNull") != "True":
                out.append(ET.canonicalize(ET.tostring(e, encoding="unicode"), strip_text=True))
    return out


def eq(got, want):
    assert got == want, "got %s, want %s" % (str(got)[:200], str(want)[:200])


def t_a_real_export_validates_without_an_engine_thing():
    eq(G.Layout.load(RING).validate(), [])
    eq(square().validate(), [])


def t_an_engine_thing_away_from_the_coordinates_is_reported():
    eq(square((2, 2)).validate(), [])
    bad = square((1, 2)).validate()
    eq(len(bad), 1)
    assert "(1, 2)" in bad[0], bad[0]


def t_coordinates_on_a_cell_with_no_foundation_are_reported():
    lay = square()
    lay.gravEngineX = 4                                             # the margin
    eq(len(lay.validate()), 1)
    lay.gravEngineX = 9
    assert "outside" in lay.validate()[0], lay.validate()[0]
    lay.gravEngineX = None
    assert "no gravEngineX/Z" in lay.validate()[0], lay.validate()[0]


def t_a_save_keeps_storage_and_comp_settings_and_the_description():
    want = settings(RING)
    eq(len(want), 26)                                 # 14 storage + 12 comp: the probe sees them
    lay = G.Layout.load(RING)
    lay.description = "A ring ship."
    with tempfile.TemporaryDirectory() as d:
        p = lay.save(os.path.join(d, "x.xml"))
        eq(settings(p), want)
        eq(G.Layout.load(p).description, "A ring ship.")


def t_the_round_trip_fails_on_a_dropped_setting():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "x.xml")
        G.Layout.load(RING).save(p)
        eq(G.roundtrip(p)[1], [])
        real = G.Layout.to_element
        def lossy(self):
            root = real(self)
            for t in root.iterfind("rows/li/li/things/li"):
                for e in t.findall("compSettings"):
                    t.remove(e)
            return root
        G.Layout.to_element = lossy
        try:
            assert G.roundtrip(p)[1], 'no difference reported'
        finally:
            G.Layout.to_element = real


def main():
    bad = 0
    for t in (t_a_real_export_validates_without_an_engine_thing,
              t_an_engine_thing_away_from_the_coordinates_is_reported,
              t_coordinates_on_a_cell_with_no_foundation_are_reported,
              t_a_save_keeps_storage_and_comp_settings_and_the_description,
              t_the_round_trip_fails_on_a_dropped_setting):
        try:
            t()
            print("PASS", t.__name__)
        except Exception as e:                                          # a crash is a fail, named
            bad += 1
            print("FAIL", t.__name__, type(e).__name__, e)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
