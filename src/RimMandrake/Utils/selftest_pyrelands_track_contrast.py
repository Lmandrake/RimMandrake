#!/usr/bin/env python3
"""Footprints in the Pyrelands' ash must be SEEN, and the hover must say ash (offline, from the mod's files).

Owner, 2026-11-08, on the first ash-on-sand build (da4c0d4d9e): "I don't see any footprints, alas." and
"Oops. It says "Windswept sand" on my hover over". The live grid then held 1,603 prints (13,980 laid, 5,854 buried):
the writer, the map component and the biome's buildup surface all worked. The prints were drawn but unseen:
the Pyrelands' RM_TrackSurfaceExtension used the track grid's own sprites, made for pale sand, and on the ash
cover (its texture x the cover tint) they moved the ground by under 12 levels of 255; and buryDepth 0.12 buried
a print in about 2 game hours of AshFall. This test goes red for each of those reasons:

  contrast   every print class on the Pyrelands surface, composited at the track grid's default opacity over
             the ash cover's mean colour x the DRY tint, darkens or lightens its core by >= MIN_DRY levels, and
             >= MIN_WET over the wet tint. Instrument check: the track grid's default sprites must FAIL it (they
             are the 2026-11-08 defect), or the metric cannot see.
  life       buryDepth / (vanilla's deposit a visit at the AshFall sandRate) x the visit interval >= MIN_ASHFALL_HOURS.
  label      the Pyrelands' Keyed file carries RM_Ash and RM_Ash_Label, and PyrelandsAshSand.cs patches both vanilla
             sites (MouseoverReadout.MouseoverReadoutOnGUI, CellInspectorDrawer.DrawMapInspector).

    python3 src/RimMandrake/Utils/selftest_pyrelands_track_contrast.py
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
RM = os.path.dirname(HERE)
PYRE = os.path.join(RM, "Pyrelands")
CB = os.path.join(RM, "CreatureBehaviors")

MIN_DRY = 20.0          # levels of 255 at the print's core, dry ash
MIN_WET = 10.0          # wet ash (darker cover)
MIN_ASHFALL_HOURS = 4.0
# Vanilla SteadyEnvironmentEffects.AddFallenSandAt: 0.046 x SandRate x noise(0.5..1) a visit; a visit every ~1,667 ticks
# (PyrelandsAshSand.cs header). 0.75 is the noise's mean.
DEPOSIT_PER_VISIT_PER_RATE = 0.046 * 0.75
TICKS_PER_VISIT = 1667.0
TICKS_PER_HOUR = 2500.0

EXT_CLASS = "RimMandrake.CreatureBehaviors.RM_TrackSurfaceExtension"
CLASSES = ("humanTexPath", "animalTexPath", "largeTexPath", "dragTexPath")


def fail(msg):
    print("FAIL " + msg)
    return 1


def cs_default(path, field):
    """A C# field's default string or float from its declaration line."""
    src = open(path, encoding="utf-8").read()
    m = re.search(r"\b" + re.escape(field) + r"\s*=\s*(\"[^\"]*\"|[0-9.]+)f?", src)
    if not m:
        raise SystemExit("cannot read %s's default from %s" % (field, path))
    v = m.group(1)
    return v.strip('"') if v.startswith('"') else float(v)


def tex_file(tex_path):
    for mod in (PYRE, CB):
        p = os.path.join(mod, "Textures", *tex_path.split("/")) + ".png"
        if os.path.isfile(p):
            return p
    return None


def core_contrast(tex, ground, opacity):
    """Mean |composite - ground| (luma) over the print's core (alpha >= half its max), opacity x texture alpha."""
    im = Image.open(tex).convert("RGBA")
    px = list(im.getdata())
    amax = max(p[3] for p in px)
    core = [p for p in px if amax and p[3] >= amax / 2]
    if not core:
        return 0.0
    total = 0.0
    for r, g, b, a in core:
        luma = 0.299 * r + 0.587 * g + 0.114 * b
        k = opacity * a / 255.0
        total += abs(ground + k * (luma - ground) - ground)
    return total / len(core)


def main():
    rc = 0
    ext_file = os.path.join(CB, "Source", "RM_TrackSurfaceExtension.cs")
    biome = ET.parse(os.path.join(PYRE, "Defs", "BiomeDefs", "Pyrelands.xml")).getroot()
    exts = [li for li in biome.iter("li") if li.get("Class") == EXT_CLASS]
    if len(exts) != 1:
        return fail("Pyrelands BiomeDef carries %d RM_TrackSurfaceExtension (want 1)" % len(exts))
    ext = exts[0]

    cover_cs = os.path.join(PYRE, "Source", "PyrelandsAshCover.cs")
    src = open(cover_cs, encoding="utf-8").read()
    tints = {}
    for name in ("Tint", "WetTint"):
        m = re.search(r"Color " + name + r" = new Color\(([0-9.]+)f", src)
        if not m:
            return fail("cannot read %s from %s" % (name, cover_cs))
        tints[name] = float(m.group(1))
    m = re.search(r'const string TexPath = "([^"]+)"', src)
    cover = tex_file(m.group(1)) if m else None
    if not cover:
        return fail("ash cover texture not found from %s" % cover_cs)
    cpx = list(Image.open(cover).convert("RGB").getdata())
    cover_luma = sum(0.299 * r + 0.587 * g + 0.114 * b for r, g, b in cpx) / len(cpx)
    opacity = cs_default(os.path.join(CB, "Source", "RM_CreatureBehaviorsMod.cs"), "trackPrintOpacity")

    def check(paths, label):
        bad = []
        for cls, tp in paths.items():
            f = tex_file(tp)
            if not f:
                bad.append("%s %s: texture not found" % (cls, tp))
                continue
            for tint, need in (("Tint", MIN_DRY), ("WetTint", MIN_WET)):
                c = core_contrast(f, cover_luma * tints[tint], opacity)
                print("  %-6s %-13s %-38s %-7s contrast %5.1f (need %.0f)" % (label, cls, tp, tint, c, need))
                if c < need:
                    bad.append("%s %s on %s: %.1f < %.0f" % (cls, tp, tint, c, need))
        return bad

    defaults = {c: cs_default(ext_file, c) for c in CLASSES}
    ours = {c: (ext.findtext(c) or defaults[c]).strip() for c in CLASSES}
    print("ash cover %s mean luma %.1f; tints %s; opacity %.2f" % (os.path.basename(cover), cover_luma, tints, opacity))
    if not check(defaults, "pale"):
        rc |= fail("instrument: the track grid's pale-sand sprites pass on ash, so the metric cannot see the 2026-11-08 defect")
    else:
        print("ok   instrument: the pale-sand sprites fail on ash (the 2026-11-08 defect is visible to this test)")
    bad = check(ours, "ash")
    for b in bad:
        rc |= fail("print unseen on ash: " + b)
    if not bad:
        print("ok   every Pyrelands print class reads on dry and wet ash")

    bury = float(ext.findtext("buryDepth") or cs_default(ext_file, "buryDepth"))
    rate = float(ET.parse(os.path.join(PYRE, "Defs", "WeatherDefs", "AshFall.xml")).getroot().findtext(".//sandRate"))
    hours = bury / (DEPOSIT_PER_VISIT_PER_RATE * rate) * TICKS_PER_VISIT / TICKS_PER_HOUR
    if hours < MIN_ASHFALL_HOURS:
        rc |= fail("a print lasts %.1f h of AshFall (buryDepth %.2f, sandRate %.2f), want >= %.0f" % (hours, bury, rate, MIN_ASHFALL_HOURS))
    else:
        print("ok   a print lasts %.1f h of AshFall (buryDepth %.2f, sandRate %.2f)" % (hours, bury, rate))

    keyed = ET.parse(os.path.join(PYRE, "Languages", "English", "Keyed", "Pyrelands.xml")).getroot()
    sand = open(os.path.join(PYRE, "Source", "PyrelandsAshSand.cs"), encoding="utf-8").read()
    for key in ("RM_Ash", "RM_Ash_Label"):
        v = keyed.findtext(key)
        if not v or "sand" in v.lower():
            rc |= fail("Keyed %s is %r: the hover on ash would not name ash" % (key, v))
    for site in ("nameof(MouseoverReadout.MouseoverReadoutOnGUI)", '"DrawMapInspector"', 'KeyAsh = "RM_Ash"',
                 'KeyAshLabel = "RM_Ash_Label"', "PatchLabels(h, rule);"):
        if site not in sand:
            rc |= fail("PyrelandsAshSand.cs lacks %s: the hover on ash reads \"Windswept sand\"" % site)
    if not rc:
        print("ok   hover label: RM_Ash / RM_Ash_Label keyed, both vanilla sites patched")
    print("PASS" if rc == 0 else "FAILED")
    return rc


if __name__ == "__main__":
    sys.exit(main())
