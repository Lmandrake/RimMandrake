#!/usr/bin/env python3
"""Offline: wind never moves a ground cord (RIMMANDRAKE_CLEAN_SLACK_SWAY_POLE_WIRES_ONLY_NOT_CONDUIT).

Owner, 2026-11-16: "Wires swaying in the wind were supposed to be about power pole wires. Wind wasn't supposed to mess
with conduit-based wiring at all, nor about terminal wires in walls extending cable hanging out."

So no ground cord piece's geometry may depend on wind or on the clock, except the sparking loose end's own flail
(CordMotion.Whip*, real-time, wind-free). Read from the production source:
  1. CordMotion (the ground cords' only motion kernel) defines no sway, ripple or shader-sway function, and no
     function of it takes a wind argument.
  2. The ground-cord draw path (RM_MapComponent_CordGraph, SectionLayer_RM_MessyCords) reads no wind speed, no
     plant-sway preference and no game clock, and calls no motion kernel but the whip.
  3. GimmeSomeSlackSettings carries none of the ground sway settings (sway, swayAmplitude, swayMode, floorRipple),
     neither as a field, nor in the Scribe, the reset or the settings screen.
  4. The pole wires keep theirs: AerialSettings still declares sway and swayStrength (the cleanup must not reach them).
"""
import re
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parent / "Source"


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def read(rel):
    return strip_comments((SRC / rel).read_text(encoding="utf-8"))


GROUND_DRAW = ("RM_MapComponent_CordGraph.cs", "SectionLayer_RM_MessyCords.cs")
GROUND_SETTINGS = ("sway", "swayAmplitude", "swayMode", "floorRipple")


class NoGroundWind(unittest.TestCase):
    def test_motion_kernel_has_no_wind(self):
        src = read("Core/CordMotion.cs")
        for name in ("Sway", "SwayInto", "Ripple", "RippleInto", "ShaderSwayAlpha", "RippleAmp"):
            self.assertIsNone(re.search(r"\b%s\s*[\(=]" % name, src), f"CordMotion still defines {name}")
        sigs = re.findall(r"(?:static|internal|public|private)[^;{()]*\(([^)]*)\)", src)
        windy = [s for s in sigs if re.search(r"\bwind\b", s)]
        self.assertEqual(windy, [], "a CordMotion function still takes a wind argument")

    def test_ground_draw_reads_no_wind_or_clock(self):
        for rel in GROUND_DRAW:
            src = read(rel)
            for pat, what in ((r"windManager|WindSpeed", "wind speed"), (r"PlantWindSway", "plant-sway preference"),
                              (r"CordMotion\.(Sway|Ripple)", "a sway/ripple kernel"),
                              (r"StrandPlant", "the plant-shader strand"), (r"\bSwayW\b|OnSwayTail", "a sway weight")):
                self.assertIsNone(re.search(pat, src), f"{rel} still reads {what}")
        # the game clock schedules sparks and polls in MapComponentTick; it must not reach the per-frame geometry
        g = read("RM_MapComponent_CordGraph.cs")
        motion = g[g.index("private void DrawMotion()"):g.index("private void DrawEffects(")]
        self.assertIsNone(re.search(r"TicksGame", motion), "DrawMotion still reads the game clock")
        self.assertEqual(sorted(set(re.findall(r"CordMotion\.(\w+)\(", motion))), ["WhipInto", "WhipRoom"],
                         "DrawMotion calls a motion kernel other than the whip")
        self.assertIsNone(re.search(r"TicksGame", read("SectionLayer_RM_MessyCords.cs")), "the section print reads the game clock")

    def test_ground_settings_gone(self):
        src = read("GimmeSomeSlackMod.cs")
        cls = src[src.index("class GimmeSomeSlackSettings"):]
        for name in GROUND_SETTINGS:
            self.assertIsNone(re.search(r"public static \w+ %s\s*=" % name, cls), f"field {name} still declared")
            self.assertIsNone(re.search(r'"%s"' % name, cls), f'"{name}" still named (Scribe, reset or screen)')
        self.assertIsNone(re.search(r"\benum SwayMode\b", src), "SwayMode enum still declared")

    def test_cord_builder_has_no_sway_fields(self):
        src = read("Core/CordBuilder.cs")
        self.assertIsNone(re.search(r"\bSwayW\b|\bOnSwayTail\b", src), "CordBuilder still declares a sway weight")

    def test_pole_wires_keep_their_sway(self):
        src = read("Aerial/AerialSettings.cs")
        self.assertTrue(re.search(r"public static WireSwayMode sway\s*=", src), "pole-wire sway mode gone")
        self.assertTrue(re.search(r"public static float swayStrength\s*=", src), "pole-wire swayStrength gone")


if __name__ == "__main__":
    r = unittest.main(exit=False, verbosity=1).result
    sys.exit(0 if r.wasSuccessful() else 1)
